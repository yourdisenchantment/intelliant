"""test_required_parameters.py

Locks the contract introduced when calibratable defaults were removed: while
calibration is in progress the library must not silently supply a value for a
parameter that calibration has not settled. Omitting one is a TypeError at
construction, not a quietly applied default.

Also locks that the constructors are keyword-only. With 20+ parameters a
positional call is unreadable, and keyword-only removes any dependence on
declaration order.
"""

import pytest
from conftest import BASE_CORE, BASE_GRAPH, BASE_PHEROMONE

from intelliant import CoreClusterer, GraphBuilder, PheromoneExtractor

# Required = no default in the signature. Heuristic parameters are NOT here:
# they are required only when the matching use_* flag is on, which is asserted
# in test_error_message_style.py as a ValueError instead.
REQUIRED_GRAPH = ["n_neighbors", "metric", "mutual"]
REQUIRED_PHEROMONE = [
    "n_iterations",
    "path_length",
    "beta",
    "alpha",
    "evaporation_rate",
    "evaporation_schedule",
    "pheromone_deposit",
    "initial_pheromone",
    "tau_min",
    "tau_max",
]
REQUIRED_CORE = ["max_iterations", "gap_ratio", "max_gap_rank"]

CASES = (
    [("GraphBuilder", GraphBuilder, BASE_GRAPH, p) for p in REQUIRED_GRAPH]
    + [("PheromoneExtractor", PheromoneExtractor, BASE_PHEROMONE, p) for p in REQUIRED_PHEROMONE]
    + [("CoreClusterer", CoreClusterer, BASE_CORE, p) for p in REQUIRED_CORE]
)


@pytest.mark.parametrize(
    ("cls_name", "cls", "base", "missing"),
    CASES,
    ids=[f"{name}.{param}" for name, _, _, param in CASES],
)
def test_omitting_a_required_parameter_raises(cls_name, cls, base, missing):
    """Every calibratable parameter must be stated explicitly."""

    kwargs = {k: v for k, v in base.items() if k != missing}
    with pytest.raises(TypeError, match=missing):
        cls(**kwargs, verbose=False)


@pytest.mark.parametrize(
    ("cls_name", "cls", "base"),
    [
        ("GraphBuilder", GraphBuilder, BASE_GRAPH),
        ("PheromoneExtractor", PheromoneExtractor, BASE_PHEROMONE),
        ("CoreClusterer", CoreClusterer, BASE_CORE),
    ],
    ids=["GraphBuilder", "PheromoneExtractor", "CoreClusterer"],
)
def test_full_parameter_set_constructs(cls_name, cls, base):
    """The complete set is accepted - the cases above fail for the missing
    parameter, not because the set itself is wrong."""

    assert cls(**base, verbose=False) is not None


@pytest.mark.parametrize(
    ("cls_name", "cls", "first_positional"),
    [
        ("GraphBuilder", GraphBuilder, 15),
        ("PheromoneExtractor", PheromoneExtractor, 20),
        ("CoreClusterer", CoreClusterer, 20),
    ],
    ids=["GraphBuilder", "PheromoneExtractor", "CoreClusterer"],
)
def test_constructors_are_keyword_only(cls_name, cls, first_positional):
    """A positional argument must be refused, so that parameter order in the
    signature is never part of the public contract."""

    with pytest.raises(TypeError, match="positional"):
        cls(first_positional)


def test_heuristic_parameters_are_not_required_while_off():
    """Heuristic parameters stay optional when their flag is off - requiring
    elite_ratio from a caller that disabled elite ants would be noise."""

    pe = PheromoneExtractor(**{k: v for k, v in BASE_PHEROMONE.items() if not _is_heuristic(k)}, verbose=False)
    assert pe.elite_ratio is None
    assert pe.elite_multiplier is None
    assert pe.node_density_gamma is None


def _is_heuristic(name: str) -> bool:
    return name in {"node_density_gamma", "elite_ratio", "elite_multiplier"}


# The flags are public attributes and the staged design invites editing an
# already-built instance, so the pairing is re-checked at fit time too - the
# constructor guarantee does not survive a post-construction assignment.
@pytest.mark.parametrize(
    ("flag", "param", "message"),
    [
        ("use_node_density", "node_density_gamma", "node_density_gamma is required when use_node_density=True"),
        ("use_elite_ants", "elite_ratio", "elite_ratio is required when use_elite_ants=True"),
    ],
    ids=["node_density", "elite_ratio"],
)
def test_flag_flipped_after_construction_is_caught_at_fit(flag, param, message, small_graph):
    kwargs = {k: v for k, v in BASE_PHEROMONE.items() if k != param}
    kwargs |= {"n_ants": 4, "n_iterations": 1, "verbose": False, "random_state": 42}
    pe = PheromoneExtractor(**kwargs)
    setattr(pe, flag, True)
    if flag == "use_elite_ants":
        pe.elite_start_iteration = 0
    with pytest.raises(ValueError, match=message):
        pe.fit(small_graph)
