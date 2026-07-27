# Intelliant

ACO-based clustering (`0.1.0a2`, Python 3.14, scipy CSR + numba `@njit`).
Stage history: `tmp/OVERVIEW.md`. Long-term ideas: `RESEARCH_NOTES.md`.

## Start here

- Active tasks -> `tmp/TASK.md` (active items only, status `[ ]`/`[~]`/`[x]`/`[!]`; archive in `ROADMAP.md`).
- What's done -> `tmp/OVERVIEW.md`. Last verdict -> `tmp/REVIEW.md`.
- Architecture/commands/workflow -> this file.

`tmp/TASK.md` and `tmp/REVIEW.md` are local working artifacts, gitignored. They are absent from git history by design.

## Commands

```bash
uv sync --all-groups --all-extras          # installs dev (ruff, pyright, pytest, scipy-stubs, ...), notebooks, embeddings (torch auto-backend)
uv run ruff check src/                     # lint
uv run pyright src/intelliant              # typecheck (0 errors = OK)
uv run pytest tests/                       # all tests
uv run pytest tests/test_<name>.py         # one file
uv run pytest tests/test_<name>.py::test_func  # one test
uv run pytest tests/ --cov                 # tests + coverage (fail_under = 95)
uv run pre-commit run --all-files          # file-content hooks (ruff, whitespace, toml/yaml)
uv run pre-commit run --hook-stage pre-push --all-files  # + pyright and pytest
uv run cz check -m "feat: msg"             # validate a commit message
uv run cz commit                           # interactive conventional commit
```

Pre-report order: `ruff check src/` -> `pyright src/intelliant` -> `pytest tests/`. All three must pass.

Enforcement (not discipline): `ruff` + `cz check` run per commit; `pyright` and
`pytest --cov` run on **push** (`pre-push` hook - slow per commit, and a hook
people skip is worse than a slow one). `filterwarnings = ["error"]` makes the
zero-warning rule a failure, `--strict-markers` makes a typo'd marker a failure.
Coverage lives in the hook rather than in `addopts` so running one test file is
not gated by `fail_under`. Numba `@njit` bodies are excluded from coverage - the
tracer cannot see compiled code, so counting them understates the real number.

### Release checklist (not automated - run by hand before a tag)

```bash
uv run pytest tests/ -m slow               # the 50k scale test, excluded by default
uv run deptry .                            # dependency hygiene
```

`bandit` and `vulture` are installed but deliberately unwired: low signal on a
numeric library. Run them ad hoc or drop them.

## Commits

Conventional Commits, validated by the `cz check` commit-msg hook. The hook
checks the FORM, not the information - these rules cover the rest:

- **A repeated subject line means the commit should have been an `--amend` or a
  squash.** The history carries five identical
  `feat: add simple_blobs intelliant etalon notebook` commits; nothing can be
  reconstructed from that. Iterating on the same artifact is one commit.
- **Put the "why" in the commit body.** The subject says what changed; the body
  says what was rejected and on what grounds. For a multi-year project the
  rationale attached to the diff is the asset, and `tmp/` is gitignored.
- Scope a commit to one concern - source, tests, notebooks and config move
  separately.
- **Never sign a commit with a model.** No `Co-Authored-By: <model>` trailer,
  no attribution of any kind. Several different models have worked on this
  repository; naming one of them misstates who produced the work, and the
  history is a record of decisions, not of tooling.

### Who may commit

Commit messages are DRAFTED INTO `tmp/commits/`, not straight into git. The
maintainer reads the draft and then either approves the commit and push or
performs it personally.

The only exception is the strong model driving a session, which may commit and
push on its own judgement so that routine work does not need per-command
approval. Every other agent operates under manual control or with explicit
permission for each commit - the point is that nothing reaches a published
branch without the maintainer having read it.

## Task classification (which model does what)

The project is solo and time is scarce, so work is split between a strong
model and a cheaper one. The dividing line is NOT task size:

> A task goes to the cheaper model when success is checkable by running a
> command, AND the spec leaves no design decisions open.

Everything else - anything where a wrong choice is expensive and CI would not
catch it - stays with the strong model.

| Cheaper model | Strong model |
|---|---|
| tests from an enumerated list of cases | producing that list |
| filling in docstrings from placed templates | the human-in-the-loop contract, conceptual docs |
| mechanical refactors from an explicit list (renames, parameter removal) | deciding what belongs on the list |
| notebook boilerplate, formatting, lint fixes | calibration protocol, algorithm mechanisms, threshold methods, API shape |
| - | reviewing what the cheaper model produced |

Two consequences worth stating, because they are easy to get backwards:

- **The cheaper model needs a STRICTER spec, not a looser one.** Part of the
  strong model's work shifts from writing code to writing specs detailed
  enough that the code becomes mechanical. `tmp/GIANT_HANDLING_TASK.md` is
  written in that format on purpose.
- **The safety net is the verify chain, not judgement.** Delegation is only
  cheap because `pre-push` runs pyright and pytest with coverage
  independently of what any agent reports about its own work. Never take
  "all green" from an agent as evidence; the hook is the evidence.

Neither model may bump the version or delete files (see Constraints).

`requires-python = ">=3.14"`; the local toolchain runs Python 3.14 (`.python-version`).

## Architecture

Package `src/intelliant/`, built with hatchling. Public API (`from intelliant import *`):

| Class/Function | Module | Input -> Output |
|---|---|---|
| `GraphBuilder` | `.graph_builder` | embeddings -> CSR graph (KNN, exact/pynndescent) |
| `PheromoneExtractor` | `.pheromone_extractor` | CSR graph -> pheromone field (ACO/MMAS) |
| `CoreClusterer` | `.core_clusterer` | pheromone field + threshold -> labels + noise absorption |
| `find_threshold`, `scan_thresholds` | `.threshold` | pheromones -> cutoff threshold (Otsu and others) |

