from structures.predictor import Predictor
from structures.sat_counter import SaturatingCounter, wntCounter

class OneLevelPred(Predictor):
    # technically "one-level global"; this is unusual

    def __init__(self, cwid : int):
        # init the sat_ctr to "most-weakly not taken"
        self.sat_ctr = wntCounter(cwid)
    
    def __len__(self):
        return len(self.sat_ctr)

    def predict(self, addr : int) -> bool:
        # one-level, so don't use the address
        return self.sat_ctr.read()

    def update(self, addr : int, pred : int, result : bool):
        # one-level, so don't use the address
        self.sat_ctr.update(result)