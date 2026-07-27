# src/intelliant/graph_builder.py

import warnings
from time import perf_counter

import numpy as np
import scipy.sparse
from pynndescent import NNDescent
from sklearn.neighbors import NearestNeighbors
from tqdm.auto import tqdm

from ._validation import _check_bool, _check_int


class GraphBuilder:
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
    ):
        self.n_neighbors = _check_int("n_neighbors", n_neighbors, 1)
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

        self.random_state = random_state
        self.verbose = _check_bool("verbose", verbose)

        self.graph_: scipy.sparse.csr_matrix | None = None

    def _log(self, msg: str):
        """Prints a message via tqdm.write if verbose is enabled.

        Args:
            msg (str): Message text to print.
        """

        if self.verbose:
            tqdm.write(msg)

    def _knn_search(self, X: np.ndarray, method: str) -> tuple[np.ndarray, np.ndarray]:
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
