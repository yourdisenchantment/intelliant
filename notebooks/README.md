# Notebooks

Calibration and comparison runs. The library is the subject; these are the
experiments performed on it.

This file covers mechanics - where things go, how a notebook is structured.
What gets measured and what makes a run usable is the protocol, in
[EXPERIMENTS.md](../EXPERIMENTS.md).

## Layout

```
notebooks/<group>/<dataset>/<clusterer>/
```

`<group>` is `2d`, `3d` or `text`, so synthetic and real data sit at the same
depth. Each clusterer folder holds one notebook pair, its run log and its
checkpoints:

```
notebooks/2d/blobs/intelliant/
    blobs_intelliant.ipynb      committed WITH executed output
    blobs_intelliant.py         jupytext source, the thing that gets reviewed
    output.txt                  run log, gitignored
    checkpoints/                gitignored
notebooks/2d/blobs/comparison/  cross-clusterer summary for this dataset
```

Notebook filenames are unique across the repository - `blobs_intelliant`, not
`notebook` - so a name in a report identifies exactly one file.

## Division of labour

The agent writes the jupytext `.py` and converts it; the maintainer runs the
notebook. Runtime output is captured to `output.txt` next to the notebook via
`utils.Tee`, which the agent reads. The maintainer reads the plots. Nobody
pastes cell output into a chat.

## What goes where

| Artifact | Location | Versioned |
|---|---|---|
| notebook + jupytext source | next to each other | yes |
| run log | `output.txt` | no |
| metrics, per-run tables | `results/<...>/*.csv`, `*.json` | yes |
| figures | `results/<...>/` | no |
| datasets and embeddings | `data/<dataset>/` | no |

`.ipynb` are committed with their output on purpose: they are the showcase on
GitHub, and a notebook whose results you cannot see proves nothing.

Synthetic data is regenerated per notebook from a fixed seed - deterministic
and cheap, so there is nothing to cache. Real datasets are prepared once into
`data/` and loaded by every clusterer notebook; kernels do not share memory,
so reuse happens through the disk.

## Structure rules

Imports go in separate cells, in this order: third-party libraries, then the
`sys.path` setup that makes `utils/` importable, then local imports, then path
and plot configuration. Splitting them this way avoids import warnings.

Every section opens with an `##` heading in its own markdown cell followed by
a separate explanation cell. Execution is sectioned so the pipeline can be
inspected between stages - that mirrors the library's staged design, which is
the thing worth showing.

Print tables in full: aligned manual output, or polars with
`pl.Config(tbl_rows=-1, tbl_cols=-1)`. Never a bare `print(df)` that hides
rows behind an ellipsis - a truncated table in a run log is a result nobody
can check.
