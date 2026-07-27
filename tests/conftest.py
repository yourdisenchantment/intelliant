"""Shared construction helpers for the test suite.

The library deliberately has NO defaults for calibratable parameters: while
calibration is in progress a default is a silently applied, unvalidated value.
Every caller must state what it runs with.

Tests would otherwise repeat that full parameter set at ~450 call sites, which
just moves the defaults out of the library and into hundreds of copies. Instead
the baseline lives here once, and a call site names only what it is actually
testing:

    pe = make_extractor(beta=3.0)      # baseline, except beta

BASE_* below are the values that used to be the library defaults. They are kept
byte-identical on purpose, so that removing the defaults changes no test
outcome. They are NOT the calibrated recommendation - the calibrated base
config (tmp/ROADMAP.md, section 2) differs on path_length, evaporation_rate,
pheromone_deposit and initial_pheromone. Moving the suite onto the calibrated
values is a separate, deliberate change: it alters what the tests exercise and
must be judged on its own.
"""

from typing import Any

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from intelliant import CoreClusterer, GraphBuilder, PheromoneExtractor

BASE_GRAPH: dict[str, Any] = {
    "n_neighbors": 15,
    "metric": "cosine",
    "mutual": True,
}

BASE_PHEROMONE: dict[str, Any] = {
    "n_iterations": 20,
    "path_length": 15,
    "beta": 2.0,
    "alpha": 1.0,
    "evaporation_rate": 0.1,
    "pheromone_deposit": 0.1,
    "initial_pheromone": 2.0,
    "tau_min": 0.01,
    "tau_max": 10.0,
    # Heuristic parameters. The library requires these only when the matching
    # use_* flag is on; they are kept in the baseline (at their former default
    # values) so that a test flipping a heuristic on does not have to restate
    # them. Validated but unused while the flags are off.
    "node_density_gamma": 1.0,
    "elite_ratio": 0.1,
    "elite_multiplier": 5.0,
    # elite_start_iteration is deliberately absent: it has no former default,
    # and "required when use_elite_ants=True" is an asserted error site.
}

BASE_CORE: dict[str, Any] = {
    "max_iterations": 20,
    "gap_ratio": 3.0,
    "max_gap_rank": 3,
}


def make_graph_builder(**overrides: Any) -> GraphBuilder:
    """Builds a GraphBuilder on the baseline, overridden by keyword."""
    return GraphBuilder(**{**BASE_GRAPH, **overrides})


def make_extractor(**overrides: Any) -> PheromoneExtractor:
    """Builds a PheromoneExtractor on the baseline, overridden by keyword."""
    return PheromoneExtractor(**{**BASE_PHEROMONE, **overrides})


def make_clusterer(**overrides: Any) -> CoreClusterer:
    """Builds a CoreClusterer on the baseline, overridden by keyword."""
    return CoreClusterer(**{**BASE_CORE, **overrides})


@pytest.fixture
def small_graph() -> csr_matrix:
    """A four-node symmetric graph with two weighted pairs - enough for fit()
    to reach the per-iteration code without any dependence on real data."""
    rows = np.array([0, 1, 2, 3])
    cols = np.array([1, 0, 3, 2])
    data = np.array([0.9, 0.9, 0.4, 0.4])
    return csr_matrix((data, (rows, cols)), shape=(4, 4))
