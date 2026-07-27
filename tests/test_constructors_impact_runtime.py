"""test_constructors_impact_runtime.py
# In-depth check: what HAPPENS with invalid parameters that constructors silently
# accept. Will the error reach execution?
"""

import warnings

import numpy as np
from conftest import make_clusterer, make_extractor, make_graph_builder
from scipy.sparse import csr_matrix

from intelliant.threshold import scan_thresholds


def section(title):
    print(f"\n=== {title} ===")


def try_runtime(label, fn):
    """Run with verbose off; catch any error or broken behavior."""
    try:
        result = fn()
        if isinstance(result, np.ndarray):
            print(f"OK: {label} -> ndarray shape={result.shape}, unique={np.unique(result)}")
        elif isinstance(result, list):
            print(f"OK: {label} -> list len={len(result)}")
        else:
            print(f"OK: {label} -> {type(result).__name__}")
    except Exception as e:
        print(f"ERR: {label} -> {type(e).__name__}: {e}")


def _build_base():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((20, 4)).astype(np.float32)
    gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=42)
    return X, gb.build(X)


# 1. GraphBuilder: what happens with n_neighbors=0 / -1 on a real build?
# F.5: n_neighbors=0/-1 are now caught in __init__, never reaching build.
def test_graphbuilder_invalid_n_neighbors_on_build():
    section("GraphBuilder with invalid n_neighbors on build()")
    rng = np.random.default_rng(42)
    X = rng.standard_normal((20, 4)).astype(np.float32)

    for nn in [0, -1, 1]:
        print(f"  n_neighbors={nn}:")
        try:
            gb = make_graph_builder(n_neighbors=nn, verbose=False, random_state=42)
            G = gb.build(X)
            print(f"    OK: nnz={G.nnz}, shape={G.shape}")
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")


# 2. PheromoneExtractor: what happens with n_iterations=-1 / path_length=-1 on fit?
# F.5: n_iterations=-1/path_length=-1 are now caught in __init__ (iteration 2-3).
def test_pheromone_extractor_invalid_counters_on_fit():
    section("PheromoneExtractor with invalid counters on fit()")

    _, G = _build_base()
    print(f"Base graph: nnz={G.nnz}")

    for ni, pl in [(-1, 5), (5, -1), (-5, -5)]:
        print(f"  n_iterations={ni}, path_length={pl}:")
        try:
            pe = make_extractor(n_ants=5, n_iterations=ni, path_length=pl, verbose=False, random_state=42)
            pe.fit(G)
            print(
                "    OK: pheromone range=["
                f"{pe.pheromone_matrix_.data.min():.3f}, {pe.pheromone_matrix_.data.max():.3f}]"
            )
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")


# 3. CoreClusterer: what happens with max_iterations=-1 / batch_size=-1 / min_cluster_size=0 on extract_cores?
# F.5: all parameters are caught in __init__ (iteration 2-3).
def test_core_clusterer_invalid_params_on_extract():
    section("CoreClusterer with invalid parameters on extract_cores/absorb()")

    _, G = _build_base()
    pheromone = G.copy().astype(np.float64)  # substitute as a pheromone graph
    pheromone.data[:] = 0.5  # all edges 0.5

    for params in [
        {"max_iterations": -1, "batch_size": 10, "min_cluster_size": 2},
        {"batch_size": 0, "min_cluster_size": 2},
        {"batch_size": -5, "min_cluster_size": 2},
        {"min_cluster_size": 0, "batch_size": 10},
        {"min_cluster_size": -1, "batch_size": 10},
        {"gap_ratio": -1.0, "min_cluster_size": 2, "batch_size": 10},
        {"max_gap_rank": 0, "min_cluster_size": 2, "batch_size": 10},
    ]:
        print(f"  Parameters: {params}")
        try:
            cc = make_clusterer(verbose=False, **params)
            labels = cc.extract_cores(pheromone, threshold_value=0.3)
            print(f"    OK: cores_ shape={labels.shape}, unique={np.unique(labels)}")
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")


# 4. scan_thresholds with center_percentile outside [0, 100]
def test_scan_thresholds_center_percentile_out_of_range():
    section("scan_thresholds with center_percentile outside [0, 100]")
    graph = csr_matrix(np.array([[0, 0.5, 0.0], [0.5, 0, 0.5], [0.0, 0.5, 0]]))

    for cp in [-50, 0, 100, 150, 200, 1000]:
        print(f"  center_percentile={cp}:")
        try:
            rows = scan_thresholds(graph, min_cluster_size=1, center_percentile=cp, n_steps=2)
            values = [r.value for r in rows]
            print(f"    OK: rows={len(rows)}, values={values}")
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")


