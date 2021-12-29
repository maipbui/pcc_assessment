from typing import List
from src.pc_methods.pc_base import Base


class GeoCNNv2(Base):
    def __init__(self):
        super().__init__()

    def encode(self, orig_pc, enc_pc) -> List[str]:
        cmd = ['python3',
               self.cfg['encoder'],
               '--input_files=' + str(orig_pc),
               '--output_files=' + str(enc_pc),
               '--opt_metrics=' + str(self.cfg['opt_metrics']),
               '--checkpoint_dir=' + str(self.cfg['params'][self.id]['checkpoint_dir']),
               '--model_config=' + str(self.cfg['params'][self.id]['model_config']),
               '--resolution=' + str(self.cfg['params'][self.id]['resolution']),
               '--octree_level=' + str(self.cfg['params'][self.id]['octree_level']),
               ]
        return cmd

    def decode(self, enc_file, dec_file) -> List[str]:
        cmd = ['python3',
               self.cfg['decoder'],
               '--input_files=' + enc_file,
               '--output_files=' + dec_file,
               '--checkpoint_dir=' + str(self.cfg['params'][self.id]['checkpoint_dir']),
               '--model_config=' + str(self.cfg['params'][self.id]['model_config']),
               ]
        return cmd