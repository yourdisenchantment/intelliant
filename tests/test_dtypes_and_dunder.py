"""test_dtypes_and_dunder.py
# Checking behavior on different dtypes and the dunder methods of the package.
"""

import warnings

import numpy as np
import pytest
from conftest import make_clusterer, make_extractor, make_graph_builder
from scipy.sparse import csr_matrix

import intelliant


def section(title):
    print(f"\n=== {title} ===")


# 1. Input dtypes
def test_dtype_inputs_in_graph_builder():
    section("Input dtypes in GraphBuilder.build")

    rng = np.random.default_rng(42)

    for dtype in [np.float32, np.float64, np.int32, np.int64]:
        print(f"  X.dtype={dtype.__name__}:")
        X = (rng.standard_normal((20, 4)) * 100).astype(dtype)
        try:
            gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=42)
            G = gb.build(X)
            print(f"    OK: nnz={G.nnz}, graph.dtype={G.dtype}, data sample={G.data[:3]}")
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")

    # Python list instead of numpy
    print("  X = list (Python list of lists):")
    X_list = [[1.0, 2.0, 3.0, 4.0]] * 20
    try:
        gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=42)
        G = gb.build(X_list)
        print(f"    OK: nnz={G.nnz}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    # X 1D
    print("  X 1D (np.array([1, 2, 3, 4, 5])):")
    X_1d = np.array([1, 2, 3, 4, 5])
    try:
        gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
        G = gb.build(X_1d)
        print(f"    BUG?: accepted 1D, nnz={G.nnz}")
    except Exception as e:
        print(f"    OK: {type(e).__name__}: {e}")


# 1a. complex-dtype X is rejected up front (REVIEW round 2, R2-9)
def test_complex_dtype_x_rejected():
    """Checks that complex-dtype X raises a clean ValueError in build.

    np.issubdtype(complex128, np.number) is True, so before round 2 complex X
    passed the numeric check and failed deep inside sklearn with the full data
    matrix dumped into the error message.
    """

    section("GraphBuilder.build: complex X -> ValueError")
    X = np.ones((10, 3), dtype=np.complex128)
    gb = make_graph_builder(n_neighbors=2, verbose=False)
    with pytest.raises(ValueError, match="X must be a real-valued array"):
        gb.build(X)


# 2. dtype in pheromone_extractor and core_clusterer
def test_dtype_in_absorb_centroid():
    section("dtype in absorb_centroid (X)")

    rng = np.random.default_rng(42)
    X = rng.standard_normal((15, 4)).astype(np.float64)
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42, mutual=False)
    G = gb.build(X)

    pe = make_extractor(n_ants=5, n_iterations=2, verbose=False, random_state=42)
    pe.fit(G)

    for dtype in [np.float32, np.float64, np.int32, np.int64]:
        print(f"  X.dtype={dtype.__name__}:")
        X_test = (rng.standard_normal((15, 4)) * 100).astype(dtype)
        try:
            cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
            labels = cc.fit_predict(pe.pheromone_matrix_, threshold_value=0.3, X=X_test)
            print(f"    OK: labels unique={np.unique(labels)}")
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")


# 3. Boundary cases on 1D/2D X
def _build_small_pipeline():
    rng = np.random.default_rng(42)
    X_small = rng.standard_normal((10, 3)).astype(np.float64)
    gb = make_graph_builder(n_neighbors=2, min_connections=2, verbose=False, random_state=42, mutual=False)
    G = gb.build(X_small)
    pe = make_extractor(n_ants=3, n_iterations=1, verbose=False, random_state=42)
    pe.fit(G)
    return pe


def test_x_none_with_absorb_isolated_warns():
    # X=None with absorb_isolated=True; the isolated weak pair (2, 3) stays
    # noise after pheromone waves, so stage 2 has work to skip -> warning.
    print("  X=None + absorb_isolated=True (expect warning):")
    G = csr_matrix(
        (np.array([0.9, 0.9, 0.05, 0.05]), (np.array([0, 1, 2, 3]), np.array([1, 0, 3, 2]))),
        shape=(4, 4),
    )
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cc = make_clusterer(min_cluster_size=2, batch_size=3, absorb_isolated=True, verbose=False)
        try:
            labels = cc.fit_predict(G, threshold_value=0.1, X=None)
            print(f"    OK: labels={labels}")
            print(f"    warnings: {len(w)} ({[str(x.message)[:60] for x in w]})")
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")
    assert len(w) == 1


