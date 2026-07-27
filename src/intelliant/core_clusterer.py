# src/intelliant/core_clusterer.py
"""Stage 3: cut the pheromone field into clusters, then absorb the noise.

Thresholding gives cores - dense regions the ants marked - and leaves
everything else unassigned. Absorption then decides what to do with the rest,
in two passes: pheromone waves spread labels along the graph, and a centroid
fallback catches whatever the waves could not reach.

Every absorbed point is assigned to *some* cluster; there is no distance cut
off. That is what produces the occasional oversized cluster on real data,
which the giant diagnostics report but do not act on.
"""

import warnings
from time import perf_counter
from typing import NamedTuple

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.metrics.pairwise import cosine_similarity
from tqdm.auto import tqdm

from ._validation import _check_bool, _check_float, _check_int


class GiantDiagnostics(NamedTuple):
    """A report on whether one cluster has swallowed the partition.

    Purely informational. Detection is separate from intervention on purpose:
    a giant is not an error, it is an under-resolved region, and what to do
    about it depends on the data.

    Attributes:
        n_clusters: Clusters found.
        top_sizes: The five largest sizes, descending.
        median: Median cluster size.
        max_gap: Largest size ratio between neighbouring ranks, or None with
            fewer than two clusters.
        gap_pos: Rank where that gap sits.
        suspected: Whether the gap is large enough, and near enough to the
            head, to look like a giant.
        single: Whether there is exactly one cluster - which may itself be a
            giant, with nothing to compare it against.
    """

    n_clusters: int
    top_sizes: list[int]
    median: float
    max_gap: float | None
    gap_pos: int | None
    suspected: bool
    single: bool


