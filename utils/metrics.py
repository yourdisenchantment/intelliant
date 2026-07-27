"""Clustering quality metrics against ground-truth labels."""

import numpy as np
from numpy.typing import NDArray
from sklearn import metrics
from sklearn.metrics import (
    adjusted_rand_score,
    completeness_score,
    homogeneity_score,
    v_measure_score,
)


def evaluate_clustering(y_true: NDArray[np.integer], y_pred: NDArray[np.integer]) -> dict[str, float]:
    """Score a clustering against ground truth.

    Every score except `NoisePct` is computed on the points the clusterer
    assigned to a cluster; points labelled `-1` are excluded.

    That choice is not neutral, and it matters for the comparison phase: a
    clusterer that gives up on 40% of the data is graded only on the easy 60%
    and can outscore one that labelled everything. Read `NoisePct` alongside
    the rest, and settle on one convention before producing numbers for the
    article rather than after.

    Args:
        y_true: Ground-truth labels, shape (N,).
        y_pred: Predicted labels, shape (N,), where negative means noise.

    Returns:
        Mapping with `Clusters` (excluding noise), `NoisePct`, `Purity`,
        `Homogeneity`, `Completeness`, `V-Measure` and `ARI`. On an all-noise
        input every score is 0.0.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    assigned = y_pred >= 0
    truth, pred = y_true[assigned], y_pred[assigned]
    noise_pct = float((~assigned).mean() * 100)

    if pred.size == 0:
        return {
            "Clusters": 0,
            "NoisePct": noise_pct,
            "Purity": 0.0,
            "Homogeneity": 0.0,
            "Completeness": 0.0,
            "V-Measure": 0.0,
            "ARI": 0.0,
        }

    contingency = metrics.cluster.contingency_matrix(truth, pred)
    purity = float(np.sum(np.amax(contingency, axis=0)) / np.sum(contingency))

    return {
        "Clusters": int(np.unique(pred).size),
        "NoisePct": noise_pct,
        "Purity": purity,
        "Homogeneity": float(homogeneity_score(truth, pred)),
        "Completeness": float(completeness_score(truth, pred)),
        "V-Measure": float(v_measure_score(truth, pred)),
        "ARI": float(adjusted_rand_score(truth, pred)),
    }
