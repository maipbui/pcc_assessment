from typing import List
from src.pc_methods.pc_base import Base


class VPCC(Base):
    def __init__(self):
        super().__init__()

    def encode(self, orig_pc, enc_pc) -> List[str]:
        cmd = [self.cfg['encoder'],
               '--uncompressedDataPath=' + orig_pc,
               '--compressedStreamPath=' + enc_pc,
               '--configurationFolder=./' + self.cfg['cfg_folder'],
               '--config=./' + self.cfg['cfg_common'],
               '--config=./' + self.cfg['cfg_condition'],
               # '--config=./' + str(self.cfg['params'][self.id]['rate_cfg']),
               #  '--geometryQP=' + str(self.cfg['params'][self.id]['geometryQP']),
               #  '--textureQP=' + str(self.cfg['params'][self.id]['textureQP']),
               #  '--occupancyPrecision=' + str(self.cfg['params'][self.id]['occupancyPrecision']),
               '--videoEncoderOccupancyPath=./' + self.cfg['vid_encoder'],
               '--videoEncoderGeometryPath=./' + self.cfg['vid_encoder'],
               '--videoEncoderAttributePath=./' + self.cfg['vid_encoder'],
               '--frameCount=1',
               '--computeMetrics=0',
               '--computeChecksum=0'
               ]
        return cmd

    def decode(self, enc_file, dec_file) -> List[str]:
        cmd = [self.cfg['decoder'],
               '--compressedStreamPath=' + enc_file,
               '--reconstructedDataPath=' + dec_file,
               '--videoDecoderOccupancyPath=' + self.cfg['vid_decoder'],
               '--videoDecoderGeometryPath=' + self.cfg['vid_decoder'],
               '--videoDecoderAttributePath=' + self.cfg['vid_decoder'],
               '--inverseColorSpaceConversionConfig=' + self.cfg['cfg_inverse_color_space_conversion'],
               '--computeMetrics=0',
               '--computeChecksum=0'
               ]
        return cmd
