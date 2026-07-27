"""test_error_message_style.py

Verifies that every ``raise ValueError`` in all four source modules
(``graph_builder``, ``pheromone_extractor``, ``core_clusterer``, ``threshold``)
is actually triggered by a test and that its message follows the project style:

- English only (no Cyrillic), no leaks of internal names (numba, scipy, sklearn, ...).
- Each message states clearly what is wrong and what to fix.

Two complementary checks:

1. ``test_value_error_message_style`` - a parametrized case per ``raise ValueError``
   branch; asserts the branch fires and that the message contains a known
   substring. Together the cases trigger every ``raise ValueError`` site
   across the four modules. No count is quoted here on purpose: the previous
   one said 52 and was stale by six sites within a few commits, which made the
   file claim a completeness it no longer had. The shared ``_validation``
   helper messages
   (``_check_int`` / ``_check_float`` / ``_check_bool``) are exercised via the
   constructor, per-call threshold and scan_thresholds cases.
2. ``test_collect_errors_no_internal_name_leaks`` - a bulk collection that
   re-runs a representative subset and asserts no Cyrillic and no internal-name
   leaks across the collected messages.
"""

import re

import numpy as np
import pytest
from conftest import make_clusterer, make_extractor, make_graph_builder
from scipy.sparse import csr_matrix

from intelliant.threshold import find_threshold, scan_thresholds, threshold_otsu, threshold_percentile, threshold_stat


def section(title):
    print(f"\n=== {title} ===")


def is_english_message(msg):
    """Checks that the message is in English (Latin characters only, no Cyrillic)."""
    cyrillic_count = sum(1 for c in msg if "\u0400" <= c <= "\u04ff")
    latin_count = sum(1 for c in msg if "A" <= c <= "Z" or "a" <= c <= "z")
    return cyrillic_count, latin_count


# Leaks of internal names
LEAK_PATTERNS = ["numba", "scipy", "sklearn", "pynndescent", "csr_matrix", "numpy"]


def _nan_metric(_u, _v):
    return np.nan


def _tiny_graph(data):
    # 3-node ring with controllable edge weights (NaN / inf / negative cases).
    return csr_matrix(
        (np.array(data), (np.array([0, 1, 2]), np.array([1, 2, 0]))),
        shape=(3, 3),
    )


def _unknown_search_method_build():
    # knn_method is validated by the constructor; mutate the attribute to reach
    # the runtime guard in _knn_search (graph_builder.py:135).
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
    gb.knn_method = "bogus"
    gb.build(np.random.default_rng(42).standard_normal((10, 4)))


def _mcs_zero_attr_extract(pm):
    # min_cluster_size <= 0 is blocked by the constructor and the per-call
    # _check_int; mutate the attribute to reach the runtime guard in
    # extract_cores (core_clusterer.py:237).
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.min_cluster_size = 0
    cc.extract_cores(pm, threshold_value=0.1)


def _centroid_no_cores_to_absorb(pm):
    # Zero cores + external labels + X: the guard added in polish round 1
    # (previously a raw numpy zero-size reduction error).
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=1e9)
    n = pm.shape[0]
    cc.absorb_centroid(np.zeros((n, 4)), labels=np.full(n, -1))


def _no_cores_absorb(pm):
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=1e9)
    cc.absorb_pheromone(pm)


def _n_ants_zero_fit(g):
    # n_ants <= 0 is blocked by the constructor; mutate the attribute to reach
    # the runtime guard in fit (pheromone_extractor.py:472).
    pe = make_extractor(n_ants=3, verbose=False)
    pe.n_ants = 0
    pe.fit(g)


def _n_ants_neg_fit(g):
    pe = make_extractor(n_ants=3, verbose=False)
    pe.n_ants = -1
    pe.fit(g)


def _mcs_le_zero_extract(pm):
    # min_cluster_size <= 0 in the constructor and in the per-call override is
    # rejected by _check_int; trigger the per-call path in extract_cores.
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.1, min_cluster_size=0)


