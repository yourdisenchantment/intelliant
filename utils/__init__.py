"""Helpers for the calibration notebooks.

Not part of the published package - `intelliant` on PyPI ships `src/intelliant`
alone. These exist so that notebooks stay about the experiment rather than
about plumbing, and so that a helper fixed once is fixed everywhere.

Notebooks import them after putting the repository root on `sys.path`; see the
import-cell order in AGENTS.md.
"""

from .graph import graph_baseline, graph_report
from .metrics import evaluate_clustering
from .tee import Tee

__all__ = ["Tee", "evaluate_clustering", "graph_baseline", "graph_report"]
