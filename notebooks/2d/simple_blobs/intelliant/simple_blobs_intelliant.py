# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # simple_blobs / intelliant - reference run
#
# The first notebook. It runs **one configuration** through every stage of the
# pipeline, linearly, so each intermediate state can be inspected, and then
# repeats it across the standard seed set.
#
# This is deliberately not a sweep. Its job is to be the reference the sweeps
# are built on and to establish the layout every later notebook follows. The
# protocol it obeys is in `EXPERIMENTS.md`.
#
# The configuration is the one the July 2026 calibration converged on, which
# scored a mean ARI of 0.774 at **1000 points**. This notebook runs at 10000,
# because the protocol calls a thousand a debugging size. Whether the
# configuration survives that change is the first thing worth knowing.

# %% [markdown]
# ## 1. Third-party imports

# %%
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib.colors import ListedColormap
from sklearn.datasets import make_blobs

# %% [markdown]
# ## 2. Local import path
#
# Walking up to the marker rather than counting directories: `parents[3]`
# breaks the day a folder level is added.

# %%
PROJECT_ROOT = next(p for p in Path.cwd().resolve().parents if (p / "pyproject.toml").exists())
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# %% [markdown]
# ## 3. Local imports
#
# Separate from the cell above on purpose - these cannot resolve until the
# path has been extended, and combining the two produces an import warning.

# %%
from intelliant import CoreClusterer, GraphBuilder, PheromoneExtractor, find_threshold
from utils import Tee, evaluate_clustering

# %% [markdown]
# ## 4. Paths and configuration
#
# `output.txt` lands beside this notebook and is gitignored; it is what the
# analysis works from. Tables print in full - a truncated table in a run log
# is a result nobody can check.
#
# Note: `tee.stop()` runs in the last cell. If a cell raises before then,
# stdout stays redirected - call `tee.stop()` by hand or restart the kernel.

# %%
NOTEBOOK_DIR = Path.cwd()
RESULTS_DIR = PROJECT_ROOT / "results" / "2d" / "simple_blobs" / "intelliant"
FIGURES_DIR = RESULTS_DIR / "figures"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

pl.Config(tbl_rows=-1, tbl_cols=-1, tbl_width_chars=200)
plt.rcParams["figure.dpi"] = 120

SEEDS = [1, 10, 100, 1000, 10000]

tee = Tee(NOTEBOOK_DIR / "output.txt")
tee.start()
print(f"project root : {PROJECT_ROOT}")
print(f"results      : {RESULTS_DIR}")
print(f"seeds        : {SEEDS}")

# %% [markdown]
# ## 5. Dataset
#
# Regenerated from a fixed seed rather than cached: deterministic and cheap,
# so there is nothing to store. The data seed and the spread together name the
# variation - this is `s42_std0.6` - and they are a different axis from the
# algorithm seeds above.

# %%
N_SAMPLES = 10_000
N_CENTERS = 7
CLUSTER_STD = 0.6
DATA_SEED = 42
VARIATION = f"s{DATA_SEED}_std{CLUSTER_STD}"

X, y_true = make_blobs(
    n_samples=N_SAMPLES,
    centers=N_CENTERS,
    cluster_std=CLUSTER_STD,
    random_state=DATA_SEED,
)
print(f"variation {VARIATION}: {X.shape[0]} points, {X.shape[1]}D, {N_CENTERS} centres")

# %% [markdown]
# ## 6. Graph settings
#
# Declared here rather than inline at the call, so the run is readable from
# `output.txt` alone.
#
# `knn_method` is pinned rather than left on `"auto"`. Under `"auto"` the
# builder switches to the approximate search above 50000 points, and the
# approximate search is not bit-reproducible under a fixed seed.

# %%
GRAPH_PARAMS = {
    "n_neighbors": 15,
    "metric": "cosine",
    "mutual": True,
    "knn_method": "exact",
}
print("graph:", GRAPH_PARAMS)