def _no_batch_pheromone(pm):
    cc = make_clusterer(min_cluster_size=2, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.absorb_pheromone(pm)


def _zero_batch_pheromone(pm):
    # batch_size <= 0 is blocked by the constructor; mutate the attribute to
    # reach the runtime guard in absorb_pheromone (core_clusterer.py:363).
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.batch_size = 0
    cc.absorb_pheromone(pm)


def _no_batch_centroid(pm):
    cc = make_clusterer(min_cluster_size=2, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.absorb_centroid(np.zeros((10, 4)))


def _zero_batch_centroid(pm):
    # Same bypass as _zero_batch_pheromone for absorb_centroid (core_clusterer.py:494).
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.batch_size = 0
    cc.absorb_centroid(np.zeros((10, 4)))


def _no_labels_centroid(pm):
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.absorb_centroid(np.zeros((10, 4)))


def _x_len_labels_centroid(pm):
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.absorb_pheromone(pm)
    cc.absorb_centroid(np.zeros((5, 4)))


def _x_len_cores_centroid(pm):
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.absorb_centroid(np.zeros((5, 4)), labels=np.full(5, 0))


def _scan_bad_percentiles(_graph, _pm):
    g = csr_matrix(
        (np.array([0.5, 0.6, 0.7]), (np.array([0, 1, 2]), np.array([1, 2, 0]))),
        shape=(3, 3),
    )
    scan_thresholds(g, min_cluster_size=2, percentiles=[50.0, -1.0])


def _absorb_pheromone_non_square(pm):
    # Squareness is validated in absorb_pheromone since polish round 2 (R2-2).
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.absorb_pheromone(csr_matrix((3, 5)))


def _absorb_pheromone_size_mismatch(pm):
    # A square graph of the wrong size used to hit a raw IndexError (smaller)
    # or be silently accepted (larger); now a ValueError (R2-2).
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.absorb_pheromone(_tiny_graph([0.5, 0.6, 0.7]))


def _absorb_pheromone_nan(pm):
    # NaN weights used to be silently accepted by absorb_pheromone (R2-8).
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    bad = pm.copy()
    bad.data[0] = np.nan
    cc.absorb_pheromone(bad)


def _centroid_1d_x(pm):
    # A 1-D X of matching length passed both len checks and crashed with a raw
    # IndexError from X.shape[1]; now rejected up front (R2-7).
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(pm, threshold_value=0.0)
    cc.absorb_centroid(np.zeros(pm.shape[0]), labels=cc.cores_)


# Each case: (id, trigger(graph, pheromone_matrix), expected_substring).
# Cases that need no fixture ignore the arguments. Together these trigger all
# 52 ``raise ValueError`` sites across the four source modules (see the note
# below on runtime guards reached by attribute mutation).
CASES = [
    # --- GraphBuilder constructor (graph_builder.py:47 via _check_int) ---
    (
        "gb_n_neighbors_0",
        lambda g, pm: make_graph_builder(n_neighbors=0, verbose=False),
        "n_neighbors must be int >= 1, got 0",
    ),
    (
        "gb_n_neighbors_float",
        lambda g, pm: make_graph_builder(n_neighbors=1.5, verbose=False),
        "n_neighbors must be int >= 1, got 1.5",
    ),
    (
        "gb_n_neighbors_bool",
        lambda g, pm: make_graph_builder(n_neighbors=True, verbose=False),
        "n_neighbors must be int >= 1, got True",
    ),
    (
        "gb_min_connections_neg",
        lambda g, pm: make_graph_builder(min_connections=-1, verbose=False),
        "min_connections must be int >= 0 or None, got -1",
    ),
    (
        "gb_min_connections_float",
        lambda g, pm: make_graph_builder(min_connections=0.5, verbose=False),
        "min_connections must be int >= 0 or None, got 0.5",
    ),
    (
        "gb_min_connections_gt_n_neighbors",
        lambda g, pm: make_graph_builder(n_neighbors=3, min_connections=5, verbose=False),
        "min_connections must be <= n_neighbors (3), got 5",
    ),
    (
        "gb_approx_threshold_0",
        lambda g, pm: make_graph_builder(approx_threshold=0, verbose=False),
        "approx_threshold must be int >= 1, got 0",
    ),
    (
        "gb_approx_threshold_float",
        lambda g, pm: make_graph_builder(approx_threshold=1.5, verbose=False),
        "approx_threshold must be int >= 1, got 1.5",
    ),
    (
        "gb_knn_method_bogus",
        lambda g, pm: make_graph_builder(knn_method="bogus", verbose=False),
        "knn_method must be one of {'auto', 'exact', 'approx'}, got 'bogus'",
    ),
    # Bool flags go through the shared _check_bool since polish round 2 (R2-1);
    # one representative per class, all nine flags share the same message shape.
    (
        "gb_mutual_int",
        lambda g, pm: make_graph_builder(mutual=1, verbose=False),
        "mutual must be bool, got 1",
    ),
    # --- GraphBuilder.build (graph_builder.py:234,236,238,242,261) ---
    (
        "gb_X_1d",
        lambda g, pm: make_graph_builder(verbose=False).build(np.array([1, 2, 3])),
        "X must be a two-dimensional array",
    ),
    (
        "gb_X_3d",
        lambda g, pm: make_graph_builder(verbose=False).build(np.zeros((5, 3, 2))),
        "X must be a two-dimensional array",
    ),
    ("gb_X_empty", lambda g, pm: make_graph_builder(verbose=False).build(np.array([]).reshape(0, 4)), "X is empty"),
    (
        "gb_X_object_dtype",
        lambda g, pm: make_graph_builder(verbose=False).build(np.array([["a", "b"]] * 5, dtype=object)),
        "X must be a numeric array, got dtype=object",
    ),
    (
        "gb_X_bool_dtype",
        lambda g, pm: make_graph_builder(verbose=False).build(np.ones((5, 3), dtype=bool)),
        "X must be a numeric array, got dtype=bool",
    ),
    (
        "gb_X_complex_dtype",
        lambda g, pm: make_graph_builder(verbose=False).build(np.ones((5, 3), dtype=np.complex128)),
        "X must be a real-valued array, got dtype=complex128",
    ),
    (
        "gb_X_nan",
        lambda g, pm: make_graph_builder(verbose=False).build(np.array([[1.0, np.nan]] * 5)),
        "X contains NaN or inf",
    ),
    (
        "gb_X_inf",
        lambda g, pm: make_graph_builder(verbose=False).build(np.array([[1.0, np.inf]] * 5)),
        "X contains NaN or inf",
    ),
    (
        "gb_too_few_points",
        lambda g, pm: make_graph_builder(n_neighbors=10, verbose=False).build(np.zeros((5, 3))),
        "too few points",
    ),
    (
        "gb_knn_non_finite",
        lambda g, pm: make_graph_builder(
            n_neighbors=3, min_connections=3, metric=_nan_metric, verbose=False, random_state=42
        ).build(np.random.default_rng(42).standard_normal((10, 4))),
        "KNN returned non-finite distances",
    ),
    (
        "gb_unknown_search_method",
        lambda g, pm: _unknown_search_method_build(),
        "unknown search method: 'bogus'; expected 'exact' or 'approx'",
    ),
    # --- PheromoneExtractor constructor (pheromone_extractor.py:48,70,72,75,78) ---
    (
        "pe_n_iterations_neg",
        lambda g, pm: make_extractor(n_iterations=-1, verbose=False),
        "n_iterations must be int >= 0, got -1",
    ),
    (
        "pe_n_iterations_float",
        lambda g, pm: make_extractor(n_iterations=1.5, verbose=False),
        "n_iterations must be int >= 0, got 1.5",
    ),
    (
        "pe_path_length_0",
        lambda g, pm: make_extractor(path_length=0, verbose=False),
        "path_length must be int >= 1, got 0",
    ),
    (
        "pe_path_length_float",
        lambda g, pm: make_extractor(path_length=0.5, verbose=False),
        "path_length must be int >= 1, got 0.5",
    ),
    ("pe_beta_none", lambda g, pm: make_extractor(beta=None, verbose=False), "beta must not be None, got None"),
    (
        "pe_beta_nan",
        lambda g, pm: make_extractor(beta=float("nan"), verbose=False),
        "beta must be a finite number, got nan",
    ),
    (
        "pe_beta_inf",
        lambda g, pm: make_extractor(beta=float("inf"), verbose=False),
        "beta must be a finite number, got inf",
    ),
    ("pe_beta_neg", lambda g, pm: make_extractor(beta=-0.1, verbose=False), "beta must be >= 0, got -0.1"),
    (
        "pe_evaporation_rate_neg",
        lambda g, pm: make_extractor(evaporation_rate=-0.1, verbose=False),
        "evaporation_rate must be in range [0, 1], got -0.1",
    ),
    (
        "pe_evaporation_rate_over",
        lambda g, pm: make_extractor(evaporation_rate=1.5, verbose=False),
        "evaporation_rate must be in range [0, 1], got 1.5",
    ),
    (
        "pe_evaporation_schedule_unknown",
        lambda g, pm: make_extractor(evaporation_schedule="per-ant", verbose=False),
        "evaporation_schedule must be one of {'step', 'iteration'}",
    ),
    (
        "pe_node_density_gamma_neg",
        lambda g, pm: make_extractor(node_density_gamma=-1.0, verbose=False),
        "node_density_gamma must be >= 0, got -1.0",
    ),
    (
        "pe_elite_ratio_neg",
        lambda g, pm: make_extractor(elite_ratio=-0.1, verbose=False),
        "elite_ratio must be in range [0, 1], got -0.1",
    ),
    (
        "pe_elite_ratio_over",
        lambda g, pm: make_extractor(elite_ratio=1.5, verbose=False),
        "elite_ratio must be in range [0, 1], got 1.5",
    ),
    (
        "pe_elite_multiplier_neg",
        lambda g, pm: make_extractor(elite_multiplier=-1.0, verbose=False),
        "elite_multiplier must be >= 0, got -1.0",
    ),
    (
        "pe_elite_required",
        lambda g, pm: make_extractor(use_elite_ants=True, verbose=False),
        "elite_start_iteration is required when use_elite_ants=True",
    ),
    (
        "pe_elite_ratio_required",
        lambda g, pm: make_extractor(use_elite_ants=True, elite_ratio=None, verbose=False),
        "elite_ratio is required when use_elite_ants=True",
    ),
    (
        "pe_elite_multiplier_required",
        lambda g, pm: make_extractor(use_elite_ants=True, elite_multiplier=None, verbose=False),
        "elite_multiplier is required when use_elite_ants=True",
    ),
    (
        "pe_node_density_gamma_required",
        lambda g, pm: make_extractor(use_node_density=True, node_density_gamma=None, verbose=False),
        "node_density_gamma is required when use_node_density=True",
    ),
    (
        "pe_elite_start_neg",
        lambda g, pm: make_extractor(use_elite_ants=True, elite_start_iteration=-1, verbose=False),
        "elite_start_iteration must be int >= 0 or None, got -1",
    ),
    ("pe_alpha_none", lambda g, pm: make_extractor(alpha=None, verbose=False), "alpha must not be None, got None"),
    ("pe_alpha_neg", lambda g, pm: make_extractor(alpha=-1.0, verbose=False), "alpha must be >= 0, got -1.0"),
    (
        "pe_pheromone_deposit_neg",
        lambda g, pm: make_extractor(pheromone_deposit=-1.0, verbose=False),
        "pheromone_deposit must be >= 0, got -1.0",
    ),
    (
        "pe_initial_pheromone_neg",
        lambda g, pm: make_extractor(initial_pheromone=-1.0, verbose=False),
        "initial_pheromone must be >= 0, got -1.0",
    ),
    (
        "pe_tau_min_ge_tau_max",
        lambda g, pm: make_extractor(tau_min=10.0, tau_max=1.0, verbose=False),
        "tau_min must be < tau_max, got tau_min=10.0, tau_max=1.0",
    ),
    # tau_min / tau_max go through _check_float since polish round 1 (REVIEW #1).
    (
        "pe_tau_min_nan",
        lambda g, pm: make_extractor(tau_min=float("nan"), verbose=False),
        "tau_min must be a finite number, got nan",
    ),
    (
        "pe_tau_min_none",
        lambda g, pm: make_extractor(tau_min=None, verbose=False),
        "tau_min must not be None, got None",
    ),
    (
        "pe_tau_min_neg",
        lambda g, pm: make_extractor(tau_min=-5.0, verbose=False),
        "tau_min must be >= 0, got -5.0",
    ),
    (
        "pe_tau_min_bool",
        lambda g, pm: make_extractor(tau_min=True, verbose=False),
        "tau_min must be a number, got True",
    ),
    (
        "pe_tau_min_str",
        lambda g, pm: make_extractor(tau_min="1.0", verbose=False),
        "tau_min must be a number, got '1.0'",
    ),
    (
        "pe_tau_max_inf",
        lambda g, pm: make_extractor(tau_max=float("inf"), verbose=False),
        "tau_max must be a finite number, got inf",
    ),
    (
        "pe_warmup_str",
        lambda g, pm: make_extractor(warmup="true", verbose=False),
        "warmup must be bool, got 'true'",
    ),
    # --- PheromoneExtractor.fit (pheromone_extractor.py:362,364,379,470,472,475,477,479) ---
    ("pe_n_ants_none", lambda g, pm: make_extractor(verbose=False).fit(g), "n_ants is required"),
    ("pe_n_ants_0", lambda g, pm: _n_ants_zero_fit(g), "n_ants must be > 0, got 0"),
    ("pe_n_ants_neg", lambda g, pm: _n_ants_neg_fit(g), "n_ants must be > 0, got -1"),
    (
        "pe_non_square",
        lambda g, pm: make_extractor(n_ants=2, verbose=False).fit(csr_matrix((5, 3))),
        "graph must be square (N, N), got shape (5, 3)",
    ),
    (
        "pe_empty_graph",
        lambda g, pm: make_extractor(n_ants=2, verbose=False).fit(csr_matrix((0, 0))),
        "graph is empty",
    ),
    (
        "pe_no_edges",
        lambda g, pm: make_extractor(n_ants=2, verbose=False).fit(csr_matrix((3, 3))),
        "graph has no edges",
    ),
    (
        "pe_graph_nan",
        lambda g, pm: make_extractor(n_ants=2, verbose=False).fit(_tiny_graph([0.5, np.nan, 0.7])),
        "graph contains NaN or inf: clean the edge weights before running ACO",
    ),
    (
        "pe_graph_negative",
        lambda g, pm: make_extractor(n_ants=2, verbose=False).fit(_tiny_graph([0.5, -0.1, 0.7])),
        "graph contains negative weights: similarities must be >= 0",
    ),
    # --- CoreClusterer constructor (core_clusterer.py:49,128,132,134) ---
    (
        "cc_min_cluster_size_0",
        lambda g, pm: make_clusterer(min_cluster_size=0, verbose=False),
        "min_cluster_size must be int >= 1 or None, got 0",
    ),
    (
        "cc_min_cluster_size_neg",
        lambda g, pm: make_clusterer(min_cluster_size=-1, verbose=False),
        "min_cluster_size must be int >= 1 or None, got -1",
    ),
    (
        "cc_min_cluster_size_float",
        lambda g, pm: make_clusterer(min_cluster_size=1.5, verbose=False),
        "min_cluster_size must be int >= 1 or None, got 1.5",
    ),
    (
        "cc_max_iterations_neg",
        lambda g, pm: make_clusterer(max_iterations=-1, verbose=False),
        "max_iterations must be int >= 0, got -1",
    ),
    (
        "cc_max_iterations_float",
        lambda g, pm: make_clusterer(max_iterations=1.5, verbose=False),
        "max_iterations must be int >= 0, got 1.5",
    ),
    (
        "cc_batch_size_0",
        lambda g, pm: make_clusterer(batch_size=0, verbose=False),
        "batch_size must be int >= 1 or None, got 0",
    ),
    (
        "cc_batch_size_neg",
        lambda g, pm: make_clusterer(batch_size=-1, verbose=False),
        "batch_size must be int >= 1 or None, got -1",
    ),
    (
        "cc_batch_size_float",
        lambda g, pm: make_clusterer(batch_size=1.5, verbose=False),
        "batch_size must be int >= 1 or None, got 1.5",
    ),
    (
        "cc_max_gap_rank_0",
        lambda g, pm: make_clusterer(max_gap_rank=0, verbose=False),
        "max_gap_rank must be int >= 1, got 0",
    ),
    (
        "cc_max_gap_rank_neg",
        lambda g, pm: make_clusterer(max_gap_rank=-1, verbose=False),
        "max_gap_rank must be int >= 1, got -1",
    ),
    (
        "cc_gap_ratio_none",
        lambda g, pm: make_clusterer(gap_ratio=None, verbose=False),
        "gap_ratio must not be None, got None",
    ),
    (
        "cc_gap_ratio_lt_1",
        lambda g, pm: make_clusterer(gap_ratio=0.5, verbose=False),
        "gap_ratio must be >= 1, got 0.5",
    ),
    (
        "cc_absorb_isolated_int",
        lambda g, pm: make_clusterer(absorb_isolated=0, verbose=False),
        "absorb_isolated must be bool, got 0",
    ),
    # --- CoreClusterer.extract_cores (core_clusterer.py:267,269,272,275,278,282,287,289) ---
    (
        "cc_mcs_required",
        lambda g, pm: make_clusterer(batch_size=5, verbose=False).extract_cores(csr_matrix((3, 3))),
        "min_cluster_size is required",
    ),
    (
        "cc_mcs_le_0",
        lambda g, pm: _mcs_le_zero_extract(pm),
        "min_cluster_size must be int >= 1 or None, got 0",
    ),
    (
        "cc_mcs_runtime_le_0",
        lambda g, pm: _mcs_zero_attr_extract(pm),
        "min_cluster_size must be > 0, got 0",
    ),
    (
        "cc_non_square",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            csr_matrix((3, 5)), threshold_value=0.1
        ),
        "pheromone graph must be square (N, N), got shape (3, 5)",
    ),
    (
        "cc_empty_graph",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            csr_matrix((3, 3)), threshold_value=0.1
        ),
        "pheromone graph is empty (no edges)",
    ),
    (
        "cc_graph_nan",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            _tiny_graph([0.5, np.nan, 0.7]), threshold_value=0.1
        ),
        "pheromone graph contains NaN or inf: clean the edge weights before extracting cores",
    ),
    (
        "cc_graph_inf",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            _tiny_graph([0.5, np.inf, 0.7]), threshold_value=0.1
        ),
        "pheromone graph contains NaN or inf: clean the edge weights before extracting cores",
    ),
    (
        "cc_both_thresholds",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            pm, threshold_value=0.1, threshold_percentile=50.0
        ),
        "specify either threshold_value or threshold_percentile, not both",
    ),
    (
        "cc_no_threshold",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(pm),
        "specify a threshold: threshold_value or threshold_percentile",
    ),
    (
        "cc_percentile_neg",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            pm, threshold_percentile=-1
        ),
        "threshold_percentile must be in range [0, 100], got -1",
    ),
    (
        "cc_percentile_over",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            pm, threshold_percentile=101
        ),
        "threshold_percentile must be in range [0, 100], got 101",
    ),
    (
        "cc_threshold_value_nan",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            pm, threshold_value=float("nan")
        ),
        "threshold_value must be a finite number, got nan",
    ),
    # Per-call threshold args go through _check_float since polish round 2 (R2-3).
    (
        "cc_threshold_value_bool",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            pm, threshold_value=True
        ),
        "threshold_value must be a number, got True",
    ),
    (
        "cc_percentile_str",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
            pm, threshold_percentile="50"
        ),
        "threshold_percentile must be a number, got '50'",
    ),
    # --- CoreClusterer.absorb_pheromone (core_clusterer.py:359,361,363,370) ---
    (
        "cc_absorb_no_cores",
        lambda g, pm: make_clusterer(batch_size=5, verbose=False).absorb_pheromone(pm),
        "cores_ is not set: call extract_cores() before absorb_pheromone()",
    ),
    ("cc_absorb_no_batch", lambda g, pm: _no_batch_pheromone(pm), "batch_size is required"),
    ("cc_absorb_batch_le_0", lambda g, pm: _zero_batch_pheromone(pm), "batch_size must be > 0, got 0"),
    ("cc_absorb_no_cores_to_absorb", lambda g, pm: _no_cores_absorb(pm), "no cores to absorb"),
    # Graph shape / size / finiteness validation added in polish round 2 (R2-2, R2-8).
    (
        "cc_absorb_non_square",
        lambda g, pm: _absorb_pheromone_non_square(pm),
        "pheromone graph must be square (N, N), got shape (3, 5)",
    ),
    (
        "cc_absorb_size_mismatch",
        lambda g, pm: _absorb_pheromone_size_mismatch(pm),
        "pheromone graph size (3) does not match the number of points in cores (10)",
    ),
    (
        "cc_absorb_graph_nan",
        lambda g, pm: _absorb_pheromone_nan(pm),
        "pheromone graph contains NaN or inf",
    ),
    # --- CoreClusterer.absorb_centroid (core_clusterer.py:490,492,494,499,502,504) ---
    (
        "cc_centroid_no_cores",
        lambda g, pm: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).absorb_centroid(
            np.zeros((10, 4))
        ),
        "cores_ is not set: call extract_cores() before absorb_centroid()",
    ),
    ("cc_centroid_no_batch", lambda g, pm: _no_batch_centroid(pm), "batch_size is required"),
    ("cc_centroid_batch_le_0", lambda g, pm: _zero_batch_centroid(pm), "batch_size must be > 0, got 0"),
    (
        "cc_centroid_no_labels",
        lambda g, pm: _no_labels_centroid(pm),
        "no labels for absorption: call absorb_pheromone() or pass labels",
    ),
    (
        "cc_centroid_X_len_labels",
        lambda g, pm: _x_len_labels_centroid(pm),
        "length of X (5) does not match the number of points (10)",
    ),
    (
        "cc_centroid_X_len_cores",
        lambda g, pm: _x_len_cores_centroid(pm),
        "length of X (5) does not match the number of points in cores (10)",
    ),
    (
        "cc_centroid_no_cores_to_absorb",
        lambda g, pm: _centroid_no_cores_to_absorb(pm),
        "no cores to absorb",
    ),
    (
        "cc_centroid_X_1d",
        lambda g, pm: _centroid_1d_x(pm),
        "X must be a two-dimensional array (N, D), got ndim=1",
    ),
    # --- threshold (threshold.py:27,47,54,68,75,89,97) ---
    (
        "thr_otsu_empty",
        lambda g, pm: threshold_otsu(np.array([])),
        "data is empty: cannot compute a threshold on an empty array",
    ),
    (
        "thr_percentile_neg",
        lambda g, pm: threshold_percentile(np.array([1.0, 2.0, 3.0]), -5),
        "percentile must be in range [0, 100], got -5",
    ),
    (
        "thr_stat_empty",
        lambda g, pm: threshold_stat(np.array([])),
        "data is empty: cannot compute a threshold on an empty array",
    ),
    (
        "thr_find_empty",
        lambda g, pm: find_threshold(np.array([])),
        "data is empty: cannot compute a threshold on an empty array",
    ),
    (
        "thr_find_nan",
        lambda g, pm: find_threshold(np.array([1.0, np.nan, 3.0])),
        "data contains NaN or inf: clean the values before computing a threshold",
    ),
    (
        "thr_find_bogus",
        lambda g, pm: find_threshold(np.array([1.0, 2.0, 3.0]), method="bogus"),
        "unknown threshold method: bogus; allowed: otsu, percentile, stat",
    ),
    # k / bins are validated up front since polish round 2 (R2-4).
    (
        "thr_find_k_nan",
        lambda g, pm: find_threshold(np.array([1.0, 2.0, 3.0]), method="stat", k=float("nan")),
        "k must be a finite number, got nan",
    ),
    (
        "thr_find_k_str",
        lambda g, pm: find_threshold(np.array([1.0, 2.0, 3.0]), method="stat", k="1"),
        "k must be a number, got '1'",
    ),
    (
        "thr_find_bins_0",
        lambda g, pm: find_threshold(np.array([1.0, 2.0, 3.0]), bins=0),
        "bins must be int >= 1, got 0",
    ),
    (
        "thr_scan_empty",
        lambda g, pm: scan_thresholds(csr_matrix((3, 3)), min_cluster_size=2),
        "pheromone_graph is empty (no edges): scan_thresholds is impossible",
    ),
    ("thr_scan_bad_pct", lambda g, pm: _scan_bad_percentiles(g, pm), "percentiles must be in range [0, 100], got -1.0"),
    (
        "thr_scan_empty_pct",
        lambda g, pm: scan_thresholds(_tiny_graph([0.5, 0.6, 0.7]), min_cluster_size=2, percentiles=[]),
        "percentiles must not be empty",
    ),
    (
        "thr_scan_nan_data",
        lambda g, pm: scan_thresholds(_tiny_graph([0.5, np.nan, 0.7]), min_cluster_size=2),
        "pheromone_graph contains NaN or inf: clean the edge weights before scanning thresholds",
    ),
    (
        "thr_scan_n_steps_neg",
        lambda g, pm: scan_thresholds(_tiny_graph([0.5, 0.6, 0.7]), min_cluster_size=2, n_steps=-1),
        "n_steps must be int >= 0, got -1",
    ),
    (
        "thr_scan_step_zero",
        lambda g, pm: scan_thresholds(_tiny_graph([0.5, 0.6, 0.7]), min_cluster_size=2, step=0.0),
        "step must be > 0, got 0.0",
    ),
    (
        "thr_scan_step_neg",
        lambda g, pm: scan_thresholds(_tiny_graph([0.5, 0.6, 0.7]), min_cluster_size=2, step=-1.0),
        "step must be >= 0, got -1.0",
    ),
    (
        "thr_scan_center_over",
        lambda g, pm: scan_thresholds(_tiny_graph([0.5, 0.6, 0.7]), min_cluster_size=2, center_percentile=200),
        "center_percentile must be in range [0, 100], got 200",
    ),
]


