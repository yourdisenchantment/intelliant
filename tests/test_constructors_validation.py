"""test_constructors_validation.py
# Validation of parameters in __init__ of all three classes.
# Goal: systematically go through each parameter and see which are rejected,
# which are silently accepted, and how clear the messages are.
#
# F.5 (iteration 3): the validation table from TASK.md. beta/alpha >= 0
# (was > 0), n_ants/path_length >= 1, n_neighbors/approx_threshold >= 1,
# min_cluster_size/batch_size/max_gap_rank >= 1, added validations
# node_density_gamma/elite_ratio/elite_multiplier/pheromone_deposit/
# initial_pheromone >= 0.
"""

import warnings

import numpy as np
import pytest
from conftest import make_clusterer, make_extractor, make_graph_builder
from scipy.sparse import csr_matrix

from intelliant.threshold import find_threshold, scan_thresholds


def section(title):
    print(f"\n=== {title} ===")


# --- GraphBuilder ---
def test_graphbuilder_init_validation():
    section("GraphBuilder: __init__ parameters")

    # n_neighbors
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(n_neighbors=0)
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(n_neighbors=-1)
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(n_neighbors=1.5)
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(n_neighbors=True)
    make_graph_builder(n_neighbors=1, min_connections=1)  # boundary >= 1

    # min_connections
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(min_connections=-1)
    make_graph_builder(min_connections=0)  # explicitly disables the extra fill
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(n_neighbors=3, min_connections=5)  # min_connections > n_neighbors
    assert make_graph_builder().min_connections == 5  # default resolves to min(5, n_neighbors)
    assert make_graph_builder(n_neighbors=3).min_connections == 3
    # explicit None takes the same adaptive path as the omitted default
    assert make_graph_builder(n_neighbors=3, min_connections=None).min_connections == 3
    assert make_graph_builder(min_connections=None).min_connections == 5

    # knn_method
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(knn_method="exactt")
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(knn_method="EXACT")
    make_graph_builder(knn_method="auto")

    # approx_threshold
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(approx_threshold=0)
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(approx_threshold=-1)
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(approx_threshold=1.5)
    make_graph_builder(approx_threshold=1)  # boundary >= 1


# --- PheromoneExtractor ---
def test_pheromone_extractor_init_validation():
    section("PheromoneExtractor: __init__ parameters")

    # n_ants and n_iterations
    make_extractor(n_ants=None)  # required in fit
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=-1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1.5)
    make_extractor(n_ants=1)  # boundary >= 1

    # numpy integers are accepted and normalized to plain int (REVIEW #10)
    pe_np = make_extractor(n_ants=np.int64(3), n_iterations=np.int64(2))
    assert pe_np.n_ants == 3
    assert type(pe_np.n_ants) is int
    assert pe_np.n_iterations == 2
    assert type(pe_np.n_iterations) is int

    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, n_iterations=-1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, n_iterations=1.5)
    make_extractor(n_ants=1, n_iterations=0)  # no-op

    # path_length
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, path_length=0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, path_length=-1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, path_length=1.5)
    make_extractor(n_ants=1, path_length=1)  # boundary >= 1

    # beta (F.5: >= 0, was > 0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, beta=-0.1)
    make_extractor(n_ants=1, beta=0)  # ACO on pure pheromone, relaxed from > 0
    make_extractor(n_ants=1, beta=2.0)  # default

    # evaporation_rate boundaries (closed in F.3)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, evaporation_rate=-0.1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, evaporation_rate=1.5)
    make_extractor(n_ants=1, evaporation_rate=0.0)
    make_extractor(n_ants=1, evaporation_rate=1.0)

    # node_density_gamma (F.5: added validation >= 0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, node_density_gamma=-1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, node_density_gamma=-0.1)
    make_extractor(n_ants=1, node_density_gamma=0)
    make_extractor(n_ants=1, node_density_gamma=1.0)  # default

    # elite ants
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, use_elite_ants=True)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_start_iteration=-1)
    make_extractor(n_ants=1, use_elite_ants=True, elite_start_iteration=0)

    # elite_ratio (F.5: added validation >= 0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_ratio=-0.1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_ratio=-1)
    make_extractor(n_ants=1, elite_ratio=0)
    make_extractor(n_ants=1, elite_ratio=0.5)
    make_extractor(n_ants=1, elite_ratio=1.0)  # boundary; all ants are elite

    # elite_multiplier (F.5: added validation >= 0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_multiplier=-1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_multiplier=-0.5)
    make_extractor(n_ants=1, elite_multiplier=0)  # degenerate: elite deposits nothing
    make_extractor(n_ants=1, elite_multiplier=5.0)  # default

    # tau boundaries
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, tau_min=10, tau_max=1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, tau_min=5, tau_max=5)
    make_extractor(n_ants=1, tau_min=0, tau_max=1e9)  # extreme spread

    # tau_min / tau_max go through _check_float: NaN, None, inf, negative,
    # bool and str all raise a clean ValueError (polish round 1, REVIEW #1).
    for bad in [float("nan"), None, float("inf"), -5.0, True, "1.0"]:
        with pytest.raises(ValueError, match="tau_min"):
            make_extractor(n_ants=1, tau_min=bad)
        with pytest.raises(ValueError, match="tau_max"):
            make_extractor(n_ants=1, tau_max=bad)
    make_extractor(n_ants=1, tau_min=0.01, tau_max=10.0)  # valid pair (defaults)

    # alpha (F.5: >= 0, was > 0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, alpha=-0.1)
    make_extractor(n_ants=1, alpha=0)  # ACO on pure weights, relaxed from > 0
    make_extractor(n_ants=1, alpha=1.0)  # default

    # pheromone_deposit (F.5: added validation >= 0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, pheromone_deposit=-0.1)
    make_extractor(n_ants=1, pheromone_deposit=0)  # ACO as structural analysis
    make_extractor(n_ants=1, pheromone_deposit=0.1)  # default

    # initial_pheromone (F.5: added validation >= 0)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, initial_pheromone=-0.1)
    make_extractor(n_ants=1, initial_pheromone=0)
    make_extractor(n_ants=1, initial_pheromone=2.0)  # default