# %% [markdown]
# ## 7. Graph

# %%
t0 = time.perf_counter()
graph = GraphBuilder(**GRAPH_PARAMS, verbose=True).build(X)
graph_seconds = time.perf_counter() - t0
print(f"\ngraph built in {graph_seconds:.2f}s")

# %% [markdown]
# ## 8. Ant settings
#
# `n_ants` is set from `N` rather than searched. `evaporation_schedule` is
# `"step"` here because that preserves the behaviour the July calibration was
# measured under - which schedule is correct is the subject of the first
# real experiment, not of this notebook.

# %%
ACO_PARAMS = {
    "n_ants": N_SAMPLES,
    "n_iterations": 20,
    "path_length": 10,
    "beta": 2.0,
    "alpha": 1.0,
    "evaporation_rate": 0.07,
    "evaporation_schedule": "step",
    "pheromone_deposit": 1.0,
    "initial_pheromone": 1.0,
    "tau_min": 0.01,
    "tau_max": 10.0,
}
effective_decay = 1 - (1 - ACO_PARAMS["evaporation_rate"]) ** ACO_PARAMS["path_length"]
print("aco:", ACO_PARAMS)
print(f"\neffective decay per iteration under 'step': {effective_decay:.3f}")
print(f"(the rate itself is {ACO_PARAMS['evaporation_rate']}, which is not the same number)")

# %% [markdown]
# ## 9. Ants

# %%
t0 = time.perf_counter()
aco = PheromoneExtractor(**ACO_PARAMS, random_state=SEEDS[0], verbose=True)
aco.fit(graph)
aco_seconds = time.perf_counter() - t0
print(f"\npheromone field extracted in {aco_seconds:.2f}s")

# %% [markdown]
# ## 10. Threshold
#
# The pheromone field is a public intermediate state, so the same field can be
# thresholded many ways without recomputing it. Here it is thresholded once;
# scanning the neighbourhood of the cutoff is phase 2 work.

# %%
THRESHOLD_PARAMS = {"method": "otsu", "bins": 100}
print("threshold:", THRESHOLD_PARAMS)

cutoff = find_threshold(aco.pheromone_matrix_.data, **THRESHOLD_PARAMS)
print(f"\ncutoff value      : {cutoff.value:.4f}")
print(f"cutoff percentile : {cutoff.percentile:.1f}")

# %% [markdown]
# ## 11. Absorption settings
#
# `batch_size` has no default and is required: it is a memory decision, not a
# quality one.

# %%
CLUSTER_PARAMS = {
    "max_iterations": 20,
    "gap_ratio": 3.0,
    "max_gap_rank": 3,
    "min_cluster_size": 15,
    "batch_size": 1000,
}
print("clusterer:", CLUSTER_PARAMS)

# %% [markdown]
# ## 12. Absorption

# %%
t0 = time.perf_counter()
clusterer = CoreClusterer(**CLUSTER_PARAMS, verbose=True)
labels = clusterer.fit_predict(aco.pheromone_matrix_, threshold_value=cutoff.value, X=X)
cluster_seconds = time.perf_counter() - t0
print(f"\nclustering done in {cluster_seconds:.2f}s")


# %% [markdown]
# ## 13. Results
#
# Quality metrics come from `utils.evaluate_clustering`. The structure block is
# computed here because the library does not expose one: `GiantDiagnostics` is
# an exported type with no public accessor, so its numbers only reach stdout.
# Once that is fixed this helper should be deleted rather than kept in
# parallel - two implementations of one statistic is two things that can
# disagree.


