"""test_warnings_emit.py
# Isolating a warning that appeared in the output of the previous test at the very
# top (BEFORE the main section output).
# If fit_predict raises X=None on absorb_isolated=True - that is expected, but in
# my test I passed X=X_noise. Where is the leak?
"""

import warnings

import numpy as np
import pytest
from conftest import make_clusterer, make_extractor, make_graph_builder
from scipy.sparse import csr_matrix


def section(title):
    print(f"\n=== {title} ===")


def _graph_with_isolated_noise():
    # One strong core pair (0, 1) and an isolated weak pair (2, 3): after
    # thresholding at 0.1 points 2 and 3 stay noise, and pheromone waves cannot
    # reach them (no edges to the core), so stage 2 actually has work to skip.
    rows = np.array([0, 1, 2, 3])
    cols = np.array([1, 0, 3, 2])
    data = np.array([0.9, 0.9, 0.05, 0.05])
    return csr_matrix((data, (rows, cols)), shape=(4, 4))


def _build_pipeline():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((15, 4))
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42, mutual=False)
    G = gb.build(X)
    pe = make_extractor(n_ants=5, n_iterations=2, verbose=False, random_state=42)
    pe.fit(G)
    return X, pe


# 1. Run fit_predict with X=None and absorb_isolated=True - expect 1 warning
def test_x_none_absorb_isolated_emits_one_warning():
    section("X=None + absorb_isolated=True")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        G = _graph_with_isolated_noise()
        cc = make_clusterer(min_cluster_size=2, batch_size=5, absorb_isolated=True, verbose=False)
        cc.fit_predict(G, threshold_value=0.1, X=None)
        print(f"  warnings: {len(w)}")
        for x in w:
            print(f"    {x.category.__name__}: {x.message} (file={x.filename}:{x.lineno})")
    assert len(w) == 1


# 2. Run with X=np.array - there must be 0 warnings
def test_x_array_absorb_isolated_no_warning():
    section("X=np.array + absorb_isolated=True")
    X, pe = _build_pipeline()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cc = make_clusterer(min_cluster_size=2, batch_size=5, absorb_isolated=True, verbose=False)
        cc.fit_predict(pe.pheromone_matrix_, threshold_value=0.1, X=X)
        print(f"  warnings: {len(w)}")
        for x in w:
            print(f"    {x.category.__name__}: {x.message} (file={x.filename}:{x.lineno})")
    assert len(w) == 0


# 3. fit_predict is called twice in a row: first with X=None, then with X
def test_two_calls_first_none_then_array_one_warning():
    section("Two calls in a row: first with X=None, then with X")
    G = _graph_with_isolated_noise()
    rng = np.random.default_rng(42)
    X = rng.standard_normal((4, 3))
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cc = make_clusterer(min_cluster_size=2, batch_size=5, absorb_isolated=True, verbose=False)
        cc.fit_predict(G, threshold_value=0.1, X=None)
        print(f"  After 1st call: warnings={len(w)}")
        cc.fit_predict(G, threshold_value=0.1, X=X)
        print(f"  After 2nd call: warnings={len(w)}")
    assert len(w) == 1


# 3a. GraphBuilder.build on antipodal cosine vectors -> edge-free graph warning
def test_build_antipodal_cosine_warns_on_edge_free_graph():
    """Checks the nnz=0 warning in build() (REVIEW #12).

    Antipodal and orthogonal unit vectors with metric='cosine' have similarity
    <= 0, so every edge weight clips to 0 and eliminate_zeros leaves an empty
    graph. Previously this was silent and the failure surfaced later in
    PheromoneExtractor.fit as "graph has no edges"; now build() itself must
    warn and return the nnz=0 graph.
    """

    section("GraphBuilder: antipodal cosine vectors -> warning + nnz=0")
    X = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
    gb = make_graph_builder(n_neighbors=3, metric="cosine", verbose=False, random_state=42)
    with pytest.warns(UserWarning, match="no edges"):
        G = gb.build(X)
    print(f"  nnz: {G.nnz}")
    assert G.nnz == 0


# 4. fit_predict + extract_cores without absorb - no warning
def test_extract_cores_no_absorb_no_warning():
    section("extract_cores without absorb")
    _, pe = _build_pipeline()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        cc = make_clusterer(min_cluster_size=2, batch_size=5, absorb_isolated=True, verbose=False)
        cc.extract_cores(pe.pheromone_matrix_, threshold_value=0.1)
        print(f"  warnings: {len(w)}")
        for x in w:
            print(f"    {x.category.__name__}: {x.message}")
    assert len(w) == 0