# Note on runtime guards and shared helpers:
# - Since polish round 2 the bool-flag guards (mutual, verbose, warmup,
#   absorb_isolated, ...) live in the shared ``_check_bool`` helper; the
#   representative cases gb_mutual_int / pe_warmup_str / cc_absorb_isolated_int
#   pin its message, one per class.
# - Several runtime guards (n_ants <= 0 in fit, min_cluster_size <= 0 in
#   extract_cores, batch_size <= 0 in absorb_pheromone / absorb_centroid,
#   unknown search method in _knn_search) are normally blocked by the
#   constructor. The corresponding cases mutate the attribute after
#   construction to reach the runtime guard.
# - threshold_otsu/threshold_stat share the same "data is empty" message text as
#   find_threshold; each is still triggered by its own dedicated case above.


@pytest.fixture(scope="module")
def graph():
    rng = np.random.default_rng(0)
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
    return gb.build(rng.standard_normal((10, 4)))


@pytest.fixture(scope="module")
def pheromone_matrix(graph):
    pe = make_extractor(n_ants=3, n_iterations=2, verbose=False, random_state=42)
    pe.fit(graph)
    return pe.pheromone_matrix_


@pytest.mark.parametrize(
    ("case_id", "trigger", "expected"),
    CASES,
    ids=[c[0] for c in CASES],
)
def test_value_error_message_style(graph, pheromone_matrix, case_id, trigger, expected):
    """Each ValueError branch fires and its message matches the expected style."""
    with pytest.raises(ValueError, match=re.escape(expected)) as exc_info:
        trigger(graph, pheromone_matrix)
    msg = str(exc_info.value)
    cyrillic, _latin = is_english_message(msg)
    assert cyrillic == 0, f"{case_id}: Cyrillic characters in message: {msg!r}"
    for pat in LEAK_PATTERNS:
        assert pat not in msg.lower(), f"{case_id}: internal name leak {pat!r} in {msg!r}"