# %%
def cluster_structure(labels: np.ndarray) -> dict:
    """Size distribution of a partition. Noise excluded from the sizes."""
    sizes = np.sort(np.bincount(labels[labels >= 0]))[::-1]
    sizes = sizes[sizes > 0]
    if sizes.size == 0:
        return {
            "SizeMin": 0,
            "SizeMax": 0,
            "SizeMean": 0.0,
            "SizeMedian": 0.0,
            "Top5": [],
            "MaxGap": None,
            "GapPos": None,
            "GiantShare": 0.0,
        }
    ratios = sizes[:-1] / np.maximum(sizes[1:], 1)
    gap_pos = int(np.argmax(ratios)) if ratios.size else None
    return {
        "SizeMin": int(sizes.min()),
        "SizeMax": int(sizes.max()),
        "SizeMean": float(sizes.mean()),
        "SizeMedian": float(np.median(sizes)),
        "Top5": [int(s) for s in sizes[:5]],
        "MaxGap": float(ratios.max()) if ratios.size else None,
        "GapPos": gap_pos,
        "GiantShare": float(sizes.max() / sizes.sum()),
    }


metrics = evaluate_clustering(y_true, labels)
structure = cluster_structure(labels)

print("quality:")
for k, v in metrics.items():
    print(f"  {k:14} {v:.4f}" if isinstance(v, float) else f"  {k:14} {v}")
print("\nstructure:")
for k, v in structure.items():
    print(f"  {k:14} {v}")

print("\nreference: the July calibration scored mean ARI 0.774 at 1000 points.")
print(f"this run is at {N_SAMPLES}.")

# %% [markdown]
# ## 14. All seeds
#
# The reference configuration across the standard seed set. A single-seed
# number is a data point, not a result: what matters below is the spread, not
# only the mean.
#
# The graph does not depend on the algorithm seed, so it is built once and
# reused.

# %%
rows = []
for seed in SEEDS:
    t0 = time.perf_counter()
    extractor = PheromoneExtractor(**ACO_PARAMS, random_state=seed, verbose=False)
    extractor.fit(graph)
    cut = find_threshold(extractor.pheromone_matrix_.data, **THRESHOLD_PARAMS)
    lab = CoreClusterer(**CLUSTER_PARAMS, verbose=False).fit_predict(
        extractor.pheromone_matrix_, threshold_value=cut.value, X=X
    )
    seconds = time.perf_counter() - t0

    row = {
        "dataset": "simple_blobs",
        "variation": VARIATION,
        "n_samples": N_SAMPLES,
        "seed": seed,
        **{f"graph_{k}": v for k, v in GRAPH_PARAMS.items()},
        **{f"aco_{k}": v for k, v in ACO_PARAMS.items()},
        "threshold_method": THRESHOLD_PARAMS["method"],
        "cutoff_value": cut.value,
        "cutoff_percentile": cut.percentile,
        **{f"cluster_{k}": v for k, v in CLUSTER_PARAMS.items()},
        **evaluate_clustering(y_true, lab),
        **{k: v for k, v in cluster_structure(lab).items() if k != "Top5"},
        "seconds": seconds,
    }
    rows.append(row)
    print(
        f"seed {seed:>5}  ARI_all {row['ARI_all']:.4f}  "
        f"clusters {row['Clusters']:>3}  noise {row['NoisePct']:5.1f}%  {seconds:.2f}s"
    )

runs = pl.DataFrame(rows)

# %% [markdown]
# ### Spread across seeds
#
# A parameter whose advantage is smaller than this spread has not been shown
# to have one.

# %%
summary = runs.select(
    pl.col("ARI_all").mean().alias("ARI_all_mean"),
    pl.col("ARI_all").std().alias("ARI_all_std"),
    pl.col("ARI_all").min().alias("ARI_all_min"),
    pl.col("ARI_all").max().alias("ARI_all_max"),
    pl.col("ARI_assigned").mean().alias("ARI_assigned_mean"),
    pl.col("Clusters").mean().alias("Clusters_mean"),
    pl.col("NoisePct").mean().alias("NoisePct_mean"),
    pl.col("seconds").sum().alias("seconds_total"),
)
print(summary)
print()
print(
    runs.select(
        "seed", "ARI_all", "ARI_assigned", "Clusters", "NoisePct", "SizeMax", "SizeMedian", "GiantShare", "seconds"
    )
)