def test_elite_start_iteration_ge_n_iterations_warns():
    section("PheromoneExtractor: elite_start_iteration >= n_iterations -> warning")

    # elite_start_iteration >= n_iterations -> warning (not an error)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        make_extractor(n_ants=1, n_iterations=2, use_elite_ants=True, elite_start_iteration=5)
        user_warnings = [x for x in w if issubclass(x.category, UserWarning)]
    assert user_warnings, f"expected UserWarning, total warnings={len(w)}"


# --- bool flags across all three classes (polish round 2, R2-1) ---
# Every public bool flag goes through the shared _check_bool: bool and np.bool_
# are accepted (normalized to plain bool), everything else - 0/1 included -
# raises ValueError. Each case: (id, factory(value) -> instance, attr name).
BOOL_FLAG_CASES = [
    ("gb_mutual", lambda v: make_graph_builder(mutual=v, verbose=False), "mutual"),
    ("gb_verbose", lambda v: make_graph_builder(verbose=v), "verbose"),
    (
        "pe_use_node_density",
        lambda v: make_extractor(n_ants=1, use_node_density=v, verbose=False),
        "use_node_density",
    ),
    (
        # elite_start_iteration is set so that use_elite_ants=True is accepted
        "pe_use_elite_ants",
        lambda v: make_extractor(n_ants=1, use_elite_ants=v, elite_start_iteration=0, verbose=False),
        "use_elite_ants",
    ),
    ("pe_use_no_return", lambda v: make_extractor(n_ants=1, use_no_return=v, verbose=False), "use_no_return"),
    ("pe_warmup", lambda v: make_extractor(n_ants=1, warmup=v, verbose=False), "warmup"),
    ("pe_verbose", lambda v: make_extractor(n_ants=1, verbose=v), "verbose"),
    (
        "cc_absorb_isolated",
        lambda v: make_clusterer(min_cluster_size=2, batch_size=5, absorb_isolated=v, verbose=False),
        "absorb_isolated",
    ),
    ("cc_verbose", lambda v: make_clusterer(min_cluster_size=2, batch_size=5, verbose=v), "verbose"),
]


@pytest.mark.parametrize(("case_id", "factory", "attr"), BOOL_FLAG_CASES, ids=[c[0] for c in BOOL_FLAG_CASES])
def test_bool_flag_accepts_bool_and_numpy_bool(case_id, factory, attr):
    """Checks that a bool flag accepts bool / np.bool_ and stores a plain bool."""

    for value, expected in [(True, True), (False, False), (np.True_, True), (np.False_, False)]:
        obj = factory(value)
        stored = getattr(obj, attr)
        assert stored == expected, f"{case_id}: {attr}={value!r} stored as {stored!r}"
        assert type(stored) is bool, f"{case_id}: {attr}={value!r} stored as {type(stored).__name__}"