# 5. extract_cores with threshold_percentile=100 and =0
def test_extract_cores_boundary_threshold_percentile():
    section("extract_cores with boundary threshold_percentile")
    graph2 = csr_matrix(np.array([[0, 0.1, 0.9], [0.1, 0, 0.5], [0.9, 0.5, 0]]))

    for p in [-1, 0, 50, 100, 101]:
        print(f"  threshold_percentile={p}:")
        try:
            cc = make_clusterer(min_cluster_size=2, batch_size=10, verbose=False)
            labels = cc.extract_cores(graph2, threshold_percentile=p)
            print(f"    OK: cores_={labels}")
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")


# 6. F.5: beta=0 (ACO on pure pheromone) and alpha=0 (ACO on pure weights)
# Previously rejected in __init__, now fit must work correctly.
def test_beta_zero_alpha_zero_fit():
    section("beta=0 / alpha=0 on fit (F.5 relaxation)")

    _, G = _build_base()
    for label, kwargs in [
        ("beta=0", {"beta": 0.0}),
        ("alpha=0", {"alpha": 0.0}),
        ("beta=0, alpha=0", {"beta": 0.0, "alpha": 0.0}),
    ]:
        print(f"  {label}:")
        try:
            pe = make_extractor(n_ants=5, verbose=False, random_state=42, **kwargs)
            pe.fit(G)
            print(
                "    OK: pheromone range=["
                f"{pe.pheromone_matrix_.data.min():.3f}, {pe.pheromone_matrix_.data.max():.3f}]"
            )
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")


# 7. F.5: elite_ratio logic (n_elite=int(round(n_ants*elite_ratio)))
def test_elite_ratio_scenarios_on_fit():
    section("elite_ratio: fit with different elite scenarios")

    _, G = _build_base()
    # elite_ratio=0.1 + use_elite_ants=True -> n_elite=int(round(10*0.1))=1
    print("  n_ants=10, elite_ratio=0.1, use_elite_ants=True (n_elite=1):")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pe = make_extractor(
                n_ants=10,
                use_elite_ants=True,
                elite_start_iteration=0,
                elite_ratio=0.1,
                verbose=False,
                random_state=42,
            )
            pe.fit(G)
            print(
                f"    OK: warnings={len(w)}, range=[{pe.pheromone_matrix_.data.min():.3f}, "
                f"{pe.pheromone_matrix_.data.max():.3f}]"
            )
            for x in w:
                print(f"      {x.category.__name__}: {x.message}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    # elite_ratio=0 + use_elite_ants=True -> n_elite=0, warning
    print("  n_ants=10, elite_ratio=0.0, use_elite_ants=True (n_elite=0 -> warning):")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pe = make_extractor(
                n_ants=10,
                use_elite_ants=True,
                elite_start_iteration=0,
                elite_ratio=0.0,
                verbose=False,
                random_state=42,
            )
            pe.fit(G)
            print(f"    OK: warnings={len(w)}")
            for x in w:
                print(f"      {x.category.__name__}: {x.message}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    # use_elite_ants=False + elite_ratio=0.5 -> ratio is not used
    print("  n_ants=5, elite_ratio=0.5, use_elite_ants=False (ratio ignored):")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pe = make_extractor(
                n_ants=5,
                use_elite_ants=False,
                elite_ratio=0.5,
                verbose=False,
                random_state=42,
            )
            pe.fit(G)
            print(f"    OK: warnings={len(w)}")
            for x in w:
                print(f"      {x.category.__name__}: {x.message}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    # n_ants=1, elite_ratio=1.0 -> all ants are elite (n_elite=1)
    print("  n_ants=1, elite_ratio=1.0, use_elite_ants=True (all elite):")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pe = make_extractor(
                n_ants=1,
                use_elite_ants=True,
                elite_start_iteration=0,
                elite_ratio=1.0,
                verbose=False,
                random_state=42,
            )
            pe.fit(G)
            print(f"    OK: warnings={len(w)}")
            for x in w:
                print(f"      {x.category.__name__}: {x.message}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")
