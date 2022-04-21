from typing import *

class LRUCache:
    def __init__(self, capacity : int, tag_size : int, rhs_type : type):
        self.capacity = capacity
        self.tag_size = tag_size
        self.rhs_type : type = rhs_type
        self.map : Dict[int, self.rhs_type] = {}
    
    def lookup(self, tag : int) :
        if tag in self.map:
            return self.map[tag]