@pytest.mark.parametrize(("case_id", "factory", "attr"), BOOL_FLAG_CASES, ids=[c[0] for c in BOOL_FLAG_CASES])
def test_bool_flag_rejects_non_bool(case_id, factory, attr):
    """Checks that a bool flag rejects 0 / 1 / str / None with a clean ValueError."""

    for bad in [0, 1, "true", None]:
        with pytest.raises(ValueError, match=f"{attr} must be bool"):
            factory(bad)


def test_graphbuilder_mutual_numpy_true_builds_and_graph():
    """Checks that mutual=np.True_ builds the same AND graph as mutual=True (R2-1).

    A 1-D chain with growing gaps and n_neighbors=1 separates AND from OR
    sharply: only the pair (0, 1) is mutually nearest, so the AND graph has 2
    entries and the OR graph 10. Before round 2 the `mutual is True` identity
    check silently sent np.True_ (any numpy comparison result) into the OR
    branch.
    """

    section("GraphBuilder: mutual=np.True_ equals mutual=True (AND graph)")
    X = np.array([[0.0], [1.0], [3.0], [6.0], [10.0], [15.0]])
    kwargs = {"n_neighbors": 1, "min_connections": 0, "metric": "euclidean", "verbose": False}

    g_true = make_graph_builder(mutual=True, **kwargs).build(X)
    g_np = make_graph_builder(mutual=np.True_, **kwargs).build(X)
    g_or = make_graph_builder(mutual=False, **kwargs).build(X)

    print(f"  AND nnz={g_true.nnz}, np.True_ nnz={g_np.nnz}, OR nnz={g_or.nnz}")
    assert g_np.nnz == g_true.nnz
    assert np.array_equal(g_np.indices, g_true.indices)
    assert np.array_equal(g_np.data, g_true.data)
    # Premise: AND and OR really differ on this data, so the equality above
    # proves the AND branch was taken.
    assert g_true.nnz == 2
    assert g_or.nnz == 10


# --- CoreClusterer ---
def test_core_clusterer_init_validation():
    section("CoreClusterer: __init__ parameters")

    make_clusterer(min_cluster_size=None, batch_size=10)  # required in extract_cores
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=0, batch_size=10)
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=-1, batch_size=10)
    make_clusterer(min_cluster_size=1, batch_size=10)  # boundary >= 1

    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=10, max_iterations=-1)
    make_clusterer(min_cluster_size=2, batch_size=10, max_iterations=0)  # no-op

    make_clusterer(min_cluster_size=2, batch_size=None)  # required in absorb
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=0)
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=-5)
    make_clusterer(min_cluster_size=2, batch_size=1)  # boundary >= 1

    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=10, gap_ratio=-1.0)
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=10, gap_ratio=0.5)
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=10, gap_ratio=0.0)
    make_clusterer(min_cluster_size=2, batch_size=10, gap_ratio=1.0)  # boundary
    make_clusterer(min_cluster_size=2, batch_size=10, gap_ratio=2.0)  # default

    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=10, max_gap_rank=0)
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=10, max_gap_rank=-1)
    make_clusterer(min_cluster_size=2, batch_size=10, max_gap_rank=1)  # boundary >= 1


# find_threshold
def test_find_threshold_validation():
    section("find_threshold: validation")

    # empty data (closed in F.1, but anyway)
    with pytest.raises((ValueError, TypeError)):
        find_threshold(np.array([]))
    with pytest.raises((ValueError, TypeError)):
        find_threshold(np.array([1, 2, 3]), method="bogus")
    with pytest.raises((ValueError, TypeError)):
        find_threshold(np.array([1, 2, 3]), method="percentile", percentile=150)
    with pytest.raises((ValueError, TypeError)):
        find_threshold(np.array([1, 2, 3]), method="percentile", percentile=-5)

    # NaN / inf data is rejected up front for every method (polish round 1,
    # REVIEW #6): previously stat returned NaN silently and otsu raised a raw
    # numpy histogram error.
    for method in ["otsu", "percentile", "stat"]:
        with pytest.raises(ValueError, match="data contains NaN or inf"):
            find_threshold(np.array([1.0, np.nan, 3.0]), method=method)
        with pytest.raises(ValueError, match="data contains NaN or inf"):
            find_threshold(np.array([1.0, np.inf, 3.0]), method=method)

    # k and bins are validated up front (polish round 2, R2-4): previously
    # k=nan returned ThresholdResult(nan, 0.0) silently and bins=0 / 1.5
    # leaked raw numpy errors.
    data = np.array([1.0, 2.0, 3.0, 4.0])
    with pytest.raises(ValueError, match="k must be a finite number"):
        find_threshold(data, method="stat", k=float("nan"))
    with pytest.raises(ValueError, match="k must be a number"):
        find_threshold(data, method="stat", k="1")
    with pytest.raises(ValueError, match="bins must be int >= 1"):
        find_threshold(data, method="otsu", bins=0)
    with pytest.raises(ValueError, match="bins must be int >= 1"):
        find_threshold(data, method="otsu", bins=1.5)

    # Negative k is legitimate: mean + k*std with k < 0 lowers the threshold.
    r_neg = find_threshold(data, method="stat", k=-1.0)
    assert np.isclose(r_neg.value, float(np.mean(data) - np.std(data)))

    # numpy integer bins is accepted and matches the plain-int run.
    r_np = find_threshold(data, method="otsu", bins=np.int64(50))
    r_int = find_threshold(data, method="otsu", bins=50)
    assert r_np == r_int


