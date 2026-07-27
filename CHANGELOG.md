# Changelog

Notable changes per release. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[PEP 440](https://peps.python.org/pep-0440/).

Versions here are milestone-driven rather than derived from commit types, so
they are passed explicitly at release time. See CONTRIBUTING.md.

## [Unreleased]

## [0.2.0a1] - 2026-07-27

First release from the rebuilt repository. **Upgrading from `0.1.0a2` breaks
existing code** - see below before installing.

### Changed - breaking

- **Constructors are keyword-only.** Positional arguments are refused. With
  twenty-odd parameters a positional call was unreadable, and this takes
  declaration order out of the public contract.
- **Parameters that shape the result no longer have defaults** and must be
  passed: `GraphBuilder` needs `n_neighbors`, `metric`, `mutual`;
  `PheromoneExtractor` needs `n_iterations`, `path_length`, `beta`, `alpha`,
  `evaporation_rate`, `evaporation_schedule`, `pheromone_deposit`,
  `initial_pheromone`, `tau_min`, `tau_max`; `CoreClusterer` needs
  `max_iterations`, `gap_ratio`, `max_gap_rank`.

  Calibration is still in progress, so a default was a value nobody had
  justified, applied silently - and three of the former defaults were wrong.
  `evaporation_rate` defaulted to 0.1, which is exactly the level measurement
  showed to fragment clusters.

  Infrastructure parameters (`verbose`, `random_state`, `warmup`,
  `knn_method`, `approx_threshold`, the `use_*` switches) keep their defaults.

### Added

- **`evaporation_schedule`**, required, `"step"` or `"iteration"`. The
  pheromone field had always decayed once per ant step rather than once per
  iteration, which is neither Ant System nor Ant Colony System behaviour and
  was never a decision anyone made. The effective per-iteration decay under
  `"step"` is `1 - (1 - rate) ** path_length` - at `rate=0.07` and
  `path_length=10` that is 0.516, not 0.07, so **no value from the ACO
  literature transfers**. `"iteration"` is the classical schedule. Which is
  better here is being settled by measurement; `"step"` preserves existing
  behaviour.
- **A warning when deposits land on missing edges.** An ant stepping `i -> j`
  deposits on both directions; on an asymmetric graph the reverse half was
  silently discarded. The count is now reported.
- `metric` accepts a callable, not only a name.

### Fixed

- `find_threshold(method="otsu", bins=1)` passed validation and then crashed
  inside numpy. Otsu needs at least two bins; the minimum is now 2.
- `find_threshold(method="percentile", percentile=True)` accepted the boolean
  and read it as the 1st percentile. The parameter now goes through the same
  validation as every other float.
- `threshold_percentile` raised `IndexError` on empty input instead of the
  project's `ValueError`.
- `absorb_centroid` built an index table with `np.empty` and filled it
  partially - safe only while `cores_` is untouched, which the staged design
  explicitly invites editing.
- The giant diagnostic after centroid absorption counted a different set of
  points than the method itself treated as resolved.
- `random_state` was never validated in either class.

### Internal

- Type annotations required on every signature (ruff `ANN`); tests exempt,
  since pyright deliberately does not check them.
- 347 tests, 99% branch coverage, verified on a clean clone rather than in a
  working folder.
- CI splits by branch: `dev` runs the verify chain, `main` additionally runs
  the release gate - scale test, dependency hygiene, version consistency, and
  a wheel build with an install smoke test.

## [0.1.0a2] - 2026-07-11

Published from the previous repository. Three-class architecture, 306 tests,
`py.typed` shipped. No docstrings.

## [0.1.0a1]

First published alpha.

[Unreleased]: https://github.com/yourdisenchantment/intelliant/compare/v0.2.0a1...dev
[0.2.0a1]: https://github.com/yourdisenchantment/intelliant/releases/tag/v0.2.0a1
[0.1.0a2]: https://pypi.org/project/intelliant/0.1.0a2/
[0.1.0a1]: https://pypi.org/project/intelliant/0.1.0a1/
