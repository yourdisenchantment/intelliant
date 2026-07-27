# src/intelliant/_validation.py
"""Shared parameter checks.

One place, so that every public parameter is rejected the same way and with
the same message shape: `<name> must be <requirement>, got <value>`. The error
text is part of the API - there is a test asserting every one of them.
"""

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
    """Check that a value is an integer at or above a minimum.

    Accepts anything registered as `numbers.Integral`, so numpy integers pass,
    and normalises the result to a plain `int`.

    Args:
        name: Parameter name, used in the error message.
        value: The value to check.
        min_val: Smallest acceptable value, inclusive.
        allow_none: Whether None is acceptable, in which case it is returned
            unchanged.

    Returns:
        The value as a plain `int`, or None when allowed and given.

    Raises:
        ValueError: If the value is not an integer, is a bool, or is below
            `min_val`.
    """
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
    """Check that a value is a finite real number within a range.

    Args:
        name: Parameter name, used in the error message.
        value: The value to check.
        min_val: Lower bound, inclusive.
        max_val: Upper bound, inclusive. None leaves the value unbounded
            above.

    Returns:
        The value as a plain `float`.

    Raises:
        ValueError: If the value is None, a bool, not a real number, not
            finite, or outside the range. NaN is rejected here rather than
            propagating into the pheromone field, where it would poison every
            comparison downstream.
    """
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
    """Check that a value is a boolean.

    `np.bool_` is accepted and normalised to a plain `bool`; anything else is
    rejected, including 0 and 1. A truthiness test would have silently taken
    `np.True_` down the wrong branch, which is exactly what happened before
    this helper existed.

    Args:
        name: Parameter name, used in the error message.
        value: The value to check.

    Returns:
        The value as a plain `bool`.

    Raises:
        ValueError: If the value is not a bool or `np.bool_`.
    """
    if not isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be bool, got {value!r}")
    return bool(value)
