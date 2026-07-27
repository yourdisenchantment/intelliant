"""test_scale_smoke.py

Scale smoke test on a larger dataset (50k points) to prepare for comparison
with other clustering algorithms. Marked slow and excluded from the default
run via addopts = "-m 'not slow'".
"""

import numpy as np
import pytest
from conftest import make_clusterer, make_extractor, make_graph_builder
from sklearn.datasets import make_blobs

from intelliant import find_threshold

pytestmark = pytest.mark.slow


def test_scale_smoke_50k():
    n_samples = 50_000

    X, _ = make_blobs(
        n_samples=n_samples,
        centers=10,
        cluster_std=0.8,
        random_state=42,
    )

    gb = make_graph_builder(n_neighbors=15, metric="cosine", verbose=False, random_state=42)
    G = gb.build(X)

    pe = make_extractor(
        n_ants=n_samples,
        n_iterations=10,
        path_length=15,
        verbose=False,
        random_state=42,
    )
    pe.fit(G)

    threshold = find_threshold(pe.pheromone_matrix_.data, method="otsu")

    cc = make_clusterer(min_cluster_size=30, batch_size=2000, verbose=False)
    labels = cc.fit_predict(pe.pheromone_matrix_, threshold_value=threshold.value, X=X)

    assert labels.shape == (n_samples,)
    assert not np.all(labels == -1)
    assert len(np.unique(labels[labels >= 0])) >= 2
