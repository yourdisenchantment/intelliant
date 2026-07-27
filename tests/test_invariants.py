"""Property-based invariant tests via hypothesis.

Graph invariants (symmetry, no diagonal, weights, shape), core invariants
(label range, core size, noise, total count) and absorption invariants
(label range, no new cluster IDs, label count).
"""

import numpy as np
from conftest import make_clusterer, make_extractor, make_graph_builder
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st
from sklearn.datasets import make_blobs


def _build_dataset(n_samples, centers, cluster_std, seed):
    X, _ = make_blobs(
        n_samples=n_samples,
        centers=centers,
        cluster_std=cluster_std,
        random_state=seed,
    )
    return X.astype(np.float64)


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    n_samples=st.integers(min_value=50, max_value=200),
    centers=st.integers(min_value=3, max_value=8),
    cluster_std=st.floats(min_value=0.3, max_value=1.0),
    n_neighbors=st.integers(min_value=5, max_value=15),
    seed=st.integers(min_value=0, max_value=1000),
    mutual=st.booleans(),
)
def test_graph_invariants(n_samples, centers, cluster_std, n_neighbors, seed, mutual):
    X = _build_dataset(n_samples, centers, cluster_std, seed)
    if len(X) <= n_neighbors:
        assume(False)

    gb = make_graph_builder(
        n_neighbors=n_neighbors,
        mutual=mutual,
        knn_method="exact",
        random_state=seed,
        verbose=False,
    )
    graph = gb.build(X)

    assert graph.shape == (len(X), len(X)), f"shape {graph.shape} != ({len(X)}, {len(X)})"

    # No diagonal: setdiag(0) + eliminate_zeros guarantees no stored self-edges.
    diag = graph.diagonal()
    assert np.allclose(diag, 0.0), f"nonzero diagonal: {diag[np.nonzero(diag)]}"

    # Structural symmetry: the sparsity pattern of G equals that of G.T.
    # Symmetrization (AND/OR) produces the same neighbor set in both directions,
    # so G and G.T must have identical nonzero patterns.
    pattern = graph.astype(bool)
    assert (pattern != pattern.T).nnz == 0, "asymmetric sparsity pattern"

    # Value symmetry: weights match across directions up to float64 epsilon.
    # Known limitation: AND-symmetrization computes sim.multiply(mask), which can
    # produce values differing at the ULP level between (i,j) and (j,i) due to
    # floating-point rounding in sparse multiplication. The strict diff.nnz == 0
    # invariant therefore does NOT hold; we check with a tight tolerance instead.
    diff = (graph - graph.T).tocoo()
    if diff.nnz > 0:
        assert np.allclose(diff.data, 0.0, atol=1e-12), (
            f"weights not symmetric within 1e-12: max diff {np.abs(diff.data).max()}"
        )

    # Weights in [0, 1].
    if graph.nnz > 0:
        assert graph.data.min() >= 0.0, f"negative weight: {graph.data.min()}"
        assert graph.data.max() <= 1.0, f"weight > 1: {graph.data.max()}"


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    n_samples=st.integers(min_value=50, max_value=200),
    centers=st.integers(min_value=3, max_value=8),
    cluster_std=st.floats(min_value=0.3, max_value=1.0),
    n_neighbors=st.integers(min_value=5, max_value=15),
    min_cluster_size=st.integers(min_value=5, max_value=20),
    seed=st.integers(min_value=0, max_value=1000),
    mutual=st.booleans(),
    threshold_percentile=st.floats(min_value=40.0, max_value=85.0),
)
def test_core_invariants(
    n_samples,
    centers,
    cluster_std,
    n_neighbors,
    min_cluster_size,
    seed,
    mutual,
    threshold_percentile,
):
    X = _build_dataset(n_samples, centers, cluster_std, seed)
    if len(X) <= n_neighbors:
        assume(False)

    gb = make_graph_builder(
        n_neighbors=n_neighbors,
        mutual=mutual,
        knn_method="exact",
        random_state=seed,
        verbose=False,
    )
    graph = gb.build(X)

    n_ants = len(X)
    pe = make_extractor(
        n_ants=n_ants,
        n_iterations=5,
        path_length=5,
        warmup=False,
        random_state=seed,
        verbose=False,
    )
    pe.fit(graph)
    pheromone = pe.pheromone_matrix_

    cc = make_clusterer(
        min_cluster_size=min_cluster_size,
        batch_size=len(X),
        verbose=False,
    )
    cores = cc.extract_cores(pheromone, threshold_percentile=threshold_percentile)

    assert len(cores) == len(X), f"cores length {len(cores)} != N {len(X)}"

    unique_labels = np.unique(cores[cores >= 0])
    k = len(unique_labels)

    if k == 0:
        assert (cores == -1).all(), "all cores should be -1 when there are no clusters"
    else:
        assert unique_labels.tolist() == list(range(k)), f"core labels not in [0, k-1]: {unique_labels}"

    assert (cores < 0).sum() + (cores >= 0).sum() == len(X), "label count mismatch"

    noise_mask = cores == -1
    assert np.all(cores[noise_mask] == -1), "noise points must be -1"

    for cid in unique_labels:
        size = int((cores == cid).sum())
        assert size >= min_cluster_size, f"core {cid} size {size} < min_cluster_size {min_cluster_size}"


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    n_samples=st.integers(min_value=50, max_value=200),
    centers=st.integers(min_value=3, max_value=8),
    cluster_std=st.floats(min_value=0.3, max_value=1.0),
    n_neighbors=st.integers(min_value=5, max_value=15),
    min_cluster_size=st.integers(min_value=5, max_value=20),
    seed=st.integers(min_value=0, max_value=1000),
    mutual=st.booleans(),
    threshold_percentile=st.floats(min_value=40.0, max_value=85.0),
)
def test_absorb_invariants(
    n_samples,
    centers,
    cluster_std,
    n_neighbors,
    min_cluster_size,
    seed,
    mutual,
    threshold_percentile,
):
    X = _build_dataset(n_samples, centers, cluster_std, seed)
    if len(X) <= n_neighbors:
        assume(False)

    gb = make_graph_builder(
        n_neighbors=n_neighbors,
        mutual=mutual,
        knn_method="exact",
        random_state=seed,
        verbose=False,
    )
    graph = gb.build(X)

    n_ants = len(X)
    pe = make_extractor(
        n_ants=n_ants,
        n_iterations=5,
        path_length=5,
        warmup=False,
        random_state=seed,
        verbose=False,
    )
    pe.fit(graph)
    pheromone = pe.pheromone_matrix_

    cc = make_clusterer(
        min_cluster_size=min_cluster_size,
        batch_size=len(X),
        absorb_isolated=True,
        verbose=False,
    )
    cores = cc.extract_cores(pheromone, threshold_percentile=threshold_percentile)

    core_clusters = set(np.unique(cores[cores >= 0]).tolist())
    if len(core_clusters) == 0:
        assume(False)

    labels = cc.absorb(pheromone, X=X)

    assert len(labels) == len(X), f"label count {len(labels)} != N {len(X)}"

    final_clusters = set(np.unique(labels[labels >= 0]).tolist())
    assert final_clusters <= core_clusters, f"new cluster IDs after absorb: {final_clusters - core_clusters}"

    if (labels == -1).sum() == 0:
        assert labels.min() >= 0, f"labels contain -1 unexpectedly: {np.unique(labels)}"
        assert labels.max() == len(final_clusters) - 1, f"max label {labels.max()} != k-1 {len(final_clusters) - 1}"
    else:
        assert labels.min() == -1, f"expected -1 in labels: {np.unique(labels)}"
