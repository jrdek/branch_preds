from structures.predictor import Predictor

class StaticPred(Predictor):
    def __init__(self, direc : bool):
        self.direction = direc
    
    def __len__(self):
        return 0

    def predict(self, addr : int) -> bool:
        return self.direction
    
    def update(self, addr : int, pred : bool, res : bool):
        pass