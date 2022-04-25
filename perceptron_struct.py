from typing import *

class Perceptron:
    def __init__(self, x_size):
        self.w : List[int] = [0 for _ in range(x_size - 1)]


    def dot_with(self, x: List[int]):
        ans : int = self.w[0]
        for i in range(len(x) - 1):
            ans += x[i] * self.w[i]
        return ans


    def train_with(self, x: List[int], t : int):
        for i in range(len(self.w)):
            self.w[i] += t*x[i]
        return