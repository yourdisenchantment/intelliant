# src/intelliant/graph_builder.py
"""Build a sparse similarity graph from embeddings.

The rest of the pipeline never sees the embeddings. Everything downstream
works on the graph built here, which is what makes the algorithm independent
of dimensionality: 2 features and 768 features look the same to the ants once
the neighbourhood structure is fixed.
"""

import warnings
from time import perf_counter

import numpy as np
import scipy.sparse
from pynndescent import NNDescent
from sklearn.neighbors import NearestNeighbors
from tqdm.auto import tqdm

from ._validation import _check_bool, _check_int


class GraphBuilder:
    """Build a symmetric k-nearest-neighbour similarity graph.

    The graph is the algorithm's actual input, and its structure bounds what
    every later stage can achieve: no pheromone threshold can separate two
    clusters that the KNN graph already merged into one connected component.
    When results disappoint, check the graph before touching ACO parameters.

    Attributes:
        graph_: The graph produced by the last `build` call, or None. Public
            on purpose - the staged design expects it to be inspected and, if
            need be, edited before being handed to `PheromoneExtractor`.

    Example:
        >>> builder = GraphBuilder(n_neighbors=15, metric="cosine", mutual=True)
        >>> graph = builder.build(embeddings)  # doctest: +SKIP
    """

    def __init__(
        self,
        *,
        n_neighbors: int,
        metric: str,
        mutual: bool,
        min_connections: int | None = None,
        knn_method: str = "auto",
        approx_threshold: int = 50_000,
        random_state: int | None = None,
        verbose: bool = True,
    ) -> None:
        """Configure the builder.

        Every argument is keyword-only, and the ones that shape the result
        carry no default: while calibration is in progress a default is a
        value nobody chose, applied silently.

        Args:
            n_neighbors: Neighbours per point, excluding the point itself.
                The single most consequential choice here - too small
                fragments genuine clusters, too large fuses distinct ones
                beyond any later repair.
            metric: Distance metric. A name understood by the search backend
                (`"cosine"`, `"euclidean"`, ...) or a callable taking two
                vectors. Must be symmetric: AND-symmetrization keeps the
                stored value of one direction and assumes the other matches.
            mutual: How to symmetrize. True keeps an edge only when both
                points chose each other (AND) - sparser, cleaner boundaries.
                False keeps an edge chosen by either (OR) - denser, more
                forgiving, more prone to bridges between clusters.
            min_connections: Vertices below this degree get their strongest
                original neighbours restored, so symmetrization cannot strand
                a point. None resolves to `min(5, n_neighbors)`; 0 disables
                the top-up.
            knn_method: `"exact"` (sklearn), `"approx"` (pynndescent), or
                `"auto"` to pick by dataset size.
            approx_threshold: Point count above which `"auto"` chooses the
                approximate search.
            random_state: Seed for the approximate search. The exact search is
                deterministic and ignores it. Note that pynndescent
                parallelizes by default, and a fixed seed does not by itself
                guarantee a bit-identical graph.
            verbose: Whether to report progress and timings.

        Raises:
            ValueError: If any argument is outside its valid range, of the
                wrong type, or if `min_connections` exceeds `n_neighbors`.
        """
        self.n_neighbors = _check_int("n_neighbors", n_neighbors, 1)

        # A name or a callable, and nothing narrower: sklearn and pynndescent
        # each accept their own set of names plus user-supplied distance
        # functions, so checking against a hardcoded list would reject metrics
        # that work. A misspelled name still surfaces from the backend; what is
        # caught here is a value that could never be a metric at all.
        if not isinstance(metric, str) and not callable(metric):
            raise ValueError(f"metric must be a string or a callable, got {type(metric).__name__}")
        self.metric = metric

        self.mutual = _check_bool("mutual", mutual)

        min_connections = _check_int("min_connections", min_connections, 0, allow_none=True)
        if min_connections is None:
            min_connections = min(5, self.n_neighbors)
        if min_connections > self.n_neighbors:
            raise ValueError(f"min_connections must be <= n_neighbors ({self.n_neighbors}), got {min_connections}")
        self.min_connections = min_connections

        if knn_method not in {"auto", "exact", "approx"}:
            raise ValueError(f"knn_method must be one of {{'auto', 'exact', 'approx'}}, got {knn_method!r}")
        self.knn_method = knn_method

        self.approx_threshold = _check_int("approx_threshold", approx_threshold, 1)

        self.random_state = _check_int("random_state", random_state, 0, allow_none=True)
        self.verbose = _check_bool("verbose", verbose)

        self.graph_: scipy.sparse.csr_matrix | None = None

    def _log(self, msg: str) -> None:
        """Write a progress message when verbose, via tqdm to avoid clobbering bars."""
        if self.verbose:
            tqdm.write(msg)

    def _knn_search(self, X: np.ndarray, method: str) -> tuple[np.ndarray, np.ndarray]:
        """Find `n_neighbors + 1` neighbours per point.

        One extra, because the backends return the point itself and `build`
        strips it afterwards.

        Args:
            X: Feature matrix of shape (N, D).
            method: Resolved search method, `"exact"` or `"approx"` - never
                `"auto"`, which the caller has already resolved.

        Returns:
            `(distances, indices)`, both of shape (N, n_neighbors + 1).

        Raises:
            ValueError: If `method` is neither `"exact"` nor `"approx"`.
        """
        if method == "exact":
            nbrs = NearestNeighbors(
                n_neighbors=self.n_neighbors + 1,
                metric=self.metric,
                n_jobs=-1,
            ).fit(X)
            distances, indices = nbrs.kneighbors(X)
        elif method == "approx":
            index = NNDescent(
                X,
                n_neighbors=self.n_neighbors + 1,
                metric=self.metric,
                random_state=self.random_state,
            )
            neighbor_graph = index.neighbor_graph
            assert neighbor_graph is not None
            indices, distances = neighbor_graph
        else:
            raise ValueError(f"unknown search method: {method!r}; expected 'exact' or 'approx'")

        return np.asarray(distances), np.asarray(indices)

    def _apply_degree_fallback(
        self,
        sym_graph: scipy.sparse.csr_matrix,
        knn_sim: scipy.sparse.csr_matrix,
    ) -> scipy.sparse.csr_matrix:
        """Restore edges for vertices left under-connected by symmetrization.

        AND-symmetrization can strand a point completely: if none of its
        neighbours picked it back, every one of its edges disappears. Such a
        point can never be reached by an ant and is noise by construction
        rather than by evidence. Here its strongest original neighbours are
        added back and mirrored, so the graph stays undirected.

        Args:
            sym_graph: The symmetrized graph.
            knn_sim: The directed similarity graph from before symmetrization,
                used as the source of candidate edges.

        Returns:
            The graph with the deficient vertices reconnected, or `sym_graph`
            unchanged when there were none.
        """
        degree = np.diff(sym_graph.indptr)
        deficient = np.where(degree < self.min_connections)[0]
        if len(deficient) == 0:
            return sym_graph

        rows: list[int] = []
        cols: list[int] = []
        vals: list[float] = []
        for i in deficient:
            start, end = knn_sim.indptr[i], knn_sim.indptr[i + 1]
            cand_idx = knn_sim.indices[start:end]
            cand_val = knn_sim.data[start:end]

            keep = (cand_idx != i) & (cand_val > 0)
            cand_idx, cand_val = cand_idx[keep], cand_val[keep]

            order = np.argsort(cand_val)[::-1][: self.min_connections]
            rows.extend([i] * len(order))
            cols.extend(cand_idx[order])
            vals.extend(cand_val[order])

        self._log(f"  connectivity top-up: {len(deficient):,} vertices augmented")

        fallback = scipy.sparse.csr_matrix((vals, (rows, cols)), shape=sym_graph.shape)
        combined = sym_graph.maximum(fallback).maximum(fallback.T).tocsr()
        combined.setdiag(0)
        combined.eliminate_zeros()

        return combined

    def build(self, X: np.ndarray) -> scipy.sparse.csr_matrix:
        """Build the similarity graph.

        Distances become similarities: `1 - d` for cosine, `1 / (1 + d)`
        otherwise. Cosine similarities are clipped at 0, so points more than a
        right angle apart are simply not connected.

        Args:
            X: Feature matrix of shape (N, D). Real-valued and finite; N must
                exceed `n_neighbors`.

        Returns:
            A symmetric CSR matrix of shape (N, N) holding similarities, with
            no self-loops and no stored zeros. Also kept in `graph_`.

        Raises:
            ValueError: If `X` is not a finite, real-valued, two-dimensional
                numeric array, if it holds too few points for `n_neighbors`,
                or if the search returns non-finite distances - which happens
                with zero vectors under `metric="cosine"`.

        Warns:
            UserWarning: If the resulting graph has no edges at all. Every
                similarity was zero, or symmetrization removed everything.
        """
        X = np.asarray(X)
        if X.ndim != 2:
            raise ValueError(f"X must be a two-dimensional array (N, D), got ndim={X.ndim}")
        if X.size == 0:
            raise ValueError("X is empty: a non-empty embedding array is required")
        if not np.issubdtype(X.dtype, np.number):
            raise ValueError(f"X must be a numeric array, got dtype={X.dtype}")
        if np.issubdtype(X.dtype, np.complexfloating):
            raise ValueError(f"X must be a real-valued array, got dtype={X.dtype}")
        if not np.isfinite(X).all():
            raise ValueError("X contains NaN or inf: clean the data before building the graph")

        n = len(X)
        if n <= self.n_neighbors:
            raise ValueError(
                f"too few points: N={n} with n_neighbors={self.n_neighbors}; "
                f"KNN requires at least n_neighbors + 1 points"
            )

        d = X.shape[1]
        method = self.knn_method
        if method == "auto":
            method = "approx" if n > self.approx_threshold else "exact"

        t_start = perf_counter()
        self._log(
            f"[graph] building {'AND' if self.mutual else 'OR'}-symmetric KNN graph "
            f"(N={n}, D={d}, method={method}, mutual={self.mutual}, metric={self.metric})"
        )

        t0 = perf_counter()
        distances, indices = self._knn_search(X, method)
        if not np.isfinite(distances).all():
            raise ValueError("KNN returned non-finite distances (NaN/inf): possible zero vectors with metric='cosine'")
        self._log(f"  neighbor search in {perf_counter() - t0:.2f}s")

        t0 = perf_counter()
        self_mask = indices == np.arange(n)[:, None]
        no_self = ~self_mask.any(axis=1)
        self_mask[no_self, -1] = True
        keep = ~self_mask
        indices = indices[keep].reshape(n, self.n_neighbors)
        distances = distances[keep].reshape(n, self.n_neighbors)
        distances = np.maximum(distances, 1e-12)

        rows = np.repeat(np.arange(n), self.n_neighbors)
        dist_matrix = scipy.sparse.csr_matrix(
            (distances.ravel(), (rows, indices.ravel())),
            shape=(n, n),
        )

        conn = (dist_matrix > 0).astype(np.int8)

        sim = dist_matrix.copy()
        if self.metric == "cosine":
            sim.data = 1.0 - sim.data
            sim.data[sim.data < 0] = 0.0
        else:
            sim.data = 1.0 / (1.0 + sim.data)

        if self.mutual:
            mask = conn.multiply(conn.T)
            sym_graph = sim.multiply(mask)
        else:
            sym_graph = sim.maximum(sim.T)

        sym_graph = sym_graph.tocsr()
        sym_graph.setdiag(0)
        sym_graph.eliminate_zeros()
        self._log(f"  symmetrization in {perf_counter() - t0:.2f}s")

        if self.min_connections > 0:
            t0 = perf_counter()
            sym_graph = self._apply_degree_fallback(sym_graph, sim.tocsr())
            self._log(f"  connectivity top-up in {perf_counter() - t0:.2f}s")

        if sym_graph.nnz == 0:
            warnings.warn(
                "built graph has no edges (nnz=0): all similarities are zero or were removed by symmetrization",
                stacklevel=2,
            )

        self.graph_ = sym_graph
        self._log(f"[graph] done: {sym_graph.nnz:,} edges, total {perf_counter() - t_start:.2f}s")
        return sym_graph
