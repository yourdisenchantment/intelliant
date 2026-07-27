"""test_degenerate_endtoend.py
# Running the full fit_predict chain on degenerate inputs:
# a single point, all zeros, random noise, isolated clusters.
"""

import warnings

import numpy as np
import pytest
from conftest import make_clusterer, make_extractor, make_graph_builder
from scipy.sparse import csr_matrix
from sklearn.metrics import adjusted_rand_score


def section(title):
    print(f"\n=== {title} ===")


def safe_run(label, fn):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # hide what is not relevant
            result = fn()
        if isinstance(result, np.ndarray):
            print(f"  OK: {label} -> shape={result.shape}, unique={np.unique(result)}")
        else:
            print(f"  OK: {label} -> {type(result).__name__}")
    except Exception as e:
        print(f"  ERR: {label} -> {type(e).__name__}: {str(e)[:120]}")


# 1. A single point - N=1
def test_single_point_n1():
    section("Chain on a single point (N=1)")

    print("  GraphBuilder.build with a single point:")
    try:
        gb = make_graph_builder(n_neighbors=1, verbose=False, random_state=42)
        G = gb.build(np.array([[1.0, 2.0, 3.0]]))
        print(f"    OK: nnz={G.nnz}, shape={G.shape}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")

    print("  PheromoneExtractor.fit on a graph of 1 point without edges:")
    try:
        pe = make_extractor(n_ants=1, n_iterations=2, verbose=False, random_state=42)
        pe.fit(csr_matrix((1, 1)))
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")


# 2. All zeros
def test_identical_points():
    section("Chain on identical points (X = [[1,2,3]]*10)")

    X_same = np.tile(np.array([1.0, 2.0, 3.0]), (10, 1))
    print("  GraphBuilder.build:")
    try:
        gb = make_graph_builder(n_neighbors=3, verbose=False, random_state=42)
        G = gb.build(X_same)
        print(f"    OK: nnz={G.nnz}, shape={G.shape}")
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")


# 3. Isolated vertices (no links)
def test_isolated_vertices():
    section("Chain on isolated vertices")

    # A 5x5 graph without edges
    G_iso = csr_matrix((5, 5))
    print("  PheromoneExtractor.fit on an empty graph (5x5 nnz=0):")
    try:
        pe = make_extractor(n_ants=3, n_iterations=1, verbose=False, random_state=42)
        pe.fit(G_iso)
    except Exception as e:
        print(f"    ERR: {type(e).__name__}: {e}")


# 4. Random noise
def test_random_noise_pipeline():
    section("Chain on pure noise (randn(50, 5))")

    rng = np.random.default_rng(42)
    X_noise = rng.standard_normal((50, 5))
    safe_run(
        "GraphBuilder.build (cosine, 50 points)",
        lambda: make_graph_builder(n_neighbors=5, verbose=False, random_state=42).build(X_noise),
    )

    gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=42, mutual=False)
    G_noise = gb.build(X_noise)
    print(f"  Noise graph: nnz={G_noise.nnz}")

    pe = make_extractor(n_ants=20, n_iterations=10, verbose=False, random_state=42)
    pe.fit(G_noise)
    print(f"  Pheromone: range=[{pe.pheromone_matrix_.data.min():.3f}, {pe.pheromone_matrix_.data.max():.3f}]")

    safe_run(
        "CoreClusterer fit_predict on noise",
        lambda: make_clusterer(min_cluster_size=3, batch_size=10, verbose=False).fit_predict(
            pe.pheromone_matrix_, threshold_percentile=90.0, X=X_noise
        ),
    )


# 5. Synthetic data: 3 clusters + noise
def test_synthetic_three_clusters_endtoend():
    section("Synthetic data: 3 clusters + noise (end-to-end)")

    rng = np.random.default_rng(42)
    centers = rng.standard_normal((3, 4))
    points_per = 30
    X_syn = np.vstack([centers[i] + 0.1 * rng.standard_normal((points_per, 4)) for i in range(3)])
    X_syn = np.vstack([X_syn, 0.5 * rng.standard_normal((30, 4))])  # noise
    true_labels = np.concatenate([np.full(points_per, i) for i in range(3)] + [np.full(30, -1)])

    safe_run(
        "GraphBuilder.build", lambda: make_graph_builder(n_neighbors=8, verbose=False, random_state=42).build(X_syn)
    )

    gb = make_graph_builder(n_neighbors=8, verbose=False, random_state=42, mutual=False)
    G_syn = gb.build(X_syn)
    print(f"  Synthetic graph: nnz={G_syn.nnz}")

    pe = make_extractor(n_ants=50, n_iterations=15, verbose=False, random_state=42)
    pe.fit(G_syn)
    print(f"  Pheromone: range=[{pe.pheromone_matrix_.data.min():.3f}, {pe.pheromone_matrix_.data.max():.3f}]")

    cc = make_clusterer(min_cluster_size=5, batch_size=20, verbose=False)
    labels = cc.fit_predict(pe.pheromone_matrix_, threshold_percentile=80.0, X=X_syn)
    print(
        f"  fit_predict: unique={np.unique(labels)}, "
        f"n_clusters={len(np.unique(labels[labels >= 0]))}, "
        f"noise={(labels == -1).sum()}"
    )

    # ARI with true_labels (only for > 1 cluster)
    valid = labels >= 0
    if valid.sum() > 0 and len(np.unique(labels[valid])) > 1:
        ari = adjusted_rand_score(true_labels[valid], labels[valid])
        print(f"  ARI (resolved only): {ari:.3f}")
    else:
        print(
            f"  ARI not computed: resolved points {valid.sum()}, "
            f"clusters {len(np.unique(labels[valid])) if valid.sum() else 0}"
        )


# 6. fit on a graph with a single component
def test_single_edge_graph():
    section("Graph with a single edge (N=2)")

    # Both directions: the graph is undirected, so "a single edge" means two
    # stored entries. With only (0, 1) the ants' deposits on (1, 0) had nowhere
    # to land and were silently dropped - which the asymmetry warning now
    # reports, and which this fixture had been doing unnoticed.
    G_tiny = csr_matrix((np.array([0.5, 0.5]), (np.array([0, 1]), np.array([1, 0]))), shape=(2, 2))
    pe_tiny = make_extractor(n_ants=2, n_iterations=2, verbose=False, random_state=42)
    pe_tiny.fit(G_tiny)
    print(
        f"  Pheromone: range=[{pe_tiny.pheromone_matrix_.data.min():.3f}, {pe_tiny.pheromone_matrix_.data.max():.3f}]"
    )

    cc_tiny = make_clusterer(min_cluster_size=2, batch_size=2, verbose=False)
    labels_tiny = cc_tiny.fit_predict(pe_tiny.pheromone_matrix_, threshold_value=0.1)
    print(f"  fit_predict: {labels_tiny}")


# 7. fit_predict with threshold_value=NaN/Inf
def test_threshold_value_nan_inf_raises():
    section("fit_predict with threshold_value=NaN/Inf")
    cc_test = make_clusterer(min_cluster_size=2, batch_size=10, verbose=False)
    G_test = csr_matrix(np.array([[0, 0.5, 0.7], [0.5, 0, 0.3], [0.7, 0.3, 0]]))
    for tv in [float("nan"), float("inf"), -float("inf")]:
        with pytest.raises(ValueError, match="threshold_value"):
            cc_test.fit_predict(G_test, threshold_value=tv)
