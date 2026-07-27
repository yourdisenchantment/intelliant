# Docstring style

Google style, Napoleon-compatible. Checked by

```bash
uv run ruff check --select D,DOC --preview src/
```

`D` (pydocstyle) covers form; `DOC` (pydoclint) checks that `Args`, `Returns`
and `Raises` actually match the signature and body. `darglint` does the same
job and is the usual recommendation, but its last release was October 2021 and
the author has said they moved off Python - no reason to add an abandoned
dependency for something the installed linter already does.

The canonical references:

- [Google Python Style Guide, section 3.8](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Napoleon example](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

Where those leave a choice, this file makes it. Enforced by `ruff --select D`
with `convention = "google"`; everything the linter cannot check is below.

## No types in docstrings

```python
# no
Args:
    n_neighbors (int): Number of neighbours.

# yes
Args:
    n_neighbors: Neighbours per point, excluding the point itself.
```

Every signature in `src/` is annotated - `ruff ANN` enforces it - so a type in
the docstring is a second copy that drifts from the first. The annotation is
checked by pyright; the prose is not.

**This is the one place the VS Code autoDocstring output must be edited**: it
emits `name (type): _description_`. Strip the parenthesised type.

## Say what the signature cannot

A docstring that restates the code earns nothing:

```python
# no
Args:
    mutual: Whether the graph is mutual.

# yes
Args:
    mutual: How to symmetrize. True keeps an edge only when both points
        chose each other (AND) - sparser, cleaner boundaries. False keeps
        an edge chosen by either (OR) - denser, more forgiving, more prone
        to bridges between clusters.
```

Write what a reader cannot deduce: units, ranges, invariants, what happens at
the boundaries, which choice hurts and how. If a parameter has a trap, the
docstring is where it gets named - notably `evaporation_schedule`, where no
value from the ACO literature transfers.

## Sections

`Args`, `Returns`, `Raises`, `Yields`, `Attributes`, `Warns`, `Example`,
`Note`. In that order, omitting the ones that do not apply.

- **`Raises` is mandatory** wherever the function raises. There are 58
  `raise ValueError` sites, and without this section a caller learns the
  contract by crashing.
- **Group by cause, do not enumerate sites.** One `ValueError:` entry naming
  the conditions beats fifteen identical lines - which is exactly what
  autoDocstring generates from a scan, and it must be collapsed.
- **`Warns`** for anything the code passes to `warnings.warn`. The asymmetric
  graph warning is a result, not a diagnostic.
- **`Attributes`** on classes, for the trailing-underscore results. State
  which are meant to be edited between stages - that is the human-in-the-loop
  contract, not an implementation detail.

## Which functions need one

- Public API: always.
- Private helpers: when the *why* is not obvious from the body. `_log` needs
  one line; `_apply_degree_fallback` needs a paragraph explaining why it
  exists at all.
- `@njit` kernels: always. They are the least readable code here and the
  hardest to change safely.

## Prose

- English, as everywhere in this repository.
- Wrap prose at 79 columns; code stays at the configured 120. Prose does not
  read the same as code at that width, in a terminal or in rendered docs.
- First line: one sentence, imperative mood, ending with a period.
  `"""Builds the similarity graph."""` - not `"""Build..."""`, not
  `"""This function builds..."""`.
- Then a blank line, then the extended description. No blank line between the
  docstring and the code that follows (`D202`).

## Examples

An example must run, or say plainly that it does not:

```python
Example:
    >>> builder = GraphBuilder(n_neighbors=15, metric="cosine", mutual=True)
    >>> graph = builder.build(embeddings)  # doctest: +SKIP
```

The README example broke silently when the API changed and stayed broken for
an unknown time. Examples that nothing executes rot the same way.

## Working from an autoDocstring template

The templates are scaffolding, not structure. Converting one:

1. Replace `_summary_` with a real first line; delete `_extended_summary_` if
   there is nothing to add.
2. Strip `(type)` from every `Args` entry.
3. Collapse the generated `Raises` list into entries grouped by cause.
4. Delete module-level `Raises` and `Returns` sections outright - a module
   raises and returns nothing, and the generator produces those from a scan
   of the file.
5. Delete the leading function name (`"""_step_ants _summary_`); the reader
   can see it.