runs.write_csv(RESULTS_DIR / "runs.csv")
print(f"\nwritten: {RESULTS_DIR / 'runs.csv'}")

# %% [markdown]
# ## 15. Figures
#
# The four panels of the pipeline side by side: input, pheromone field with
# the cutoff marked, cores before absorption, final labels. One colour per
# cluster held across panels; noise is grey and never a palette colour.
#
# Saving is commented out on purpose. While the configuration is still being
# searched, figures are drawn and looked at but not written to `results/`.
# Uncomment the last line when the values are settled.


# %%
NOISE_GREY = [0.72, 0.72, 0.72, 1.0]


def panel_colours(labels: np.ndarray) -> tuple[np.ndarray, ListedColormap]:
    """Map labels to colour indices, noise last and grey.

    Cluster colours are drawn from the three tab20 families, which give 60
    distinct hues and - unlike tab20 alone - none of them grey, so a real
    cluster can never be mistaken for noise. Past roughly twenty clusters
    colour identity stops working regardless; the size table is what carries
    the information then, not the picture.
    """
    ids = np.unique(labels[labels >= 0])
    lookup = {label: i for i, label in enumerate(ids)}
    idx = np.array([lookup.get(v, len(ids)) for v in labels])
    families = np.vstack([plt.colormaps[n](np.linspace(0, 1, 20)) for n in ("tab20", "tab20b", "tab20c")])
    keep = families[np.ptp(families[:, :3], axis=1) > 0.12]  # drop the greys
    base = keep[np.arange(max(len(ids), 1)) % len(keep)]
    return idx, ListedColormap(np.vstack([base, NOISE_GREY]))


fig, axes = plt.subplots(1, 4, figsize=(20, 5))

idx, cmap = panel_colours(y_true)
axes[0].scatter(X[:, 0], X[:, 1], c=idx, cmap=cmap, s=3)
axes[0].set_title(f"dataset - {VARIATION}, N={N_SAMPLES}")

values = aco.pheromone_matrix_.data
axes[1].hist(values, bins=100, color="#4a6fa5")
axes[1].axvline(cutoff.value, color="#c0392b", lw=2, label=f"otsu = {cutoff.value:.3f} (p{cutoff.percentile:.0f})")
axes[1].set_yscale("log")
axes[1].set_title("pheromone field with cutoff")
axes[1].legend()

idx, cmap = panel_colours(clusterer.labels_pheromone_)
axes[2].scatter(X[:, 0], X[:, 1], c=idx, cmap=cmap, s=3)
axes[2].set_title(f"cores - {len(np.unique(clusterer.cores_[clusterer.cores_ >= 0]))} found")

idx, cmap = panel_colours(labels)
axes[3].scatter(X[:, 0], X[:, 1], c=idx, cmap=cmap, s=3)
axes[3].set_title(f"clusters - ARI_all {metrics['ARI_all']:.3f}, noise {metrics['NoisePct']:.1f}%")

for ax in (axes[0], axes[2], axes[3]):
    ax.set_xlim(X[:, 0].min() - 1, X[:, 0].max() + 1)
    ax.set_ylim(X[:, 1].min() - 1, X[:, 1].max() + 1)

fig.suptitle(
    f"simple_blobs / intelliant - k={GRAPH_PARAMS['n_neighbors']} "
    f"{GRAPH_PARAMS['metric']}, evap={ACO_PARAMS['evaporation_rate']} "
    f"({ACO_PARAMS['evaporation_schedule']}), otsu",
    y=1.02,
)
fig.tight_layout()

# fig.savefig(FIGURES_DIR / "grid_reference.png", bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Done

# %%
tee.stop()
print(f"run log written to {NOTEBOOK_DIR / 'output.txt'}")
