# Roadmap

What remains before `1.0.0`, and what each milestone means. The protocol for
the runs themselves is in [EXPERIMENTS.md](EXPERIMENTS.md).

Versions track milestones, not commits. Three releases remain:

| Version | Reached when |
|---|---|
| `1.0.0a1` | synthetic and real-dataset calibration complete |
| `1.0.0b1` | comparison against other clusterers complete |
| `1.0.0` | article published, feedback incorporated |

Everything below `1.0.0` may break the API. `1.0.0` is the promise that it
will not.

## Already established

Carried over from calibration done in July 2026, on the previous
implementation. Conclusions that survive the rebuild; the run-by-run record
stays in working notes.

**A base configuration exists.** Three tuning iterations over a 972-run
factorial converged on `n_neighbors=15`, cosine, `n_ants=N`,
`n_iterations=20`, `path_length=10`, `beta=2.0`, `alpha=1.0`,
`evaporation_rate=0.07`, `pheromone_deposit=1.0`, `initial_pheromone=1.0`,
`tau_min=0.01`, `tau_max=10.0`, Otsu. Mean ARI 0.774 across four 2D
variations, floor 0.719. These are the values in the README example.

**Five of six tuned parameters were flat.** Only evaporation moved the result,
and its peak was bracketed at 0.07. The base is a plateau around 0.77, which
means further parameter tuning is not where the remaining quality is.

**The remaining quality is in the threshold, not the parameters.** Ward gaps
of 0.11-0.24 persisted at the best configuration. On `s42_std0.3` Otsu lands
at p70.7 for ARI 0.834 while p60 gives 0.9465 - the cutoff overshoots and no
parameter setting recovers it.

**The graph bounds everything downstream.** Even the easiest variation has
`n_components=6`: one blob pair is already merged in the cosine KNN graph, and
no threshold splits an already-connected component. `n_neighbors` was held at
15 throughout and never probed.

**The pheromone field has a universal shape** - a "fence with whiskers",
holding up to 3.3M real nodes - with two failure faces. On synthetic data a
dominant middle plateau makes Otsu land mid-plateau. On real data a `tau_min`
spike covering ~97% of edges drags all-data Otsu down, while Otsu over active
edges only lands near p97 and shatters the giant component.

**All of it was measured at a thousand points per dataset.** The experiment
protocol now calls that a debugging size, since `n_ants` is set from `N` and
the total deposit per iteration scales with it. The values above are not
wrong, but they were established under conditions no real dataset shares, and
re-confirmation at a realistic size is part of phase 1 rather than a formality.

**The metric has to match what carries the meaning.** Measured 2026-07-28 on
the first notebook and then isolated across four conditions. Same pipeline,
same parameters; only the data and the metric change:

| Data | euclidean | cosine |
|---|---|---|
| 2D blobs, as generated | **0.731** (5 clusters) | 0.695 (8) |
| 2D blobs, L2-normalised onto the unit circle | **0.791** (13) | 0.695 (8) |
| 256D on the unit sphere, direction is the signal | 1.000 (7) | 1.000 (7) |
| ...the same, with per-point magnitude noise x[0.2, 5] | 0.965 (10) | **1.000** (7) |

Cosine discards vector length and keeps direction, so which metric wins
depends entirely on which of the two carries the signal.

**On embeddings the length is nuisance** - direction encodes semantics while
the norm tracks document length, token counts, tokenizer artifacts - so
discarding it is exactly right. Rows three and four isolate this: on the unit
sphere the two metrics are monotonically equivalent and give identical
results, but add a spread of magnitudes and euclidean drops to 0.965 while
cosine holds at 1.000. This is why cosine outperformed euclidean on the
earlier text-embedding work.

**On spatial blobs the position is the meaning** - a point is defined by both
its angle and its distance from the origin - so cosine throws away half the
information and identifies everything lying on one ray. The blobs sit off the
origin, points inside one span a range of angles, and their nearest neighbours
by cosine are neighbours *by angle*: the graph becomes angular wedges and each
blob is sliced into diagonal stripes.

**The rule, which predicts rather than records:** cosine when direction
carries the meaning and magnitude is nuisance; euclidean when the meaning is
position. They coincide on L2-normalised data.

**The artifact scales with sampling density.** At N=4000 the gap is 0.731
against 0.695; at N=10000 it is 0.847 against 0.421. Denser sampling narrows
the angular sector that the fifteen nearest neighbours occupy, so the wedges
get thinner and more numerous. A metric choice validated at one size can fail
at another.

Two consequences for the earlier work. The 0.77 plateau, and with it "five of
six parameters are flat", may be properties of a graph that was wrong for the
data rather than of the algorithm - consistent with the note above that the
graph bounds everything downstream. And the already-merged blob pair now has a
candidate explanation.

