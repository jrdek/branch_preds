class SaturatingCounter:
    def __init__(self, width : int, init_val : int):
        assert(width > 0)  # negative width makes no sense
        self.max = 2**width - 1
        self.ctr = init_val
    
    def __len__(self):
        return self.max + 1
    
    def update(self, actual : bool):
        self.ctr = min(self.max, self.ctr + 1) if actual else max(0, self.ctr - 1)

    def read(self) -> bool:
        return self.ctr > (self.max >> 1)


# convenience function: return a weakest-not-taken sat counter
def wntCounter(width : int) -> SaturatingCounter:
    return SaturatingCounter(width, (2**(width-1)-1))