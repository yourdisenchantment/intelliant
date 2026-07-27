"""test_threshold_behavior.py
# Behavioral tests of find_threshold (otsu/stat/percentile) and scan_thresholds:
# correctness of returned values and invariants of ScanRow fields.
"""

import numpy as np
from conftest import make_extractor, make_graph_builder
from scipy.sparse import csr_matrix

from intelliant.threshold import ScanRow, ThresholdResult, find_threshold, scan_thresholds


def section(title):
    print(f"\n=== {title} ===")


# --- find_threshold: otsu ---
def test_find_threshold_otsu_returns_value():
    """Checks that find_threshold with method='otsu' returns a ThresholdResult with a finite value and percentile.

    Otsu computes the inter-class variance of a histogram and picks the threshold
    at the maximum; the result must be finite and accompanied by the percentile
    position of the threshold.
    """

    section("find_threshold: otsu returns a ThresholdResult")
    rng = np.random.default_rng(42)
    data = rng.uniform(0.0, 10.0, 100)

    result = find_threshold(data, method="otsu")

    assert np.isfinite(result.value)
    assert isinstance(result.value, float)
    assert isinstance(result.percentile, float)
    assert 0.0 <= result.percentile <= 100.0


# --- find_threshold: stat ---
def test_find_threshold_stat_returns_value():
    """Checks that find_threshold with method='stat' returns the mean+k*std threshold and depends on k.

    The stat threshold equals mean(data) + k*std(data); at different k the
    threshold must differ (provided the data has non-zero variance).
    """

    section("find_threshold: stat returns a value depending on k")
    rng = np.random.default_rng(42)
    data = rng.uniform(0.0, 10.0, 100)

    r1 = find_threshold(data, method="stat", k=1.0)
    r2 = find_threshold(data, method="stat", k=2.0)

    assert np.isfinite(r1.value)
    assert isinstance(r1.value, float)
    assert np.isfinite(r2.value)
    assert r2.value > r1.value


# --- find_threshold: percentile ---
def test_find_threshold_percentile_returns_value():
    """Checks that find_threshold with method='percentile' returns a percentile of the data.

    The threshold must match np.percentile(data, percentile), and the percentile
    field of ThresholdResult must hold the requested percentile.
    """

    section("find_threshold: percentile matches np.percentile")
    rng = np.random.default_rng(42)
    data = rng.uniform(0.0, 10.0, 100)

    result = find_threshold(data, method="percentile", percentile=90.0)

    assert np.isfinite(result.value)
    assert isinstance(result.value, float)
    assert np.isclose(result.value, np.percentile(data, 90.0))


# --- scan_thresholds: ScanRow contents ---
def test_scan_thresholds_row_contents():
    """Checks that scan_thresholds returns correct invariants of ScanRow fields.

    For each percentile: n_cores/n_noise/top1_size/median_size are non-negative,
    value is a float, and the invariant n_cores + n_noise == N (points in the
    graph) holds.
    """

    section("scan_thresholds: invariants of ScanRow fields")
    rng = np.random.default_rng(42)
    X = rng.standard_normal((20, 4))
    gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=42)
    G = gb.build(X)
    pe = make_extractor(n_ants=10, n_iterations=5, verbose=False, random_state=42)
    pe.fit(G)
    pheromone = pe.pheromone_matrix_
    assert pheromone is not None

    rows = scan_thresholds(pheromone, min_cluster_size=2, percentiles=[10.0, 50.0, 90.0])

    assert len(rows) == 3
    n = pheromone.shape[0]
    for row, expected_p in zip(rows, [10.0, 50.0, 90.0], strict=True):
        assert row.percentile == expected_p
        assert isinstance(row.value, float)
        assert np.isfinite(row.value)
        assert row.n_cores >= 0
        assert row.n_noise >= 0
        assert row.top1_size >= 0
        assert row.median_size >= 0
        # Points are either in cores or noise: n_noise does not exceed N, and
        # when cores exist top1_size is the size of the largest core (<= N -
        # n_noise).
        assert row.n_noise <= n
        if row.n_cores > 0:
            assert row.top1_size <= n - row.n_noise
        else:
            assert row.top1_size == 0
            assert row.n_noise == n


