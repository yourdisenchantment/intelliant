"""test_evaporation_schedule.py

Pins down WHEN the pheromone matrix decays. The two schedules are not
interchangeable, and the difference is large enough that a value taken from
the ACO literature means something else under "step".
"""

import itertools

import numpy as np
import pytest
from conftest import BASE_PHEROMONE
from scipy.sparse import csr_matrix

from intelliant import PheromoneExtractor


def _complete_graph(n: int) -> csr_matrix:
    """A complete graph, so ants never run out of moves and every step runs."""
    rows, cols = zip(*itertools.permutations(range(n), 2), strict=True)
    return csr_matrix((np.ones(len(rows)), (np.array(rows), np.array(cols))), shape=(n, n))


def _decay_after_one_iteration(schedule: str, path_length: int, rate: float) -> float:
    """Runs one iteration with deposits switched off, so only decay is left."""
    kwargs = {
        **BASE_PHEROMONE,
        "evaporation_schedule": schedule,
        "evaporation_rate": rate,
        "path_length": path_length,
        "pheromone_deposit": 0.0,
        "initial_pheromone": 1.0,
        "n_iterations": 1,
        "tau_min": 1e-12,
        "tau_max": 1e9,
    }
    pe = PheromoneExtractor(**kwargs, n_ants=4, warmup=False, verbose=False, random_state=42)
    pe.fit(_complete_graph(6))
    assert pe.pheromone_matrix_ is not None
    return float(pe.pheromone_matrix_.data.max())


@pytest.mark.parametrize("path_length", [1, 2, 3, 5])
def test_step_schedule_decays_once_per_step(path_length):
    """Under "step" the matrix decays path_length times per iteration.

    This is the property that makes evaporation_rate and path_length
    inseparable: changing the walk length changes the effective decay.
    """

    got = _decay_after_one_iteration("step", path_length, rate=0.5)
    assert got == pytest.approx(0.5**path_length)


@pytest.mark.parametrize("path_length", [1, 2, 3, 5])
def test_iteration_schedule_decays_once_per_iteration(path_length):
    """Under "iteration" the decay is one factor regardless of walk length."""

    got = _decay_after_one_iteration("iteration", path_length, rate=0.5)
    assert got == pytest.approx(0.5)


def test_schedules_diverge_beyond_a_single_step():
    """At path_length=1 the two coincide; past that they must not."""

    assert _decay_after_one_iteration("step", 1, 0.5) == pytest.approx(_decay_after_one_iteration("iteration", 1, 0.5))
    assert _decay_after_one_iteration("step", 5, 0.5) != pytest.approx(_decay_after_one_iteration("iteration", 5, 0.5))


def test_effective_rate_matches_the_documented_formula():
    """The formula quoted in the constructor comment and the docs.

    Effective per-iteration decay under "step" is 1 - (1 - rate)**path_length.
    At the calibrated rate=0.07 with path_length=10 that is 0.516 - which is
    why no literature value transfers to this schedule.
    """

    rate, path_length = 0.07, 10
    remaining = _decay_after_one_iteration("step", path_length, rate)
    assert remaining == pytest.approx((1 - rate) ** path_length)
    assert 1 - remaining == pytest.approx(0.516, abs=0.001)


def test_unknown_schedule_is_rejected():
    with pytest.raises(ValueError, match="evaporation_schedule must be one of"):
        PheromoneExtractor(**{**BASE_PHEROMONE, "evaporation_schedule": "per-ant"}, n_ants=1, verbose=False)
