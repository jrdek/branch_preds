class Predictor:
    def predict(self, addr : int) -> bool:
        raise Exception("Unimplemented predict function")
    
    def update(self, addr : int, pred : bool, result : bool):
        raise Exception("Unimplemented update function")

    def __len__(self):
        raise Exception("Unimplemented length function")