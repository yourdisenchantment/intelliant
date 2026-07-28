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

The library computes most of this internally - `GiantDiagnostics` carries
`n_clusters`, `top_sizes`, `median`, `max_gap`, `gap_pos` and `suspected` -
but **there is no public way to obtain one**. The type is exported in
`__all__`, the value is built by a private method, and its numbers reach the
user only by being printed under `verbose`. Until that is fixed the notebooks
compute the block themselves, which is a second implementation of one
statistic and therefore a second thing that can disagree with the first. The
local helper is a stopgap and should be deleted, not kept in parallel, once
the clusterer exposes the diagnostics it already builds.

This block carries the weight on real data, where the spatial figures are
meaningless and the size distribution is the whole picture. A giant component
is a size-distribution phenomenon and shows up nowhere else.

## The graph baseline is recorded on every run

Before any ants run, the KNN graph already has connected components, and those
components are already a clustering. Every run records what they score:

- `baseline_components` - how many the graph has;
- `baseline_ARI` - what they score against the ground truth;
- `ARI_over_baseline` - the run's score minus that.

**A result that does not clear its own baseline is not a result.** This is not
hypothetical: on 10000-point blobs three of four fork configurations returned
the graph's components untouched, identical on all five seeds to six decimal
places, and the fourth cleared the baseline by less than its own seed spread.
None of that is visible from the ARI alone, and none of the earlier
calibration measured it.

A seed spread of exactly zero is the signature to watch for. It means the
stochastic part of the pipeline changed nothing, so whatever came out was
decided by the graph.

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

Two different sources of randomness, kept apart on purpose.

**Algorithm seed.** `PheromoneExtractor` takes `random_state`; this is the
stochasticity of the ant colony itself. The set is fixed and does not change:

```
1, 10, 100, 1000, 10000
```

Five values, always these five. Fixing them repository-wide is what makes any
two runs comparable without re-deriving whether they were measured on the same
footing. A run on a different seed set is not comparable with anything already
recorded - it is a new experiment, not a data point in the old one.

Reproducibility has one hole, and it is not in the colony: the approximate
neighbour search is not bit-reproducible under a fixed seed. Calibration runs
therefore pin `knn_method="exact"` rather than letting `"auto"` decide - see
the fork table.

**Data seed.** The difficulty of the layout itself, which is a different
question and does not belong on the same axis. It varies through the named
dataset variations - seed and spread together, as in `s42_std0.3` - so that
"this parameter is better" and "this layout is easier" cannot be confused.
Synthetic data is regenerated from its seed rather than cached; `GraphBuilder`
is deterministic and takes no seed of its own.

**A single-seed number is a data point, not a result.** Report the spread
across the five, not only the mean: a parameter whose advantage is smaller
than the seed-to-seed variation has not been shown to have one. That check
has already overturned a finding here - an apparent +0.21 from `alpha` turned
out to be one lucky seed, and across five it was +0.07 with a standard
deviation of 0.083.

If five seeds make a grid too slow, cut the grid, not the seeds. A wide grid
measured on one seed answers nothing.

## Parameter grids

A sweep narrows in three passes. Skipping the first produces a confident
number from a window nobody checked.

**1. Exploration - 5 or 6 values per parameter, wide.** The question at this
stage is the *shape* of the response, not the optimum: is it flat, monotone,
or does it have an interior peak? Three points cannot tell those apart, which
is how a flat parameter gets mistaken for a lever and a lever for noise.

**2. Narrowing - three values: both edges and one representative.** Once the
shape is known, three points confirm it holds and bracket the optimum. This is
where most of the grid budget is saved, and it is only safe after step 1.

**3. Confirmation - the chosen value, full seed protocol.**

**An optimum at the edge of the window is not an optimum.** It means the
window was wrong: extend it and rerun that parameter. This is not a
hypothetical - the July calibration hit it twice, with `alpha` winning at the
bottom edge and evaporation moving to the top edge, and only the third pass
bracketed evaporation properly at 0.07 with 0.05 and 0.09 below it on both
sides.

**Watch the arithmetic.** A full factorial is `k` values to the power of `p`
parameters: at five values and four parameters that is 625 configurations,
and multiplied by the variations and the five seeds it becomes five figures of
runs. Two things make the wide grid affordable. Calibration already showed
five of six parameters to be flat, which justifies varying one parameter at a
time for exploration and reserving a factorial for the few suspected of
interacting - `tau_max` and `initial_pheromone` with `alpha` are the named
candidates. And the narrowing in step 2 collapses the survivors to three
points before any expensive combination is run.

