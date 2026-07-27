# Intelliant

ACO-based clustering (`0.2.0a1`, Python 3.14, scipy CSR + numba `@njit`).

## Read CONTRIBUTING.md first

**[CONTRIBUTING.md](CONTRIBUTING.md) is the binding document, and it applies
to agents exactly as written.** It carries the whole development process:
environment setup, the verify chain and what runs at which stage, branch
rules, commit rules, pull requests, releases, and the section on what an agent
may and may not do on its own. None of that is repeated here - a rule stated
in two places drifts, and this repository has already shipped two counters
that disagreed with reality because of it.

This file is the other half: what the code IS, so that a rule in CONTRIBUTING
can be applied to it. Architecture, test layout, the style choices a linter
cannot express, and the maintainer's own working setup.

Working notes live under `tmp/`, which is gitignored: task specs, review
verdicts, and commit drafts. They are absent from git history by design, so
do not link to them from anything that ships.

## Non-negotiable

Restated from CONTRIBUTING.md because a miss here is expensive and often
cannot be undone. Everything else, read there.

- **Never delete a file.** List the paths and the command; the maintainer runs
  it.
- **Never bump the version, create a tag, or push one.**
- **Never use `--no-verify`.** A failing hook is reporting something.
- **Never report a check as passing without its output.** "All green" is a
  claim, not evidence.
- **Never add an attribution trailer.** The commit-msg hook rejects every
  `Co-Authored-By:` and `Signed-off-by:`.
- **Do not touch `.env` or any file holding secrets.**
- **Do not add files that pin the repository to one assistant.** `CLAUDE.md`,
  `.cursorrules`, `.mcp.json` and their kin are gitignored on purpose. This
  file is the exception, because every agent reads it.
- Coder edits only `src/intelliant/` unless told otherwise.

## Standing orders

The maintainer runs the research. The agent runs the process, and does not
ask permission for work that can be undone. The line is reversibility, not
importance.

### Do without asking

Everything here lands on `dev`, where a mistake costs one more commit.

- Run the verify chain after touching `src/` or `tests/`, and report it with
  its output. Never "all green" on its own.
- Commit. One concern per commit, source and tests separately, the "why" in
  the body. Draft the message yourself; do not ask for wording.
- Push `dev`. Then watch CI and report the result.
- Fix a mechanical CI failure and push again - a bad action pin, a formatting
  slip, a stale count. Report what broke and why afterwards, not before.
- Add an entry to `[Unreleased]` in CHANGELOG for anything a user would
  notice: a changed API, a new parameter, a revised recommended value, a fixed
  behaviour. Not for internal work.
- Say when a finding needs a decision instead of deciding it.

### Hand over as commands, do not run

These are irreversible, outward-facing, or both. Print the exact command and
stop.

- `cz bump`, `git tag`, and the push of a `v*` tag. The tag push publishes to
  PyPI and burns the version number forever.
- Deleting any file.
- Changing repository settings, rulesets, or anything on GitHub outside a
  branch push.
- Posting anything public in the maintainer's name: issue comments, PR
  comments, releases notes beyond what the workflow generates.

### The two loops

**Calibration.** The maintainer runs a notebook and reads the plots; the agent
reads `output.txt`. A finding either changes the library or it does not. If it
does: change, test, verify, commit, push. If it does not: commit the notebook
with its executed output and the CSV/JSON under `results/`, push. Either way,
`[Unreleased]` gets the entry if a user would notice.

**Release.** The agent prepares everything and stops at the tag: `[Unreleased]`
complete, clean-clone verify, release-gate commands run locally, all of it
reported with output. Then it hands over the bump-and-tag block from
CONTRIBUTING.md. Once the tag exists the agent merges `dev` into `main`,
pushes both branches, waits for the release gate on `main` to go green, and
hands back the single command that publishes. After the run it installs from
PyPI into a clean environment and executes the README example against what
actually downloaded.

This is the low-touch default: roughly four commands per release, and none
between releases. If the maintainer would rather read every commit message
before it lands, the drafting rule in CONTRIBUTING.md replaces the "commit"
line above - one instruction flips it, and nothing else in this section
changes.

## When something breaks

Every entry below actually happened while publishing `0.2.0a1`. Fix it and
report what you did afterwards - none of these need a decision, and asking
about them is the interruption this section exists to prevent.

**pre-commit refuses: "Your pre-commit configuration is unstaged."**
It reads its config from the index, not the working tree. Commit
`.pre-commit-config.yaml` on its own first, then the rest.

**A push is rejected but the ref looks fine.**
Read the whole output, not the tail. A failed hook prints above the push error
and is easy to mistake for a remote rejection.

