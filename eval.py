#!/usr/local/bin/pypy
import sys
import math
from predictors.correlating_pred import CorrelatingPred
from predictors.gshare import GsharePred
from predictors.static_pred import StaticPred
from predictors.one_level import OneLevelPred
from predictors.bimodal import BimodalPred
from predictors.local_adaptive import LocalAdaptivePred
from predictors.skew import SkewPred
from structures.predictor import Predictor
from predictors.yags import YagsPred
from predictors.perceptron_pred import PerceptronPred
from predictors.weirdshare import SGharePred
from predictors.alpha_tournament import AlphaPredictor
from typing import *

class Stats:
    numCorrect = 0
    numIncorrect = 0
    total = 0

    def log(self, pred : bool, actual : bool):
        self.total += 1
        if pred == actual:
            self.numCorrect += 1
        else:
            self.numIncorrect += 1

class PerBranchStats:
    branch_data : Dict[int, Stats] = {}

    def log(self, addr : int, pred : bool, actual : bool):
        if addr not in self.branch_data:
            self.branch_data[addr] = Stats()
        self.branch_data[addr].log(pred, actual)
    

def parseTrace(trace_loc):
    with open(trace_loc) as trace_file:
        trace_arr = []
        for branch in trace_file.readlines():
            addr, direc = (lambda pair : (int(pair[0], 16), pair[1]=='t'))(branch.strip().split(' '))
            trace_arr.append((addr, direc))
        return trace_arr

def parse240Trace(trace_loc):
    with open(trace_loc) as trace_file:
        trace_arr = []
        for branch in trace_file.readlines():
            addr, direc = (lambda pair : (int(pair[0], 16) * 4, pair[1]=='1'))(branch.strip().split(' '))
            trace_arr.append((addr, direc))
        return trace_arr

if __name__ == '__main__':
    # TODO: put in a -help flag probably
    if len(sys.argv) < 2:
        raise Exception("Usage: ./eval.py PREDICTOR TRACEFILE")
    p_arg = sys.argv[1]
    p : Predictor
    if p_arg == 'static':
        p = StaticPred(False)
    elif p_arg == 'globalCtr':
        width = sys.argv[2] if len(sys.argv) > 3 else '2'
        assert(width.isdigit())
        p = OneLevelPred(int(width))
    elif p_arg == 'bimodal':
        indBits = 11
        cwidth = 2  # TODO input parsing
        p = BimodalPred(indBits, cwidth)
    elif p_arg == 'local':
        indBits = 8
        patLen = 5
        cwidth = 2  # TODO input parsing
        p = LocalAdaptivePred(indBits, patLen, cwidth)
    elif p_arg == 'gshare':
        indBits = 13
        histLen = 13
        cwidth = 2
        p = GsharePred(indBits, histLen, cwidth)
    elif p_arg == 'sghare':
        indBits = 8
        histLen = 15
        cwidth = 2
        p = SGharePred(indBits, histLen, cwidth)
    elif p_arg == 'skew':
        indBits = 10
        histLen = 12
        cwidth = 2
        p = SkewPred(indBits, histLen, cwidth)
    elif p_arg == 'yags':  # 16, 8, 13: 94.2872% correct on trace_gcc
        choiceBits = 11  # how big is the choice pht?
        tagBits = 6
        cacheBits = 14 #choiceBits - 2  # how big are the caches?
        p = YagsPred(cacheBits, choiceBits, tagBits)
        # 2kb-ish: 11 choice bits, 6 tag bits, (choice - 1) cache bits
        # 4kb-ish: 12 choice bits
        # 18kb-ish: 14 choice bits! (wow)
    elif p_arg == 'perceptron':
        # TODO: the paper says nothing about how big the main
        # BHT is...
        hashBits = 6
        histBits = 34  # paper says this is good for 8kb
        thresh = math.floor(1.93*histBits + 14)
        p = PerceptronPred(hashBits, histBits, thresh)
    elif p_arg == 'correlating':
        indBits = 8
        histLen = 16
        p = CorrelatingPred(indBits, histLen)
    elif p_arg == 'alpha':
        indBits = 10
        localBits = 10
        globalBits = 12
        p = AlphaPredictor(indBits, localBits, globalBits)
    else:
        raise Exception("Unknown predictor type")
    trace_loc = sys.argv[-1]

    print(f"Predictor: {p.__class__.__name__}")
    print(f"Total predictor size: {len(p) // 8} bytes")
    print(f"Trace: {trace_loc}")
    if '240' in trace_loc:
        trace = parse240Trace(trace_loc)
    else:
        trace = parseTrace(trace_loc)
    print(f"\tTrace has {len(trace)} branches")
    s = Stats()

    # run the simulation:
    for br in trace:
        pred = p.predict(br[0])
        s.log(pred, br[1])
        #print(int(pred))  # yeah
        p.update(br[0], pred, br[1])
    
    print(f'Incorrect: {s.total - s.numCorrect}')
    print(f"Prediction accuracy: {100 * s.numCorrect / (s.total)}%")