def test_x_none_without_absorb_isolated_no_warning():
    # X=None with absorb_isolated=False
    print("  X=None + absorb_isolated=False (there must be NO warning):")
    pe = _build_small_pipeline()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cc = make_clusterer(min_cluster_size=2, batch_size=3, absorb_isolated=False, verbose=False)
        try:
            labels = cc.fit_predict(pe.pheromone_matrix_, threshold_value=0.1, X=None)
            print(f"    OK: labels={labels}")
            print(f"    warnings: {len(w)}")
        except Exception as e:
            print(f"    ERR: {type(e).__name__}: {e}")
    assert len(w) == 0


def test_empty_x_raises():
    # X = empty array
    print("  X=[] (empty):")
    pe = _build_small_pipeline()
    with warnings.catch_warnings():
        warnings.simplefilter("always")
        cc = make_clusterer(min_cluster_size=2, batch_size=3, verbose=False)
        try:
            labels = cc.fit_predict(pe.pheromone_matrix_, threshold_value=0.1, X=np.array([]))
            print(f"    BUG?: accepted empty X, labels={labels}")
            raise AssertionError("expected ValueError for empty X")
        except ValueError as e:
            print(f"    OK: {type(e).__name__}: {e}")


# 3a. absorb_centroid with int64 X matches the float64 run (REVIEW #2)
def test_absorb_centroid_int64_x_matches_float64():
    """Checks that integer X goes through stage 2 and matches the float64 run.

    Two cores (0,1) and (2,3) plus a weak noise pair (4,5): after thresholding
    at 0.1 nodes 4 and 5 stay noise and pheromone waves cannot reach them, so
    the centroid fallback actually runs. Previously int64 X crashed there with
    a raw numpy UFuncTypeError (centroids allocated with X.dtype); now the
    labels must match the run on the same X cast to float64.
    """

    section("absorb_centroid: int64 X matches float64 X")
    rows = np.array([0, 1, 2, 3, 4, 5])
    cols = np.array([1, 0, 3, 2, 5, 4])
    data = np.array([0.9, 0.9, 0.9, 0.9, 0.05, 0.05])
    G = csr_matrix((data, (rows, cols)), shape=(6, 6))

    X_int = np.array([[10, 0], [12, 0], [0, 10], [0, 12], [11, 1], [1, 11]], dtype=np.int64)
    X_float = X_int.astype(np.float64)

    cc_int = make_clusterer(min_cluster_size=2, batch_size=3, verbose=False)
    labels_int = cc_int.fit_predict(G, threshold_value=0.1, X=X_int)

    cc_float = make_clusterer(min_cluster_size=2, batch_size=3, verbose=False)
    labels_float = cc_float.fit_predict(G, threshold_value=0.1, X=X_float)

    print(f"  int64: {labels_int}, float64: {labels_float}")
    assert np.array_equal(labels_int, labels_float)
    # Stage 2 really absorbed the noise pair: no -1 left.
    assert (labels_int >= 0).all()


