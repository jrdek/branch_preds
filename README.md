# branch_preds

A Python framework for creating and testing branch predictors. Type annotations are used

Traces are expected to be a text file with one branch per line, where branches consist of a hex address followed by either the letter t or the letter n.

To run, use `./eval.py [predictor_name] [trace_location]`. To check and tune implemented predictors, look in `eval.py`. 

---

Predictors extend the `Predictor` class, so they must have the following functions:

- `predict(addr : int) -> bool`, which returns True to mean taken and False to mean not-taken;
- `update(addr : int, pred : bool, result : bool) -> None`, which can update predictor state using the branch address, the last prediction made, and the branch's actual direction; and

- `__len__() -> {x : int | x >= 0}`, which returns the size of the predictor in bits.

