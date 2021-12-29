from typing import List
from src.pc_methods.pc_base import Base


class PCGCv1(Base):
    def __init__(self):
        super().__init__()

    def encode(self, orig_pc, enc_pc) -> List[str]:
        cmd = ['python3',
               self.cfg['coder'],
               'compress',
               str(orig_pc),
               str(enc_pc),
               '--modelname=' + str(self.cfg['params'][self.id]['modelname']),
               '--ckpt_dir=' + str(self.cfg['params'][self.id]['ckpt_dir']),
               '--mode=' + str(self.cfg['params'][self.id]['mode']),
               '--scale=' + str(self.cfg['params'][self.id]['scale']),
               '--cube_size=' + str(self.cfg['params'][self.id]['cube_size']),
               '--min_num=' + str(self.cfg['params'][self.id]['min_num']),
               '--rho=' + str(self.cfg['params'][self.id]['rho']),
               ]
        return cmd

    def decode(self, enc_file, dec_file) -> List[str]:
        cmd = ['python3',
               self.cfg['coder'],
               'decompress',
               str(enc_file),
               str(dec_file),
               '--modelname=' + str(self.cfg['params'][self.id]['modelname']),
               '--ckpt_dir=' + str(self.cfg['params'][self.id]['ckpt_dir']),
               '--mode=' + str(self.cfg['params'][self.id]['mode'])
               ]
        return cmd
