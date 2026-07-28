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

**One finding needs re-reading.** All of the above was measured before the
`evaporation_schedule` semantics came to light. Under `"step"` the field
decays once per ant step, so changing `path_length` silently changes the
effective per-iteration decay - `1 - (1 - rate)**path_length`, which is 0.516
at the base configuration rather than 0.07. The conclusion "path_length 10 is
equivalent to 15" was therefore measured across two different decay levels and
came out flat anyway. That is weak evidence the exact level does not matter
much in that range, not evidence the two parameters are independent.

## Phase 1 - synthetic calibration -> `1.0.0a1`

**Settle `evaporation_schedule` first.** It changes what `evaporation_rate`
means, so any value calibrated before it is fixed is valid only for one
schedule at one `path_length`. Calibrating anything else first means
recalibrating it afterwards.

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
