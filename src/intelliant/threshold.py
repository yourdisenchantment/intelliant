# src/intelliant/threshold.py
"""Pick the pheromone cutoff that separates cores from the rest.

After the ants have run, the pheromone field is a distribution of edge
weights, and clustering reduces to choosing where to cut it. The functions
here suggest a cutoff; `scan_thresholds` shows what a range of them would
produce, so the choice can be made on evidence rather than on a default.

The choice matters as much as any ACO parameter: the same field yields a
different partition at every cutoff, and re-cutting is cheap while re-running
the colony is not.
"""

from typing import NamedTuple

import numpy as np
from scipy.sparse import csr_matrix

from ._validation import _check_float, _check_int
from .core_clusterer import CoreClusterer


class ThresholdResult(NamedTuple):
    """A cutoff and where it falls in the distribution.

    Attributes:
        value: The cutoff itself, in pheromone units.
        percentile: Share of edge weights at or below `value`, in percent.
            Useful because a raw pheromone value means little on its own -
            the same number is aggressive on one field and permissive on
            another.
    """

    value: float
    percentile: float


class ScanRow(NamedTuple):
    """What one cutoff would produce, without committing to it.

    Attributes:
        percentile: The percentile scanned.
        value: The corresponding cutoff.
        n_cores: Cores surviving `min_cluster_size`.
        n_noise: Points left unassigned.
        top1_size: Size of the largest core. The most informative column on
            real data: a giant collapsing as the cutoff rises is the signal
            that the field is being cut in the right place, and it moves long
            before `n_cores` does.
        median_size: Median core size.
    """

    percentile: float
    value: float
    n_cores: int
    n_noise: int
    top1_size: int
    median_size: float


def threshold_otsu(data: np.ndarray, bins: int = 100) -> ThresholdResult:
    """Find the cutoff that best splits the distribution in two.

    Otsu's method, borrowed from image binarisation: histogram the values and
    pick the boundary maximising between-class variance. It assumes the
    distribution is bimodal, which the pheromone field is not always - on a
    flat field the result is arbitrary rather than wrong, and worth checking
    against `scan_thresholds` before trusting.

    Args:
        data: Edge weights, typically `pheromone_matrix_.data`.
        bins: Histogram resolution.

    Returns:
        The cutoff and its percentile.

    Raises:
        ValueError: If `data` is empty, or `bins` is below 2 - a single bin
            cannot be split.
    """
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
    """Cut at a fixed percentile of the distribution.

    The blunt option, and the honest one when the field has no clear split:
    it makes no claim about structure, only about how much to keep.

    Args:
        data: Edge weights.
        percentile: Where to cut, in [0, 100].

    Returns:
        The cutoff and the percentile it was asked for.

    Raises:
        ValueError: If `data` is empty or `percentile` is out of range or not
            a number.
    """
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
    """Cut at mean plus k standard deviations.

    Args:
        data: Edge weights.
        k: Standard deviations above the mean. Larger keeps less.

    Returns:
        The cutoff and its percentile.

    Raises:
        ValueError: If `data` is empty.
    """
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
    """Compute a cutoff by the named method.

    The entry point for the three strategies; call it rather than them.

    Args:
        data: Edge weights, typically `pheromone_matrix_.data`.
        method: `"otsu"`, `"percentile"` or `"stat"`.
        percentile: Used by `"percentile"` only.
        k: Used by `"stat"` only.
        bins: Used by `"otsu"` only.

    Returns:
        The cutoff and its percentile.

    Raises:
        ValueError: If `data` is empty or holds NaN or inf, if any numeric
            argument is invalid, or if `method` is not one of the three.
    """
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
    """Report what a range of cutoffs would produce.

    Extraction is cheap and the colony run is not, so the sensible move on an
    unfamiliar field is to look before choosing. Each row is a full extraction
    at one cutoff, with no absorption and nothing stored.

    Watch `top1_size` rather than `n_cores`: on real data a giant collapsing
    as the cutoff rises is the informative signal, and it moves long before
    the core count does.

    Args:
        pheromone_graph: The pheromone field to scan.
        min_cluster_size: Minimum size for a component to count as a core.
        center_percentile: Centre of the generated grid.
        percentiles: An explicit list of percentiles. Overrides the grid.
        step: Spacing of the generated grid, in percentiles.
        n_steps: Steps taken either side of the centre. 0 scans one point.

    Returns:
        One `ScanRow` per cutoff, in ascending percentile order.

    Raises:
        ValueError: If the graph is empty or holds NaN or inf, if `step` is
            not positive, if `percentiles` is empty or holds a value outside
            [0, 100], or if a numeric argument is invalid.
    """
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
