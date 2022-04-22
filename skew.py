from typing import *
from predictor import Predictor
from sat_counter import SaturatingCounter, wntCounter
from shift_register import ShiftRegister

# TODO: check
# these functions are described here:
# https://hal.inria.fr/inria-00073720/document
# H takes an n-bit string
def H(y : int, n : int) -> int:  # TODO maybe avoid passing in n
    y1 = y & 1
    yn = (y & (1 << (n-1))) >> (n - 1)
    ans = ((yn ^ y1) << (n-1)) | (y >> 1)
    # assert(y < 2**n)
    # assert(ans < 2**n)
    return ans
    
def H_inv(y : int, n : int) -> int:
    yn_x_y1 = y & (1 << (n-1))
    yn = (y & (1 << (n-2))) << 1
    y1 = (yn_x_y1 ^ yn) >> (n-1)
    ans = ((y << 1) & ((1 << (n-1)) - 1)) | y1
    # assert(y < 2**n)
    # assert(ans < 2**n)
    return ans

# convenience function to turn a 2n-bit string into two n-bit strings
def bitsplit(y : int, n : int) -> Tuple[int, int]:
    V1 = y % (2**n)
    V2 = y >> n
    return (V2, V1)

# convenience function to join two bitstrings

# these three functions meld together two n-bit strings
# into one
def f0(V2 : int, V1 : int, n : int) -> int:
    return H(V1, n) ^ H_inv(V2, n) ^ V2

def f1(V2 : int, V1 : int, n : int) -> int:
    return H(V1, n) ^ H_inv(V2, n) ^ V1

def f2(V2 : int, V1 : int, n : int) -> int:
    return H_inv(V1, n) ^ H(V2, n) ^ V2

class SkewPred(Predictor):

    def __init__(self, ind_bits : int, hist_len : int, cwid : int):
        assert((ind_bits + hist_len) % 2 == 0)  # per the paper
        # skew uses global history
        self.ghr : ShiftRegister = ShiftRegister(ind_bits)
        # we use THREE phts
        self.pht0 : List[SaturatingCounter] = []
        self.pht1 : List[SaturatingCounter] = []
        self.pht2 : List[SaturatingCounter] = []
        self.n = (ind_bits + hist_len) // 2
        for i in range(2**self.n):
            self.pht0.append(wntCounter(cwid))
            self.pht1.append(wntCounter(cwid))
            self.pht2.append(wntCounter(cwid))
        self.ind_bits = ind_bits
    
    def __len__(self):
        return len(self.ghr) + 3 * len(self.pht0) * len(self.pht0[0])

    def predict(self, addr : int) -> bool:
        # get predictions from EACH pht
        seed = ((addr % 2**self.ind_bits) << (len(self.ghr) - 2)) | (self.ghr.read())
        # assert(seed < 2**(2*self.n))
        V2, V1 = bitsplit(seed, self.n)
        # assert(V2 < 2**self.n)
        # assert(V1 < 2**self.n)
        pred0 = self.pht0[f0(V2, V1, self.n)].read()
        pred1 = self.pht1[f1(V2, V1, self.n)].read()
        pred2 = self.pht2[f2(V2, V1, self.n)].read()
        return (pred0 + pred1 + pred2) > 1

    def update(self, addr : int, pred : int, result : bool):
        # we discarded the component-wise predictions, and we need them again now
        # TODO: memoize this
        seed = ((addr % 2**self.ind_bits) << (len(self.ghr) - 2)) | (self.ghr.read())
        V2, V1 = bitsplit(seed, self.n)
        pred_c0 = self.pht0[f0(V2, V1, self.n)]
        pred_c1 = self.pht1[f1(V2, V1, self.n)]
        pred_c2 = self.pht2[f2(V2, V1, self.n)]
        # use partial updating:
        # when a bank gives a bad prediction, but the overall prediction is good, DON'T UPDATE THE BAD ONE
        # if the overall prediction is bad, update everything
        for p_comp in (pred_c0, pred_c1, pred_c2):
            p = p_comp.read()
            if (p == result) or ((p != result) and (p == pred)):
                p_comp.update(result)
        # update the GHR
        self.ghr.put(result)
