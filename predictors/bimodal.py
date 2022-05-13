from typing import *
from structures.predictor import Predictor
from structures.sat_counter import SaturatingCounter, wntCounter

class BimodalPred(Predictor):

    def __init__(self, ind_bits : int, c_wid : int):
        # init the sat_ctr to "most-weakly not taken"
        self.bht : List[SaturatingCounter] = []
        self.ind_bits = ind_bits
        for i in range(2**ind_bits):
            self.bht.append(wntCounter(c_wid))
    
    def __len__(self):
        return len(self.bht) * len(self.bht[0])

    def predict(self, addr : int) -> bool:
        ctr : SaturatingCounter = self.bht[(addr>>2) % (2**self.ind_bits)]
        return ctr.read()

    def update(self, addr : int, pred : int, result : bool):
        ctr : SaturatingCounter = self.bht[(addr>>2) % (2**self.ind_bits)]
        ctr.update(result)