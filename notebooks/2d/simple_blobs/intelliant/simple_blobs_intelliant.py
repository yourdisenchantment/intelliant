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
from utils import Tee, evaluate_clustering, graph_baseline, graph_report

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
# `metric` is euclidean, not the cosine the July calibration used. Cosine
# measures angle from the origin, and these blobs sit off it - the sweep below
# and ROADMAP record what that does. On embeddings the choice inverts.
#
# `knn_method` is pinned rather than left on `"auto"`. Under `"auto"` the
# builder switches to the approximate search above 50000 points, and the
# approximate search is not bit-reproducible under a fixed seed.

# %%
GRAPH_PARAMS = {
    "n_neighbors": 15,
    "metric": "euclidean",
    "mutual": True,
    "knn_method": "exact",
}
print("graph:", GRAPH_PARAMS)

# %% [markdown]
# ## 7. Graph
#
# The scan below is read before anything else in the run. It says which of the
# two failure faces this graph has, and they are opposite: **merge**, where
# fewer components than classes means two clusters are already joined and only
# a cut inside a component can separate them; and **fragmentation**, where
# isolated points and islands mean the pipeline has pieces it can reach by
# absorption alone.
#
# On real embeddings this block is the only description of the graph there is -
# the spatial figures below stop meaning anything once the data is not 2D.

# %%
t0 = time.perf_counter()
graph = GraphBuilder(**GRAPH_PARAMS, verbose=True).build(X)
graph_seconds = time.perf_counter() - t0
print(f"\ngraph built in {graph_seconds:.2f}s")

print("\ngraph scan:")
for k, v in graph_report(graph).items():
    print(f"  {k:14} {v:.4f}" if isinstance(v, float) else f"  {k:14} {v}")
print(f"\n{N_CENTERS} true classes against the component count above.")
print("Fewer components than classes is a merge; the threshold has to cut inside one.")

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
# ### The graph alone
#
# The ablation: take the colony out, keep everything else, and see whether the
# answer moves. `graph_baseline` hands the KNN graph straight to
# `CoreClusterer` under a cutoff below its smallest edge, so nothing is
# dropped and the graph's own components go through the same
# `min_cluster_size` cut and the same absorption the run's output received.
# One function, one code path, the colony subtracted.
#
# Two numbers come back because they answer different questions.
# `baseline_ARI` is the components scored raw - the floor. The pipeline
# reading is the honest comparison, since it is the same final step.
#
# This is only computable where there is ground truth, which is the reason the
# synthetic sets come first. On CC3M there is nothing to score against, and a
# pipeline returning its input unchanged looks exactly like a result.

# %%
t0 = time.perf_counter()
base = graph_baseline(graph, y_true, cluster_params=CLUSTER_PARAMS, X=X)
print(f"ablation run in {time.perf_counter() - t0:.2f}s\n")
for k, v in base.items():
    print(f"  {k:26} {v:.4f}" if isinstance(v, float) else f"  {k:26} {v}")

reach = graph_report(graph, min_cluster_size=CLUSTER_PARAMS["min_cluster_size"])
print(f"\n  {'islands below min_cluster_size':30} {reach['Islands']}")
print(f"  {'points in them':30} {reach['IslandPoints']}")

gain = metrics["ARI_all"] - base["baseline_pipeline_ARI"]
print(f"\nthe colony added {gain:+.6f} over the same pipeline without it.")
if abs(gain) < 1e-9:
    print("Exactly zero: the pheromone threshold cut nothing the graph had not already cut.")

