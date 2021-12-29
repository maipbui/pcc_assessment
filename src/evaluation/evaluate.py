import re
import subprocess as sp
from pathlib import Path
from plyfile import PlyData
from dataclasses import dataclass
from typing import Union, Dict, List


@dataclass
class Evaluator:
    orig_pc: Union[str, Path]
    enc_pc: Union[str, Path]
    dec_pc: Union[str, Path]
    pcerror: Union[str, Path]
    color: bool = None
    resolution: int = None

    @staticmethod
    def find_pattern(metrics, results) -> List[str]:
        metrics_values = []
        for metric in metrics:
            exist = None
            for line in results:
                m = re.search(f'(?<={metric}).*', line)
                if m:
                    metrics_values.append(m.group())
                    exist = True
                    break
            if exist is None:
                metrics_values.append('NaN')
        assert len(metrics) == len(metrics_values)
        return metrics_values

    def evaluate_geometry_distortion(
            self,
            orig_pc,
            dec_pc
    ) -> Dict[str, str]:
        """
        Evaluate geometry distortion between the original PC and decoded PC.
        :param orig_pc: Original PC file to be evaluated
        :param dec_pc: Decoded PC file to be evaluated
        :return: geoemtry_distortion values such as MSE-PSNR, H-PSNR, Y-PSNR (if applicable)
        """
        metrics = ['mseF      \(p2point\): ',
                   'mseF,PSNR \(p2point\): ',
                   'mseF      \(p2plane\): ',
                   'mseF,PSNR \(p2plane\): ',
                   'h.        \(p2point\): ',
                   'h.,PSNR   \(p2point\): ',
                   'h.        \(p2plane\): ',
                   'h.,PSNR   \(p2plane\): ',
                   ]

        if self.color:
            metrics.extend(
                ['c\[0\],    F         : ',
                'c\[1\],    F         : ',
                'c\[2\],    F         : ',
                'c\[0\],PSNRF         : ',
                'c\[1\],PSNRF         : ',
                'c\[2\],PSNRF         : ',
                'h.c\[0\],    F         : ',
                'h.c\[1\],    F         : ',
                'h.c\[2\],    F         : ',
                'h.c\[0\],PSNRF         : ',
                'h.c\[1\],PSNRF         : ',
                'h.c\[2\],PSNRF         : ']
            )
        pcerror_cmd = ['./test/pc_error',
                       '--fileA=' + str(orig_pc),
                       '--fileB=' + str(dec_pc),
                       '--resolution=' + str(2 ** self.resolution - 1),
                       '--hausdorff=1'
                       ]

        if self.color:
            pcerror_cmd.append('--color=1')
        pcerror = sp.run(
            pcerror_cmd,
            cwd=self.pcerror,
            stdout=sp.PIPE,
            stderr=sp.DEVNULL,
            universal_newlines=True
        )
        results = pcerror.stdout.splitlines()
        metrics_vals = self.find_pattern(metrics, results)

        geometric_distortion = dict(zip(metrics, metrics_vals))
        return geometric_distortion

    def evaluate_bpp(
            self,
            orig_pc,
            enc_pc,
            dec_pc
    ) -> Dict[str, float]:
        """
        Evaluate bits per point (bpp) between the original PC and decoded PC
        :param orig_pc: Original PC file to be evaluated
        :param enc_pc: Encoded PC file to be evaluated
        :param dec_pc: Decoded PC file to be evaluated
        :return: bpp: bits per point
        """
        orig_ply = PlyData.read(orig_pc)

        orig_size = Path.stat(orig_pc).st_size / 1000
        enc_size = Path.stat(enc_pc).st_size / 1000
        dec_size = Path.stat(dec_pc).st_size / 1000
        compression_ratio = orig_size / enc_size
        bpp_orig = (orig_size * 1000 * 8) / len(orig_ply['vertex']['x'])
        bpp = (enc_size * 1000 * 8) / len(orig_ply['vertex']['x'])

        bpp_values = {'Orig PC size in KB': orig_size,
                      'Orig num points': len(orig_ply['vertex']['x']),
                      'Enc PC size in KB': enc_size,
                      'Dec PC size in KB': dec_size,
                      'Compression Ratio': compression_ratio,
                      'Bits per point bpp before cps': bpp_orig,
                      'Bits per point bpp after cps': bpp
                      }
        return bpp_values
