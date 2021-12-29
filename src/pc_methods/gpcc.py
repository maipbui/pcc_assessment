from typing import List
from src.pc_methods.pc_base import Base


class GPCC(Base):
    def __init__(self):
        super().__init__()

    def encode(self, orig_pc, enc_pc) -> List[str]:
        cmd = [self.cfg['encoder'],
               '--uncompressedDataPath=' + str(orig_pc),
               '--compressedStreamPath=' + str(enc_pc),
               '--positionQuantizationScale=' + str(self.cfg['params'][self.id]['positionQuantizationScale']),
               '--mergeDuplicatedPoints=' + str(self.cfg['params'][self.id]['mergeDuplicatedPoints']),
               '--mode=' + str(0),
               # '--transformType=' + str(parameters['transformType']),
               # '--colourMatrix=' + str(parameters['colourMatrix']),
               # '--convertPlyColourspace=' + str(parameters['convertPlyColourspace']),
               # '--qp=' + str(parameters['qp']),
               # '--qpChromaOffset=' + str(parameters['qpChromaOffset']),
               ]
        if self.color:
            cmd.append('--attribute=color')
        return cmd

    def decode(self, enc_file, dec_file) -> List[str]:
        cmd = [self.cfg['decoder'],
               '--compressedStreamPath=' + enc_file,
               '--reconstructedDataPath=' + dec_file,
               '--mode=1',
               '--outputBinaryPly=1'
               ]
        return cmd
