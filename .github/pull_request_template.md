## What and why

<!-- What the change does, and what you decided against. The diff shows the
     what; only you know the alternatives you rejected. -->

## Verification

<!-- Paste the result, do not just tick the box. "All green" without output is
     not evidence - that rule applies to people and agents alike. -->

```
uv run ruff check src/ tests/ utils/
uv run pyright src/intelliant
uv run pytest tests/ --cov
```

## Checklist

- [ ] Targets `dev`, not `main`
- [ ] Conventional Commits, one concern per commit
- [ ] The "why" is in the commit body, not only in this description
- [ ] No `Co-Authored-By` model trailers
- [ ] No version bump (releases are maintainer-only)
