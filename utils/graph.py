"""Graph diagnostics and the ablation the colony has to beat.

Two things a run cannot be read without.

`graph_report` describes the object the ants are about to walk on: how it
fell apart on its own, how much of it one component holds, and how many
points sit in pieces too small to ever become a core. On synthetic data this
is a sanity check. On real embeddings it is the only description of the graph
there is, because the spatial figures stop meaning anything.

`graph_baseline` removes the colony and runs everything else. That is the
standard ablation: take out the part under investigation, keep the rest
identical, and see whether the answer moves. If it does not, the part under
investigation did nothing on this data - and without ground truth there is no
way to notice, which is why the synthetic sets come first.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from intelliant import CoreClusterer

from .metrics import evaluate_clustering


def graph_report(graph: csr_matrix, *, min_cluster_size: int | None = None) -> dict[str, Any]:
    """Describe a KNN graph before anything runs on it.

    Components are counted on the graph as built - no threshold, no
    pheromone. Isolated points are counted separately from small components,
    because they arise differently: `mutual=True` can strip a point of every
    edge, while a small component is a genuine island of several points that
    the search connected to each other and to nothing else.

    Args:
        graph: The similarity graph from `GraphBuilder.build`.
        min_cluster_size: The clusterer's threshold for a component counting
            as a core. When given, components below it are reported as
            islands - points the pipeline can only reach by absorption.

    Returns:
        Mapping with node and edge counts, degree statistics, `Asymmetric`
        (nonzero entries where the graph disagrees with its transpose - zero
        for anything `GraphBuilder` produced), the component count, the
        largest component's share, singleton and island counts, and the five
        largest component sizes under `CompTop5`.
    """
    n = graph.shape[0]
    degrees = np.diff(graph.indptr)

    n_comp, comp = connected_components(graph, directed=False)
    sizes = np.sort(np.bincount(comp, minlength=n_comp))[::-1]

    islands = 0
    island_points = 0
    if min_cluster_size is not None:
        small = sizes < min_cluster_size
        islands = int(small.sum())
        island_points = int(sizes[small].sum())

    return {
        "Nodes": int(n),
        "Edges": int(graph.nnz // 2),
        "DegreeMin": int(degrees.min()),
        "DegreeMean": float(degrees.mean()),
        "DegreeMax": int(degrees.max()),
        "Isolated": int((degrees == 0).sum()),
        "Asymmetric": int(abs(graph - graph.T).nnz),
        "Components": int(n_comp),
        "GiantShare": float(sizes[0] / n),
        "CompMedian": float(np.median(sizes)),
        "Singletons": int((sizes == 1).sum()),
        "Islands": islands,
        "IslandPoints": island_points,
        "CompTop5": [int(s) for s in sizes[:5]],
    }


def graph_baseline(
    graph: csr_matrix,
    y_true: NDArray[np.integer],
    *,
    cluster_params: dict[str, Any],
    X: NDArray[np.floating] | None = None,
) -> dict[str, Any]:
    """Score the graph with the colony removed and everything else kept.

    Two readings, and they answer different questions.

    `baseline_ARI` is the graph's own connected components, scored as they
    are. It is the floor: a pipeline that hands them back unchanged has done
    nothing, and the identity is visible in the score to six decimal places.

    `baseline_pipeline_ARI` runs those same components through the rest of
    the pipeline - the `min_cluster_size` cut and absorption - by handing the
    graph itself to `CoreClusterer` under a cutoff below its smallest edge,
    so nothing is dropped. This is the honest comparison, because it is the
    same final step the colony's output receives. The difference between the
    two numbers is what absorption contributes on its own.

    Neither involves `PheromoneExtractor`, and neither has a seed: the whole
    point is that this is what remains when the stochastic part is removed.

    Args:
        graph: The similarity graph from `GraphBuilder.build`.
        y_true: Ground-truth labels. This is only computable on data that has
            them, which is why synthetic sets carry the argument.
        cluster_params: The same mapping the run's `CoreClusterer` is built
            from, so the ablation differs from the run in the colony alone.
        X: Feature matrix for the centroid fallback, as in the run.

    Returns:
        Mapping with `baseline_components`, `baseline_ARI`,
        `baseline_pipeline_ARI`, `baseline_pipeline_clusters` and
        `baseline_pipeline_noise`.
    """
    n_comp, comp = connected_components(graph, directed=False)

    cutoff = float(graph.data.min()) - 1.0
    clusterer = CoreClusterer(**cluster_params, verbose=False)
    cores = clusterer.extract_cores(graph, threshold_value=cutoff)
    labels = clusterer.absorb(graph, X) if (cores >= 0).any() else cores

    pipeline_metrics = evaluate_clustering(y_true, labels)

    return {
        "baseline_components": int(n_comp),
        "baseline_ARI": evaluate_clustering(y_true, comp)["ARI_all"],
        "baseline_pipeline_ARI": pipeline_metrics["ARI_all"],
        "baseline_pipeline_clusters": pipeline_metrics["Clusters"],
        "baseline_pipeline_noise": pipeline_metrics["NoisePct"],
    }