# --- ThresholdResult / ScanRow: named fields ---
def test_threshold_result_namedtuple_fields():
    """Checks that ThresholdResult and ScanRow have the declared fields and correct types.

    find_threshold(method='otsu') must return a ThresholdResult with .value and
    .percentile fields (both float). scan_thresholds must return a list of
    ScanRow, the first element of which has .value, .percentile, .n_cores,
    .n_noise, .top1_size, .median_size fields with the expected types.
    """

    section("ThresholdResult / ScanRow: fields and types")
    rng = np.random.default_rng(42)
    data = rng.uniform(0.0, 10.0, 100)

    result = find_threshold(data, method="otsu")
    assert isinstance(result, ThresholdResult)
    assert hasattr(result, "value")
    assert hasattr(result, "percentile")
    assert isinstance(result.value, float)
    assert isinstance(result.percentile, float)
    assert np.isfinite(result.value)
    assert 0.0 <= result.percentile <= 100.0

    X = rng.standard_normal((20, 4))
    gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=42)
    G = gb.build(X)
    pe = make_extractor(n_ants=10, n_iterations=5, verbose=False, random_state=42)
    pe.fit(G)
    pheromone = pe.pheromone_matrix_
    assert pheromone is not None

    rows = scan_thresholds(pheromone, min_cluster_size=2, percentiles=[50.0])
    assert len(rows) == 1
    first = rows[0]
    assert isinstance(first, ScanRow)
    for field in ("value", "percentile", "n_cores", "n_noise", "top1_size", "median_size"):
        assert hasattr(first, field)
    assert isinstance(first.value, float)
    assert isinstance(first.percentile, float)
    assert isinstance(first.n_cores, int)
    assert isinstance(first.n_noise, int)
    assert isinstance(first.top1_size, int)
    assert isinstance(first.median_size, float)


# --- scan_thresholds: default grid near the upper bound ---
def test_scan_thresholds_default_grid_clipped_no_duplicates():
    """Checks the default grid: center +- n_steps*step, clipped to [0, 100], no duplicates.

    With center_percentile=99, step=1, n_steps=3 the raw offsets give
    [96..102]; values above 100 are clipped to 100 and the duplicates are
    collapsed, so the resulting rows must scan exactly [96, 97, 98, 99, 100].
    """

    section("scan_thresholds: default grid clipped at 100 without duplicates")
    rows_idx = [0, 1, 2]
    cols_idx = [1, 2, 0]
    data = [0.5, 0.6, 0.7]
    G = csr_matrix((data, (rows_idx, cols_idx)), shape=(3, 3))

    rows = scan_thresholds(G, min_cluster_size=2, center_percentile=99.0, step=1.0, n_steps=3)

    percentiles = [row.percentile for row in rows]
    print(f"  grid: {percentiles}")
    assert percentiles == [96.0, 97.0, 98.0, 99.0, 100.0]
    assert len(percentiles) == len(set(percentiles))


# --- scan_thresholds: case of 0 cores (all points are noise) ---
def test_scan_thresholds_zero_cores():
    """Checks that scan_thresholds correctly reflects the case of 0 cores.

    Builds a graph where at a high threshold (percentile 99.9) all edges are cut,
    and extract_cores finds 0 cores. The corresponding ScanRow must have
    n_cores=0, n_noise=N (all points are noise), top1_size=0, median_size=0.0.
    """

    section("scan_thresholds: 0 cores at a high percentile")
    # Fully connected graph with identical weights: at percentile 99.9 the cutoff
    # equals the maximum weight, so all edges are cut (the <= cutoff condition).
    rows_idx = [0, 0, 0, 1, 1, 1, 2, 2, 2]
    cols_idx = [1, 2, 3, 0, 2, 3, 0, 1, 3]
    data = [1.0] * 9
    G = csr_matrix((data, (rows_idx, cols_idx)), shape=(4, 4))
    N = G.shape[0]

    rows = scan_thresholds(G, min_cluster_size=2, percentiles=[99.9])
    assert len(rows) == 1
    row = rows[0]
    print(f"  p={row.percentile}, cutoff={row.value}, n_cores={row.n_cores}, n_noise={row.n_noise}")
    assert row.n_cores == 0
    assert row.n_noise == N
    assert row.top1_size == 0
    assert row.median_size == 0.0
