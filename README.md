# intelliant

Clustering by ant colony optimization on a k-nearest-neighbour graph.

[![PyPI](https://img.shields.io/pypi/v/intelliant)](https://pypi.org/project/intelliant/)
[![Python](https://img.shields.io/pypi/pyversions/intelliant)](https://pypi.org/project/intelliant/)
[![CI](https://github.com/yourdisenchantment/intelliant/actions/workflows/ci.yml/badge.svg)](https://github.com/yourdisenchantment/intelliant/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![intelliant-core](https://img.shields.io/badge/intelliant--core-superseded-lightgrey)](https://pypi.org/project/intelliant-core/)

## Overview

Most clustering algorithms draw boundaries in feature space. This one does
not. It turns the data into a k-nearest-neighbour similarity graph, releases
a colony of ants onto it, and reads the clusters out of the pheromone trails
they leave behind: dense regions accumulate pheromone, sparse ones do not.

Because everything after the first step happens on the graph, the algorithm
does not care how many dimensions the input had. Two features and 768 look
the same to the ants.

> **Alpha.** The public API still changes between versions, and the parameter
> ranges are being calibrated. This is research software, not a
> production-ready package.

## Features

- **Works on a graph, not on coordinates.** Any symmetric metric, any
  dimensionality.
- **Three separate stages.** Graph, pheromone field, clusters - each is its
  own object, and the state between them is inspectable and editable. You can
  threshold the same pheromone field a dozen ways without recomputing it.
- **Sparse and compiled.** scipy CSR throughout, ant steps in Numba.
- **Two-stage noise absorption.** Pheromone waves first, centroid fallback
  second, so isolated points are not simply discarded.
- **Typed.** Ships `py.typed`; pyright-clean.

## Installation

```bash
pip install intelliant
```

Python 3.14 or newer. With [uv](https://docs.astral.sh/uv/):

```bash
uv add intelliant
```

## Usage

```python
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score

from intelliant import CoreClusterer, GraphBuilder, PheromoneExtractor, find_threshold

X, y = make_blobs(n_samples=1000, centers=7, cluster_std=0.6, random_state=42)

# 1. embeddings -> KNN similarity graph
graph = GraphBuilder(n_neighbors=15, metric="cosine", mutual=True).build(X)

# 2. graph -> pheromone field
aco = PheromoneExtractor(
    n_ants=len(X), n_iterations=20, path_length=10,
    beta=2.0, alpha=1.0,
    evaporation_rate=0.07, evaporation_schedule="step",
    pheromone_deposit=1.0, initial_pheromone=1.0,
    tau_min=0.01, tau_max=10.0,
    random_state=42,
)
aco.fit(graph)

# 3. pheromone field -> clusters
cutoff = find_threshold(aco.pheromone_matrix_.data, method="otsu")
labels = CoreClusterer(
    min_cluster_size=15, max_iterations=20,
    gap_ratio=3.0, max_gap_rank=3, batch_size=1000,
).fit_predict(aco.pheromone_matrix_, threshold_value=cutoff.value, X=X)

print(adjusted_rand_score(y, labels))  # 0.807
```

The stages are deliberately not fused into a single `fit`. Everything between
them - `graph_`, `pheromone_matrix_`, `cores_`, `labels_pheromone_` - is
public, and re-running only the last stage with a different threshold is
cheap.

## Configuration

**Parameters that shape the result have no defaults.** Passing them is not
optional, and every constructor is keyword-only.

That is unusual, and deliberate: calibration is still in progress, so a
default would be a value nobody has justified, applied silently. One of the
former defaults sat exactly on the evaporation rate that measurement showed
to fragment clusters. Explicit parameters make a run reproducible from its
call site.

Parameters that do not shape the result - `verbose`, `random_state`,
`warmup`, `knn_method`, the `use_*` heuristic switches - keep their defaults.

Two that are easy to get wrong:

- `n_neighbors` bounds everything downstream. No threshold can separate two
  clusters that the KNN graph already merged into one component. When results
  disappoint, look at the graph before touching ACO parameters.
- `evaporation_schedule` changes what `evaporation_rate` means. Under
  `"step"` the field decays once per ant step, so the effective per-iteration
  decay is `1 - (1 - rate) ** path_length` - at `rate=0.07` and
  `path_length=10` that is 0.516, not 0.07. **No value from the ACO
  literature transfers to this schedule.** `"iteration"` is the classical
  behaviour. Which is better here is being measured.

## Project status

Under active development as research work by a single maintainer. The library
itself is complete and tested; what remains is calibration - establishing
which parameter values hold across datasets, and on which the algorithm
breaks. Until that settles, expect the API to move between versions.

The previous version was published as
[`intelliant-core`](https://pypi.org/project/intelliant-core/) with a
single-class API. It is superseded and should not be installed.

## Contributing

Issues and questions are welcome. Pull requests target `dev`; the setup, the
verify chain and the commit rules are in [CONTRIBUTING.md](CONTRIBUTING.md).
Security policy: [SECURITY.md](SECURITY.md).

## License

MIT - see [LICENSE](LICENSE).