Record the grid in the results file the same as any other parameter. A table
that shows which value won but not which values were offered cannot be read
later - "the best of three" and "the best of six" are different claims.

## What is actually being searched

Everything the calibration can move, grouped by role. A parameter that is
fixed is fixed for a stated reason, and the reason is part of the record.

### Fixed by decision

| Parameter | Value | Why |
|---|---|---|
| `metric` | `"cosine"` | Touches the whole pipeline - graph, weights, absorption - so varying it multiplies every other axis. Worth one pass early to confirm the choice, then held. |
| `evaporation_schedule` | settled first | Changes what `evaporation_rate` means. Fixed before anything else is calibrated. |
| algorithm seeds | `1, 10, 100, 1000, 10000` | Fixed repository-wide so runs stay comparable. |
| `n_ants` | `N` | Set from the dataset rather than searched. |

### Graph

| Parameter | Notes |
|---|---|
| `n_neighbors` | Held at 15 through all previous work and never probed. Bounds everything downstream. |
| `mutual` | AND vs OR symmetrisation. Changes connectivity, so it interacts with `n_neighbors`. |
| `min_connections` | Connectivity top-up after symmetrisation. |

### Colony

| Parameter | Notes |
|---|---|
| `n_iterations` | Previously 20; +0.004 up to 50, not worth 2.5x the cost. |
| `path_length` | Under `"step"` it moves the effective decay - not independent of evaporation. |
| `beta` | Edge weight exponent. Measured flat. |
| `alpha` | Pheromone exponent. Field-shaping; flat once evaporation was fixed. |
| `evaporation_rate` | The only lever found so far. Peak bracketed at 0.07. |
| `pheromone_deposit` | Measured flat. |
| `initial_pheromone` | Suspected of interacting with `alpha`. |
| `tau_min`, `tau_max` | MMAS clamps. `tau_max` suspected of interacting with `alpha`; the `tau_min` spike is the real-data failure face. |

### Heuristic switches

**There are three, not two**, and one of them is on by default:

| Switch | Default | Sub-parameters |
|---|---|---|
| `use_node_density` | off | `node_density_gamma` |
| `use_elite_ants` | off | `elite_ratio`, `elite_multiplier`, `elite_start_iteration` |
| `use_no_return` | **on** | none |

The 2x2 over density and elite gives the four sets a calibration pass reports
on: neither, density only, elite only, both. `use_no_return` has been on in
every run ever made here, which means its contribution has never been
measured - it is a third axis silently held, not an absent one. Worth one
deliberate pass rather than continued assumption.

A switch turned on drags its sub-parameters into the grid with it. Enabling
elite ants adds three, so the cost of the "both" cell is not comparable to the
cost of the "neither" cell.

### Forks

Discrete choices rather than ranges. They are searched as a set of variants,
not as an interval, and a pass either covers a fork or states that it held it.

| Fork | Options | Notes |
|---|---|---|
| `metric` | cosine, euclidean, callable | Held at cosine after one confirming pass. |
| `mutual` | AND / OR symmetrisation | Changes connectivity, so it interacts with `n_neighbors`. |
| `knn_method` | exact / approx / auto | **See below - not infrastructure.** |
| `evaporation_schedule` | step / iteration | Settled before anything else. |
| `use_no_return` | on / off | On by default and never measured. |
| `use_node_density` | on / off | With `node_density_gamma`. |
| `use_elite_ants` | on / off | With three sub-parameters. |
| threshold `method` | otsu / percentile / stat | Scan-based methods arrive in phase 2. |
| `absorb_isolated` | on / off | Whether isolated points are absorbed at all. |

**`knn_method` is a fork and it fires by itself.** Under `"auto"` the builder
switches from the exact search to pynndescent above `approx_threshold`, which
defaults to 50000 points. Two consequences, and both bite exactly where the
calibration is aimed:

- A sweep at ten thousand points runs exact and a real dataset at a hundred
  thousand runs approximate. The graph is built by a different algorithm on
  either side of that line, so a value calibrated below it has crossed a fork
  before it is applied above it.
- The approximate search is **not bit-reproducible**. pynndescent parallelises
  by default and a fixed `random_state` does not by itself guarantee an
  identical graph - the library's own docstring says so. Above the threshold,
  the reproducibility this protocol requires does not hold.

