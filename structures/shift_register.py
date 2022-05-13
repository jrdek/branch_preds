class ShiftRegister:
    # we shift to the left; direction shouldn't matter, though
    def __init__(self, width : int):
        self.width = width
        self.value = 0
    
    def __len__(self):
        return self.width
    
    def read(self) -> int:
        return self.value
    
    def put(self, b : bool):
        self.value = ((self.value << 1) & ((2 ** self.width) - 1)) | b