# 3b. coo_matrix input: end-to-end equals the csr run (REVIEW #5)
def test_coo_matrix_end_to_end_matches_csr():
    """Checks that a coo_matrix pheromone graph runs end-to-end and matches CSR.

    Previously extract_cores converted to CSR but absorb_pheromone indexed the
    raw coo_matrix and crashed with TypeError halfway. Now fit_predict on the
    coo copy must return the same labels as on the CSR original (same seed and
    threshold); PheromoneExtractor.fit on a coo graph must also produce the
    same pheromone field as on the CSR graph.
    """

    section("coo_matrix: fit and fit_predict match the csr run")
    rng = np.random.default_rng(42)
    X = rng.standard_normal((15, 4))
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42, mutual=False)
    G = gb.build(X)

    pe_csr = make_extractor(n_ants=5, n_iterations=2, verbose=False, random_state=42)
    pe_csr.fit(G)
    pe_coo = make_extractor(n_ants=5, n_iterations=2, verbose=False, random_state=42)
    pe_coo.fit(G.tocoo())
    assert pe_csr.pheromone_matrix_ is not None
    assert pe_coo.pheromone_matrix_ is not None
    assert np.array_equal(pe_csr.pheromone_matrix_.data, pe_coo.pheromone_matrix_.data)
    assert np.array_equal(pe_csr.pheromone_matrix_.indices, pe_coo.pheromone_matrix_.indices)

    pheromone = pe_csr.pheromone_matrix_
    cc_csr = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    labels_csr = cc_csr.fit_predict(pheromone, threshold_value=0.1, X=X)
    cc_coo = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    labels_coo = cc_coo.fit_predict(pheromone.tocoo(), threshold_value=0.1, X=X)

    print(f"  csr unique: {np.unique(labels_csr)}, coo unique: {np.unique(labels_coo)}")
    assert np.array_equal(labels_csr, labels_coo)


# 3c. fit does not mutate the caller's unsorted CSR (REVIEW #13)
def test_fit_does_not_mutate_callers_unsorted_csr():
    """Checks that fit leaves the caller's unsorted CSR arrays byte-equal.

    Previously graph.tocsr() returned the same object for CSR input and
    sort_indices() reordered the caller's indices/data in place. Now fit must
    sort only its private copy: the input arrays stay byte-identical and the
    matrix keeps its unsorted flag.
    """

    section("fit: caller's unsorted CSR is not mutated")
    indptr = np.array([0, 2, 4, 6])
    indices = np.array([2, 1, 2, 0, 1, 0])
    data = np.array([0.5, 0.6, 0.7, 0.5, 0.6, 0.7])
    g = csr_matrix((data, indices, indptr), shape=(3, 3))
    assert not g.has_sorted_indices

    indices_before = g.indices.tobytes()
    data_before = g.data.tobytes()

    pe = make_extractor(n_ants=3, n_iterations=2, verbose=False, random_state=42)
    pe.fit(g)

    assert g.indices.tobytes() == indices_before
    assert g.data.tobytes() == data_before
    assert not g.has_sorted_indices


# 3d. fit canonicalizes a non-canonical CSR on its private copy (REVIEW R2-6, R2-10)
def test_fit_canonicalizes_duplicate_and_zero_entries():
    """Checks that fit merges duplicate entries and drops explicit zeros.

    The input CSR carries a duplicate entry for edge (0, 1) (0.5 + 0.5) and an
    explicit-zero edge (0, 2)/(2, 0). Before round 2 deposits hit only the
    leftmost duplicate (the second copy only evaporated) and zero edges fed
    dead-ant no-op runs. Now fit must canonicalize its private copy: the
    pheromone matrix is bit-identical to a run on the equivalent clean CSR,
    both directions of the formerly duplicated edge accumulate deposits, and
    the caller's arrays stay untouched (nnz still 7).
    """

    section("fit: duplicate + explicit-zero CSR canonicalized on the private copy")
    indptr = np.array([0, 3, 5, 7])
    indices = np.array([1, 1, 2, 0, 2, 0, 1])
    data = np.array([0.5, 0.5, 0.0, 1.0, 0.8, 0.0, 0.8])
    dirty = csr_matrix((data, indices, indptr), shape=(3, 3))
    assert dirty.nnz == 7

    # The same logical graph in canonical form: (0, 1) merged, zeros gone.
    clean = csr_matrix(
        (np.array([1.0, 1.0, 0.8, 0.8]), (np.array([0, 1, 1, 2]), np.array([1, 0, 2, 1]))),
        shape=(3, 3),
    )

    indices_before = dirty.indices.tobytes()
    data_before = dirty.data.tobytes()

    # evaporation off + small deposit: pheromone grows monotonically but stays
    # below tau_max, so the data comparison is not saturated by clamping.
    params = {
        "n_ants": 4,
        "n_iterations": 1,
        "pheromone_deposit": 0.01,
        "evaporation_rate": 0.0,
        "use_no_return": False,
        "verbose": False,
        "random_state": 42,
    }
    pe_dirty = make_extractor(**params)
    pe_dirty.fit(dirty)
    pe_clean = make_extractor(**params)
    pe_clean.fit(clean)

    ph = pe_dirty.pheromone_matrix_
    ph_clean = pe_clean.pheromone_matrix_
    assert ph is not None
    assert ph_clean is not None
    print(f"  dirty run data: {ph.data}, clean run data: {ph_clean.data}")

    # Canonical structure: duplicates merged, explicit zeros gone.
    assert ph.nnz == 4
    assert np.array_equal(ph.indptr, ph_clean.indptr)
    assert np.array_equal(ph.indices, ph_clean.indices)
    # Identical run: deposits land on the merged entries exactly as on clean input.
    assert np.array_equal(ph.data, ph_clean.data)
    # Deposits are real and unsaturated; both directions of the formerly
    # duplicated edge (0, 1) accumulated pheromone.
    assert ph.data.max() < pe_dirty.tau_max
    assert ph[0, 1] > pe_dirty.initial_pheromone
    assert ph[0, 1] == ph[1, 0]

    # The caller's non-canonical matrix is untouched.
    assert dirty.nnz == 7
    assert dirty.indices.tobytes() == indices_before
    assert dirty.data.tobytes() == data_before


