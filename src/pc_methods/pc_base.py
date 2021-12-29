import yaml
import json
import time
import logging
import functools
from tqdm import tqdm
import subprocess as sp
from pathlib import Path
from multiprocessing import Pool
from dataclasses import dataclass
from src.pc_methods.dir_base import Directory
from src.evaluation.evaluate import Evaluator
from typing import Union, List, Iterable, Dict

logger = logging.getLogger(__name__)


@dataclass
class Base:
    orig_pc: Union[str, Path] = None
    enc_pc: Union[str, Path] = None
    dec_pc: Union[str, Path] = None
    cfg_file: Union[str, Path] = None
    cfg: Dict[str, str] = None
    id: int = None
    rate_name: str = None
    resolution: int = None
    color: bool = None

    def __post_init__(self):
        directory = Directory()
        self.dataset_dir = directory.dataset_dir
        self.expt_dir = directory.experiments_dir
        self.pcerror = directory.pcerror
        self.cfg_dir = directory.cfg_dir

        pc_methods_name = self.get_pc_method_name()
        self.cfg_file = Path(self.cfg_dir).joinpath(f'{pc_methods_name}.yml')
        with open(self.cfg_file, 'r') as f:
            cfg = yaml.load(f.read(), Loader=yaml.FullLoader)
        self.cfg = cfg

    def get_pc_method_name(self):
        """
        Get the name of the current point cloud algorithm.
        :return: pc_methods name
        """
        return str(type(self).__name__)

    def set_resolution(
            self,
            resolution: int
    ):
        """
        Set resolution of the dataset.
        :param resolution: dataset resolution
        :return: dataset resolution
        """
        self.resolution = resolution
        return self.resolution

    def set_color(
            self,
            color: bool
    ):
        """
        Set color of the dataset
        :param color: dataset color
        :return: dataset color
        """
        self.color = color
        return self.color

    def encode(self, orig_pc, enc_pc) -> List[str]:
        raise NotImplementedError("Please implement encode method!")

    def decode(self, enc_file, dec_file) -> List[str]:
        raise NotImplementedError("Please implement decode method!")

    def run_experiments(
            self,
            dataset_name: str,
            resolution: int,
            color: bool
    ):
        """
        Begin run experiments & evaluation
        :param dataset_name: dataset's name
        :param resolution: dataset's resolution
        :param color: dataset's color
        :return: None
        """
        self.resolution = self.set_resolution(resolution)
        self.color = self.set_color(color)
        files = self.is_valid_dataset(dataset_name)
        self.multiprocessing(files)

    def multiprocessing(
            self,
            files: Iterable,
            num_processes: int = None,
            is_multiprocessing: bool = True
    ):
        """
        Multiprocessing all point cloud files in the dataset
        :param files: point cloud files
        :param num_processes:   [optional]
                                number of CPU pool workers/ processes. If None, num_processes = cpu_count. Default: None
        :param is_multiprocessing: options to run experiments IN/ NOT IN multiprocessing. Default: True
        :return: None
        """
        with Pool(processes=num_processes) as p:
            process_f = functools.partial(self.process)
            if is_multiprocessing:
                # With multiprocessing
                list(tqdm(p.imap(process_f, files), total=len(files)))
            else:
                # Without multiprocessing
                list(tqdm((process_f(f) for f in files), total=len(files)))

    def process(
            self,
            orig_pc,
    ):
        """
        Process a PC file, including encode, decode, get inference time, distortion values, bpp values, and write logs.
        :param orig_pc: Original PC file that is in processing
        :return: None
        """

        for i, param in enumerate(self.cfg['params']):
            self.id = i
            self.rate_name = param['id']
            self.orig_pc = orig_pc
            self.enc_pc, self.dec_pc, eval_file = self.set_filepath(orig_pc=orig_pc, rate_name=self.rate_name)
            enc_t, dec_t = self.encode_and_decode(self.orig_pc, self.enc_pc, self.dec_pc)
            inference_time = self.get_inference_time(enc_t, dec_t)
            distortion, bpp = self.eval_geom_distortion_bpp(
                self.orig_pc,
                self.enc_pc,
                self.dec_pc,
            )
            data = {**inference_time, **distortion, **bpp}
            self.write_eval_log(data, eval_file)

    def is_valid_dataset(
            self,
            dataset_name: str
    ):
        """
        Check if the given dataset is valid/ exists and if there are any files in the dataset.
        :param dataset_name: dataset's name
        :return: All PC files in the dataset to be processed
        """
        dataset_fdir = Path(self.dataset_dir).joinpath(dataset_name)

        # Check if dataset directory exists
        if not Path.exists(dataset_fdir):
            logger.error(f'{dataset_fdir} does not exist')
            raise FileNotFoundError
        paths = Path(dataset_fdir).glob('*.ply')
        files = [p for p in paths]
        files_len = len(files)

        # Check if files are found in dataset directory
        if files_len <= 0:
            logger.error(f'Not found any files in {dataset_fdir}')
            raise ValueError

        # Finished files checking. Begin to run experiments & evaluate
        logger.info(f'Found {files_len} files in {dataset_fdir}. Start run experiments & evaluate')
        return files

    def set_filepath(
            self,
            orig_pc,
            rate_name
    ):
        """
        Given original PC file, create encoded, decoded, and evaluation directory.
        :param orig_pc: Current original PC file that is in processing
        :param rate_name: rate id containing all parameters to be used in PC algorithms. Can be found in root/cfg
        :return:
            enc_file: full path to encoded PC file
            dec_file: full path to decoded PC file
            eval_file: full path to eval PC file
        """
        pc_methods_name = self.get_pc_method_name()
        dataset_name = orig_pc.parent.name
        plyfile_name = orig_pc.name

        enc_file = Path(self.expt_dir).joinpath(pc_methods_name, dataset_name, rate_name, 'enc', plyfile_name)
        enc_file = enc_file.parent / (enc_file.name + str(self.cfg['bin_extension']))
        enc_file.parent.mkdir(parents=True, exist_ok=True)

        dec_file = Path(self.expt_dir).joinpath(pc_methods_name, dataset_name, rate_name, 'dec', plyfile_name)
        dec_file = dec_file.parent / (dec_file.name + '.ply')
        dec_file.parent.mkdir(parents=True, exist_ok=True)

        eval_file = Path(self.expt_dir).joinpath(pc_methods_name, dataset_name, rate_name, 'eval', plyfile_name)
        eval_file = eval_file.parent / (eval_file.name + '.json')
        eval_file.parent.mkdir(parents=True, exist_ok=True)
        return enc_file, dec_file, eval_file

    def encode_and_decode(
            self,
            orig_pc,
            enc_pc,
            dec_pc
    ):
        """
        Run encode and decode command and compute encode time and decode time.
        :param orig_pc: Original PC file that is in processing
        :param enc_pc: Encoded PC file that is in processing
        :param dec_pc: Decoded PC file that is in processing
        :return:
            enc_time: Time it takes to encode a PC file
            dec_time: Time it takes to decode a PC file
        """
        encode_cmd = self.encode(orig_pc, enc_pc)
        enc_begin = time.time()
        sp.run(
            encode_cmd,
            cwd=self.cfg['pcc_directory'],
            stdout=sp.DEVNULL,
            stderr=sp.DEVNULL,
        )
        enc_end = time.time()
        enc_time = enc_end - enc_begin

        decode_cmd = self.decode(enc_pc, dec_pc)
        dec_begin = time.time()
        sp.run(
            decode_cmd,
            cwd=self.cfg['pcc_directory'],
            stdout=sp.DEVNULL,
            stderr=sp.DEVNULL,
        )
        dec_end = time.time()
        dec_time = dec_end - dec_begin
        return enc_time, dec_time

    def get_inference_time(
            self,
            enc_time,
            dec_time
    ):
        """
        Get a summary of inference time,
        containing pcc algorithm, original PC, encoded bitstream, decoded PC, encode time, decode time.
        :param enc_time: Time it took to encode a PC file
        :param dec_time: Time it took to decode a PC file
        :return: inference_time
        """
        inference_time = {
            'PCC Algorithm': self.get_pc_method_name(),
            'Original PC': str(self.orig_pc),
            'Encoded bitstream': str(self.enc_pc),
            'Decoded PC': str(self.dec_pc),
            'Encode time in sec': enc_time,
            'Decode time in sec': dec_time
        }
        return inference_time

    def eval_geom_distortion_bpp(
            self,
            orig_pc,
            enc_pc,
            dec_pc,
    ):
        """
        Evaluate geometry distortion and bits per point (bpp) between the original PC and decoded PC
        :param orig_pc: Original PC file to be evaluated
        :param enc_pc: Encoded PC file to be evaluated
        :param dec_pc: Decoded PC file to be evaluated
        :return:
            distortion: MSE-PSNR, H-PSNR, Y-PSNR (if applicable)
            bpp: bits per point
        """
        evaluate = Evaluator(
            orig_pc,
            enc_pc,
            dec_pc,
            self.pcerror,
            self.color,
            self.resolution
        )

        distortion = evaluate.evaluate_geometry_distortion(orig_pc, dec_pc)
        bpp = evaluate.evaluate_bpp(orig_pc, enc_pc, dec_pc)
        return distortion, bpp

    @staticmethod
    def write_eval_log(data, eval_file):
        """
        Get combined data and write this data to the evaluation file.
        :param data: results combined from evaluation steps.
        :param eval_file: evaluation file to be writed
        :return: None
        """
        with open(eval_file, 'w') as eval_file:
            json.dump(data, eval_file, indent=4)
