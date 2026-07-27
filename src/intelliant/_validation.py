# src/intelliant/_validation.py

import numbers
from typing import Literal, overload

import numpy as np


# `value: object` is the contract, not laziness: these helpers exist to be
# handed anything a caller passes and to reject it cleanly. A narrower
# annotation would claim the caller had already validated what is being
# validated here.
@overload
def _check_int(name: str, value: object, min_val: int, allow_none: Literal[False] = False) -> int: ...


@overload
def _check_int(name: str, value: object, min_val: int, allow_none: Literal[True]) -> int | None: ...


def _check_int(name: str, value: object, min_val: int, allow_none: bool = False) -> int | None:
    if allow_none and value is None:
        return None
    suffix = " or None" if allow_none else ""
    # DO NOT drop the bool check: bool subclasses int, so isinstance(True,
    # numbers.Integral) is True at runtime and True would pass as a valid int.
    # pyright in strict mode reports this as an unnecessary isinstance - that
    # verdict is type-level only and wrong here.
    if not isinstance(value, numbers.Integral) or isinstance(value, bool) or value < min_val:
        raise ValueError(f"{name} must be int >= {min_val}{suffix}, got {value!r}")
    return int(value)


def _check_float(name: str, value: object, min_val: float = 0.0, max_val: float | None = None) -> float:
    if value is None:
        raise ValueError(f"{name} must not be None, got None")
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(f"{name} must be a number, got {value!r}")
    fvalue = float(value)
    if not np.isfinite(fvalue):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    if max_val is not None:
        if not min_val <= fvalue <= max_val:
            raise ValueError(f"{name} must be in range [{min_val:g}, {max_val:g}], got {value!r}")
    else:
        if fvalue < min_val:
            raise ValueError(f"{name} must be >= {min_val:g}, got {value!r}")
    return fvalue


def _check_bool(name: str, value: object) -> bool:
    if not isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be bool, got {value!r}")
    return bool(value)
