# oops, turns out YAGS does not need this structure!
# still a useful thing to have though

from typing import *
from collections import OrderedDict  # this is very handy!
from sat_counter import SaturatingCounter, wntCounter

T = TypeVar('T')
class LRUCache(Generic[T]):
    def __init__(self, capacity : int, tag_size : int, c_wid : int):
        self.capacity = capacity
        self.tag_size = tag_size
        self.c_wid = c_wid
        self.map : OrderedDict[int, SaturatingCounter] = OrderedDict()  # maps tags to cells
    
    def lookup(self, tag : int) -> Tuple[bool, SaturatingCounter]:
        if tag in self.map:
            self.map.move_to_end(tag)
            return True, self.map[tag]
        # otherwise, we missed
        if len(self.map) >= self.capacity:
            self.map.popitem(last=False)
        self.map[tag] = wntCounter(self.c_wid)
        self.map.move_to_end(tag)
        return False, self.map[tag]