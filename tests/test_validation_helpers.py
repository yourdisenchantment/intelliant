"""test_validation_helpers.py

Direct tests for the private `_check_int` / `_check_float` helpers extracted in
F.2. Locks the exact error message format that the refactor must preserve
byte-for-byte, plus the None-handling and overload contract.
"""

import math

import numpy as np
import pytest

from intelliant._validation import _check_bool
from intelliant.core_clusterer import _check_int as cc_check_int
from intelliant.graph_builder import _check_int as gb_check_int
from intelliant.pheromone_extractor import _check_float
from intelliant.pheromone_extractor import _check_int as pe_check_int

# All three module copies of _check_int are identical by construction; we test
# each to guard against a future copy-divergence.
_CHECK_INTS = [gb_check_int, pe_check_int, cc_check_int]


@pytest.mark.parametrize("check_int", _CHECK_INTS, ids=["graph", "pheromone", "core"])
class TestCheckInt:
    def test_ok(self, check_int):
        assert check_int("x", 5, 1) == 5

    def test_min_boundary(self, check_int):
        assert check_int("x", 1, 1) == 1
        assert check_int("x", 0, 0) == 0

    def test_none_default_rejects(self, check_int):
        with pytest.raises(ValueError, match=r"^x must be int >= 1, got None$"):
            check_int("x", None, 1)

    def test_none_allowed(self, check_int):
        assert check_int("x", None, 1, allow_none=True) is None

    def test_bool_rejected(self, check_int):
        with pytest.raises(ValueError, match=r"^x must be int >= 1, got True$"):
            check_int("x", True, 1)

    def test_float_rejected(self, check_int):
        with pytest.raises(ValueError, match=r"^x must be int >= 1, got 1\.0$"):
            check_int("x", 1.0, 1)

    def test_below_min(self, check_int):
        with pytest.raises(ValueError, match=r"^x must be int >= 1, got 0$"):
            check_int("x", 0, 1)

    def test_below_min_none_suffix(self, check_int):
        with pytest.raises(ValueError, match=r"^x must be int >= 1 or None, got 0$"):
            check_int("x", 0, 1, allow_none=True)

    def test_none_allowed_keeps_min_check(self, check_int):
        # allow_none only relaxes the None case; other invalid values still raise
        with pytest.raises(ValueError, match=r"^x must be int >= 0 or None, got -1$"):
            check_int("x", -1, 0, allow_none=True)

    def test_numpy_int_accepted_as_plain_int(self, check_int):
        # numbers.Integral covers numpy integers; the helper converts to plain int
        result = check_int("x", np.int64(5), 1)
        assert result == 5
        assert type(result) is int

    def test_str_rejected_with_value_error(self, check_int):
        # a string must be a clean ValueError, not a TypeError from a comparison
        with pytest.raises(ValueError, match=r"^x must be int >= 1, got '5'$"):
            check_int("x", "5", 1)


class TestCheckFloat:
    def test_ok_lower_bound(self):
        assert _check_float("x", 0.5, 0.0) == 0.5

    def test_lower_boundary_inclusive(self):
        assert _check_float("x", 0.0, 0.0) == 0.0

    def test_range_inclusive_both_ends(self):
        assert _check_float("x", 0.0, 0.0, 1.0) == 0.0
        assert _check_float("x", 1.0, 0.0, 1.0) == 1.0

    def test_below_lower(self):
        with pytest.raises(ValueError, match=r"^x must be >= 0, got -1$"):
            _check_float("x", -1, 0.0)

    def test_out_of_range(self):
        with pytest.raises(ValueError, match=r"^x must be in range \[0, 1\], got 2$"):
            _check_float("x", 2, 0.0, 1.0)

    def test_out_of_range_negative(self):
        with pytest.raises(ValueError, match=r"^x must be in range \[0, 1\], got -0.5$"):
            _check_float("x", -0.5, 0.0, 1.0)

    def test_none_rejected(self):
        with pytest.raises(ValueError, match=r"^x must not be None, got None$"):
            _check_float("x", None, 0.0)

    def test_nan_rejected(self):
        with pytest.raises(ValueError, match=r"^x must be a finite number, got nan$"):
            _check_float("x", math.nan, 0.0)

    def test_inf_rejected(self):
        with pytest.raises(ValueError, match=r"^x must be a finite number, got inf$"):
            _check_float("x", math.inf, 0.0)

    def test_neg_inf_rejected(self):
        with pytest.raises(ValueError, match=r"^x must be a finite number, got -inf$"):
            _check_float("x", -math.inf, 0.0)

    def test_int_accepted_as_float(self):
        # int is a valid finite number for np.isfinite; helper returns it as-is
        assert _check_float("x", 3, 0.0) == 3

    def test_numpy_float_accepted_as_plain_float(self):
        # numbers.Real covers numpy floats; the helper converts to plain float
        result = _check_float("x", np.float32(0.5), 0.0)
        assert result == 0.5
        assert type(result) is float

    def test_bool_rejected(self):
        # bool is an int subclass but not a valid float parameter
        with pytest.raises(ValueError, match=r"^x must be a number, got True$"):
            _check_float("x", True, 0.0)
        with pytest.raises(ValueError, match=r"^x must be a number, got False$"):
            _check_float("x", False, 0.0)

    def test_str_rejected_with_value_error(self):
        # a string must be a clean ValueError, not a TypeError from np.isfinite
        with pytest.raises(ValueError, match=r"^x must be a number, got '1.0'$"):
            _check_float("x", "1.0", 0.0)


class TestCheckBool:
    # _check_bool was added in polish round 2 (REVIEW R2-1): every public bool
    # flag goes through it, accepting bool | np.bool_ and rejecting the rest.

    def test_plain_bool_passthrough(self):
        assert _check_bool("x", True) is True
        assert _check_bool("x", False) is False

    def test_numpy_bool_normalized_to_plain_bool(self):
        for value, expected in [(np.True_, True), (np.False_, False)]:
            result = _check_bool("x", value)
            assert result == expected
            assert type(result) is bool

    def test_int_rejected(self):
        # 0 and 1 are the classic truthy traps; both must raise, not coerce
        with pytest.raises(ValueError, match=r"^x must be bool, got 0$"):
            _check_bool("x", 0)
        with pytest.raises(ValueError, match=r"^x must be bool, got 1$"):
            _check_bool("x", 1)

    def test_str_rejected(self):
        with pytest.raises(ValueError, match=r"^x must be bool, got 'true'$"):
            _check_bool("x", "true")

    def test_none_rejected(self):
        with pytest.raises(ValueError, match=r"^x must be bool, got None$"):
            _check_bool("x", None)