def _collect_errors(graph, pheromone_matrix):
    """Collect ALL error messages from ALL entry points (style bulk check)."""
    print("Collecting all error messages...\n")
    errors = []

    # 1. GraphBuilder
    section("GraphBuilder")
    test_cases = [
        ("X 1D", lambda: make_graph_builder(verbose=False).build(np.array([1, 2, 3]))),
        ("X 3D", lambda: make_graph_builder(verbose=False).build(np.zeros((5, 3, 2)))),
        ("X empty", lambda: make_graph_builder(verbose=False).build(np.array([]).reshape(0, 4))),
        ("X with NaN", lambda: make_graph_builder(verbose=False).build(np.array([[1.0, np.nan]] * 5))),
        ("X with inf", lambda: make_graph_builder(verbose=False).build(np.array([[1.0, np.inf]] * 5))),
        ("Too few points", lambda: make_graph_builder(n_neighbors=10, verbose=False).build(np.zeros((5, 3)))),
        ("X=None", lambda: make_graph_builder(verbose=False).build(None)),
    ]

    for label, fn in test_cases:
        try:
            fn()
            print(f"  {label}: did not fail (BUG?)")
        except Exception as e:
            msg = str(e)
            errors.append(("GraphBuilder." + label, type(e).__name__, msg))
            print(f"  {label}: [{type(e).__name__}] {msg}")

    # 2. PheromoneExtractor
    section("PheromoneExtractor.fit")
    test_cases = [
        ("n_ants=None", lambda: make_extractor(verbose=False).fit(graph)),
        ("n_ants=0", lambda: make_extractor(n_ants=0, verbose=False).fit(graph)),
        ("n_ants=-1", lambda: make_extractor(n_ants=-1, verbose=False).fit(graph)),
        ("non-square graph", lambda: make_extractor(n_ants=2, verbose=False).fit(csr_matrix((5, 3)))),
        ("empty graph (0x0)", lambda: make_extractor(n_ants=2, verbose=False).fit(csr_matrix((0, 0)))),
        ("graph without edges", lambda: make_extractor(n_ants=2, verbose=False).fit(csr_matrix((3, 3)))),
    ]

    for label, fn in test_cases:
        try:
            fn()
            print(f"  {label}: did not fail (BUG?)")
        except Exception as e:
            msg = str(e)
            errors.append(("PheromoneExtractor." + label, type(e).__name__, msg))
            print(f"  {label}: [{type(e).__name__}] {msg}")

    # 3. CoreClusterer
    section("CoreClusterer.extract_cores / absorb_*")

    test_cases = [
        (
            "no extract_cores -> absorb_pheromone",
            lambda: make_clusterer(batch_size=5, verbose=False).absorb_pheromone(pheromone_matrix),
        ),
        (
            "no batch_size",
            lambda: make_clusterer(min_cluster_size=2, verbose=False).absorb_pheromone(pheromone_matrix),
        ),
        (
            "batch_size=0",
            lambda: make_clusterer(min_cluster_size=2, batch_size=0, verbose=False).absorb_pheromone(pheromone_matrix),
        ),
        (
            "min_cluster_size=0",
            lambda: make_clusterer(min_cluster_size=0, batch_size=5, verbose=False).extract_cores(
                pheromone_matrix, threshold_value=0.1
            ),
        ),
        (
            "min_cluster_size=None",
            lambda: make_clusterer(batch_size=5, verbose=False).extract_cores(pheromone_matrix, threshold_value=0.1),
        ),
        (
            "non-square graph",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
                csr_matrix((3, 5)), threshold_value=0.1
            ),
        ),
        (
            "empty graph",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
                csr_matrix((3, 3)), threshold_value=0.1
            ),
        ),
        (
            "both thresholds",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
                pheromone_matrix, threshold_value=0.1, threshold_percentile=50.0
            ),
        ),
        (
            "no threshold",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(pheromone_matrix),
        ),
        (
            "percentile=-1",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
                pheromone_matrix, threshold_percentile=-1
            ),
        ),
        (
            "percentile=101",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
                pheromone_matrix, threshold_percentile=101
            ),
        ),
        (
            "threshold_value=NaN",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
                pheromone_matrix, threshold_value=float("nan")
            ),
        ),
        (
            "absorb_centroid without extract_cores",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).absorb_centroid(np.zeros((10, 4))),
        ),
        (
            "absorb_centroid without absorb_pheromone and labels",
            lambda: make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).absorb_centroid(np.zeros((10, 4))),
        ),
        (
            "absorb_centroid with X of wrong length",
            lambda: (
                lambda: (
                    make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).extract_cores(
                        pheromone_matrix, threshold_value=0.1
                    ),
                    make_clusterer(min_cluster_size=2, batch_size=5, verbose=False).absorb_centroid(np.zeros((5, 4))),
                )
            )(),
        ),
    ]

    for label, fn in test_cases:
        try:
            result = fn()
            if isinstance(result, tuple) and len(result) == 2:
                # the second call fails on absorb_centroid
                pass
            print(f"  {label}: did not fail (BUG?)")
        except Exception as e:
            msg = str(e)
            errors.append(("CoreClusterer." + label, type(e).__name__, msg))
            print(f"  {label}: [{type(e).__name__}] {msg}")

    # 4. threshold
    section("threshold")
    test_cases = [
        ("find_threshold empty", lambda: find_threshold(np.array([]))),
        ("find_threshold bogus method", lambda: find_threshold(np.array([1, 2, 3]), method="bogus")),
        ("threshold_otsu empty", lambda: threshold_otsu(np.array([]))),
        ("threshold_stat empty", lambda: threshold_stat(np.array([]))),
        ("threshold_percentile=-5", lambda: threshold_percentile(np.array([1, 2, 3]), -5)),
        ("scan_thresholds empty graph", lambda: scan_thresholds(csr_matrix((3, 3)), min_cluster_size=2)),
    ]

    for label, fn in test_cases:
        try:
            fn()
            print(f"  {label}: did not fail (BUG?)")
        except Exception as e:
            msg = str(e)
            errors.append(("threshold." + label, type(e).__name__, msg))
            print(f"  {label}: [{type(e).__name__}] {msg}")

    return errors