# %% [markdown]
# %% [markdown]
# %% [markdown]
# ## 14. What gets compared
#
# Two axes, and which one is worth spending on changes between passes.
#
# **Forks** are discrete choices that change the graph or the process rather
# than tuning it. This pass varies `mutual` - AND against OR symmetrisation -
# and `evaporation_schedule`, the two remaining forks that alter what the ants
# walk on and how the field decays.
#
# Every graph is scanned and ablated before any ant runs on it. The scan says
# what the graph is; the ablation says what it already achieves. Without the
# second, a score cannot be read - a pipeline that hands back the graph's
# components unchanged looks like a result and is not one.
#
# Two baselines land in every row. `baseline_ARI` is the components scored
# raw, and `baseline_pipeline_ARI` is the same graph through the same
# `min_cluster_size` cut and the same absorption the run received, so the only
# difference left between it and the run is the colony. `over_pipe` is
# therefore the number that answers "did the ants do anything", and
# `over_baseline` is kept beside it because the earlier results were recorded
# against it.
#
# **Heuristic sets** collapse to `none` here. The previous pass ran the full
# 2x2 across the metric fork and found every difference between the sets
# smaller than the seed spread within them under euclidean, so the axis is not
# where the information is. That result is in `runs_metric_heuristics.csv`;
# widening this axis again needs a reason, not a habit.
#
# `metric` is held at euclidean, which the previous pass settled for this
# data - cosine slices spatial blobs into angular wedges. That choice does not
# carry to the text datasets, where the rule inverts.
#
# Each sweep writes its own results file. Overwriting one file per pass would
# leave only the newest question answered.

# %%
SWEEP_NAME = "graph_forks"

FORKS = {
    "mutual_step": {"graph": {"mutual": True}, "aco": {"evaporation_schedule": "step"}},
    "mutual_iter": {"graph": {"mutual": True}, "aco": {"evaporation_schedule": "iteration"}},
    "or_step": {"graph": {"mutual": False}, "aco": {"evaporation_schedule": "step"}},
    "or_iter": {"graph": {"mutual": False}, "aco": {"evaporation_schedule": "iteration"}},
}

HEURISTIC_SETS = {"none": {}}

print(f"sweep          : {SWEEP_NAME}")
print(f"forks          : {list(FORKS)}")
print(f"heuristic sets : {list(HEURISTIC_SETS)}")
print(f"seeds          : {SEEDS}")
print(f"cells          : {len(FORKS)} x {len(HEURISTIC_SETS)} = {len(FORKS) * len(HEURISTIC_SETS)}")
print(f"runs           : {len(FORKS) * len(HEURISTIC_SETS) * len(SEEDS)}")

for name, fork in FORKS.items():
    rate = {**ACO_PARAMS, **fork["aco"]}["evaporation_rate"]
    length = {**ACO_PARAMS, **fork["aco"]}["path_length"]
    schedule = {**ACO_PARAMS, **fork["aco"]}["evaporation_schedule"]
    decay = 1 - (1 - rate) ** length if schedule == "step" else rate
    print(f"  {name:12} effective decay per iteration: {decay:.3f}")


# %% [markdown]
# ## 15. Sweep
#
# Graphs are cached by their parameters, so two forks that differ only in an
# ACO setting share one graph instead of rebuilding it.


# %%
def run_once(built_graph, aco_extra: dict, seed: int, features: np.ndarray):
    """One full pipeline run. Returns the artifacts a grid needs."""
    extractor = PheromoneExtractor(**{**ACO_PARAMS, **aco_extra}, random_state=seed, verbose=False)
    extractor.fit(built_graph)
    cut = find_threshold(extractor.pheromone_matrix_.data, **THRESHOLD_PARAMS)
    clusterer_ = CoreClusterer(**CLUSTER_PARAMS, verbose=False)
    lab = clusterer_.fit_predict(extractor.pheromone_matrix_, threshold_value=cut.value, X=features)
    return extractor, cut, clusterer_, lab


graphs = {}
baselines = {}
scans = {}
rows = []

