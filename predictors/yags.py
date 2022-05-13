from typing import *
from structures.shift_register import ShiftRegister
from structures.sat_counter import SaturatingCounter, wntCounter
from structures.predictor import Predictor


# TODO: maybe implement associativity as in the paper
# though they do say it isn't very performant...
class YagsPred(Predictor):
    def __init__(self, cache_ind_bits : int, ind_bits : int, tag_bits : int):
        self.cache_ind_bits : int = cache_ind_bits
        self.ind_bits : int = ind_bits
        self.tag_bits : int = tag_bits
        self.used_choice_pht : bool = True
        self.used_t_cache : bool = False

        self.ghr = ShiftRegister(self.cache_ind_bits)
        self.choice_pht : List[SaturatingCounter] = [wntCounter(2) for _ in range(2**self.ind_bits)]
        # the "caches" are direct-mapped; just use lists
        # TODO: there has GOT to be a cleaner way to write this and still appease mypy
        # Tuples aren't mutable :(
        
        # TODO why in the world is 2**self.cache_ind_bits turning into a float
        self.t_cache : List[List[Union[int, SaturatingCounter]]] = []
        self.nt_cache : List[List[Union[int, SaturatingCounter]]] = []
        for i in range(int(2**self.cache_ind_bits)):
            self.t_cache.append([0, wntCounter(2)])
            self.nt_cache.append([0, wntCounter(2)])

    def predict(self, addr : int) -> bool:
        # read from the choice pht
        choice_key : int = (addr>>2) % (2**self.ind_bits)
        cache_key = ((addr>>2) % (2**self.cache_ind_bits)) ^ self.ghr.read()
        tag = (addr>>2) % (2**self.tag_bits)
        choice : bool = self.choice_pht[choice_key].read()
        if choice:
            #print("Choice says 1... ", end='')
            # use the nt-cache pred iff an nt-cache lookup hits
            if self.nt_cache[cache_key][0] == tag:
                #print(f"Ncache hit @ cacheKey {cache_key}!")
                self.used_choice_pht = False
                self.used_t_cache = False
                return cast(Any,self).nt_cache[cache_key][1].read()
            else:
                #print("Ncache miss.")
                self.used_choice_pht = True
                return choice
        else:
            #print("Choice says 0... ", end='')
            # use the t-cache pred iff a t-cache lookup hits
            if self.t_cache[cache_key][0] == tag:
                #print("Tcache hit!")
                self.used_choice_pht = False
                self.used_t_cache = True
                return cast(Any,self).t_cache[cache_key][1].read()
            else:
                #print("Tcache miss.")
                self.used_choice_pht = True
                return choice
    
    def update(self, addr : int, pred : bool, result : bool):
        choice_key : int = (addr>>2) % (2**self.ind_bits)
        cache_key = ((addr>>2) % (2**self.cache_ind_bits)) ^ self.ghr.read()
        tag = (addr>>2) % (2**self.tag_bits)
        choice : bool = self.choice_pht[choice_key].read()
        nt_pred : bool = self.nt_cache[cache_key][1].read()
        t_pred : bool = self.t_cache[cache_key][1].read()
        """
        The “not taken” cache is updated if a prediction from it was
        used. It is also updated if the choice PHT is indicating
        “taken” and the branch outcome was “not taken.”
        """
        if ((not self.used_choice_pht) and (not self.used_t_cache)) \
          or (choice and not result):
            #print("Updating Ncache... ", end='')
            self.nt_cache[cache_key][0] = tag
            cast(Any,self).nt_cache[cache_key][1].update(result)
            #print(f'Ncache[{choice_key}].ctr is now {self.nt_cache[cache_key][1].ctr}.')
        if ((not self.used_choice_pht) and self.used_t_cache) \
          or (result and not choice):
            #print("Updating Tcache... ", end='')
            self.t_cache[cache_key][0] = tag
            cast(Any,self).t_cache[cache_key][1].update(result)
            #print(f'Tcache[{choice_key}].ctr is now {self.t_cache[cache_key][1].ctr}.')

        """
        The choice PHT is normally updated too, but not if it gives
        a prediction contradicting the branch outcome and the
        direction PHT chosen gives the correct prediction.
        """

        #if not ((choice != result) and (pred == result)):
        if not ((choice != result) and ((nt_pred if choice else t_pred) == result)):
            #print("Updating the choice predictor... ", end='')
            self.choice_pht[choice_key].update(result)
            #print(f"Cpred[{choice_key}] is now {self.choice_pht[choice_key].ctr}.")

        # remember to update the GHR also
        self.ghr.put(result)
        #print(f"GHR is now {self.ghr.read()}.")
        return
        

    def __len__(self):
        """
        STORAGE REQUIREMENTS (in bits):
            used_choice_pht : 1
            used_t_cache : 1
            GHR: cache_ind_bits
            choice pht: (2**ind_bits)
            t_cache: (2**cache_ind_bits) * (tag_bits + 2)
            nt_cache: (2**cache_ind_bits) * (tag_bits + 2)
        """
        return 2 + \
            len(self.ghr) + \
            2**self.ind_bits + \
            2* ((self.tag_bits + 2) * (2**self.cache_ind_bits))