No unified pipeline: three classes called sequentially, each independently.

## Tests

- `tests/` — pytest, 307 tests (306 default + 1 slow). Config in `pyproject.toml` `[tool.pytest.ini_options]`.
- Coverage: constructor validation, edge cases, dtype, degenerate end-to-end, warnings, error message coverage (all 52 ValueError sites), tie-breaking determinism, threshold integration, property-based invariants (hypothesis), scale smoke (50k, slow marker).
- LSP diagnostics in `tests/` are expected: tests deliberately pass invalid types to check validation. Pyright `include` is `src/intelliant` only, not `tests/`.
- The default run must stay at ZERO pytest warnings; every expected warning goes through `pytest.warns`.
- Slow tests excluded by default (`addopts = "-m 'not slow'"`). Run with `uv run pytest tests/ -m slow`.

## Code style (repo-specific, not defaults)

- Docstrings and error messages in English, google-style.
- `ValueError`: `"<name> must be <range>, got <value>"`.
- Results are attributes with trailing underscore (sklearn convention): `graph_`, `pheromone_matrix_`, `labels_`.
- Parameter validation via shared helpers in `src/intelliant/_validation.py`: `_check_int` (accepts `numbers.Integral`, rejects bool), `_check_float` (rejects bool/non-numeric with ValueError), `_check_bool` (bool / `np.bool_` only, normalized to plain bool). All public params go through them.
- The staged pipeline is a feature (human-in-the-loop): intermediate state (`graph_`, `pheromone_matrix_`, `cores_`, `labels_pheromone_`, external `labels=`) is public API for user editing between stages. Validation stays per-stage; do not enforce cross-stage provenance or merge stages.
- Source files: Python 3.14, ASCII only, no Cyrillic. ruff: line-length 120, double quotes. pyright: standard mode.
- Commits: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, ...). commitizen configured; `version_files` auto-updates `pyproject.toml` and `src/intelliant/__init__.py`. Version bump only on explicit command. Commit-msg hook `cz check` rejects non-conventional messages.

## Constraints

- Never delete files — list paths and commands, the user deletes themselves.
- Do not touch `.env` or files with secrets.
- Do not bump package version without an explicit command.
- Coder edits only `src/intelliant/` unless told otherwise.

## Notebooks workflow (user conventions, 2026-07-11)

**Not in this repository yet.** `notebooks/` and its `utils/` helpers live
outside it for now - the repository holds the library alone until the first
release. The conventions below are the contract for when that work lands, so
they are kept rather than rediscovered.

Division of labor: the agent writes jupytext `.py` scripts and converts
them to `.ipynb`; the USER runs the notebooks. Runtime output is captured
to `output.txt` (via `utils/tee.py`) NEXT TO the notebook (gitignored) -
the agent analyzes `output.txt`, the user analyzes the plots. Do not ask
the user to paste notebook output. Metrics/results go to
`results/<...>/` as CSV/JSON (may be duplicated next to the notebook).
`.ipynb` are ALWAYS committed WITH executed output (showcase on GitHub).

Folder layout (agreed 2026-07-11): dataset-first with a clusterer
subfolder - `notebooks/<group>/<dataset>/<clusterer>/`, where group =
`2d` / `3d` / `text` (uniform depth for synthetic and real data alike).
Each clusterer folder holds its own notebook pair
(`<dataset>_<clusterer>.ipynb` + jupytext `.py` - unique filenames
repo-wide), its `output.txt` and its `checkpoints/`. A `comparison/`
subfolder per dataset holds the cross-clusterer summary. Synthetic data
is regenerated per notebook from a fixed seed (deterministic, cheap -
no caching). Real datasets/embeddings are prepared once and cached in
root `data/<dataset>/` (gitignored), then loaded by every clusterer
notebook - kernels do not share memory, reuse happens via disk.

Structure rules:
- Imports split into SEPARATE cells, in this order: (1) third-party
  libraries, (2) sys.path setup for `utils/`/scripts, (3) local imports,
  (4) path/plot configuration. This avoids import warnings.
- Every logical section starts with an `##` heading in its own markdown
  cell, followed by a separate explanation cell; individual code cells
  may get an optional note.
- Execution is sectioned so intermediate pipeline states can be
  inspected between stages (mirrors the library's human-in-the-loop
  design - showcase it).
- Tables are printed FULL - either aligned manual print or polars
  with `pl.Config(tbl_rows=-1, tbl_cols=-1)`; never a bare truncated
  `print(df)` that hides rows/columns behind `...`.
- output.txt carries debug-level run info; results/ carries ALL data
  (full CSV/JSON + figures).

Purpose taxonomy (keep in mind when designing runs):
- Synthetic tests: universality demo, base-parameter calibration,
  metrics for articles.
- Real-dataset tests: universality + strength demo, recommended-parameter
  calibration, metrics for articles.
- Same datasets on other algorithms (HDBSCAN, Louvain/Leiden): capability
  comparison.
- Collect results machine-readable (CSV/JSON per run, multi-seed) so
  cross-dataset tables for articles assemble without reruns.

## Workflow cycle (`tmp/TASK.md` <-> `tmp/REVIEW.md`)

- `tmp/TASK.md` holds **only active items** (one stage). Archive goes to `ROADMAP.md`.
- Coder takes **one item at a time**, writes a report under it, marks `[~]`. Final status (`[x]` OK / `[!]` NEEDS_WORK) is set by reviewer.
- Reviewer writes a section "Проверка правки <X>" in `tmp/REVIEW.md` per item.
- After all items: final summary verdict in `tmp/REVIEW.md`.
