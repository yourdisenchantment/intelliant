"""test_threshold_integration.py
# Integration of find_threshold / scan_thresholds with CoreClusterer.extract_cores:
# the cutoff computed externally must produce the same labels as the in-place path.
"""

import numpy as np
from conftest import make_clusterer, make_extractor, make_graph_builder
from sklearn.datasets import make_blobs

from intelliant import find_threshold, scan_thresholds


def section(title):
    print(f"\n=== {title} ===")


def _build_pheromone_matrix():
    X, _ = make_blobs(n_samples=200, n_features=4, centers=3, random_state=42)
    gb = make_graph_builder(n_neighbors=8, verbose=False, random_state=42)
    G = gb.build(X)
    pe = make_extractor(n_ants=20, n_iterations=10, verbose=False, random_state=42)
    pe.fit(G)
    return pe.pheromone_matrix_


# --- threshold_percentile and threshold_value give the same labels ---
def test_threshold_percentile_consistent():
    """Checks that threshold_value from find_threshold(method='percentile') matches threshold_percentile.

    For a set of percentiles, extract_cores(threshold_value=thr.value) and
    extract_cores(threshold_percentile=P) must produce identical core labels,
    since both compute the cutoff as np.percentile(data, P).
    """

    section("threshold_percentile vs threshold_value consistency")
    phero = _build_pheromone_matrix()

    for p in [50, 75, 90, 95]:
        thr = find_threshold(phero.data, method="percentile", percentile=p)

        cc_value = make_clusterer(min_cluster_size=5, verbose=False)
        labels_value = cc_value.extract_cores(phero, threshold_value=thr.value)

        cc_percentile = make_clusterer(min_cluster_size=5, verbose=False)
        labels_percentile = cc_percentile.extract_cores(phero, threshold_percentile=p)

        assert np.array_equal(labels_value, labels_percentile), (
            f"labels differ for percentile={p}: threshold_value={thr.value}"
        )


# --- otsu threshold yields at least one core ---
def test_threshold_otsu_consistent():
    """Checks that find_threshold(method='otsu') gives a finite cutoff and extract_cores finds at least one core.

    Otsu splits the weight histogram between two classes; on a clustered
    pheromone field the lower class (weak edges) should be cut, leaving at
    least one connected component large enough to be a core.
    """

    section("otsu threshold consistency")
    phero = _build_pheromone_matrix()

    thr = find_threshold(phero.data, method="otsu")
    assert np.isfinite(thr.value)

    cc = make_clusterer(min_cluster_size=5, verbose=False)
    labels = cc.extract_cores(phero, threshold_value=thr.value)

    n_cores = len(np.unique(labels[labels >= 0]))
    assert n_cores >= 1, f"otsu cutoff {thr.value} produced no cores"


# --- stat threshold gives a finite cutoff ---
def test_threshold_stat_consistent():
    """Checks that find_threshold(method='stat') gives a finite cutoff and extract_cores runs.

    The stat cutoff is mean + k*std, which can be high enough to cut all edges
    (zero cores) or leave some. Both outcomes are acceptable; the only
    invariant is that the cutoff is finite and extract_cores completes.
    """

    section("stat threshold consistency")
    phero = _build_pheromone_matrix()

    thr = find_threshold(phero.data, method="stat")
    assert np.isfinite(thr.value)

    cc = make_clusterer(min_cluster_size=5, verbose=False)
    labels = cc.extract_cores(phero, threshold_value=thr.value)

    n_cores = len(np.unique(labels[labels >= 0]))
    n_noise = int((labels < 0).sum())
    assert n_cores >= 1 or n_noise == len(labels), "stat threshold produced an inconsistent state"


# --- scan_thresholds rows match a fresh extract_cores call ---
def test_scan_thresholds_matches_extract_cores():
    """Checks that each ScanRow from scan_thresholds matches a fresh extract_cores(threshold_value=row.value).

    scan_thresholds computes n_cores and n_noise internally; re-running
    extract_cores with the same cutoff value must reproduce both counts
    exactly.
    """

    section("scan_thresholds matches extract_cores")
    phero = _build_pheromone_matrix()

    scan_rows = scan_thresholds(phero, min_cluster_size=5, percentiles=[50, 90])
    assert len(scan_rows) == 2

    for row in scan_rows:
        cc = make_clusterer(min_cluster_size=5, verbose=False)
        labels = cc.extract_cores(phero, threshold_value=row.value)

        n_cores = len(np.unique(labels[labels >= 0]))
        n_noise = int((labels < 0).sum())

        assert row.n_cores == n_cores, (
            f"n_cores mismatch at percentile={row.percentile}: scan={row.n_cores} fresh={n_cores}"
        )
        assert row.n_noise == n_noise, (
            f"n_noise mismatch at percentile={row.percentile}: scan={row.n_noise} fresh={n_noise}"
        )
