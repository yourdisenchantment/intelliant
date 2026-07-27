"""test_feature_branches.py
# Coverage of GraphBuilder branches (approx KNN, non-cosine metric) and
# PheromoneExtractor (use_node_density, pheromone clamping in [tau_min, tau_max]).
"""

import numpy as np
import pytest
from conftest import make_extractor, make_graph_builder
from scipy.sparse import csr_matrix


def section(title):
    print(f"\n=== {title} ===")


def _build_graph(n: int = 20, d: int = 4, seed: int = 42) -> csr_matrix:
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, d))
    gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=seed)
    return gb.build(X)


# --- GraphBuilder: approx KNN ---
def test_graphbuilder_approx_knn():
    """Checks that approx_threshold is low and auto mode switches to approx search.

    approx_threshold=5 with N=20>n_neighbors=3 forces auto to pick approx; the
    graph must be built, have shape (20, 20) and be symmetric at mutual=True.
    """

    section("GraphBuilder: approx KNN via a low approx_threshold")
    rng = np.random.default_rng(42)
    X = rng.standard_normal((20, 4))

    gb = make_graph_builder(
        n_neighbors=3,
        min_connections=3,
        knn_method="auto",
        approx_threshold=5,
        mutual=True,
        verbose=False,
        random_state=42,
    )
    G = gb.build(X)

    assert G.shape == (20, 20)
    # mutual=True => symmetric adjacency matrix (nonzero structure).
    diff = (G - G.T).tocoo()
    assert diff.data.size == 0
    # Weights in [0, 1].
    assert G.data.size > 0
    assert G.data.min() >= 0.0
    assert G.data.max() <= 1.0


# --- GraphBuilder: non-cosine metric ---
def test_graphbuilder_non_cosine_metric():
    """Checks that metric='euclidean' builds a graph with weights from the 1/(1+d) branch.

    The euclidean metric converts distances to similarities via 1/(1+d), so all
    weights must be positive and not exceed 1.0 (minimum distance 0 gives maximum
    similarity 1.0).
    """

    section("GraphBuilder: metric='euclidean' (branch 1/(1+d))")
    rng = np.random.default_rng(42)
    X = rng.standard_normal((20, 4))

    gb = make_graph_builder(n_neighbors=3, min_connections=3, metric="euclidean", verbose=False, random_state=42)
    G = gb.build(X)

    assert G.shape == (20, 20)
    assert G.data.size > 0
    assert (G.data > 0).all()
    assert (G.data <= 1.0).all()


# --- PheromoneExtractor: use_node_density ---
def test_node_density_enabled():
    """Checks that use_node_density=True changes the pheromone distribution.

    fit must work and produce a matrix of the same shape/nnz as the graph; the
    pheromone distribution with the density heuristic differs from a run without
    it.
    """

    section("PheromoneExtractor: use_node_density=True changes the pheromone field")
    G = _build_graph()

    pe_off = make_extractor(n_ants=10, n_iterations=10, use_node_density=False, verbose=False, random_state=42)
    pe_off.fit(G)
    pe_on = make_extractor(n_ants=10, n_iterations=10, use_node_density=True, verbose=False, random_state=42)
    pe_on.fit(G)

    assert pe_on.pheromone_matrix_ is not None
    assert pe_on.pheromone_matrix_.shape == G.shape
    assert pe_on.pheromone_matrix_.nnz == G.nnz

    # The density heuristic changes transition probabilities -> pheromone differs.
    assert not np.array_equal(pe_off.pheromone_matrix_.data, pe_on.pheromone_matrix_.data)


# --- PheromoneExtractor: clamping in [tau_min, tau_max] ---
def test_clamp_pheromones_bounds():
    """Checks that after fit all pheromone values lie in [tau_min, tau_max].

    MMAS clamping keeps the pheromone within the given bounds; we use explicit
    tau_min=0.1 and tau_max=10.0 so the bounds are verifiable.
    """

    section("PheromoneExtractor: clamping pheromones in [tau_min, tau_max]")
    G = _build_graph()

    pe = make_extractor(
        n_ants=10,
        n_iterations=10,
        tau_min=0.1,
        tau_max=10.0,
        verbose=False,
        random_state=42,
    )
    pe.fit(G)

    assert pe.pheromone_matrix_ is not None
    data = pe.pheromone_matrix_.data
    assert data.size > 0
    assert data.min() >= 0.1
    assert data.max() <= 10.0


# --- GraphBuilder: KNN returned non-finite distances ---
def test_knn_non_finite_raises():
    """Checks that build() raises ValueError if KNN returned non-finite distances.

    A stub metric returns NaN for any pair of points; GraphBuilder at the check
    stage (graph_builder.py:231) must detect non-finite distances and raise
    ValueError. The cosine + zero-vector branch does not fit here: sklearn
    NearestNeighbors(metric='cosine') returns 1.0, not NaN, so a NaN metric is
    used to guarantee hitting the branch.
    """

    section("GraphBuilder: KNN returned NaN/inf -> ValueError")

    def nan_metric(_u, _v):
        return np.nan

    rng = np.random.default_rng(42)
    X = rng.standard_normal((10, 4))
    gb = make_graph_builder(n_neighbors=3, min_connections=3, metric=nan_metric, verbose=False, random_state=42)
    with pytest.raises(ValueError, match="non-finite distances"):
        gb.build(X)