class CoreClusterer:
    """Extract cores from a pheromone field and absorb the noise.

    Attributes:
        cores_: Labels after thresholding, noise as -1. Contiguous from 0.
        labels_pheromone_: Labels after the pheromone-wave pass.
        labels_: Final labels after both absorption passes.

    All three are public and may be edited between calls - that is the point
    of the staged design. Edited state must still satisfy the contract: noise
    is -1, cluster ids appear in `cores_`, and the arrays keep their length.

    Example:
        >>> clusterer = CoreClusterer(
        ...     min_cluster_size=15,
        ...     max_iterations=20,
        ...     gap_ratio=3.0,
        ...     max_gap_rank=3,
        ...     batch_size=1000,
        ... )
        >>> labels = clusterer.fit_predict(field, threshold_value=0.5, X=X)  # doctest: +SKIP
    """

    def __init__(
        self,
        *,
        max_iterations: int,
        gap_ratio: float,
        max_gap_rank: int,
        min_cluster_size: int | None = None,
        batch_size: int | None = None,
        absorb_isolated: bool = True,
        verbose: bool = True,
    ) -> None:
        """Configure the clusterer.

        Args:
            max_iterations: Cap on pheromone-wave passes. Waves stop early
                when a pass resolves nothing.
            gap_ratio: Size ratio between neighbouring ranks that counts as a
                giant. Note that a merged pair of equal clusters produces a
                ratio near 2.0 and slips under the usual 3.0.
            max_gap_rank: How far down the ranking a gap still counts. A gap
                between the 50th and 51st cluster says nothing about a giant.
            min_cluster_size: Smallest component that counts as a core.
                Required here or per call.
            batch_size: Rows processed at once during absorption. Trades
                memory for speed; required because the right value depends on
                the data and the machine.
            absorb_isolated: Whether to run the centroid fallback for points
                the waves could not reach. Needs `X`.
            verbose: Whether to report progress and timings.

        Raises:
            ValueError: If any argument is outside its valid range or of the
                wrong type.
        """
        self.min_cluster_size = _check_int("min_cluster_size", min_cluster_size, 1, allow_none=True)

        self.max_iterations = _check_int("max_iterations", max_iterations, 0)

        self.batch_size = _check_int("batch_size", batch_size, 1, allow_none=True)

        self.absorb_isolated = _check_bool("absorb_isolated", absorb_isolated)

        self.gap_ratio = _check_float("gap_ratio", gap_ratio, 1.0)

        self.max_gap_rank = _check_int("max_gap_rank", max_gap_rank, 1)

        self.verbose = _check_bool("verbose", verbose)

        self.cores_: np.ndarray | None = None
        self.labels_pheromone_: np.ndarray | None = None
        self.labels_: np.ndarray | None = None

    def _log(self, msg: str) -> None:
        """Write a progress message when verbose, via tqdm to avoid clobbering bars."""
        if self.verbose:
            tqdm.write(msg)

    def _detect_giant(self, sizes: np.ndarray) -> GiantDiagnostics:
        """Look for a size gap that suggests one cluster has swallowed others.

        Ratios between neighbouring ranks are compared, and the largest is
        flagged when it exceeds `gap_ratio` near the head of the ranking. Size
        alone is not evidence of a merge - a large cluster may simply be
        dense - so this suspects rather than concludes.

        Args:
            sizes: Cluster sizes, in any order.

        Returns:
            The diagnostics; `suspected` is False when there are fewer than
            two clusters.
        """
        sizes_sorted = np.sort(sizes)[::-1]
        n = len(sizes_sorted)
        top_sizes = [int(s) for s in sizes_sorted[:5]]

        if n < 2:
            return GiantDiagnostics(
                n_clusters=n,
                top_sizes=top_sizes,
                median=float(np.median(sizes_sorted)) if n else 0.0,
                max_gap=None,
                gap_pos=None,
                suspected=False,
                single=(n == 1),
            )

        gaps = sizes_sorted[:-1] / sizes_sorted[1:]
        gap_pos = int(np.argmax(gaps))
        max_gap = float(gaps[gap_pos])
        suspected = (gap_pos < self.max_gap_rank) and (max_gap > self.gap_ratio)

        return GiantDiagnostics(
            n_clusters=n,
            top_sizes=top_sizes,
            median=float(np.median(sizes_sorted)),
            max_gap=max_gap,
            gap_pos=gap_pos,
            suspected=suspected,
            single=False,
        )

    def _log_giant(
        self,
        diag: GiantDiagnostics,
        header: str,
        suspected_note: str,
    ) -> None:
        """Print a giant report.

        Args:
            diag: The diagnostics to print.
            header: Line introducing the block.
            suspected_note: What to say when a giant is suspected.
        """
        self._log(header)
        self._log(f"  top sizes: {diag.top_sizes}, median: {diag.median:,.0f}")
        if diag.max_gap is not None:
            self._log(f"  max gap: {diag.max_gap:.2f}x at position {diag.gap_pos}")
        else:
            self._log("  max gap: n/a (fewer than 2 clusters)")
        if diag.single:
            self._log("  note: only one cluster - a possible giant on its own")
        if diag.suspected:
            self._log(f"  SUSPICION: {suspected_note}")
        else:
            self._log("  verdict: no giant detected")

    def extract_cores(
        self,
        pheromone_graph: csr_matrix,
        threshold_value: float | None = None,
        threshold_percentile: float | None = None,
        min_cluster_size: int | None = None,
    ) -> np.ndarray:
        """Cut the pheromone field and label the connected components.

        Edges at or below the cutoff are dropped; what remains falls apart
        into components, and those above `min_cluster_size` become cores.
        Everything else is noise, to be dealt with by absorption.

        Cheap enough to re-run at several cutoffs on the same field - see
        `scan_thresholds`.

        Args:
            pheromone_graph: The field produced by `PheromoneExtractor.fit`.
            threshold_value: Absolute cutoff. Mutually exclusive with
                `threshold_percentile`.
            threshold_percentile: Cutoff as a percentile of the edge weights.
            min_cluster_size: Overrides the constructor value for this call.

        Returns:
            Labels of length N, cores numbered contiguously from 0 and noise
            as -1. Also stored in `cores_`.

        Raises:
            ValueError: If the graph is not square, has no edges, or holds
                NaN or inf; if both or neither threshold argument is given;
                or if `min_cluster_size` is unset and was not given here.
        """
        min_cluster_size = _check_int("min_cluster_size", min_cluster_size, 1, allow_none=True)
        if min_cluster_size is None:
            min_cluster_size = self.min_cluster_size
        if min_cluster_size is None:
            raise ValueError("min_cluster_size is required: set it in the constructor or pass to extract_cores")
        if min_cluster_size <= 0:
            raise ValueError(f"min_cluster_size must be > 0, got {min_cluster_size}")

        if pheromone_graph.shape is None or pheromone_graph.shape[0] != pheromone_graph.shape[1]:
            raise ValueError(f"pheromone graph must be square (N, N), got shape {pheromone_graph.shape}")

        if pheromone_graph.nnz == 0:
            raise ValueError("pheromone graph is empty (no edges): core extraction is impossible")

        if not np.all(np.isfinite(pheromone_graph.data)):
            raise ValueError("pheromone graph contains NaN or inf: clean the edge weights before extracting cores")

        if threshold_value is not None and threshold_percentile is not None:
            raise ValueError("specify either threshold_value or threshold_percentile, not both")

        if threshold_percentile is not None:
            threshold_percentile = _check_float("threshold_percentile", threshold_percentile, 0.0, 100.0)
            cutoff = float(np.percentile(pheromone_graph.data, threshold_percentile))
        elif threshold_value is not None:
            cutoff = _check_float("threshold_value", threshold_value, min_val=float("-inf"))
        else:
            raise ValueError("specify a threshold: threshold_value or threshold_percentile")

        self.labels_pheromone_ = None
        self.labels_ = None

        t_start = perf_counter()
        if threshold_percentile is not None:
            self._log(
                f"[cluster] extracting cores (cutoff={cutoff:.4f} "
                f"(percentile {threshold_percentile:g}), min_cluster_size={min_cluster_size})"
            )
        else:
            self._log(f"[cluster] extracting cores (cutoff={cutoff:.4f}, min_cluster_size={min_cluster_size})")

        t0 = perf_counter()
        adj = pheromone_graph.tocsr(copy=True)
        adj.data[adj.data <= cutoff] = 0.0
        adj.eliminate_zeros()

        n_comps, labels = connected_components(adj, directed=False)
        self._log(f"  thresholding + connected components in {perf_counter() - t0:.2f}s")

        unique_labels, counts = np.unique(labels, return_counts=True)
        core_ids = unique_labels[counts >= min_cluster_size]
        lookup = np.full(n_comps, -1, dtype=labels.dtype)
        lookup[core_ids] = np.arange(len(core_ids), dtype=labels.dtype)
        cores = lookup[labels]

        noise = (cores < 0).sum()
        self._log(
            f"[cluster] extracted {len(core_ids)} cores from {n_comps} components "
            f"(noise: {noise:,} of {len(labels):,}, {100 * noise / len(labels):.1f}%), "
            f"total {perf_counter() - t_start:.2f}s"
        )

        core_sizes = np.unique(cores[cores >= 0], return_counts=True)[1]
        diag = self._detect_giant(core_sizes)
        self._log_giant(
            diag,
            "Giant check (cores):",
            "possible core merging, check the threshold",
        )

        self.cores_ = cores
        return cores

    def absorb_pheromone(self, pheromone_graph: csr_matrix) -> np.ndarray:
        """Spread cluster labels outward along the graph.

        Each pass lets unassigned points vote among the clusters their
        neighbours belong to, weighted by pheromone, and takes the winner.
        Only points already resolved when the pass began may vote, so a wave
        advances by one ring per iteration rather than racing along a chain
        within one pass.

        Stops when nothing is left, when a pass resolves nothing, or at
        `max_iterations`. Points with no resolved neighbour at all - isolated
        vertices - stay noise; that is what the centroid fallback is for.

        Args:
            pheromone_graph: The same field the cores were extracted from.

        Returns:
            Labels after the waves, noise still -1. Also stored in
            `labels_pheromone_`.

        Raises:
            ValueError: If `cores_` is unset, `batch_size` is unset, the graph
                is not square or does not match `cores_` in size, holds NaN or
                inf, or no cores survived extraction.
        """
        if self.cores_ is None:
            raise ValueError("cores_ is not set: call extract_cores() before absorb_pheromone()")
        if self.batch_size is None:
            raise ValueError("batch_size is required: set it explicitly based on data size and memory")
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be > 0, got {self.batch_size}")

        if pheromone_graph.shape is None or pheromone_graph.shape[0] != pheromone_graph.shape[1]:
            raise ValueError(f"pheromone graph must be square (N, N), got shape {pheromone_graph.shape}")
        if pheromone_graph.shape[0] != len(self.cores_):
            raise ValueError(
                f"pheromone graph size ({pheromone_graph.shape[0]}) does not match "
                f"the number of points in cores ({len(self.cores_)})"
            )

        pheromone_graph = pheromone_graph.tocsr()

        if not np.all(np.isfinite(pheromone_graph.data)):
            raise ValueError("pheromone graph contains NaN or inf: clean the edge weights before extracting cores")

        self.labels_ = None

        labels = self.cores_
        valid_clusters = np.unique(labels[labels >= 0])
        if len(valid_clusters) == 0:
            raise ValueError(
                "no cores to absorb: extract_cores() found 0 cores "
                "(all points are noise); lower threshold or min_cluster_size"
            )

        new_labels = labels.copy()

        max_label = int(new_labels.max()) + 1
        cluster_to_idx = np.full(max_label, -1, dtype=np.int32)
        for i, c in enumerate(valid_clusters):
            cluster_to_idx[c] = i
        n_clusters = len(valid_clusters)

        t_start = perf_counter()
        initial_noise = int((labels < 0).sum())
        self._log(f"[cluster] absorbing {initial_noise:,} noise points into {n_clusters} clusters")

        for iteration in range(self.max_iterations):
            is_resolved = new_labels >= 0
            noise_indices = np.where(~is_resolved)[0]

            if len(noise_indices) == 0:
                self._log(f"All points resolved, iterations done: {iteration}")
                break

            newly_resolved = 0

            for i in tqdm(
                range(0, len(noise_indices), self.batch_size),
                desc=f"Iteration {iteration + 1}",
                leave=False,
                disable=not self.verbose,
            ):
                batch = noise_indices[i : i + self.batch_size]
                sub = pheromone_graph[batch]

                col_idx = sub.indices
                weights = sub.data.astype(np.float32)
                row_idx = np.repeat(np.arange(len(batch)), np.diff(sub.indptr))

                valid_edge = is_resolved[col_idx]
                if not valid_edge.any():
                    continue

                r = row_idx[valid_edge]
                neighbor_labels = new_labels[col_idx[valid_edge]]
                c = cluster_to_idx[neighbor_labels]
                w = weights[valid_edge]

                vote_mat = csr_matrix((w, (r, c)), shape=(len(batch), n_clusters))
                has_vote = np.diff(vote_mat.indptr) > 0
                # np.asarray(...).ravel() rather than .A1: the latter is an
                # np.matrix attribute, and np.matrix is legacy - this breaks on
                # a scipy release, which Dependabot now proposes.
                assigned = np.asarray(vote_mat.argmax(axis=1)).ravel()

                new_labels[batch[has_vote]] = valid_clusters[assigned[has_vote]]
                newly_resolved += has_vote.sum()

            self._log(
                f"Iteration {iteration + 1}: resolved {newly_resolved:,} points, "
                f"{len(noise_indices) - newly_resolved:,} remaining"
            )

            if newly_resolved == 0:
                self._log("No progress - early stop.")
                break

        still_noise = int((new_labels < 0).sum())
        self._log(
            f"  stage 1 (pheromone waves): absorbed {initial_noise - still_noise:,}, "
            f"{still_noise:,} remaining, in {perf_counter() - t_start:.2f}s"
        )

        cluster_sizes = np.unique(new_labels[new_labels >= 0], return_counts=True)[1]
        diag = self._detect_giant(cluster_sizes)
        self._log_giant(
            diag,
            "Giant check (after pheromone waves):",
            "cluster grew a lot during pheromone waves",
        )

        self.labels_pheromone_ = new_labels
        return new_labels

    def absorb_centroid(
        self,
        X: np.ndarray | None = None,
        labels: np.ndarray | None = None,
    ) -> np.ndarray:
        """Assign whatever the waves could not reach to the nearest centroid.

        Cluster centroids are computed from the RAW cores - not from the
        wave-absorbed labels - so that absorption cannot drag a centroid
        toward the points it is about to claim. Each remaining point goes to
        the centroid it is most cosine-similar to.

        There is no distance limit: every point gets a cluster. On real data
        this is what produces an oversized catch-all cluster, and it is the
        deliberate cost of leaving nothing unlabelled.

        Args:
            X: Feature matrix, needed to compute centroids. Without it the
                pass is skipped and a warning is issued.
            labels: Labels to start from. Defaults to `labels_pheromone_`.

        Returns:
            Final labels. Also stored in `labels_`.

        Raises:
            ValueError: If `cores_` is unset, `batch_size` is unset, no labels
                are available, `X` is not two-dimensional, its length does not
                match, or no cores survived extraction.

        Warns:
            UserWarning: If `absorb_isolated` is True, points remain
                unresolved, and `X` was not supplied - the pass cannot run and
                those points stay -1.
        """
        if self.cores_ is None:
            raise ValueError("cores_ is not set: call extract_cores() before absorb_centroid()")
        if self.batch_size is None:
            raise ValueError("batch_size is required: set it explicitly based on data size and memory")
        if self.batch_size <= 0:
            raise ValueError(f"batch_size must be > 0, got {self.batch_size}")

        if labels is None:
            labels = self.labels_pheromone_
        if labels is None:
            raise ValueError("no labels for absorption: call absorb_pheromone() or pass labels")

        if X is not None:
            X = np.asarray(X)
            if X.ndim != 2:
                raise ValueError(f"X must be a two-dimensional array (N, D), got ndim={X.ndim}")
        if X is not None and len(X) != len(labels):
            raise ValueError(f"length of X ({len(X)}) does not match the number of points ({len(labels)})")
        if X is not None and len(X) != len(self.cores_):
            raise ValueError(
                f"length of X ({len(X)}) does not match the number of points in cores ({len(self.cores_)})"
            )

        valid_clusters = np.unique(self.cores_[self.cores_ >= 0])
        if len(valid_clusters) == 0:
            raise ValueError(
                "no cores to absorb: extract_cores() found 0 cores "
                "(all points are noise); lower threshold or min_cluster_size"
            )
        new_labels = labels.copy()
        n_clusters = len(valid_clusters)

        t_start = perf_counter()
        still_noise = int((~np.isin(new_labels, valid_clusters)).sum())

        if self.absorb_isolated and X is None and still_noise > 0:
            warnings.warn(
                "absorb_isolated=True but X is None: stage 2 (centroid fallback) skipped, isolated points remain -1",
                stacklevel=2,
            )

        if self.absorb_isolated and still_noise and X is not None:
            t0 = perf_counter()
            # np.full rather than np.empty, matching absorb_pheromone: the
            # empty version is safe only while every value in cores_ is also in
            # valid_clusters, and the staged design lets a caller edit cores_
            # between stages. Uninitialised memory fails silently and
            # non-deterministically once that stops holding.
            core_to_idx = np.full(valid_clusters.max() + 1, -1, dtype=np.int32)
            core_to_idx[valid_clusters] = np.arange(len(valid_clusters))
            idx = core_to_idx[self.cores_]
            mask = self.cores_ >= 0
            centroids = np.zeros((len(valid_clusters), X.shape[1]), dtype=np.float64)
            np.add.at(centroids, idx[mask], X[mask])
            counts = np.bincount(idx[mask], minlength=len(valid_clusters))
            nonzero = counts > 0
            centroids[nonzero] /= counts[nonzero, None]
            self._log(f"  centroids in {perf_counter() - t0:.2f}s")

            noise_indices = np.where(~np.isin(new_labels, valid_clusters))[0]
            n_isolated = len(noise_indices)
            t0 = perf_counter()
            for i in tqdm(
                range(0, len(noise_indices), self.batch_size),
                desc="Stage 2",
                leave=False,
                disable=not self.verbose,
            ):
                batch = noise_indices[i : i + self.batch_size]
                sims = np.asarray(cosine_similarity(X[batch], centroids))
                new_labels[batch] = valid_clusters[np.argmax(sims, axis=1)]

            left = int((~np.isin(new_labels, valid_clusters)).sum())
            self._log(
                f"  stage 2 (centroid fallback): absorbed {n_isolated - left:,}, "
                f"{left:,} remaining, in {perf_counter() - t0:.2f}s"
            )

        final_noise = int((~np.isin(new_labels, valid_clusters)).sum())
        self._log(
            f"[cluster] absorption done: {n_clusters} clusters, "
            f"{final_noise:,} points left as -1, total {perf_counter() - t_start:.2f}s"
        )

        # np.isin against valid_clusters, not `>= 0`: this method treats
        # anything outside valid_clusters as unresolved, and the diagnostic has
        # to count the same points the log above just reported.
        resolved = np.isin(new_labels, valid_clusters)
        cluster_sizes = np.unique(new_labels[resolved], return_counts=True)[1]
        diag = self._detect_giant(cluster_sizes)
        self._log_giant(
            diag,
            "Giant check (clusters):",
            "cluster grew a lot during absorption",
        )

        self.labels_ = new_labels
        return new_labels

    def absorb(
        self,
        pheromone_graph: csr_matrix,
        X: np.ndarray | None = None,
    ) -> np.ndarray:
        """Run both absorption passes in order.

        Args:
            pheromone_graph: The field the cores came from.
            X: Feature matrix for the centroid fallback.

        Returns:
            Final labels.

        Raises:
            ValueError: Anything either pass raises.
        """
        self.absorb_pheromone(pheromone_graph)
        return self.absorb_centroid(X)

    def fit_predict(
        self,
        pheromone_graph: csr_matrix,
        threshold_value: float | None = None,
        threshold_percentile: float | None = None,
        X: np.ndarray | None = None,
        min_cluster_size: int | None = None,
    ) -> np.ndarray:
        """Extract cores and absorb, in one call.

        The convenience path. Prefer the separate calls when you intend to
        inspect the cores or try several cutoffs - re-cutting the same field
        costs milliseconds.

        Args:
            pheromone_graph: The field produced by `PheromoneExtractor.fit`.
            threshold_value: Absolute cutoff.
            threshold_percentile: Cutoff as a percentile.
            X: Feature matrix for the centroid fallback.
            min_cluster_size: Overrides the constructor value.

        Returns:
            Final labels.

        Raises:
            ValueError: Anything extraction or absorption raises.
        """
        self.extract_cores(pheromone_graph, threshold_value, threshold_percentile, min_cluster_size)
        return self.absorb(pheromone_graph, X)
