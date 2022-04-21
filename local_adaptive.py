from typing import *
from predictor import Predictor
from sat_counter import SaturatingCounter
from shift_register import ShiftRegister

class LocalAdaptivePred(Predictor):

    def __init__(self, ind_bits : int, pat_len : int, cwid : int):
        # the BHT is a table of "recent-results" shift registers
        self.bht : List[ShiftRegister] = []
        for i in range(2**ind_bits):
            self.bht.append(ShiftRegister(pat_len))
        # the BHT then indexes into a PHT containing sat counters
        self.pht : List[SaturatingCounter] = []
        for i in range(2**pat_len):
            self.pht.append(SaturatingCounter(cwid, (2**(cwid-1)-1)))
        self.ind_bits = ind_bits
    
    def __len__(self):
        return sum(len(sr) for sr in self.bht) + sum(len(ctr) for ctr in self.pht)

    def predict(self, addr : int) -> bool:
        pat = self.bht[(addr>>2) % (2**self.ind_bits)].read()
        return self.pht[pat].read()

    def update(self, addr : int, pred : int, result : bool):
        patReg = self.bht[(addr>>2) % (2**self.ind_bits)]
        self.pht[patReg.read()].update(result)
        # enter the result into the applicable pattern register
        patReg.put(result)
        