**A hook blocks a legitimate push.**
Check which stage it ran at. `no-commit-to-branch` inspects the CURRENT branch
rather than the ref being pushed - it is now restricted to `pre-commit` for
exactly that reason, so do not widen it again. Never reach for `--no-verify`;
push both refs from `dev` instead.

**CI fails on `uv sync --frozen` right after a version bump.**
`uv.lock` records this project's own version. Re-lock and fold it into the
bump commit - see the `--files-only` recipe in CONTRIBUTING.md. Doing it in a
later commit leaves the tag pointing at a broken tree.

**The tag is not on the last commit.**
`git commit --amend` after a bump builds a new commit and strands the tag on
the old one. Move the tag, keeping it annotated. Only possible before the
push: the ruleset refuses to move or delete a pushed `v*` tag.

**A workflow fails in seconds without running a single check.**
An action pin does not resolve. Verify every `uses:` with
`git ls-remote --tags`; a floating major tag may not exist even when the
release does, which is what `setup-uv@v9` turned out to be.

**Tests pass locally and fail on a clean clone.**
Something is untracked. This is why a release is verified in a fresh clone
with `--frozen` rather than in the working folder.

**`cz bump` hangs.**
Missing `--yes`; it is waiting on "is this the first tag?" forever.

**Dependabot proposes a downgrade.**
A dependency has no lower bound, so the resolver has no floor. Fix the bound
in `[project.dependencies]` - the pull request is the symptom.

**Coverage looks implausibly low.**
numba `@njit` bodies are invisible to the tracer and already excluded. Do not
lower `fail_under` to make a number agree.

### When to interrupt anyway

Three cases, and only these:

- the fix requires a research or design decision;
- the action is irreversible - anything from the hand-over list;
- the same failure returns after a fix, which means the diagnosis was wrong
  and guessing again wastes more than asking.

## Commands