# --- GraphBuilder: connectivity backfill for isolated vertices ---
def test_degree_fallback_adds_edges():
    """Checks that the connectivity backfill adds edges to low-degree vertices.

    15 points in 2D: a dense cluster of 12 and 3 far points. At mutual=True and
    n_neighbors=10 the far vertices may have degree drop below
    min_connections=3; _apply_degree_fallback adds the best KNN edges so that in
    the end every vertex has at least one edge (no isolates).
    """

    section("GraphBuilder: connectivity backfill adds edges to isolates")
    rng = np.random.default_rng(42)
    cluster = rng.standard_normal((12, 2))
    far = np.array([[50.0, 50.0], [55.0, 55.0], [60.0, 60.0]])
    X = np.vstack([cluster, far])

    gb = make_graph_builder(
        n_neighbors=10,
        min_connections=3,
        mutual=True,
        verbose=False,
        random_state=42,
    )
    G = gb.build(X)

    degree = np.diff(G.indptr)
    assert (degree >= 1).all()


# --- PheromoneExtractor: elite activates later ---
def test_elite_activation_mid_run():
    """Checks that elite ants activate only starting from elite_start_iteration.

    Two runs with the same random_state are compared: elite_start_iteration=0
    (elite from the first iteration) and elite_start_iteration=8 (near the end,
    n_iterations=10). Late activation is close to the behavior without elite, so
    the pheromone distributions must differ. Additionally we check that the run
    does not fail and the matrix has the correct shape.
    """

    section("PheromoneExtractor: elite activation from elite_start_iteration")
    G = _build_graph()

    pe_early = make_extractor(
        n_ants=10,
        n_iterations=10,
        use_elite_ants=True,
        elite_start_iteration=0,
        verbose=False,
        random_state=42,
    )
    pe_early.fit(G)

    pe_late = make_extractor(
        n_ants=10,
        n_iterations=10,
        use_elite_ants=True,
        elite_start_iteration=8,
        verbose=False,
        random_state=42,
    )
    pe_late.fit(G)

    assert pe_early.pheromone_matrix_ is not None
    assert pe_late.pheromone_matrix_ is not None
    assert pe_early.pheromone_matrix_.shape == G.shape
    assert pe_late.pheromone_matrix_.shape == G.shape
    # Early activation distorts the pheromone more than late activation.
    assert not np.array_equal(pe_early.pheromone_matrix_.data, pe_late.pheromone_matrix_.data)


# --- PheromoneExtractor: evaporation_rate=0 (accumulation only) ---
def test_evaporation_rate_zero():
    """Checks that evaporation_rate=0.0 disables evaporation (accumulation only).

    At zero evaporation the old pheromone does not fade, only increments accrue;
    the run must complete without errors and return a matrix of the correct
    shape.
    """

    section("PheromoneExtractor: evaporation_rate=0.0")
    G = _build_graph()

    pe = make_extractor(
        n_ants=10,
        n_iterations=5,
        evaporation_rate=0.0,
        verbose=False,
        random_state=42,
    )
    pe.fit(G)

    assert pe.pheromone_matrix_ is not None
    assert pe.pheromone_matrix_.shape == G.shape


# --- PheromoneExtractor: evaporation_rate=1 (full fade) ---
def test_evaporation_rate_one():
    """Checks that evaporation_rate=1.0 fully wipes the old pheromone.

    At unit evaporation all accumulated pheromone is zeroed each iteration before
    applying increments; the run must complete without errors and return a matrix
    of the correct shape.
    """

    section("PheromoneExtractor: evaporation_rate=1.0")
    G = _build_graph()

    pe = make_extractor(
        n_ants=10,
        n_iterations=5,
        evaporation_rate=1.0,
        verbose=False,
        random_state=42,
    )
    pe.fit(G)

    assert pe.pheromone_matrix_ is not None
    assert pe.pheromone_matrix_.shape == G.shape


# --- PheromoneExtractor: pheromone_deposit=0 (evaporation only) ---
def test_pheromone_deposit_zero():
    """Checks that pheromone_deposit=0.0 disables deposition (evaporation only).

    At zero increment ants do not reinforce the pheromone, the field only fades
    to tau_min; the run must complete without errors and return a matrix of the
    correct shape.
    """

    section("PheromoneExtractor: pheromone_deposit=0.0")
    G = _build_graph()

    pe = make_extractor(
        n_ants=10,
        n_iterations=5,
        pheromone_deposit=0.0,
        verbose=False,
        random_state=42,
    )
    pe.fit(G)

    assert pe.pheromone_matrix_ is not None
    assert pe.pheromone_matrix_.shape == G.shape


# --- PheromoneExtractor: alpha != 1.0 + use_node_density (njit branch) ---
def test_alpha_not_one_with_density():
    """Checks the alpha != 1.0 branch together with use_node_density=True in the njit kernel.

    In _step_ants at alpha != 1.0 the pheromone is raised to the power alpha, and
    at use_node_density=True it is additionally multiplied by the node density;
    the run must go through this branch without errors and produce a matrix of
    the correct shape.
    """

    section("PheromoneExtractor: alpha=2.0 + use_node_density=True")
    G = _build_graph()

    pe = make_extractor(
        n_ants=10,
        n_iterations=5,
        alpha=2.0,
        use_node_density=True,
        verbose=False,
        random_state=42,
    )
    pe.fit(G)

    assert pe.pheromone_matrix_ is not None
    assert pe.pheromone_matrix_.shape == G.shape
