# Security

## Scope

`intelliant` is a numeric library. It takes arrays and sparse matrices, does
arithmetic on them, and returns labels. It opens no sockets, executes no user
input, deserialises nothing, and writes no files.

The realistic risk surface is therefore small and mostly indirect:

- a crash or a hang on adversarial input (degenerate graphs, NaN, extreme
  parameter values);
- unbounded memory growth on input the caller did not expect to be that large;
- a bug in a dependency (numpy, scipy, scikit-learn, numba, pynndescent).

Reports about any of these are welcome.

## Supported versions

Only the latest published version. The project is in alpha and the public API
still changes between versions; there are no backports.

## Reporting

Report privately through GitHub's
[security advisories](https://github.com/yourdisenchantment/intelliant/security/advisories/new)
rather than in a public issue.

Expect a slow first response - this is a single-maintainer research project,
not a staffed product. If a report turns out to be a plain bug rather than a
vulnerability, it will be moved to a normal issue and handled there.
