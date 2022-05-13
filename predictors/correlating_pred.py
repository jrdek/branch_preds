from typing import *
from structures.predictor import Predictor
from structures.sat_counter import SaturatingCounter, wntCounter
from structures.shift_register import ShiftRegister

class CorrelatingPred(Predictor):

    def __init__(self, ind_bits : int, pat_len : int, cwid : int = 2):
        self.ghr = ShiftRegister(pat_len)
        # the GHR indexes into a PHT containing sat counters
        self.pht : List[SaturatingCounter] = []
        for i in range(2**pat_len):
            self.pht.append(wntCounter(cwid))
        self.ind_bits = ind_bits
    
    def __len__(self):
        return len(self.ghr) + sum(len(ctr) for ctr in self.pht)

    def predict(self, addr : int) -> bool:
        pat = self.ghr.read()
        return self.pht[pat].read()

    def update(self, addr : int, pred : int, result : bool):
        self.pht[self.ghr.read()].update(result)
        # enter the result into the applicable pattern register
        self.ghr.put(result)
        