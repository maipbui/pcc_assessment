from typing import List
from src.pc_methods.pc_base import Base


class Draco(Base):
    def __init__(self):
        super().__init__()

    def encode(self, orig_pc, enc_pc) -> List[str]:
        cmd = [self.cfg['encoder'],
               '-i', str(orig_pc),
               '-o', str(enc_pc),
               '-qp', str(self.cfg['params'][self.id]['qp']),
               '-qt', str(self.cfg['params'][self.id]['qt']),
               '-qn', str(self.cfg['params'][self.id]['qn']),
               '-qg', str(self.cfg['params'][self.id]['qg']),
               '-cl', str(self.cfg['params'][self.id]['cl']),
               '-point_cloud'
               ]
        return cmd

    def decode(self, enc_file, dec_file) -> List[str]:
        cmd = [self.cfg['decoder'],
               '-i', str(enc_file),
               '-o', str(dec_file)
               ]
        return cmd
