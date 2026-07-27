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
uv run cz bump --yes 0.2.0a1
uv lock                       # the lock carries the project version too
git add uv.lock && git commit --amend --no-edit
```

`uv.lock` records the version of this project alongside its dependencies, so
a bump leaves it stale. Left that way, CI fails immediately: `uv sync
--frozen` refuses a lock that disagrees with `pyproject.toml`, and by then the
tag exists. Re-lock and fold it into the bump commit.

`--yes` because without it commitizen asks whether this is the first tag and
waits forever in a non-interactive shell.

The tag must sit on the LAST commit of the release. `cz bump` tags whatever is
current, so anything committed afterwards is simply not in the release - the
first attempt here left a documentation fix outside the tag. Bump last, or
move the tag.

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
