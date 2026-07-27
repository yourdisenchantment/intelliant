"""test_determinism.py
# End-to-end determinism of the full pipeline (GraphBuilder -> PheromoneExtractor
# -> find_threshold -> CoreClusterer): fixed random_state -> identical result,
# different random_state -> differing labels.
"""

import numpy as np
from conftest import make_clusterer, make_extractor, make_graph_builder
from sklearn.datasets import make_blobs

from intelliant import find_threshold


def _run_pipeline(X: np.ndarray, seed: int, knn_method: str = "exact"):
    """Runs the full pipeline once and returns (graph, pheromones, threshold, labels)."""

    gb = make_graph_builder(n_neighbors=10, knn_method=knn_method, random_state=seed, verbose=False)
    graph = gb.build(X)

    pe = make_extractor(n_ants=50, n_iterations=10, path_length=10, random_state=seed, verbose=False)
    pe.fit(graph)

    result = find_threshold(pe.pheromone_matrix_.data, method="otsu")
    threshold = result.value

    labels = make_clusterer(min_cluster_size=5, batch_size=128, verbose=False).fit_predict(
        pe.pheromone_matrix_, threshold_value=threshold, X=X
    )
    return graph, pe.pheromone_matrix_, threshold, labels


def _assert_graphs_equal(g1, g2):
    assert g1.shape == g2.shape
    assert np.array_equal(g1.data, g2.data)
    assert np.array_equal(g1.indices, g2.indices)
    assert np.array_equal(g1.indptr, g2.indptr)


def test_determinism_exact_knn():
    """Two full runs with exact KNN and the same seed produce identical outputs."""

    X, _ = make_blobs(n_samples=200, centers=4, random_state=42)

    g1, p1, t1, l1 = _run_pipeline(X, seed=42, knn_method="exact")
    g2, p2, t2, l2 = _run_pipeline(X, seed=42, knn_method="exact")

    _assert_graphs_equal(g1, g2)
    assert np.array_equal(p1.data, p2.data)
    assert np.array_equal(p1.indices, p2.indices)
    assert np.array_equal(p1.indptr, p2.indptr)
    assert t1 == t2
    assert np.array_equal(l1, l2)


def test_determinism_approx_knn():
    """Approx KNN (pynndescent) is bit-reproducible across runs with a fixed seed.

    Empirically stable with pynndescent 0.6.0 across 5 repeated runs each at
    n_samples=200/1000 and OMP_NUM_THREADS in {1, 4, 8}. If this test starts
    flaking, restore the xfail(strict=False) mark and note the version that broke.
    """
    X, _ = make_blobs(n_samples=200, centers=4, random_state=42)

    g1, p1, t1, l1 = _run_pipeline(X, seed=42, knn_method="approx")
    g2, p2, t2, l2 = _run_pipeline(X, seed=42, knn_method="approx")

    _assert_graphs_equal(g1, g2)
    assert np.array_equal(p1.data, p2.data)
    assert np.array_equal(p1.indices, p2.indices)
    assert np.array_equal(p1.indptr, p2.indptr)
    assert t1 == t2
    assert np.array_equal(l1, l2)


def test_seed_affects_labels():
    """Different seeds produce different labels, proving the seed is not ignored."""

    X, _ = make_blobs(n_samples=200, centers=4, random_state=42)

    _, _, _, l1 = _run_pipeline(X, seed=42, knn_method="exact")
    _, _, _, l2 = _run_pipeline(X, seed=123, knn_method="exact")

    assert not np.array_equal(l1, l2)
