"""test_validation_refactor.py
# F.5 (iteration 3): a comprehensive check of the new validation against the table
# from TASK.md. Each parameter with a changed/added boundary is a separate case.
# Includes positive (boundary = 1) and negative (-1 / -0.1 / 0 where it should be
# an error) scenarios.
"""

import warnings

import numpy as np
import pytest
from conftest import make_clusterer, make_extractor, make_graph_builder


def section(title):
    print(f"\n=== {title} ===")


# --- Boundary values (>= 1) ---
def test_boundary_values_ge_one():
    section("Boundary values >= 1")

    # GraphBuilder
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(n_neighbors=0)
    make_graph_builder(n_neighbors=1, min_connections=1)
    with pytest.raises((ValueError, TypeError)):
        make_graph_builder(approx_threshold=0)
    make_graph_builder(approx_threshold=1)

    # PheromoneExtractor
    make_extractor(n_ants=1)
    make_extractor(n_ants=1, path_length=1)

    # CoreClusterer
    make_clusterer(min_cluster_size=1, batch_size=10)
    make_clusterer(min_cluster_size=2, batch_size=1)
    make_clusterer(min_cluster_size=2, batch_size=10, max_gap_rank=1)


# --- Relaxed validation (>= 0 instead of > 0) ---
def test_relaxed_validation_beta_alpha_zero():
    section("Relaxed validation: beta=0 and alpha=0 are now VALID")

    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, beta=-0.1)
    make_extractor(n_ants=1, beta=0)  # ACO on pure pheromone
    make_extractor(n_ants=1, beta=0.0)

    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, alpha=-0.1)
    make_extractor(n_ants=1, alpha=0)  # ACO on pure weights
    make_extractor(n_ants=1, alpha=0.0)


# --- New validations (>= 0) ---
def test_new_validations_ge_zero():
    section("New validations: >= 0")

    # node_density_gamma
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, node_density_gamma=-1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, node_density_gamma=-0.1)
    make_extractor(n_ants=1, node_density_gamma=0)
    make_extractor(n_ants=1, node_density_gamma=0.0)

    # elite_ratio
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_ratio=-0.1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_ratio=-1)
    make_extractor(n_ants=1, elite_ratio=0)
    make_extractor(n_ants=1, elite_ratio=1.0)  # all ants are elite

    # elite_multiplier
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_multiplier=-1)
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, elite_multiplier=-0.5)
    make_extractor(n_ants=1, elite_multiplier=0)  # degenerate

    # pheromone_deposit
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, pheromone_deposit=-0.1)
    make_extractor(n_ants=1, pheromone_deposit=0)  # no deposit; evaporation only

    # initial_pheromone
    with pytest.raises((ValueError, TypeError)):
        make_extractor(n_ants=1, initial_pheromone=-0.1)
    make_extractor(n_ants=1, initial_pheromone=0)  # start from zero


# --- Strengthened validation (>= 1 instead of > 0) ---
def test_strengthened_validation_ge_one():
    section("Strengthened validation: >= 1 (was > 0)")

    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=0, batch_size=10)
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=0)
    with pytest.raises((ValueError, TypeError)):
        make_clusterer(min_cluster_size=2, batch_size=10, max_gap_rank=0)


# --- fit behavior: elite_ratio=0 + use_elite_ants=True -> UserWarning ---
def _build_graph():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((15, 4))
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42)
    return gb.build(X)


def test_elite_ratio_zero_with_use_elite_ants_warns():
    section("elite_ratio=0 with use_elite_ants=True -> warning about n_elite=0")

    G = _build_graph()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        pe = make_extractor(
            n_ants=10,
            use_elite_ants=True,
            elite_start_iteration=0,
            elite_ratio=0.0,
            verbose=False,
            random_state=42,
        )
        pe.fit(G)
        user_warnings = [x for x in w if issubclass(x.category, UserWarning)]
    assert user_warnings, f"expected UserWarning, total warnings={len(w)}"


# --- elite_ratio=0.1 -> n_elite=1, fit without warning ---
def test_elite_ratio_01_no_warning():
    section("elite_ratio=0.1 with n_ants=10 -> n_elite=1 without warning")

    G = _build_graph()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        pe = make_extractor(
            n_ants=10,
            use_elite_ants=True,
            elite_start_iteration=0,
            elite_ratio=0.1,
            verbose=False,
            random_state=42,
        )
        pe.fit(G)
    assert len(w) == 0


# --- use_elite_ants=False + elite_ratio=0.5 -> fit works without warning ---
def test_use_elite_ants_false_ratio_ignored_no_warning():
    section("use_elite_ants=False + elite_ratio=0.5 -> ratio is not used, fit without warning")

    G = _build_graph()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        pe = make_extractor(
            n_ants=5,
            use_elite_ants=False,
            elite_ratio=0.5,
            verbose=False,
            random_state=42,
        )
        pe.fit(G)
    assert len(w) == 0


# --- beta=0 / alpha=0 on fit ---
def test_beta_alpha_zero_fit():
    section("beta=0 / alpha=0 on fit (F.5: relaxation)")

    G = _build_graph()
    for label, kwargs in [
        ("beta=0", {"beta": 0.0}),
        ("alpha=0", {"alpha": 0.0}),
        ("beta=0 + alpha=0", {"beta": 0.0, "alpha": 0.0}),
    ]:
        print(f"  {label}:")
        pe = make_extractor(n_ants=5, verbose=False, random_state=42, **kwargs)
        pe.fit(G)
        print(f"    OK: range=[{pe.pheromone_matrix_.data.min():.3f}, {pe.pheromone_matrix_.data.max():.3f}]")