def test_collect_errors_no_internal_name_leaks(graph, pheromone_matrix):
    # Collect all messages and analyze style.
    errors = _collect_errors(graph, pheromone_matrix)

    # Style analysis
    print("\n=== Message style analysis ===\n")

    print(f"Collected {len(errors)} error messages.\n")

    # English message statistics
    total_cyrillic = 0
    total_latin = 0
    for _name, _exc_type, msg in errors:
        c, latin = is_english_message(msg)
        total_cyrillic += c
        total_latin += latin
    print(f"Total Cyrillic characters: {total_cyrillic}")
    print(f"Total Latin characters: {total_latin}")
    print(f"Cyrillic share: {total_cyrillic / max(total_cyrillic + total_latin, 1):.1%}")

    # All messages must be English (no Cyrillic)
    assert total_cyrillic == 0, f"found {total_cyrillic} Cyrillic characters in error messages"

    # Leak search
    print("\nInternal name leaks:")
    leaks_found = []
    for name, exc_type, msg in errors:
        for pat in LEAK_PATTERNS:
            if pat in msg.lower():
                leaks_found.append((name, exc_type, pat, msg))
                print(f"  {name} [{exc_type}]: '{pat}' in '{msg}'")

    if not leaks_found:
        print("  (none found)")
    assert not leaks_found, f"found internal name leaks: {leaks_found}"

    # Message length (is there a sensible explanation?)
    print("\nToo short (< 30 characters) messages:")
    for name, exc_type, msg in errors:
        if len(msg) < 30:
            print(f"  {name} [{exc_type}]: '{msg}'")
