"""test_constructors_edge_cases.py
# Running boundary and borderline validation scenarios not covered by the main
# tests: inf/nan, None, bool as int, elite_ratio > 1, min_cluster_size=1 on a
# graph with 1 edge, etc.
"""

import warnings

import numpy as np
from conftest import make_clusterer, make_extractor, make_graph_builder
from scipy.sparse import csr_matrix


def section(title):
    print(f"\n=== {title} ===")


def _build_graph():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((20, 4))
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
    return X, gb.build(X)


# --- 1. Boundary parameter values on a real fit/build ---


def test_boundary_values_on_fit_build():
    section("Boundary parameter values on fit/build")

    rng = np.random.default_rng(42)
    X = rng.standard_normal((20, 4))

    # n_neighbors=1 on 2 points (minimum for KNN+1)
    print("  n_neighbors=1 on 2 points:")
    try:
        gb = make_graph_builder(n_neighbors=1, min_connections=1, verbose=False, random_state=42)
        G = gb.build(X[:2])
        print(f"    OK: nnz={G.nnz}, shape={G.shape}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    # path_length=1 (one step per iteration)
    print("  path_length=1:")
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
    G = gb.build(X)
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pe = make_extractor(n_ants=3, path_length=1, verbose=False, random_state=42)
            pe.fit(G)
            print(
                f"    OK: range=[{pe.pheromone_matrix_.data.min():.3f}, "
                f"{pe.pheromone_matrix_.data.max():.3f}], warnings={len(w)}"
            )
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    # n_ants=1 (a single ant)
    print("  n_ants=1:")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pe = make_extractor(n_ants=1, verbose=False, random_state=42)
            pe.fit(G)
            print(
                f"    OK: range=[{pe.pheromone_matrix_.data.min():.3f}, "
                f"{pe.pheromone_matrix_.data.max():.3f}], warnings={len(w)}"
            )
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    # min_cluster_size=1 (degenerate: a component of size 1 is a core)
    print("  min_cluster_size=1 on a graph with 1 edge (3 vertices):")
    G_tiny = csr_matrix((np.array([0.5]), (np.array([0]), np.array([1]))), shape=(3, 3))
    try:
        pe = make_extractor(n_ants=2, verbose=False, random_state=42)
        pe.fit(G_tiny)
        cc = make_clusterer(min_cluster_size=1, batch_size=10, verbose=False)
        cores = cc.extract_cores(pe.pheromone_matrix_, threshold_value=0.1)
        print(f"    OK: cores={cores}, n_cores={len(np.unique(cores[cores >= 0]))}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    # batch_size=1 (one noise point at a time)
    print("  batch_size=1 on absorb:")
    try:
        pe = make_extractor(n_ants=5, verbose=False, random_state=42)
        pe.fit(G)
        cc = make_clusterer(min_cluster_size=2, batch_size=1, max_iterations=3, verbose=False)
        labels = cc.fit_predict(pe.pheromone_matrix_, threshold_value=0.1, X=X)
        print(f"    OK: unique={np.unique(labels)}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")


# --- 2. elite_ratio > 1.0 ---


def test_elite_ratio_greater_than_one():
    section("elite_ratio > 1.0 -> n_elite=int(round(n_ants*ratio)) can be > n_ants")

    _, G = _build_graph()
    # n_ants=10, elite_ratio=1.5 -> n_elite=15, numpy silently clips is_elite[:15]
    print("  n_ants=10, elite_ratio=1.5 (n_elite=15 > n_ants=10):")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            pe = make_extractor(
                n_ants=10,
                use_elite_ants=True,
                elite_start_iteration=0,
                elite_ratio=1.5,
                verbose=False,
                random_state=42,
            )
            pe.fit(G)
            # numpy silently clips the slice -> is_elite=True for all n_ants
            print(f"    fit passed without IndexError. warnings={len(w)}")
            for x in w:
                print(f"      [{x.category.__name__}] {x.message}")
            print(f"    range=[{pe.pheromone_matrix_.data.min():.3f}, {pe.pheromone_matrix_.data.max():.3f}]")
    except IndexError as e:
        print(f"    IndexError as expected: {e}")
    except Exception as e:
        print(f"    {type(e).__name__}: {e}")


# --- 3. inf/nan in float parameters ---


def test_inf_nan_in_float_params():
    section("inf / nan in float parameters")

    for v in [float("inf"), float("-inf"), float("nan")]:
        try:
            pe = make_extractor(n_ants=1, beta=v)
            # accepted: check fit
            gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
            rng = np.random.default_rng(42)
            G2 = gb.build(rng.standard_normal((10, 4)))
            pe.fit(G2)
            print(
                f"  beta={v}: ACCEPTED, fit range=[{pe.pheromone_matrix_.data.min():.3f}, "
                f"{pe.pheromone_matrix_.data.max():.3f}]"
            )
        except (ValueError, TypeError) as e:
            print(f"  beta={v}: {type(e).__name__}: {str(e)[:80]}")

    for v in [float("inf"), float("-inf"), float("nan")]:
        try:
            pe = make_extractor(n_ants=1, alpha=v)
            gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
            rng = np.random.default_rng(42)
            G2 = gb.build(rng.standard_normal((10, 4)))
            pe.fit(G2)
            print(
                f"  alpha={v}: ACCEPTED, fit range=[{pe.pheromone_matrix_.data.min():.3f}, "
                f"{pe.pheromone_matrix_.data.max():.3f}]"
            )
        except (ValueError, TypeError) as e:
            print(f"  alpha={v}: {type(e).__name__}: {str(e)[:80]}")

    for v in [float("inf"), float("-inf"), float("nan")]:
        try:
            pe = make_extractor(n_ants=1, pheromone_deposit=v)
            print(f"  pheromone_deposit={v}: ACCEPTED")
        except (ValueError, TypeError) as e:
            print(f"  pheromone_deposit={v}: {type(e).__name__}: {str(e)[:80]}")

    for v in [float("inf"), float("-inf"), float("nan")]:
        try:
            pe = make_extractor(n_ants=1, initial_pheromone=v)
            gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
            rng = np.random.default_rng(42)
            G2 = gb.build(rng.standard_normal((10, 4)))
            pe.fit(G2)
            print(
                f"  initial_pheromone={v}: ACCEPTED, fit range=[{pe.pheromone_matrix_.data.min():.3f}, "
                f"{pe.pheromone_matrix_.data.max():.3f}]"
            )
        except (ValueError, TypeError) as e:
            print(f"  initial_pheromone={v}: {type(e).__name__}: {str(e)[:80]}")


# --- 4. None in float parameters (TypeError expected) ---


def test_none_in_float_params():
    section("None in float parameters -> TypeError (not ValueError)")

    for pname in [
        "beta",
        "alpha",
        "evaporation_rate",
        "pheromone_deposit",
        "initial_pheromone",
        "node_density_gamma",
        "elite_ratio",
        "elite_multiplier",
    ]:
        try:
            make_extractor(n_ants=1, **{pname: None})
            print(f"  {pname}=None: ACCEPTED (bug: should be ValueError)")
        except ValueError as e:
            print(f"  {pname}=None: ValueError: {str(e)[:80]}")
        except TypeError as e:
            print(f"  {pname}=None: TypeError: {str(e)[:80]}")


# --- 5. bool as int (rejected) ---


def test_bool_as_int_rejected():
    section("bool as int -> ValueError")

    # True/False as n_neighbors
    for v in [True, False]:
        try:
            make_graph_builder(n_neighbors=v)
            print(f"  make_graph_builder(n_neighbors={v}): ACCEPTED (bug)")
        except (ValueError, TypeError) as e:
            print(f"  make_graph_builder(n_neighbors={v}): {type(e).__name__}: {str(e)[:80]}")

    # True/False as approx_threshold
    for v in [True, False]:
        try:
            make_graph_builder(approx_threshold=v)
            print(f"  make_graph_builder(approx_threshold={v}): ACCEPTED (bug)")
        except (ValueError, TypeError) as e:
            print(f"  make_graph_builder(approx_threshold={v}): {type(e).__name__}: {str(e)[:80]}")

    # True/False as max_gap_rank
    for v in [True, False]:
        try:
            make_clusterer(min_cluster_size=2, batch_size=10, max_gap_rank=v)
            print(f"  make_clusterer(max_gap_rank={v}): ACCEPTED (bug)")
        except (ValueError, TypeError) as e:
            print(f"  make_clusterer(max_gap_rank={v}): {type(e).__name__}: {str(e)[:80]}")

    # float as int
    for v, name in [
        (0.5, "GraphBuilder.n_neighbors"),
        (0.5, "PheromoneExtractor.n_ants"),
        (0.5, "CoreClusterer.batch_size"),
    ]:
        try:
            if "GraphBuilder" in name:
                make_graph_builder(n_neighbors=v)
            elif "PheromoneExtractor" in name:
                make_extractor(n_ants=v)
            else:
                make_clusterer(min_cluster_size=2, batch_size=v)
            print(f"  {name}={v}: ACCEPTED (bug)")
        except (ValueError, TypeError) as e:
            print(f"  {name}={v}: {type(e).__name__}: {str(e)[:80]}")


# --- 6. abs(int) as float (numpy types) ---


def test_numpy_scalars_as_int_float():
    section("numpy.int64 / numpy.float64 as int/float parameters")

    # numpy.int64 as n_neighbors (valid by isinstance(x, int))
    try:
        make_graph_builder(n_neighbors=np.int64(5))
        print("  make_graph_builder(n_neighbors=np.int64(5)): ACCEPTED")
    except (ValueError, TypeError) as e:
        print(f"  make_graph_builder(n_neighbors=np.int64(5)): {type(e).__name__}: {str(e)[:80]}")

    # numpy.float64 as beta
    try:
        make_extractor(n_ants=1, beta=np.float64(2.0))
        print("  make_extractor(beta=np.float64(2.0)): ACCEPTED")
    except (ValueError, TypeError) as e:
        print(f"  make_extractor(beta=np.float64(2.0)): {type(e).__name__}: {str(e)[:80]}")


# --- 7. None in int parameters (for parameters with None as a valid value) ---


def test_none_in_int_params():
    section("None in int parameters with None as a valid value")

    # n_ants=None - valid
    try:
        make_extractor(n_ants=None)
        print("  make_extractor(n_ants=None): ACCEPTED (valid)")
    except (ValueError, TypeError) as e:
        print(f"  make_extractor(n_ants=None): {type(e).__name__}: {str(e)[:80]}")

    # min_cluster_size=None - valid
    try:
        make_clusterer(min_cluster_size=None, batch_size=10)
        print("  make_clusterer(min_cluster_size=None): ACCEPTED (valid)")
    except (ValueError, TypeError) as e:
        print(f"  make_clusterer(min_cluster_size=None): {type(e).__name__}: {str(e)[:80]}")

    # batch_size=None - valid
    try:
        make_clusterer(min_cluster_size=2, batch_size=None)
        print("  make_clusterer(batch_size=None): ACCEPTED (valid)")
    except (ValueError, TypeError) as e:
        print(f"  make_clusterer(batch_size=None): {type(e).__name__}: {str(e)[:80]}")

    # None for parameters that must NOT accept None
    print("  None in parameters that do not allow None:")
    for pname, klass_name in [
        ("n_iterations", "PheromoneExtractor"),
        ("path_length", "PheromoneExtractor"),
        ("elite_start_iteration", "PheromoneExtractor"),
    ]:
        try:
            make_extractor(n_ants=1, **{pname: None})
            print(f"    {klass_name}({pname}=None): ACCEPTED")
        except (ValueError, TypeError) as e:
            print(f"    {klass_name}({pname}=None): {type(e).__name__}: {str(e)[:80]}")

    for pname in ["n_neighbors", "approx_threshold", "min_connections", "max_gap_rank"]:
        try:
            if pname in ["n_neighbors", "approx_threshold", "min_connections"]:
                make_graph_builder(**{pname: None})
            else:
                make_clusterer(min_cluster_size=2, batch_size=10, **{pname: None})
            print(f"    {pname}=None: ACCEPTED")
        except (ValueError, TypeError) as e:
            print(f"    {pname}=None: {type(e).__name__}: {str(e)[:80]}")
