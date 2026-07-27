"""test_pheromone_determinism.py
# Checking determinism and reproducibility of PheromoneExtractor:
# same random_state -> identical result,
# different random_state -> differing result.
"""

import numpy as np
from conftest import make_extractor, make_graph_builder
from scipy.sparse import csr_matrix


def section(title):
    print(f"\n=== {title} ===")


def _build_graph(n: int = 20, d: int = 4, seed: int = 42) -> csr_matrix:
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, d))
    gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=seed)
    return gb.build(X)


def test_pheromone_extractor_determinism():
    """Checks that two fits with the same random_state produce an identical pheromone field.

    The seed controls ant position initialization and roulette-wheel selection, so
    two runs with the same random_state must produce byte-identical pheromone
    matrix data.
    """

    section("PheromoneExtractor: determinism of the same random_state")
    G = _build_graph()

    pe1 = make_extractor(n_ants=10, n_iterations=5, verbose=False, random_state=42)
    pe1.fit(G)
    pe2 = make_extractor(n_ants=10, n_iterations=5, verbose=False, random_state=42)
    pe2.fit(G)

    assert pe1.pheromone_matrix_ is not None
    assert pe2.pheromone_matrix_ is not None
    assert np.array_equal(pe1.pheromone_matrix_.data, pe2.pheromone_matrix_.data)
    assert np.array_equal(pe1.pheromone_matrix_.indices, pe2.pheromone_matrix_.indices)


def test_pheromone_extractor_reproducibility():
    """Checks that different random_state values produce a differing pheromone field.

    Changing the seed changes ant trajectories, so the pheromone distribution must
    differ (given a long enough run for the seed noise to show up).
    """

    section("PheromoneExtractor: reproducibility of different random_state")
    G = _build_graph()

    pe1 = make_extractor(n_ants=10, n_iterations=10, verbose=False, random_state=42)
    pe1.fit(G)
    pe2 = make_extractor(n_ants=10, n_iterations=10, verbose=False, random_state=99)
    pe2.fit(G)

    assert pe1.pheromone_matrix_ is not None
    assert pe2.pheromone_matrix_ is not None
    assert not np.array_equal(pe1.pheromone_matrix_.data, pe2.pheromone_matrix_.data)


def test_warmup_disabled():
    """Checks that warmup=False skips njit kernel warmup and the run goes normally.

    Compilation warmup runs only at warmup=True; at False the kernels compile on
    the first step of the main run. The run must complete without errors and
    return a matrix of the correct shape.
    """

    section("PheromoneExtractor: warmup=False")
    G = _build_graph()

    pe = make_extractor(
        n_ants=10,
        n_iterations=5,
        warmup=False,
        verbose=False,
        random_state=42,
    )
    pe.fit(G)

    assert pe.pheromone_matrix_ is not None
    assert pe.pheromone_matrix_.shape == G.shape


def test_n_iterations_zero():
    """Checks that n_iterations=0 leaves the pheromone equal to the initial value.

    At zero iterations the swarm loop body does not run: the pheromone matrix is
    initialized to initial_pheromone and clamped, but no increments or
    evaporation happen. All edges must have the value initial_pheromone.
    """

    section("PheromoneExtractor: n_iterations=0 -> initialization only")
    G = _build_graph()

    pe = make_extractor(
        n_ants=10,
        n_iterations=0,
        initial_pheromone=1.0,
        tau_min=0.0,
        tau_max=10.0,
        verbose=False,
        random_state=42,
    )
    pe.fit(G)

    assert pe.pheromone_matrix_ is not None
    assert pe.pheromone_matrix_.shape == G.shape
    assert np.allclose(pe.pheromone_matrix_.data, 1.0)