**The metric does not transfer, and calibrating it on synthetic 2D would give
the opposite of the right answer for real data.** That is sharper than the
existing "dimensionality does not transfer": the metric determines the graph
that every other parameter is measured on top of. Phase 1 calibrates under
euclidean and carries none of that choice to the text datasets, where it is
settled again - the rule above says what the answer will be, and the run has
to confirm it rather than assume it.

**Heuristics: nothing demonstrated on a good graph, damage on a bad one.**
Same notebook, four heuristic sets across five seeds, 10000 points.

Under euclidean: none 0.778, density 0.794, elite 0.752, both 0.764, with a
seed spread of 0.05 to 0.06 within each. Every difference between the sets is
smaller than the spread inside them, so on this dataset no heuristic has been
shown to do anything - which is what the July work concluded from a different
direction.

Under cosine they are actively harmful, and the worse the metric fits the more
damage they do: none 0.485, elite 0.311, density 0.158, both 0.145. Density
takes the partition from 25 clusters to 102. On a graph built by angle the
density heuristic steers ants toward high-degree vertices, which means further
into the wedges - it amplifies the error rather than compensating for it.

Worth carrying forward: a heuristic that looks inert on good data is not
therefore harmless. It may be what decides how badly a bad graph fails. One
variation, one dataset - indicative, not established.

`use_no_return` is on by default, was on in every run ever made here, and has
never been measured. It is a third heuristic axis held silently rather than an
absent one.

**One finding needs re-reading.** All of the above was measured before the
`evaporation_schedule` semantics came to light. Under `"step"` the field
decays once per ant step, so changing `path_length` silently changes the
effective per-iteration decay - `1 - (1 - rate)**path_length`, which is 0.516
at the base configuration rather than 0.07. The conclusion "path_length 10 is
equivalent to 15" was therefore measured across two different decay levels and
came out flat anyway. That is weak evidence the exact level does not matter
much in that range, not evidence the two parameters are independent.

## Phase 1 - synthetic calibration -> `1.0.0a1`

**Order matters here, and it is not the order things were discovered in.**
The metric comes first because it determines the graph, and every other
parameter is measured on top of whatever graph it produces. The evaporation
schedule comes second because it changes what `evaporation_rate` means - any
value calibrated before it is fixed is valid only for one schedule at one
`path_length`. Anything calibrated ahead of these two gets recalibrated.

- [ ] **`metric` on spatial data: euclidean versus cosine.** Comes first -
      it changes the graph, and every other parameter is measured on top of
      the graph. Indicative at one seed already; needs the full protocol.
- [ ] `evaporation_schedule`: `"step"` versus `"iteration"`, base config
      otherwise held, full seed protocol. Settled by measurement.
- [ ] Re-confirm the base configuration under the winning schedule.
- [ ] Probe `n_neighbors`, held at 15 through all previous work and the one
      parameter shown to bound the result.
- [ ] `anisotropic_blobs`, `moons`, `circles` - non-convex geometries, which
      is where `alpha` as a field-shaping knob gets re-judged.
- [ ] `blobs_grid`: universality sweep across k, cluster size and spread.
- [ ] `varied_density_blobs`: the target case for the density heuristic.
- [ ] 3D: Swiss roll, spheres.

## Phase 2 - threshold work

Motivated by the two failure faces above rather than by dissatisfaction with
the parameters.

- [ ] Quantify what Otsu leaves on the table per variation, using
      `scan_thresholds`.
- [ ] `find_threshold` option to exclude clamp spikes - the real-data fix.
- [ ] Scan-based `find_threshold` (`method="scan"`): pick the cutoff by giant
      collapse or `n_cores` plateau. Addresses both faces.
- [ ] Graph-statistics diagnostic - components, giant share, islands - for
      real-data connectivity.

## Phase 3 - real datasets -> `1.0.0a1`

- [ ] AG_NEWS with `embeddinggemma-300m`, Matryoshka dimensions.
- [ ] Further text datasets.
- [ ] Checkpointing for intermediate results at that scale.

## Phase 4 - comparison -> `1.0.0b1`

- [ ] HDBSCAN on the same datasets and seeds.
- [ ] Louvain/Leiden on the same datasets and seeds.
- [ ] Cross-dataset summary table.

`ARI_all` leads these tables. The abstention rates will differ, which is the
case it exists for.

## Phase 5 - publication -> `1.0.0`

- [ ] Habr article, reviewed by ML-adjacent channel admins.
- [ ] Scientific advisor, then a VAK-level paper and an arXiv preprint.
- [ ] `docs/`, English default with a Russian mirror. Must carry the
      human-in-the-loop contract and the calibration findings.
- [ ] Cross-check docstrings against the final code.

The paper text is written fresh rather than adapted from the article -
self-copied text is flagged by plagiarism checks. Check the target journal's
preprint policy before the arXiv submission; it is usually permissive.

## Deferred

- Giant-component handling, phases 1-2. Needs its own threshold calibration,
  so it follows phase 2 rather than preceding it.
- Graph factorial over `n_neighbors` x `mutual`.