for fork_name, fork in FORKS.items():
    graph_params = {**GRAPH_PARAMS, **fork["graph"]}
    key = tuple(sorted(graph_params.items()))
    if key not in graphs:
        t0 = time.perf_counter()
        graphs[key] = GraphBuilder(**graph_params, verbose=False).build(X)
        scan = graph_report(graphs[key], min_cluster_size=CLUSTER_PARAMS["min_cluster_size"])
        baselines[key] = graph_baseline(graphs[key], y_true, cluster_params=CLUSTER_PARAMS, X=X)
        print(f"\ngraph {dict(fork['graph'])} built in {time.perf_counter() - t0:.2f}s, {graphs[key].nnz:,} edges")
        print(
            f"  scan: {scan['Components']} components, giant share {scan['GiantShare']:.3f}, "
            f"{scan['Isolated']} isolated, {scan['Islands']} islands holding {scan['IslandPoints']} points"
        )
        print(f"  sizes: {scan['CompTop5']}")
        scans[key] = {f"scan_{k}": v for k, v in scan.items() if k != "CompTop5"}
        print(
            f"  baseline: components alone ARI_all {baselines[key]['baseline_ARI']:.4f}, "
            f"through the same final step {baselines[key]['baseline_pipeline_ARI']:.4f} "
            f"({baselines[key]['baseline_pipeline_clusters']} clusters) - "
            f"what this graph gives before a single ant runs"
        )
    built = graphs[key]
    baseline = baselines[key]

    for set_name, heuristics in HEURISTIC_SETS.items():
        aco_extra = {**fork["aco"], **heuristics}
        for seed in SEEDS:
            t0 = time.perf_counter()
            _, cut, _, lab = run_once(built, aco_extra, seed, X)
            seconds = time.perf_counter() - t0
            rows.append(
                {
                    "sweep": SWEEP_NAME,
                    "dataset": "simple_blobs",
                    "variation": VARIATION,
                    "n_samples": N_SAMPLES,
                    "fork": fork_name,
                    "heuristics": set_name,
                    "seed": seed,
                    **{f"graph_{k}": v for k, v in graph_params.items()},
                    **{f"aco_{k}": v for k, v in {**ACO_PARAMS, **aco_extra}.items()},
                    "threshold_method": THRESHOLD_PARAMS["method"],
                    "cutoff_value": cut.value,
                    "cutoff_percentile": cut.percentile,
                    **evaluate_clustering(y_true, lab),
                    **{k: v for k, v in cluster_structure(lab).items() if k != "Top5"},
                    **scans[key],
                    **baseline,
                    "seconds": seconds,
                }
            )
            rows[-1]["ARI_over_baseline"] = rows[-1]["ARI_all"] - baseline["baseline_ARI"]
            rows[-1]["ARI_over_pipeline_baseline"] = rows[-1]["ARI_all"] - baseline["baseline_pipeline_ARI"]
        done = [r for r in rows if r["fork"] == fork_name and r["heuristics"] == set_name]
        print(
            f"  {fork_name:12} {set_name:8} ARI_all "
            f"{np.mean([r['ARI_all'] for r in done]):.4f} +/- "
            f"{np.std([r['ARI_all'] for r in done]):.4f}   "
            f"clusters {np.mean([r['Clusters'] for r in done]):.1f}"
        )

runs = pl.DataFrame(rows)
runs_path = RESULTS_DIR / f"runs_{SWEEP_NAME}.csv"
runs.write_csv(runs_path)
print(f"\nwritten: {runs_path}")

# %% [markdown]
# ### Summary
#
# A difference smaller than the spread has not been shown to be a difference.

# %%
summary = (
    runs.group_by("fork", "heuristics")
    .agg(
        pl.col("ARI_all").mean().alias("ARI_mean"),
        pl.col("ARI_all").std().alias("ARI_std"),
        pl.col("ARI_all").min().alias("ARI_min"),
        pl.col("ARI_all").max().alias("ARI_max"),
        pl.col("Clusters").mean().alias("Clusters"),
        pl.col("NoisePct").mean().alias("NoisePct"),
        pl.col("GiantShare").mean().alias("GiantShare"),
        pl.col("baseline_ARI").first().alias("baseline"),
        pl.col("baseline_pipeline_ARI").first().alias("baseline_pipe"),
        pl.col("ARI_over_baseline").mean().alias("over_baseline"),
        pl.col("ARI_over_pipeline_baseline").mean().alias("over_pipe"),
        pl.col("cutoff_percentile").mean().alias("cutoff_pct"),
        pl.col("seconds").mean().alias("seconds"),
    )
    .sort("ARI_mean", descending=True)
)
print(summary)
print()
print("over_baseline is what the colony added to the graph's own components.")
print("over_pipe is the same against the ablation - the graph through the same final step.")
print("Read both against ARI_std: a gain smaller than the seed spread is not a gain.")

# %% [markdown]
# ## 16. Grids
#
# One per cell, showing that cell's best seed by `ARI_all`. The winner is
# re-run rather than held in memory - a rerun costs a fraction of a second,
# keeping every pheromone matrix does not.

# %%
NOISE_GREY = [0.72, 0.72, 0.72, 1.0]


