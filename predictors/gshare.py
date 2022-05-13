from typing import *
from structures.predictor import Predictor
from structures.sat_counter import SaturatingCounter, wntCounter
from structures.shift_register import ShiftRegister

class GsharePred(Predictor):

    def __init__(self, ind_bits : int, pat_len : int, cwid : int):
        # GSHARE is like the local two-level adaptive predictor, but with
        # an additional global history register:
        self.ghr : ShiftRegister = ShiftRegister(ind_bits)
        # the BHT is a table of "recent-results" shift registers
        self.bht : List[ShiftRegister] = []
        for i in range(2**ind_bits):
            self.bht.append(ShiftRegister(pat_len))
        # the BHT then indexes into a PHT containing sat counters
        self.pht : List[SaturatingCounter] = []
        for i in range(2**pat_len):
            self.pht.append(wntCounter(cwid))
        self.ind_bits = ind_bits
    
    def __len__(self):
        return sum(len(sr) for sr in self.bht) + sum(len(ctr) for ctr in self.pht) + len(self.ghr)

    def predict(self, addr : int) -> bool:
        # XOR the branch address's last bits and the GHR
        hash = self.ghr.read() ^ ((addr>>2) % (2**self.ind_bits))
        pat = self.bht[hash].read()
        return self.pht[pat].read()

    def update(self, addr : int, pred : int, result : bool):
        hash = self.ghr.read() ^ ((addr>>2) % (2**self.ind_bits))
        patReg = self.bht[hash]
        self.pht[patReg.read()].update(result)
        # enter the result into the applicable pattern register
        patReg.put(result)
        # ...and also the GHR
        self.ghr.put(result)
        