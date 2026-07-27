# src/intelliant/__init__.py
"""Clustering by ant colony optimization on a k-nearest-neighbour graph.

Three stages, deliberately separate objects rather than one `fit`:

1. `GraphBuilder` turns embeddings into a sparse similarity graph. Everything
   after this point works on the graph, which is why the algorithm does not
   care about dimensionality.
2. `PheromoneExtractor` releases ants onto that graph. Dense regions
   accumulate pheromone; sparse ones do not.
3. `find_threshold` picks where to cut the pheromone field, and
   `CoreClusterer` turns the cut into labels, absorbing noise afterwards.

The state between stages - `graph_`, `pheromone_matrix_`, `cores_`,
`labels_pheromone_` - is public and meant to be inspected and edited. Cutting
the same field at a different threshold costs milliseconds; re-running the
colony does not.

Parameters that shape the result carry no defaults and must be passed by
keyword. See the README for why.
"""

from .core_clusterer import CoreClusterer, GiantDiagnostics
from .graph_builder import GraphBuilder
from .pheromone_extractor import PheromoneExtractor
from .threshold import ScanRow, ThresholdResult, find_threshold, scan_thresholds

__version__ = "0.1.0a2"
__all__ = [
    "CoreClusterer",
    "GiantDiagnostics",
    "GraphBuilder",
    "PheromoneExtractor",
    "ScanRow",
    "ThresholdResult",
    "find_threshold",
    "scan_thresholds",
]