def panel_colours(labels: np.ndarray) -> tuple[np.ndarray, ListedColormap]:
    """Map labels to colour indices, noise last and grey.

    Cluster colours come from the three tab20 families - 60 hues, none of them
    grey - so a real cluster can never be mistaken for noise. Past roughly
    twenty clusters colour identity stops working regardless; the size table
    is what carries the information then, not the picture.
    """
    ids = np.unique(labels[labels >= 0])
    lookup = {label: i for i, label in enumerate(ids)}
    idx = np.array([lookup.get(v, len(ids)) for v in labels])
    families = np.vstack([plt.colormaps[n](np.linspace(0, 1, 20)) for n in ("tab20", "tab20b", "tab20c")])
    keep = families[np.ptp(families[:, :3], axis=1) > 0.12]
    base = keep[np.arange(max(len(ids), 1)) % len(keep)]
    return idx, ListedColormap(np.vstack([base, NOISE_GREY]))


def draw_grid(fork_name: str, set_name: str, seed: int) -> None:
    """Four panels: input, pheromone field with its cutoff, cores, clusters."""
    fork = FORKS[fork_name]
    graph_params = {**GRAPH_PARAMS, **fork["graph"]}
    built = graphs[tuple(sorted(graph_params.items()))]
    aco_extra = {**fork["aco"], **HEURISTIC_SETS[set_name]}
    extractor, cut, clusterer_, lab = run_once(built, aco_extra, seed, X)
    stats = evaluate_clustering(y_true, lab)

    fig, axes = plt.subplots(1, 4, figsize=(20, 4.6))

    idx, cmap = panel_colours(y_true)
    axes[0].scatter(X[:, 0], X[:, 1], c=idx, cmap=cmap, s=3)
    axes[0].set_title(f"dataset - {VARIATION}, N={N_SAMPLES}")

    axes[1].hist(extractor.pheromone_matrix_.data, bins=100, color="#4a6fa5")
    axes[1].axvline(
        cut.value,
        color="#c0392b",
        lw=2,
        label=f"{THRESHOLD_PARAMS['method']} = {cut.value:.3f} (p{cut.percentile:.0f})",
    )
    axes[1].set_yscale("log")
    axes[1].set_title("pheromone field with cutoff")
    axes[1].legend()

    cores = clusterer_.labels_pheromone_
    idx, cmap = panel_colours(cores)
    axes[2].scatter(X[:, 0], X[:, 1], c=idx, cmap=cmap, s=3)
    axes[2].set_title(f"cores - {len(np.unique(cores[cores >= 0]))} found")

    idx, cmap = panel_colours(lab)
    axes[3].scatter(X[:, 0], X[:, 1], c=idx, cmap=cmap, s=3)
    axes[3].set_title(f"clusters - ARI_all {stats['ARI_all']:.3f}, noise {stats['NoisePct']:.1f}%")

    for ax in (axes[0], axes[2], axes[3]):
        ax.set_xlim(X[:, 0].min() - 1, X[:, 0].max() + 1)
        ax.set_ylim(X[:, 1].min() - 1, X[:, 1].max() + 1)

    aco_all = {**ACO_PARAMS, **aco_extra}
    fig.suptitle(
        f"{fork_name} / heuristics: {set_name} / seed {seed} - "
        f"{graph_params['metric']}, k={graph_params['n_neighbors']}, "
        f"mutual={graph_params['mutual']}, evap={aco_all['evaporation_rate']} "
        f"({aco_all['evaporation_schedule']}), {THRESHOLD_PARAMS['method']}",
        y=1.04,
    )
    fig.tight_layout()
    # fig.savefig(FIGURES_DIR / f"grid_{SWEEP_NAME}_{fork_name}_{set_name}.png", bbox_inches="tight")
    plt.show()


best = runs.sort("ARI_all", descending=True).group_by("fork", "heuristics").first().sort("fork", "heuristics")
print(best.select("fork", "heuristics", "seed", "ARI_all", "Clusters", "NoisePct"))

for row in best.iter_rows(named=True):
    draw_grid(row["fork"], row["heuristics"], row["seed"])

# %% [markdown]
# ## Done

# %%
tee.stop()
print(f"run log written to {NOTEBOOK_DIR / 'output.txt'}")
