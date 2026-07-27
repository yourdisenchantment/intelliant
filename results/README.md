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

What a row must contain - the metric set, the parameters, the seed - is in
[EXPERIMENTS.md](../EXPERIMENTS.md), together with the rule for adding a
metric and what makes a run reportable at all. It is not repeated here: two
copies of a protocol drift, and the results are what drift into.
