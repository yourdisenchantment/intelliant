# Experiment protocol

One protocol so that runs made weeks apart pool into a single table without
rerunning anything: what is measured, how a notebook is laid out, and what is
kept afterwards. It lives here rather than in a README beside each folder -
`notebooks/` holds notebooks and their output, `results/` holds results, and
neither holds instructions about itself.

The plan those runs serve is in [ROADMAP.md](ROADMAP.md).

## The metric set is closed

These seven, and nothing else without a reason recorded below.

| Metric | Role |
|---|---|
| `ARI_all` | **Primary.** Every point scored, noise as singletons. |
| `NoisePct` | Mandatory context. No score is interpretable without it. |
| `ARI_assigned` | Diagnostic: when the clusterer commits, is it right? |
| `Clusters` | Sanity: did it find roughly the right number? |
| `Purity` | Diagnostic on assigned points. |
| `Homogeneity`, `Completeness`, `V-Measure` | Entropy view, assigned points. |

`ARI_all` leads because it is the only one that survives a comparison between
clusterers with different abstention rates. Dropping noise makes giving up
look like success: on synthetic data a clusterer that labelled 90% of points
as noise and got the rest perfect scores `ARI_assigned = 1.000`, against
`0.790` for one that labelled everything with 10% errors. Under `ARI_all` they
score `0.015` and `0.790`. See the docstring in `utils/metrics.py` for why
noise becomes singletons rather than one shared cluster.

Entropy-based scores are assigned-only on purpose: singletons are trivially
pure, so homogeneity pins at 1.0 and stops measuring.

### Adding or removing one

**Adding** requires a sentence here saying which question it answers that no
existing metric does. "It is standard" is not that sentence; neither is
completeness for its own sake. Every added column is one more thing to read in
every table forever.

**Removing** is the more likely correction. A metric that has never changed a
decision is noise in the table - drop it, and say here that it was dropped and
when. The list above is expected to get shorter, not longer.

## Every row records what produced it

A metric without its settings cannot be pooled with anything later, and the
whole point of versioning these files is not rerunning. One row per run, and
the row carries:

- `dataset` and its shape
- `seed`
- every parameter that varied in the sweep, one column each
- every parameter that was **fixed**, if the sweep is meant to be compared
  with another one - otherwise the two tables cannot be joined
- the metric set above
- runtime, in seconds

Multi-seed runs go in one file with `seed` as a column, never in one file per
seed.

## Seeds

Every stage is seeded: `GraphBuilder` is deterministic, `PheromoneExtractor`
takes `random_state`, and synthetic data is regenerated from a fixed seed
rather than cached.

A single-seed number is a data point, not a result. Report a sweep across at
least five seeds and give the spread, not only the mean - a parameter whose
advantage is smaller than the seed-to-seed variation has not been shown to
have one. If five is too slow for a given grid, reduce the grid rather than
the seeds.

## What makes a run reportable

- It ran from a clean regeneration of its data, not from a mutated kernel.
- Its `output.txt` is next to the notebook and covers the whole run.
- Its parameters appear in the results file, not only in the notebook.
- Its seed set is the same as the run it will be compared against.

A run that fails any of these gets rerun rather than reported with a caveat.
Caveats do not survive into a table three months later; the number does.

## Comparisons

Two runs are comparable only on identical data, identical seeds and the same
metric convention. Comparing a five-seed mean against a single-seed number, or
`ARI_all` against `ARI_assigned`, is the same mistake in two shapes.

When comparing against another algorithm, the abstention rates will differ -
that is the case `ARI_all` exists for. Report `NoisePct` for both.

## Notebook layout

```
notebooks/<group>/<dataset>/<clusterer>/
```

`<group>` is `2d`, `3d` or `text`, so synthetic and real data sit at the same
depth. Each clusterer folder holds one notebook pair, its run log and its
checkpoints:

```
notebooks/2d/blobs/intelliant/
    blobs_intelliant.ipynb      committed WITH executed output
    blobs_intelliant.py         jupytext source, the reviewed artifact
    output.txt                  run log, gitignored
    checkpoints/                gitignored
notebooks/2d/blobs/comparison/  cross-clusterer summary for this dataset
```

Notebook filenames are unique across the repository - `blobs_intelliant`, not
`notebook` - so a name in a report identifies exactly one file.

Synthetic data is regenerated per notebook from a fixed seed: deterministic
and cheap, so there is nothing to cache. Real datasets are prepared once into
`data/` and loaded by every clusterer notebook, since kernels do not share
memory and reuse happens through the disk.

## Notebook structure

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

## What is kept

`results/` holds what a publication needs: the tables, and the figures built
from them.

| Artifact | Location | Versioned |
|---|---|---|
| notebook + jupytext source | `notebooks/<...>/` | yes |
| run log | `output.txt` beside the notebook | no |
| tables | `results/<...>/*.csv`, `*.json` | yes |
| figures | `results/<...>/` | no |
| datasets and embeddings | `data/<dataset>/` | no |

`.ipynb` are committed with their output on purpose: they are the showcase on
GitHub, and a notebook whose results you cannot see proves nothing.

Figures are the one deliberate exception among publication artifacts. A run's
numbers are a few kilobytes and expensive to reproduce; figures are derived
from those numbers and cost megabytes. The previous repository reached 425 MB
that way and its history had to be rewritten to recover.

Mirror the notebook path under `results/` so a table traces back to the run
that produced it. The rules are in `.gitignore` under `results/**` - note the
`**`, since with a plain `results/` git never descends into the directory and
the negations below it would silently do nothing.
