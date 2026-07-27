# src/intelliant/threshold.py

from typing import NamedTuple

import numpy as np
from scipy.sparse import csr_matrix

from ._validation import _check_float, _check_int
from .core_clusterer import CoreClusterer


class ThresholdResult(NamedTuple):
    value: float
    percentile: float


class ScanRow(NamedTuple):
    percentile: float
    value: float
    n_cores: int
    n_noise: int
    top1_size: int
    median_size: float


def threshold_otsu(data: np.ndarray, bins: int = 100) -> ThresholdResult:
    if data.size == 0:
        raise ValueError("data is empty: cannot compute a threshold on an empty array")
    # Otsu splits the histogram in two, so one bin leaves nothing to split:
    # variance_between is built from weight1[:-1] and comes out empty, and
    # np.argmax then fails with a message about numpy internals rather than
    # about the caller's argument.
    if bins < 2:
        raise ValueError(f"bins must be >= 2 for otsu (a single bin cannot be split), got {bins}")
    counts, bin_edges = np.histogram(data, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    weight1 = np.cumsum(counts)
    weight2 = np.cumsum(counts[::-1])[::-1]

    mean1 = np.cumsum(counts * bin_centers) / (weight1 + 1e-9)
    mean2 = (np.cumsum((counts * bin_centers)[::-1]) / (weight2[::-1] + 1e-9))[::-1]

    variance_between = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2
    idx = int(np.argmax(variance_between))
    value = float(bin_centers[idx])

    percentile = float((data <= value).mean() * 100.0)
    return ThresholdResult(value=value, percentile=percentile)


def threshold_percentile(data: np.ndarray, percentile: float) -> ThresholdResult:
    if data.size == 0:
        raise ValueError("data is empty: cannot compute a threshold on an empty array")
    # Through _check_float rather than a bare range test: the range test
    # accepts True, which numpy then reads as the 1st percentile. Rejecting
    # bool is the reason the helper exists, and every other float parameter
    # in this module already goes through it.
    percentile = _check_float("percentile", percentile, 0.0, 100.0)
    value = float(np.percentile(data, percentile))
    return ThresholdResult(value=value, percentile=float(percentile))


def threshold_stat(data: np.ndarray, k: float = 1.0) -> ThresholdResult:
    if data.size == 0:
        raise ValueError("data is empty: cannot compute a threshold on an empty array")
    value = float(np.mean(data) + k * np.std(data))
    percentile = float((data <= value).mean() * 100.0)
    return ThresholdResult(value=value, percentile=percentile)


def find_threshold(
    data: np.ndarray,
    method: str = "otsu",
    percentile: float = 95.0,
    k: float = 1.0,
    bins: int = 100,
) -> ThresholdResult:
    if data.size == 0:
        raise ValueError("data is empty: cannot compute a threshold on an empty array")
    if not np.isfinite(data).all():
        raise ValueError("data contains NaN or inf: clean the values before computing a threshold")
    k = _check_float("k", k, min_val=float("-inf"))
    bins = _check_int("bins", bins, 2)
    if method == "otsu":
        return threshold_otsu(data, bins=bins)
    if method == "percentile":
        return threshold_percentile(data, percentile)
    if method == "stat":
        return threshold_stat(data, k=k)
    raise ValueError(f"unknown threshold method: {method}; allowed: otsu, percentile, stat")


def scan_thresholds(
    pheromone_graph: csr_matrix,
    min_cluster_size: int,
    center_percentile: float = 95.0,
    percentiles: list[float] | None = None,
    step: float = 1.0,
    n_steps: int = 3,
) -> list[ScanRow]:
    data = pheromone_graph.data

    if data.size == 0:
        raise ValueError("pheromone_graph is empty (no edges): scan_thresholds is impossible")
    if not np.isfinite(data).all():
        raise ValueError("pheromone_graph contains NaN or inf: clean the edge weights before scanning thresholds")

    n_steps = _check_int("n_steps", n_steps, 0)
    step = _check_float("step", step, 0.0)
    if step == 0.0:
        raise ValueError(f"step must be > 0, got {step}")
    center_percentile = _check_float("center_percentile", center_percentile, 0.0, 100.0)

    if percentiles is None:
        offsets = np.arange(-n_steps, n_steps + 1) * step
        grid = [float(np.clip(center_percentile + off, 0.0, 100.0)) for off in offsets]
        grid = list(dict.fromkeys(grid))
    else:
        if len(percentiles) == 0:
            raise ValueError("percentiles must not be empty")
        for p in percentiles:
            if not 0.0 <= p <= 100.0:
                raise ValueError(f"percentiles must be in range [0, 100], got {p}")
        grid = [float(p) for p in percentiles]

    # These three do not affect the scan: only extract_cores runs here, so
    # absorption (max_iterations) never happens, and the giant diagnostic
    # (gap_ratio, max_gap_rank) feeds logging that verbose=False suppresses.
    # ScanRow carries none of it. Stated explicitly because the constructor
    # requires them.
    clusterer = CoreClusterer(
        min_cluster_size=min_cluster_size,
        max_iterations=20,
        gap_ratio=3.0,
        max_gap_rank=3,
        verbose=False,
    )

    rows: list[ScanRow] = []
    for p in grid:
        cutoff = float(np.percentile(data, p))
        labels = clusterer.extract_cores(pheromone_graph, threshold_value=cutoff)

        valid = labels[labels >= 0]
        sizes = np.unique(valid, return_counts=True)[1] if valid.size else np.array([], dtype=int)
        rows.append(
            ScanRow(
                percentile=p,
                value=cutoff,
                n_cores=int(sizes.size),
                n_noise=int((labels < 0).sum()),
                top1_size=int(sizes.max()) if sizes.size else 0,
                median_size=float(np.median(sizes)) if sizes.size else 0.0,
            )
        )

    return rows
