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

## Cluster structure is recorded too

Separate from the metric set above, and not subject to its closed list. Those
seven score a clustering against ground truth and compete with each other for
which number leads a table. These describe the partition itself, answer no
question about quality, and are mandatory context in the same way `NoisePct`
is - a mean ARI says nothing about whether one cluster swallowed the data.

Every run records:

- number of clusters, and the number of points in each;
- size minimum, maximum, mean and median;
- the five largest sizes, descending;
- the largest ratio between neighbouring ranks, and where it sits;
- the largest cluster as a share of assigned points.

Most of this already exists: `CoreClusterer` attaches a `GiantDiagnostics`
with `n_clusters`, `top_sizes`, `median`, `max_gap`, `gap_pos` and
`suspected`. Record what it reports rather than recomputing it - a second
implementation of the same statistic is a second thing that can disagree.

This block carries the weight on real data, where the spatial figures are
meaningless and the size distribution is the whole picture. A giant component
is a size-distribution phenomenon and shows up nowhere else.

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

Every calibration or test notebook has the same skeleton. Each numbered item
is one `##` section, opening with a markdown heading in its own cell followed
by a short explanation cell, then the code.

**Setup**

1. Third-party imports.
2. `sys.path` setup for local imports.
3. Local imports - `intelliant`, `utils`.
4. Paths and plot configuration for this notebook.

These are four **separate** cells, in this order. Combining them produces
import warnings, because step 3 cannot resolve until step 2 has run.

**Every path is a `pathlib.Path`.** No `os.path`, no string concatenation, no
manual separators - a notebook that builds paths by hand breaks on the first
machine with a different layout, and these are meant to be rerun.

Find the repository root by walking up to the marker rather than counting
directories - `parents[3]` breaks the day a folder level is added:

```python
PROJECT_ROOT = next(p for p in Path.cwd().resolve().parents if (p / "pyproject.toml").exists())
```

Results go to `PROJECT_ROOT / "results" / <group> / <dataset> / <clusterer>`,
mirroring this notebook's own path.

**Pipeline**

5. Build or load the dataset.
6. Graph settings.
7. Build the graph.
8. Ant settings.
9. Run the ants.
10. Threshold: pick the cutoff, and scan around it when that is the question.
11. Absorption settings.
12. Run absorption.
13. Results.

Settings are declared in their own section before the stage that consumes
them, never inline at the call. That is what makes a run readable from the log
alone, and it is why the library takes no defaults for these parameters.

Keep the stages separate. Inspecting `graph_`, `pheromone_matrix_` and
`cores_` between them is the library's staged design, and a notebook that
collapses them into one cell demonstrates the opposite of the point.

A sweep is the same skeleton with steps 6-13 inside the loop. Run one
reference configuration linearly first so the stages stay inspectable, then
sweep.

Print tables in full: aligned manual output, or polars with
`pl.Config(tbl_rows=-1, tbl_cols=-1)`. Never a bare `print(df)` that hides
rows behind an ellipsis - a truncated table in a run log is a result nobody
can check.

## Two modes, and they produce different artifacts

A notebook is written once but used in two phases, and confusing them fills
the repository with noise.

**While searching.** Parameters are not settled; the output exists for the
agent to read. Print machine-readable tables, write `runs.csv`, wrap the run
in `utils.Tee` so it lands in `output.txt`. Do not produce figures - nothing is
settled enough to be worth drawing, and every one of them is redrawn once it
is. Do not commit the executed
`.ipynb` on every iteration either: the `.py` is what changes, and a rerun of
a sweep is not a revision worth keeping. Iterate on the `.py`, and let
`output.txt` be the deliverable the agent works from.

**Once the values are settled.** The run becomes the record. Execute the
notebook a final time, commit the `.ipynb` with its output, and write the full
results to `results/`: tables as CSV/JSON, and now the figures, which is the
one point at which they are worth producing.

A document on how those results are then read - which comparisons are
meaningful, how to present them - belongs with the article work, not here. It
is deliberately not written yet.

## Figures

Built in the settled phase only, and then for **every** variant, not only the
ones that worked. A variant that failed is the more interesting picture, and
it is the one nobody thinks to save.

### The four-panel grid

One grid per variant, the four stages of the pipeline side by side:

| Panel | Shows |
|---|---|
| dataset | the input, coloured by ground truth |
| pheromone field | the distribution with the chosen cutoff marked, or the graph with sub-threshold edges dropped - the point is that the cut is visible |
| cores | what survived thresholding, before absorption |
| clusters | the final labels, noise included |

The grid exists because it makes the staged design legible: a reader sees
where a result was won or lost, which a single scatter of final labels cannot
show. When a sweep produced many runs per configuration, plot the best one per
configuration by `ARI_all` rather than all of them.

### The grid does not survive every dimensionality

**2D.** The grid as described, all four panels.

**3D.** Same four panels, but a projection has to be chosen. Fix one camera
angle - or one 2D projection - and hold it across every panel and every
variant. A grid where the viewpoint drifts between panels compares nothing.
Expect the pheromone panel to carry more of the message than it does in 2D,
since the spatial panels get harder to read as the geometry thickens.

**Real data, hundreds of dimensions.** Drop the spatial panels. Plot the
pheromone field, and let the cluster-structure table do the rest.

This is not just "it would look cluttered". A UMAP or PCA layout is fitted
independently of the clustering, so agreement between the two is partly an
artifact of the projection: a projection can pull apart points the clusterer
merged, or fold together points it separated, and the picture will look
decisive either way. Such a plot is an illustration, never evidence. If one is
made for the article, the caption must say the layout is the projection's and
not the algorithm's.

What replaces it is the size distribution - the number of clusters, the top
sizes, the giant share. On 512-dimensional embeddings that is the result.

### What makes them informative rather than merely bright

- **One colour per cluster, held across all four panels.** If cluster 3 is
  green in the dataset panel it is green in the cores panel. Without this the
  grid is four unrelated pictures.
- **Noise is grey**, never a palette colour. It is not a cluster and should
  not read as one.
- **The title carries the parameters and the metric** - the figure has to
  survive being pasted into an article draft without its notebook.
- **Axes fixed across variants of the same dataset**, so two grids can be laid
  side by side and compared.
- **Colourblind-safe palette**, and readable at the size a paper prints.
- PNG, at a DPI that survives a zoom.

## What is kept

`results/` holds what a publication needs: the tables, and the figures built
from them.

| Artifact | Location | Versioned |
|---|---|---|
| notebook + jupytext source | `notebooks/<...>/` | yes |
| run log | `output.txt` beside the notebook | no |
| tables | `results/<...>/*.csv`, `*.json` | yes |
| figures | `results/<...>/figures/` | no |
| datasets and embeddings | `data/<dataset>/` | no |

Mirror the notebook path under `results/`, so a table traces back to the run
that produced it:

```
results/2d/blobs/intelliant/
    runs.csv          versioned
    summary.json      versioned
    figures/          not versioned
```

Figures are the one deliberate exception among publication artifacts, and the
asymmetry is the reason. A run's numbers are a few kilobytes and expensive to
reproduce; figures are derived from those numbers and cost megabytes - the
previous repository reached 425 MB that way and its history had to be
rewritten to recover. A figure can always be redrawn from the tables, but a
rerun cannot be recovered from a figure, which is also why the tables must
carry every parameter.

`.ipynb` are committed with their output - they are the showcase on GitHub,
and a notebook whose results you cannot see proves nothing - but only once the
values are settled, per the two modes above.

The rules are in `.gitignore` under `results/**` - note the `**`, since with a
plain `results/` git never descends into the directory and the negations below
it would silently do nothing.