# 4. Import via `from intelliant import *`
def test_public_api_import_and_all():
    section("Import via `from intelliant import *`")

    print(f"  intelliant.__version__ = {intelliant.__version__}")
    print(f"  intelliant.__all__ = {intelliant.__all__}")
    print(f"  intelliant.__file__ = {intelliant.__file__}")

    # Check that __all__ has nothing extra
    unexpected = [s for s in intelliant.__all__ if not hasattr(intelliant, s)]
    print(f"  Missing from the module: {unexpected}")
    assert unexpected == []

    # Check that the public API has no private symbols and no utility imports
    all_public = [s for s in dir(intelliant) if not s.startswith("_")]
    print(f"  Public attributes: {all_public}")

    # from intelliant import * in practice
    ns = {}
    exec("from intelliant import *", ns)
    imported = [k for k in ns if not k.startswith("_")]
    print(f"  Imported via `import *`: {imported}")


# 4a. Result NamedTuples are exported from the package root (REVIEW #20)
def test_result_namedtuples_exported():
    """Checks that ThresholdResult, ScanRow and GiantDiagnostics are public exports.

    Users need them importable from the package root for type annotations; each
    must be present in __all__ and be the same object as the defining module's
    attribute.
    """

    section("Package root exports: result NamedTuples")
    from intelliant import GiantDiagnostics, ScanRow, ThresholdResult
    from intelliant.core_clusterer import GiantDiagnostics as CCGiantDiagnostics
    from intelliant.threshold import ScanRow as ThrScanRow
    from intelliant.threshold import ThresholdResult as ThrThresholdResult

    for name in ("ThresholdResult", "ScanRow", "GiantDiagnostics"):
        assert name in intelliant.__all__, f"{name} missing from __all__"

    assert ThresholdResult is ThrThresholdResult
    assert ScanRow is ThrScanRow
    assert GiantDiagnostics is CCGiantDiagnostics


# 5. repr / str
def test_repr_str_classes():
    section("repr / str of classes")
    for name, factory, extra in [
        ("GraphBuilder", make_graph_builder, {}),
        ("PheromoneExtractor", make_extractor, {"n_ants": 5}),
        ("CoreClusterer", make_clusterer, {"min_cluster_size": 2, "batch_size": 10}),
    ]:
        obj = factory(verbose=False, **extra)
        print(f"  {name}.__repr__ = {obj!r}")
        print(f"  {name}.__str__ = {obj!s}")
