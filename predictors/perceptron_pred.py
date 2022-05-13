from typing import *
from structures.predictor import Predictor
from structures.perceptron_struct import Perceptron
from structures.shift_register import ShiftRegister

def bipolarize (b : bool) -> int:
    return 1 if b else -1

class PerceptronPred(Predictor):
    def __init__(self, hash_bits : int, hist_len : int, thresh : int):
        self.ghr = ShiftRegister(hist_len)
        self.bht : List[Perceptron] = [Perceptron(hist_len) for _ in range(2**hash_bits)]
        self.hash_bits = hash_bits
        self.hist_len = hist_len
        self.thresh = thresh

    def get_bipolar_hist(self) -> List[int]:
        hist = self.ghr.read()
        return [bipolarize(bool(hist & (1<<n))) for n in range(self.hist_len)]

    """
    Hash the branch address, to be used as an index into the BHT.
    Default hash: just use the last hash_bits bits.
    """
    def addrHash(self, addr : int) -> int:
        return (addr >> 2) % (2**self.hash_bits)

    def predict(self, addr : int) -> bool:
        # TODO: the paper says the branch address is hashed
        # but does not specify what the hash is...
        hashed_addr = self.addrHash(addr)
        used_ptron = self.bht[hashed_addr]
        y = used_ptron.dot_with(self.get_bipolar_hist())
        return y >= 0

    def update(self, addr : int, pred : bool, result : bool):
        # recalculate y
        hashed_addr = self.addrHash(addr)
        used_ptron = self.bht[hashed_addr]
        bipolar_hist = self.get_bipolar_hist()
        y = used_ptron.dot_with(self.get_bipolar_hist())
        t = bipolarize(result)
        if (bipolarize(y >= 0) != t) or abs(y) <= self.thresh:
            used_ptron.train_with(bipolar_hist, t)

    def __len__(self):
        # weights are 32-bit integers
        return len(self.bht) * len(self.bht[0].w) * 32 \
           + len(self.ghr)