```bash
uv sync --all-groups --all-extras          # ALL of it: a bare `uv sync` gives runtime deps only - no ruff, pyright, pytest or pre-commit
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

Two artifacts of this setup are worth knowing before reading a result wrong.
`filterwarnings = ["error"]` makes the zero-warning rule a failure and
`--strict-markers` makes a typo'd marker a failure, so both surface as test
errors rather than as notices. And numba `@njit` bodies are excluded from
coverage - the tracer cannot see compiled code, and counting them understates
the real number.

Release-gate commands, the branch table, and the release procedure are in
CONTRIBUTING.md.

`bandit` and `vulture` are installed but deliberately unwired: low signal on a
numeric library. Run them ad hoc or drop them.

## Architecture

Package `src/intelliant/`, built with hatchling. Public API (`from intelliant import *`):

| Name | Module | Input -> Output |
|---|---|---|
| `GraphBuilder` | `.graph_builder` | embeddings -> CSR graph (KNN, exact/pynndescent) |
| `PheromoneExtractor` | `.pheromone_extractor` | CSR graph -> pheromone field (ACO/MMAS) |
| `CoreClusterer` | `.core_clusterer` | pheromone field + threshold -> labels + noise absorption |
| `find_threshold`, `scan_thresholds` | `.threshold` | pheromones -> cutoff threshold (Otsu and others) |
| `ThresholdResult`, `ScanRow` | `.threshold` | return types of the two functions above |
| `GiantDiagnostics` | `.core_clusterer` | giant-component report attached to the clusterer |

No unified pipeline: three classes called sequentially, each independently.

## Tests

- `tests/` — pytest, 348 tests (347 default + 1 slow). Config in `pyproject.toml` `[tool.pytest.ini_options]`.
- Coverage: constructor validation, edge cases, dtype, degenerate end-to-end, warnings, error message coverage (every `raise ValueError` site), tie-breaking determinism, threshold integration, property-based invariants (hypothesis), scale smoke (50k, slow marker).
- LSP diagnostics in `tests/` are expected: tests deliberately pass invalid types to check validation. Pyright `include` is `src/intelliant` only, not `tests/`.
- The default run must stay at ZERO pytest warnings; every expected warning goes through `pytest.warns`.
- Slow tests excluded by default (`addopts = "-m 'not slow'"`). Run with `uv run pytest tests/ -m slow`.

## Code style (repo-specific, not defaults)

- Docstrings and error messages in English, google-style. The conventions the
  linter cannot check - no types in docstrings, what belongs in `Raises`, how
  to convert a generated template - are in [DOCSTRINGS.md](DOCSTRINGS.md).
- `ValueError`: `"<name> must be <range>, got <value>"`.
- Results are attributes with trailing underscore (sklearn convention): `graph_`, `pheromone_matrix_`, `labels_`.
- Parameter validation via shared helpers in `src/intelliant/_validation.py`: `_check_int` (accepts `numbers.Integral`, rejects bool), `_check_float` (rejects bool/non-numeric with ValueError), `_check_bool` (bool / `np.bool_` only, normalized to plain bool). All public params go through them.
- The staged pipeline is a feature (human-in-the-loop): intermediate state (`graph_`, `pheromone_matrix_`, `cores_`, `labels_pheromone_`, external `labels=`) is public API for user editing between stages. Validation stays per-stage; do not enforce cross-stage provenance or merge stages.
- Source files: Python 3.14, ASCII only, no Cyrillic. ruff: line-length 120, double quotes. pyright: standard mode.
- Parameters that shape the result have NO defaults and are keyword-only.
  Calibration is unfinished, so a default would be a value nobody justified,
  applied silently. Do not add one back to make a call site shorter.

`requires-python = ">=3.14"`; the local toolchain runs Python 3.14 (`.python-version`).

## Task classification (which model does what)

The maintainer's own setup, not a rule for outside contributors. The project
is solo and time is scarce, so work is split between a strong model and a
cheaper one. The dividing line is NOT task size:

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

**If you do not know which column you are in, you are in the left one.** Take
the task as specified, do not widen it, and raise anything that requires a
design decision instead of deciding it.

Two consequences worth stating, because they are easy to get backwards:

- **The cheaper model needs a STRICTER spec, not a looser one.** Part of the
  strong model's work shifts from writing code to writing specs detailed
  enough that the code becomes mechanical.
- **The safety net is the verify chain, not judgement.** Delegation is only
  cheap because `pre-push` runs pyright and pytest with coverage
  independently of what any agent reports about its own work. Never take
  "all green" from an agent as evidence; the hook is the evidence.

## Notebooks workflow (user conventions, 2026-07-11)

**Not in this repository yet.** `notebooks/` and its `utils/` helpers live
outside it for now - the repository holds the library alone until the first
release, and `utils/` is gitignored so that a stray `git add .` cannot pull it
in. The conventions below are the contract for when that work lands, so they
are kept rather than rediscovered.

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

## The experiment cycle

The protocol - which metrics, how many seeds, what makes a run reportable -
is in [EXPERIMENTS.md](EXPERIMENTS.md). This is who does what.

1. **Agent writes the jupytext `.py`**, following the layout and cell rules in
   `notebooks/README.md`. This file is the reviewable artifact.
2. **Agent converts it**, and never afterwards edits the `.ipynb` by hand -
   the two would silently diverge and the `.py` is what gets read:
   ```bash
   uv run jupytext --to ipynb notebooks/<group>/<dataset>/<clusterer>/<name>.py
   ```
3. **Hand off. The maintainer runs the notebook.** Do not ask for output to be
   pasted, and do not ask what the plots showed unless the question is about
   the plots specifically.
4. **Agent reads `output.txt` and the files under `results/`.** That is the
   whole reason `utils.Tee` exists.
5. **Agent analyses.** Three outcomes, and they are different:
   - the run is broken - fix the `.py`, reconvert, back to step 3;
   - the run is fine and produced a finding - record it;
   - the finding implies a decision about the research - raise it, do not
     take it.
6. **Agent commits** the notebook with its executed output and the results
   files, then pushes `dev`.

A finding either changes the library or it does not. If it does, the change
goes through the normal cycle - tests, verify chain, its own commit. If a user
would notice, `[Unreleased]` gets an entry.

## Working state under `tmp/`

Everything here is gitignored. It has **no history and no backup** - a lost
disk loses all of it, which matters most for the roadmap, since that is the
plan rather than a note about it.

```
tmp/ROADMAP.md    phases and what "done" means for each
tmp/TASK.md       active items only, one stage at a time
tmp/REVIEW.md     one section per item, then a verdict once all are covered
tmp/done/         finished stages, moved out of TASK.md and dated
tmp/commits/      drafted commit messages, when the drafting rule is in force
```

There are no templates for these in the repository. If you have not been
handed the file, ask for it rather than inventing a format.

- `tmp/TASK.md` holds **only active items**. Finished stages move to
  `tmp/done/` rather than accumulating, so the file stays readable at a
  glance.
- The coder takes **one item at a time**, writes a report under it and marks
  it `[~]`. Only the reviewer sets the final status: `[x]` for done, `[!]`
  for needs work.
- Nothing that ships may link to any of this. It is absent from git history by
  design, so a reference to it from a released document points nowhere - that
  already happened once, in an issue template promising a roadmap nobody could
  open.
- Report findings you reproduced, not findings you inferred from reading. Two
  of eleven in the last round were withdrawn because the tests proved the
  review wrong.
