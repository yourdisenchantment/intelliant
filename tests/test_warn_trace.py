"""test_warn_trace.py
# Isolating the source of a warning in test_degenerate_endtoend.py.
"""

import traceback
import warnings

import numpy as np
from conftest import make_clusterer, make_extractor, make_graph_builder


def test_warn_trace_no_unexpected_warning():
    # Intercept all warnings and trace where they came from.
    original_warn = warnings.warn

    def traced_warn(message, *args, **kwargs):
        print(f"!!! WARNING: {message} (kwargs={kwargs})")
        traceback.print_stack()
        return original_warn(message, *args, **kwargs)

    warnings.warn = traced_warn
    try:
        # Reproduce the scenario.
        rng = np.random.default_rng(42)
        X_noise = rng.standard_normal((50, 5))
        gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=42, mutual=False)
        G_noise = gb.build(X_noise)
        pe = make_extractor(n_ants=20, n_iterations=10, verbose=False, random_state=42)
        pe.fit(G_noise)
        labels = make_clusterer(min_cluster_size=3, batch_size=10, verbose=False).fit_predict(
            pe.pheromone_matrix_, threshold_percentile=90.0, X=X_noise
        )
        assert isinstance(labels, np.ndarray)
    finally:
        warnings.warn = original_warn
