from dataclasses import dataclass
from typing import Union
from pathlib import Path


@dataclass
class Directory:
    dataset_dir: Union[str, Path] = "/media/mb/mb/datasets/final/"
    experiments_dir: Union[str, Path] = "/media/mb/mb/experiments/"
    pcerror: Union[str, Path] = "/media/mb/mb/pcc_assessment/pcerror/mpeg-pcc-dmetric"
    cfg_dir: Union[str, Path] = "/media/mb/mb/pcc_assessment/cfg"