So: **set `knn_method` explicitly in every calibration run** rather than
leaving it on `"auto"`, so the fork cannot fire without being recorded. Use
`"exact"` while calibrating, and measure the fork deliberately - exact against
approx at a size where both are affordable - to find out what the
approximation costs. On synthetic that measurement is cheap, and it is the
only way the transfer to real scale is anything but an assumption.

### Threshold

| Parameter | Notes |
|---|---|
| `method` | `otsu`, `percentile`, `stat`. Scan-based methods are phase 2. |
| `percentile` | Used by `method="percentile"`. |
| `k` | Used by `method="stat"`. |
| `bins` | Otsu histogram resolution; minimum 2. |

Also available on `fit_predict`: `threshold_value` or `threshold_percentile`
directly, which is how a scan around the chosen cutoff is run without
recomputing the field.

### Clustering

| Parameter | Notes |
|---|---|
| `max_iterations` | Absorption passes. |
| `gap_ratio`, `max_gap_rank` | Giant detection. Pairwise merges slip under a ratio of 3.0. |
| `min_cluster_size` | Smallest component counting as a core. |
| `batch_size` | Centroid fallback batching. Cost only. |
| `absorb_isolated` | Whether isolated points are absorbed at all. |

### Not parameters

The noise convention in ARI is **not** a search axis. `ARI_all` leads and
`ARI_assigned` is reported beside it, both always. Choosing between them per
run would mean selecting the metric that flatters the result, which is the
one thing a fixed convention exists to prevent.

`verbose` and `warmup` are infrastructure and do not shape the result.
`knn_method` and `approx_threshold` look like infrastructure and are not - see
the fork above.

## What to display

A calibration pass produces more runs than anyone can look at, and the point
of looking is to see shape, not to audit rows.

**Four grids per pass, one per heuristic set** - neither, density only, elite
only, both - each the best run in its set by `ARI_all`. That is a constant
four regardless of how large the grid was, which is what keeps the output
readable as the sweep grows.

Print the full results table as well; it is machine-readable and the agent
reads it. The four grids are for the eye, and the eye needs a fixed number of
things to compare.

If a set is empty because the switch was not varied in that pass, say so
rather than silently showing three.

## Scale, and what transfers

Synthetic and real data are searched under different budgets, and that
asymmetry is the point of doing synthetic first.

**On synthetic, cost is not the constraint.** Data is generated, runs are
seconds, and there is no reason to be frugal: keep the exploration pass wide,
run a full factorial wherever interaction is suspected rather than assuming
independence, and cover the variations exhaustively. The narrowing in the
previous section exists to save budget; where there is no budget to save, it
is a readability device rather than a necessity.

**Use realistic sizes.** A thousand points is a debugging size. Calibrate at
ten thousand or more, because several parameters are not scale-free: `n_ants`
is set from `N`, `path_length` interacts with the diameter of the graph, and
total deposit per iteration scales as `n_ants` times `path_length`, which
governs how quickly edges saturate at `tau_max`. A value tuned at N=1000 and
applied at N=100000 is an extrapolation, not a result.

**On real data the grid is confirmation, not search.** Take the values
synthetic produced, verify they hold, and vary only what is shown not to
transfer. A real-data sweep at synthetic width is unaffordable and, worse, it
would answer questions that were already answered more cheaply.

### Two purposes, two designs

Synthetic data is used for two different things, and a dataset built for one
answers the other badly.

**Calibration** asks what settings solve a given geometry. Few datasets, many
parameter values, the full seed set, realistic size. The output is a
configuration with a window around it.

**Coverage** asks how wide the range of solvable geometries is. Many
geometries, each calibrated in turn. The output is a catalogue: for every
shape, the configuration that handles it and the grid that was searched to
find it.

Other clusterers appear in neither. Comparison is its own phase, run once the
configurations exist, and mixing it into calibration answers a question nobody
asked yet while making the runs more expensive.

### The claim is existence, not a single setting

The algorithm is not one configuration that copes with everything, and the
protocol should not be written as though it were. The claim is that **for any
geometry there exists a configuration that solves it** - which is a different
and weaker statement, and an honest one. Flexibility and its cost are the same
property: the range is wide because the parameters move, and the parameters
have to move because the range is wide.

Stated that way, the claim is testable but easy to fake. Search hard enough
and any sufficiently flexible method fits anything. Three things separate a
result from a fit, and all three are cheap:

**Record the grid, not only the winner.** A configuration that won out of six
values and one that won out of six hundred are different claims. Without the
grid in the results file, they read identically a year later.

**Confirm across the seed set.** A configuration found on one seed and holding
on five is a finding; found on one and reported from one is a coincidence.
That check has already overturned a result here once.

