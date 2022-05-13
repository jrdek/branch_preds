from structures.sat_counter import wntCounter, SaturatingCounter
from structures.shift_register import ShiftRegister
from typing import *

class AlphaPredictor:

    def __init__(self, pc_bits : int, lh_bits : int, gh_bits : int):
        self.pc_bits = pc_bits
        self.gTable : List[SaturatingCounter] = [wntCounter(2) for i in range(2**gh_bits)]
        self.cTable : List[SaturatingCounter] = [wntCounter(2) for i in range(2**gh_bits)]
        self.ghr : ShiftRegister = ShiftRegister(gh_bits)
        self.lTable : List[ShiftRegister ]= [ShiftRegister(lh_bits) for i in range(2**pc_bits)]
        self.pTable : List[SaturatingCounter] = [wntCounter(2) for i in range(2**lh_bits)]

    def predict(self, addr : int) -> bool:
        localPat = self.lTable[addr % 2**self.pc_bits].read()
        localPred = self.pTable[localPat].read()
        globalPred = self.gTable[self.ghr.read()].read()
        choicePred = self.cTable[self.ghr.read()].read()
        return globalPred if choicePred else localPred
    
    def update(self, addr : int, pred : bool, result : bool):
        localPat = self.lTable[addr % 2**self.pc_bits].read()
        localCtr = self.pTable[localPat]
        localPred = localCtr.read()
        localCtr.update(result)
        globalCtr = self.gTable[self.ghr.read()]
        globalPred = globalCtr.read()
        globalCtr.update(result)
        choiceCtr = self.cTable[self.ghr.read()]
        if localPred != globalPred:
            choiceCtr.update(globalPred == result)
        self.ghr.put(result)
        return

    def __len__(self):
        # bleh
        return 0