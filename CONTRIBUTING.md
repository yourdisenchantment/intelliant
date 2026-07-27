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

The three hook stages are not optional: they are the same checks CI runs, and
installing them locally means finding out in seconds rather than after a push.

## The verify chain

```bash
uv run ruff check src/ tests/           # lint
uv run ruff format --check src/ tests/  # formatting
uv run pyright src/intelliant           # types, 0 errors required
uv run pytest tests/                    # tests
uv run pytest tests/ --cov              # tests + coverage (fail_under = 95)
```

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
```

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
- **No model attribution.** No `Co-Authored-By: <model>` trailers. Several
  models have worked on this repository and crediting one of them misstates
  authorship; the history records decisions, not tooling.

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

Pushing the resulting `v*` tag triggers the release workflow, which builds and
publishes to PyPI through Trusted Publishing (OIDC - no API tokens exist in
this repository). Pushes to `main` and `dev` only run checks; they never
publish, and a second push of an unchanged version would be rejected by PyPI
anyway.

## Agents

Automated agents work under `AGENTS.md`, which is part of the contract rather
than a hint: it defines which model may take which task, requires commit
messages to be drafted into `tmp/commits/` for review before anything is
committed, and forbids version bumps and file deletion.
