# Contributing

The project is an early alpha and is developed by a single maintainer as
research work. Issues and discussions are welcome at any time; pull requests
are welcome too, with the caveats below.

## Requirements

- Python 3.14 (strict - see `.python-version` and `requires-python`)
- [uv](https://docs.astral.sh/uv/)
- git

## Setup

```bash
uv sync --all-groups --all-extras
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
uv run pre-commit install --hook-type commit-msg
```

**The flags matter.** A bare `uv sync` installs the runtime dependencies and
nothing else - no ruff, no pyright, no pytest, no pre-commit - and the first
thing you try will fail with a missing command rather than with anything
informative. `--all-groups` brings in `dev`, `notebooks` and `embeddings`;
`--all-extras` brings in the optional ones. CI runs the same line.

**All three `install` lines are needed.** A bare `pre-commit install` wires up
the pre-commit stage alone - you get ruff and the whitespace checks, and
silently get no `cz check` on commit messages and no pyright or pytest on
push. The first sign is CI failing on something a hook was supposed to catch.

## Project layout

```
src/intelliant/    the library - five modules and a validation helper
tests/             pytest, 348 tests (347 default + 1 marked slow)
```

The public API is four entry points and three return types:

| Name | Module | Input -> Output |
|---|---|---|
| `GraphBuilder` | `graph_builder.py` | embeddings -> CSR similarity graph (KNN, exact or pynndescent) |
| `PheromoneExtractor` | `pheromone_extractor.py` | CSR graph -> pheromone field (ACO/MMAS, numba) |
| `find_threshold`, `scan_thresholds` | `threshold.py` | pheromones -> cutoff (`ThresholdResult`, `ScanRow`) |
| `CoreClusterer` | `core_clusterer.py` | pheromone field + cutoff -> labels, noise absorption, `GiantDiagnostics` |

**There is no unified `fit`, and adding one would be rejected.** The three
classes are called in sequence and the state between them - `graph_`,
`pheromone_matrix_`, `cores_`, `labels_pheromone_` - is public API that a user
is expected to inspect and edit. That is the human-in-the-loop design the
library exists to offer; fusing the stages would remove it. For the same
reason validation stays per-stage: do not add cross-stage provenance checks
that would refuse a matrix the user modified on purpose.

Tests mirror that structure - one file per concern rather than per class:
constructor validation, edge cases, dtypes, degenerate end-to-end runs,
warnings, error-message style, tie-breaking determinism, threshold
integration, property-based invariants (hypothesis), and a 50k scale smoke
test behind the `slow` marker. Pyright's `include` is `src/intelliant` only,
so type diagnostics inside `tests/` are expected: the tests pass invalid types
on purpose.

## Code style

Beyond what ruff and pyright enforce:

- **Python 3.14, ASCII only.** Line length 120, double quotes.
- **`ValueError` messages take one shape:** `"<name> must be <range>, got
  <value>"`. There are many of them and they are tested as a group.
- **Results are attributes with a trailing underscore**, following sklearn:
  `graph_`, `pheromone_matrix_`, `labels_`.
- **Validate through `_validation.py`, not by hand.** `_check_int` accepts
  `numbers.Integral` and rejects `bool`; `_check_float` rejects `bool` and
  non-numerics; `_check_bool` takes `bool` or `np.bool_` and normalizes to a
  plain `bool`. Every public parameter goes through one of them. The bool
  checks look redundant - `bool` subclasses `int`, so `True` passes an
  `Integral` test at runtime - and removing them is a real bug, not cleanup.
- **Parameters that shape the result get no defaults and are keyword-only.**
  Calibration is unfinished, so a default would be an unjustified value
  applied silently. Do not add one back to shorten a call site.
- **The default test run must stay at zero warnings.** `filterwarnings =
  ["error"]` turns a stray warning into a failure; anything expected goes
  through `pytest.warns`.

## The verify chain

```bash
uv run ruff check src/ tests/           # lint
uv run ruff format --check src/ tests/  # formatting
uv run pyright src/intelliant           # types, 0 errors required
uv run pytest tests/                    # tests
uv run pytest tests/ --cov              # tests + coverage (fail_under = 95)
```

The last two lines are not redundant. `--cov` is deliberately kept out of
`addopts`, so that running one file - `uv run pytest tests/test_threshold.py`
- is not failed by a coverage floor it was never going to meet. The floor
belongs to a full run, which is why the pre-push hook is the thing that
passes `--cov`.

All of it must pass before a change is reported as done. Enforcement is split
by cost:

| Stage | Runs |
|---|---|
| commit | ruff check, ruff format, whitespace/toml/yaml |
| commit-msg | `cz check` - Conventional Commits |
| push | pyright, pytest with coverage |
| CI | the whole chain again, independently |

pyright and pytest run on push rather than per commit because they take about
a minute, and a hook people skip is worse than a slow one. CI repeats
everything because a local hook can be bypassed with `--no-verify`.

Some checks stay manual and belong to a release rather than to a commit:

```bash
uv run pytest tests/ -m slow    # the 50k scale test, excluded by default
uv run deptry .                 # dependency hygiene
uv run ruff check --select DOC --ignore DOC502 --preview src/   # docstrings
```

CI runs these on `main` only, as a release gate.

### Verify on a clean clone, not in your working folder

A working folder carries untracked leftovers and a populated `.venv`, and it
will pass things CI fails:

```bash
git clone --branch dev . /tmp/verify && cd /tmp/verify
uv sync --all-groups --all-extras --frozen
uv run ruff check src/ tests/ && uv run pyright src/intelliant && uv run pytest tests/ --cov
```

This is not caution for its own sake. It has already caught a real failure
here: a test imported a module that existed locally but had never been added
to the repository, and the whole test collection would have died on the first
push. `--frozen` matters too - it refuses a `uv.lock` that disagrees with
`pyproject.toml`, which is exactly what a version bump leaves behind.

## Branches

- `main` - the published state. Nothing is committed here directly; it
  receives merges from `dev` at a release.
- `dev` - active development. Pull requests target `dev`.

**`main` carries the shipped package and nothing else** - the library, its
tests, and the files a user or a packaging tool needs to install, cite and
understand it. Everything that exists to develop or justify the library stays
on `dev`: the experiments, the literature record, the roadmap and research
notes, the protocols, and the agent instructions. They are research apparatus,
they grow without bound, and the one branch meant to stay readable is not
where they belong.

What crosses over, and it is the whole list: `src/`, `tests/`, `pyproject.toml`,
`uv.lock`, `.github/`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`,
`CITATION.cff`, `LICENSE`, `.gitignore`, `.pre-commit-config.yaml`,
`DOCSTRINGS.md` - the last because this file links to it, and a shipped
document with a dangling link is a defect this repository has already had
once.

What does not: `notebooks/`, `results/`, `literature/`, `utils/`, `AGENTS.md`,
`EXPERIMENTS.md`, `LITERATURE.md`, `ROADMAP.md`, `RESEARCH_NOTES.md`.

That makes the two branches diverge permanently, so a release merge is no
longer a fast-forward:

```bash
git checkout main
git merge --no-commit --no-ff dev
git rm -r -f --ignore-unmatch notebooks results literature utils \
  AGENTS.md EXPERIMENTS.md LITERATURE.md ROADMAP.md RESEARCH_NOTES.md
git commit --no-edit
git checkout dev
```

The `git rm` both applies the exclusion and resolves the modify/delete
conflict that the previous exclusion creates, so the same four lines work at
every release rather than only the first.

Note what this does not do: the merge brings `dev`'s history with it, so those
files stay reachable from `main` and a clone still fetches them. The exclusion
governs what `main`'s tree contains - what a visitor browses and what a source
archive holds - not the size of the repository.

Do not edit `README.md` or any other shared file directly on `main`: a single
direct edit there turns every future release merge into a conflict.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/), enforced by the
`cz check` commit-msg hook. `uv run cz commit` walks through the format
interactively.

The hook validates the FORM. These rules cover the rest:

- **A repeated subject means the change should have been an amend or a
  squash.** Iterating on one artifact is one commit.
- **The "why" goes in the body.** The subject says what changed; the body says
  what was rejected and on what grounds. For a project measured in years the
  rationale attached to the diff is the asset.
- **One concern per commit.** Source, tests, notebooks and config move
  separately.
- **No attribution trailers at all.** The commit-msg hook rejects every
  `Co-Authored-By:` and `Signed-off-by:` line, not just the ones naming a
  model. The rule exists because several models have worked on this
  repository and crediting one of them misstates authorship - but a hook that
  tried to tell a model from a co-author would need a list of model names that
  goes stale monthly, so it refuses the whole trailer. On a single-maintainer
  project that costs nothing; if you are genuinely co-authoring, name the
  other person in the commit body.

## Docstrings

Google style, Napoleon-compatible, enforced by `ruff --select D`. The rules a
linter cannot check - no types in the docstring since every signature is
annotated, what belongs in `Raises`, how to convert a generated template - are
in [DOCSTRINGS.md](DOCSTRINGS.md).

## Pull requests

Target `dev`. Before opening one, run the verify chain locally - CI runs the
same thing, and a red PR is slower for everyone than a local minute.

Say in the description what the change does and why the alternatives were
rejected. A diff shows what; only you know what you decided against.

## Releases

Maintainer only. Contributors never need publishing credentials.

Versions follow project MILESTONES rather than commit types, so the number is
passed explicitly:

```bash
uv run cz bump --yes --files-only 1.0.0a1   # rewrite the version files, nothing else
uv lock                                     # the lock carries the project version too
git add -A
git commit -m "bump: version 0.2.0a1 -> 1.0.0a1"
git tag -a v1.0.0a1 -m "Release 1.0.0a1"
```

`uv.lock` records the version of this project alongside its dependencies, so
a bump leaves it stale. Left that way, CI fails immediately: `uv sync
--frozen` refuses a lock that disagrees with `pyproject.toml`.

**`--files-only`, and the commit and tag made by hand, is the point of this
recipe.** A plain `cz bump` also commits and tags, which forces the re-lock to
arrive as `git commit --amend` - and an amend builds a new commit object,
leaving the tag on the old one, which is no longer on any branch. The release
then points at a commit nobody can reach. Rewriting the files first and
committing once puts the tag on the final commit by construction, instead of
requiring it to be moved afterwards and remembered.

`--yes` because without it commitizen asks whether this is the first tag and
waits forever in a non-interactive shell.

Pass the version explicitly and in full - `1.0.0a1`, never `1.0.0a`. PEP 440
reads a missing pre-release number as zero, so `1.0.0a` becomes `1.0.0a0` in
the built artifact while the tag stays `v1.0.0a`, and the two no longer name
the same thing.

`cz bump` rewrites the version in `pyproject.toml`, `src/intelliant/__init__.py`
and `CITATION.cff` - they are its `version_files`. Do not edit any of the
three by hand; the release gate on `main` fails if they disagree, which is
what stops a release from shipping one number, reporting another and handing
out a citation for a third.

Bump last. The tag must sit on the final commit of the release, so anything
committed after it is simply not in the release - the first attempt here left
a documentation fix outside the tag. If something does have to land
afterwards, move the tag rather than accepting the gap, and keep it annotated:

```bash
git tag -f -a v1.0.0a1 <commit> -m "$(git tag -l --format='%(contents)' v1.0.0a1)"
```

That is safe only before the tag is pushed. Once a tag reaches GitHub the
release ruleset refuses to move or delete it, and rightly so: it names a
version number that PyPI has burned forever.

Pushing the resulting `v*` tag triggers the release workflow, which builds and
publishes to PyPI through Trusted Publishing (OIDC - no API tokens exist in
this repository). Pushes to `main` and `dev` only run checks; they never
publish, and a second push of an unchanged version would be rejected by PyPI
anyway.

## Agents

Everything above applies to automated agents unchanged - the verify chain, the
commit rules, the branch rules. What follows is the part that only comes up
when the contributor is a model.

**Commit messages are drafted into `tmp/commits/`, not straight into git.**
The maintainer reads the draft and then either approves the commit or performs
it personally. The one exception is the strong model driving a session, which
may commit and push on its own judgement so that routine work does not need
approval per command. Every other agent works under manual control, or with
explicit permission for each commit. The point is not ceremony: nothing
reaches a published branch without the maintainer having read it.

Hard limits, in addition to the rules above:

- **Never delete a file.** List the paths and the command; the maintainer runs
  it.
- **Never bump the version, create a tag, or push one.** Versions track
  project milestones, and only the maintainer knows when one was reached.
- **Never use `--no-verify`.** A failing hook is reporting something. The fix
  is the code.
- **Never report a check as passing without its output.** "All green" is a
  claim, not evidence - and the whole reason pyright and pytest run in a hook
  and again in CI is that self-reports are not trusted.
- **Do not add files that pin the repository to one assistant.** `CLAUDE.md`,
  `.cursorrules`, `.mcp.json` and their kin are gitignored deliberately.
- **Do not touch `.env` or any file holding secrets.**

Work is split between a strong model and a cheaper one, and the dividing line
is not task size:

> A task goes to the cheaper model when success is checkable by running a
> command, AND the spec leaves no design decisions open.

So: tests from an enumerated list of cases, docstrings from placed templates,
mechanical refactors from an explicit list, lint fixes. Producing that list -
and reviewing what came back - stays with the strong model, along with
anything where a wrong choice is expensive and CI would not catch it: the
calibration protocol, the algorithm mechanisms, the threshold methods, the
shape of the public API.

Two consequences that are easy to get backwards. The cheaper model needs a
**stricter** spec, not a looser one, so part of the strong model's work shifts
from writing code to writing specs detailed enough that the code becomes
mechanical. And the safety net is the verify chain, not judgement - delegation
is only cheap because the pre-push hook runs pyright and pytest independently
of what any agent claims about its own work.