# scan_thresholds
def test_scan_thresholds_validation():
    section("scan_thresholds: validation")

    graph = csr_matrix((np.array([0, 1, 0, 1]), (np.array([0, 0, 1, 1]), np.array([1, 0, 0, 1]))), shape=(2, 2))
    graph.data = np.array([0.5, 0.5, 0.5, 0.5])  # all 4 edges with weight 0.5

    with pytest.raises((ValueError, TypeError)):
        scan_thresholds(graph, min_cluster_size=1, percentiles=[-5])
    with pytest.raises((ValueError, TypeError)):
        scan_thresholds(graph, min_cluster_size=1, percentiles=[105])
    scan_thresholds(graph, min_cluster_size=1, percentiles=[0, 50, 100])
    with pytest.raises((ValueError, TypeError)):
        scan_thresholds(graph, min_cluster_size=1, center_percentile=200, n_steps=1)  # out of [0, 100]

    # grid parameters are validated up front (polish round 1, REVIEW #9):
    # previously n_steps=-1 silently returned [] and step<=0 was accepted.
    with pytest.raises(ValueError, match="n_steps"):
        scan_thresholds(graph, min_cluster_size=1, n_steps=-1)
    with pytest.raises(ValueError, match="step"):
        scan_thresholds(graph, min_cluster_size=1, step=0)
    with pytest.raises(ValueError, match="step"):
        scan_thresholds(graph, min_cluster_size=1, step=-1)
    with pytest.raises(ValueError, match="center_percentile"):
        scan_thresholds(graph, min_cluster_size=1, center_percentile=-5)

    # An explicit empty percentiles list raises (polish round 2, R2-5):
    # previously it silently returned [].
    with pytest.raises(ValueError, match="percentiles must not be empty"):
        scan_thresholds(graph, min_cluster_size=1, percentiles=[])

    # NaN edge weights are rejected before any clustering runs.
    bad_graph = graph.copy()
    bad_graph.data[0] = np.nan
    with pytest.raises(ValueError, match="pheromone_graph contains NaN or inf"):
        scan_thresholds(bad_graph, min_cluster_size=1, percentiles=[50.0])


# --- GraphBuilder: determinism ---
def _build_X(n: int = 20, d: int = 4, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n, d))


def test_graphbuilder_determinism_same_random_state():
    """Checks that two runs with the same random_state produce an identical graph.

    Exact search is deterministic and does not depend on the seed, so two build
    calls with the same parameters must produce matching indices and data.
    """

    section("GraphBuilder: determinism of the same random_state")
    X = _build_X()

    gb1 = make_graph_builder(n_neighbors=3, min_connections=3, knn_method="exact", verbose=False, random_state=42)
    G1 = gb1.build(X)
    gb2 = make_graph_builder(n_neighbors=3, min_connections=3, knn_method="exact", verbose=False, random_state=42)
    G2 = gb2.build(X)

    assert np.array_equal(G1.indices, G2.indices)
    assert np.array_equal(G1.data, G2.data)
    assert G1.nnz == G2.nnz


def test_graphbuilder_reproducibility_different_random_state():
    """Checks that exact KNN does not depend on random_state: different seeds give the same graph.

    Exact search is deterministic, so changing random_state must not change the
    result; reproducibility (different results) is checked only for approx search.
    Here we assert that exact matches across different seeds.
    """

    section("GraphBuilder: exact KNN does not depend on random_state")
    X = _build_X()

    gb1 = make_graph_builder(n_neighbors=3, min_connections=3, knn_method="exact", verbose=False, random_state=42)
    G1 = gb1.build(X)
    gb2 = make_graph_builder(n_neighbors=3, min_connections=3, knn_method="exact", verbose=False, random_state=99)
    G2 = gb2.build(X)

    # Exact KNN is deterministic: the result does not depend on random_state.
    assert np.array_equal(G1.indices, G2.indices)
    assert np.array_equal(G1.data, G2.data)
