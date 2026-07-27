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
    """Score a clustering against ground truth, under both noise conventions.

    Noise (`-1`) can be handled two ways, and they disagree so violently that
    reporting only one is a methodological choice rather than a detail.

    `ARI_assigned` drops the noise points and scores the rest. It answers "when
    this clusterer commits, is it right?", which is the useful question while
    tuning one algorithm. It is useless for comparing two, because abstaining
    raises it: on a synthetic set, a clusterer that labelled 90% of the points
    as noise and got the rest perfect scores 1.000, beating one that labelled
    everything with 10% errors and scored 0.790.

    `ARI_all` scores every point, with each noise point as its own singleton.
    ARI counts pairs, and a point marked noise makes no claim about belonging
    with anything - a singleton encodes exactly that, so the score reflects
    what was claimed and nothing else. This is the number to compare
    clusterers on. The same two above score 0.015 and 0.790.

    A third convention, noise as one shared cluster, is deliberately not
    offered: it penalises the claim that all noise points group together,
    which no clusterer makes.

    The entropy-based scores are reported on assigned points only. They cannot
    use the singleton convention - every singleton is trivially pure, so
    homogeneity is pinned at 1.0 regardless of the clustering.

    Always read a score next to `NoisePct`. A number without its coverage is
    not interpretable under either convention.

    Args:
        y_true: Ground-truth labels, shape (N,).
        y_pred: Predicted labels, shape (N,), where negative means noise.

    Returns:
        Mapping with `Clusters` (excluding noise), `NoisePct`, `ARI_all`,
        `ARI_assigned`, `Purity`, `Homogeneity`, `Completeness` and
        `V-Measure`. On an all-noise input every score is 0.0.
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
            "ARI_all": 0.0,
            "ARI_assigned": 0.0,
            "Purity": 0.0,
            "Homogeneity": 0.0,
            "Completeness": 0.0,
            "V-Measure": 0.0,
        }

    # Offset past any real label so the singletons cannot collide with one.
    singleton_ids = y_pred.max() + 1 + np.arange(y_pred.size)
    as_singletons = np.where(assigned, y_pred, singleton_ids)

    contingency = metrics.cluster.contingency_matrix(truth, pred)
    purity = float(np.sum(np.amax(contingency, axis=0)) / np.sum(contingency))

    return {
        "Clusters": int(np.unique(pred).size),
        "NoisePct": noise_pct,
        "ARI_all": float(adjusted_rand_score(y_true, as_singletons)),
        "ARI_assigned": float(adjusted_rand_score(truth, pred)),
        "Purity": purity,
        "Homogeneity": float(homogeneity_score(truth, pred)),
        "Completeness": float(completeness_score(truth, pred)),
        "V-Measure": float(v_measure_score(truth, pred)),
    }