**Look for the rule.** This is where the actual contribution sits. A table of
per-geometry winners is overfitting with extra steps; a statement of the form
"when clusters touch, the cutoff has to come down" or "varying density is what
the density heuristic is for" is a result, because it predicts rather than
records. Every calibration pass should ask what the winning direction has in
common with the shape that produced it, and the answer belongs in ROADMAP
under established findings.

The cost side of the flexibility deserves the same honesty. Requiring the user
to calibrate is a real burden, and the answers to it are the adaptive
threshold work in phase 2 and whatever rule the calibration yields - not
silence about it.

### What actually transfers

Being clear about this is what makes the synthetic phase worth its time.

**Scale transfers, with care.** The N-dependent parameters above are the ones
to re-check, and raising N on synthetic is what makes that check possible
before real data is involved.

**Dimensionality does not transfer, and 2D and 3D cannot fix it.** The reason
kNN graphs are used at all is that distances concentrate in high dimensions -
and at two or three dimensions there is no concentration to observe. Whatever
2D says about the shape of the pheromone field, it says under conditions the
real case does not share. This is already visible: on synthetic the field's
middle plateau dominates and Otsu lands mid-plateau, while on real data a
`tau_min` spike covers around 97% of edges and drags the same method somewhere
else entirely. Two different failure faces, and only one of them is reachable
from a plane.

**Cluster geometry does not transfer either.** Gaussian blobs are convex,
isotropic and equally dense. Embedding clusters are none of those. The
non-convex datasets in phase 1 exist for exactly this reason and are not
decoration.

**Neither does the metric, and this one inverts.** Cosine discards vector
length and keeps direction, so it wins where the length is nuisance -
embeddings, where the norm tracks document length rather than meaning - and
loses where position is the meaning. On 2D blobs it slices each cluster into
angular wedges; on 512-dimensional embeddings it is the right choice.
Calibrating the metric on synthetic 2D therefore produces the opposite of the
right answer for real data. It is settled separately on each, and the rule -
cosine when direction carries the signal, euclidean when position does -
predicts which, so a run confirms it rather than searching for it. Measured;
see ROADMAP.

That makes the metric the sharpest example of why the transfer question is
asked at all. It determines the graph, every other parameter is measured on
top of the graph, and it is exactly the parameter that does not carry over.

### Measure one run before launching a sweep

Runtime is already a recorded column; use it. Time a single run at the target
size, multiply by configurations times variations times seeds, and decide with
the number in front of you. This is a thirty-second check that prevents
starting a forty-hour sweep by accident, and it costs nothing to make a habit.

## What makes a run reportable

- It ran from a clean regeneration of its data, not from a mutated kernel.
- Its `output.txt` is next to the notebook and covers the whole run.
- Its parameters appear in the results file, not only in the notebook.
- It used the standard seed set, and the grid it came from is recorded.

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
    blobs_intelliant.ipynb      generated; carries output once settled
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

Regenerate with `--update`:

```bash
uv run jupytext --update --to ipynb <notebook>.py
```

Without it jupytext rewrites every cell id on conversion, so a notebook that
did not change produces a diff that says it did - and once that happens twice
nobody reads the diff again.

**While searching.** Parameters are not settled. Print machine-readable
tables, write `runs.csv`, wrap the run in `utils.Tee` so it lands in
`output.txt` - that file is what the agent works from.

Draw whatever you need to look at. Judging a sweep without seeing it is
guesswork, and a plot in a cell costs nothing. What changes in this phase is
that **nothing is saved**: no figure written to `results/`, and no executed
`.ipynb` committed. The `.py` is what changes between iterations, and a rerun
of a sweep is not a revision worth keeping. The only artifacts that outlive
the iteration are the calibration tables.

**Once the values are settled.** The run becomes the record. Execute the
notebook a final time, commit the `.ipynb` with its output, and write the full
results to `results/`: tables as CSV/JSON, and now the figures, which is the
one point at which they are worth producing.

A document on how those results are then read - which comparisons are
meaningful, how to present them - belongs with the article work, not here. It
is deliberately not written yet.

## Figures

Drawn whenever they are worth looking at, **saved** only once the values are
settled - and then for **every** variant, not only the ones that worked. A
variant that failed is the more interesting picture, and it is the one nobody
thinks to save.

Everything below describes the saved figure: the one that goes into `results/`
and possibly into an article. A throwaway plot in a cell during a sweep is not
held to it.

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
