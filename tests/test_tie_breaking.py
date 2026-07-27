"""test_tie_breaking.py
# Deterministic tie-breaking in CoreClusterer absorption:
# - absorb_pheromone resolves vote ties via argmax (favors smallest cluster index)
# - absorb_centroid resolves cosine similarity ties via argmax (same rule)
# The ties below are EXACT (identical float values), not approximate.
"""

import numpy as np
from conftest import make_clusterer
from scipy.sparse import csr_matrix

from intelliant import CoreClusterer


def _build_pheromone_tie_graph() -> csr_matrix:
    """Builds a pheromone graph where point 4 has EXACTLY equal pheromone weight
    to point 0 (core 0) and point 2 (core 1).

    Layout (5 points): 0,1 -> core 0; 2,3 -> core 1; 4 -> noise.
    Point 4 connects to point 0 and point 2 with the same weight (1.0), producing
    a vote tie between cluster 0 and cluster 1. Cores within each cluster are
    held together by a stronger edge so they survive as a single core on their
    own; point 4 is left as noise.
    """

    rows = [0, 1, 1, 2, 3, 3, 4, 4]
    cols = [1, 0, 2, 3, 2, 4, 0, 2]
    data = [5.0, 5.0, 0.1, 5.0, 5.0, 1.0, 1.0, 1.0]
    return csr_matrix((data, (rows, cols)), shape=(5, 5))


def _make_clusterer_with_cores(cores: np.ndarray, max_iterations: int = 20) -> CoreClusterer:
    """Builds a verbose=False CoreClusterer with batch_size set and cores_ assigned
    directly (bypassing extract_cores) to control the test setup."""

    cc = make_clusterer(batch_size=4, max_iterations=max_iterations, verbose=False)
    cc.cores_ = cores.copy()
    return cc


def test_tie_breaking_pheromone():
    """absorb_pheromone assigns a noise point with equal pheromone weight to two
    cores to the cluster with the smallest index (cluster 0). Stable across 3 runs.
    """

    cores = np.array([0, 0, 1, 1, -1])
    G = _build_pheromone_tie_graph()

    # Sanity: the two pheromone edges from point 4 carry the exact same float value.
    sub = G[4]
    weights_to_cores = sub.data
    assert len(weights_to_cores) == 2, "point 4 must have exactly two edges"
    assert weights_to_cores[0] == weights_to_cores[1], "pheromone tie must be exact"

    for run in range(3):
        cc = _make_clusterer_with_cores(cores, max_iterations=1)
        labels = cc.absorb_pheromone(G)
        assert labels[4] == 0, f"run {run}: expected cluster 0 (smallest index), got {labels[4]}"


def test_tie_breaking_centroid():
    """absorb_centroid assigns a noise point equidistant (equal cosine similarity)
    to two cluster centroids to the cluster with the smallest index. Stable
    across 3 runs.

    Construction (2D):
      cluster 0: points (1,0), (2,0) -> centroid (1.5, 0)
      cluster 1: points (0,1), (0,2) -> centroid (0, 1.5)
      noise point 4: (1, 1)
    cosine_similarity((1,1), (1.5,0)) == cosine_similarity((1,1), (0,1.5)) == 1/sqrt(2),
    an exact tie. argmax picks cluster 0 (smallest index).
    """

    X = np.array(
        [
            [1.0, 0.0],  # 0 -> core 0
            [2.0, 0.0],  # 1 -> core 0
            [0.0, 1.0],  # 2 -> core 1
            [0.0, 2.0],  # 3 -> core 1
            [1.0, 1.0],  # 4 -> noise (equidistant to both centroids)
        ]
    )
    cores = np.array([0, 0, 1, 1, -1])

    # Sanity: the cosine similarities of point 4 to the two centroids are equal.
    from sklearn.metrics.pairwise import cosine_similarity

    centroids = np.array([X[cores == 0].mean(axis=0), X[cores == 1].mean(axis=0)])
    sims = np.asarray(cosine_similarity(X[[4]], centroids))[0]
    assert sims[0] == sims[1], f"cosine tie must be exact, got {sims}"

    for run in range(3):
        cc = _make_clusterer_with_cores(cores)
        # labels_pheromone_ stays None; pass labels=cores directly so stage 2 runs
        # on the noise point.
        labels = cc.absorb_centroid(X=X, labels=cores)
        assert labels[4] == 0, f"run {run}: expected cluster 0 (smallest index), got {labels[4]}"


def test_tie_breaking_stable_across_runs():
    """Repeating the pheromone tie-breaking test 10 times always yields cluster 0.

    Catches any hidden RNG dependence in the absorption path.
    """

    cores = np.array([0, 0, 1, 1, -1])
    G = _build_pheromone_tie_graph()

    for run in range(10):
        cc = _make_clusterer_with_cores(cores, max_iterations=1)
        labels = cc.absorb_pheromone(G)
        assert labels[4] == 0, f"run {run}: tie-breaking is not deterministic, got {labels[4]}"
