# Results

Machine-readable output of the notebook runs. Kept so that cross-dataset
tables for an article assemble without rerunning anything.

## What is versioned

**CSV and JSON are. Figures are not.**

A run's numbers are a few kilobytes and expensive to reproduce - the seeds,
the parameter grid, the metrics. Figures are derived from those numbers and
cost megabytes; the previous repository reached 425 MB that way, and the
history had to be rewritten to get it back.

The rules live in `.gitignore`, in the `results/**` block. Note the `**`: with
a plain `results/` git never descends into the directory and the negations
below it would silently do nothing.

## Layout

Mirror the notebook that produced it, so a table can be traced back to a run:

```
results/2d/blobs/intelliant/
    grid_evaporation.csv
    summary.json
```

Write one row per run, with every parameter that varied as its own column, and
the seed among them. A table that records the metric but not the settings that
produced it cannot be pooled with anything later - which is the entire reason
these files are versioned rather than regenerated.

Multi-seed runs go in the same file with the seed as a column, not in separate
files per seed.
