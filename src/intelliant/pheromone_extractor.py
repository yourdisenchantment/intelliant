# src/intelliant/pheromone_extractor.py

import warnings
from time import perf_counter
from typing import Self

import numpy as np
from numba import njit
from scipy.sparse import csr_matrix
from tqdm.auto import tqdm

from ._validation import _check_bool, _check_float, _check_int


@njit(cache=True, fastmath=True)
def _step_ants(
    indptr: np.ndarray,
    indices: np.ndarray,
    pheromone_data: np.ndarray,
    weight_data: np.ndarray,
    density: np.ndarray,
    current_nodes: np.ndarray,
    prev_nodes: np.ndarray,
    is_elite: np.ndarray,
    alive: np.ndarray,
    alpha: float,
    use_no_return: bool,
    use_density: bool,
    pheromone_deposit: float,
    elite_multiplier: float,
    rng_states: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n_ants = len(current_nodes)

    delta_rows = np.empty(n_ants * 2, dtype=np.intp)
    delta_cols = np.empty(n_ants * 2, dtype=np.intp)
    delta_vals = np.empty(n_ants * 2, dtype=np.float64)
    count = 0

    for ant_idx in range(n_ants):
        if not alive[ant_idx]:
            continue

        current = current_nodes[ant_idx]
        s = indptr[current]
        e = indptr[current + 1]

        if s == e:
            alive[ant_idx] = False
            continue

        neighbors = indices[s:e]
        pheromones = pheromone_data[s:e]
        weights_beta = weight_data[s:e]

        n_nb = e - s
        probs = np.empty(n_nb, dtype=np.float64)

        if use_density:
            for i in range(n_nb):
                if alpha == 1.0:
                    probs[i] = pheromones[i] * weights_beta[i] * density[neighbors[i]]
                else:
                    probs[i] = (pheromones[i] ** alpha) * weights_beta[i] * density[neighbors[i]]
        else:
            for i in range(n_nb):
                if alpha == 1.0:
                    probs[i] = pheromones[i] * weights_beta[i]
                else:
                    probs[i] = (pheromones[i] ** alpha) * weights_beta[i]

        prev = prev_nodes[ant_idx]
        if use_no_return and prev != -1:
            for i in range(n_nb):
                if neighbors[i] == prev:
                    probs[i] = 0.0
                    break

        prob_sum = 0.0
        for i in range(n_nb):
            prob_sum += probs[i]

        if prob_sum < 1e-9:
            alive[ant_idx] = False
            continue

        if is_elite[ant_idx]:
            best_i = 0
            for i in range(1, n_nb):
                if probs[i] > probs[best_i]:
                    best_i = i
            next_node = neighbors[best_i]
            deposit = pheromone_deposit * elite_multiplier
        else:
            r = rng_states[ant_idx] * prob_sum
            cumsum = 0.0
            next_node = neighbors[n_nb - 1]
            for i in range(n_nb):
                cumsum += probs[i]
                if cumsum >= r:
                    next_node = neighbors[i]
                    break
            deposit = pheromone_deposit

        delta_rows[count] = current
        delta_cols[count] = next_node
        delta_vals[count] = deposit
        count += 1

        delta_rows[count] = next_node
        delta_cols[count] = current
        delta_vals[count] = deposit
        count += 1

        prev_nodes[ant_idx] = current
        current_nodes[ant_idx] = next_node

    return delta_rows[:count], delta_cols[:count], delta_vals[:count]


@njit(cache=True)
def _update_edges(
    indptr: np.ndarray,
    col_indices: np.ndarray,
    data: np.ndarray,
    rows: np.ndarray,
    cols: np.ndarray,
    vals: np.ndarray,
) -> None:
    for k in range(len(rows)):
        r = rows[k]
        c = cols[k]
        v = vals[k]
        s = indptr[r]
        e = indptr[r + 1]

        lo, hi = s, e
        while lo < hi:
            mid = (lo + hi) // 2
            if col_indices[mid] < c:
                lo = mid + 1
            else:
                hi = mid

        if lo < e and col_indices[lo] == c:
            data[lo] += v


class PheromoneExtractor:
    def __init__(
        self,
        *,
        n_iterations: int,
        path_length: int,
        beta: float,
        alpha: float,
        evaporation_rate: float,
        pheromone_deposit: float,
        initial_pheromone: float,
        tau_min: float,
        tau_max: float,
        n_ants: int | None = None,
        use_node_density: bool = False,
        node_density_gamma: float | None = None,
        use_elite_ants: bool = False,
        elite_ratio: float | None = None,
        elite_multiplier: float | None = None,
        elite_start_iteration: int | None = None,
        use_no_return: bool = True,
        random_state: int | None = None,
        warmup: bool = True,
        verbose: bool = True,
    ) -> None:
        self.n_ants = _check_int("n_ants", n_ants, 1, allow_none=True)

        self.n_iterations = _check_int("n_iterations", n_iterations, 0)

        self.path_length = _check_int("path_length", path_length, 1)

        self.beta = _check_float("beta", beta, 0.0)

        self.evaporation_rate = _check_float("evaporation_rate", evaporation_rate, 0.0, 1.0)

        self.use_node_density = _check_bool("use_node_density", use_node_density)

        if self.use_node_density and node_density_gamma is None:
            raise ValueError("node_density_gamma is required when use_node_density=True")
        self.node_density_gamma = (
            None if node_density_gamma is None else _check_float("node_density_gamma", node_density_gamma, 0.0)
        )

        self.use_elite_ants = _check_bool("use_elite_ants", use_elite_ants)

        if self.use_elite_ants and elite_ratio is None:
            raise ValueError("elite_ratio is required when use_elite_ants=True")
        self.elite_ratio = None if elite_ratio is None else _check_float("elite_ratio", elite_ratio, 0.0, 1.0)

        if self.use_elite_ants and elite_multiplier is None:
            raise ValueError("elite_multiplier is required when use_elite_ants=True")
        self.elite_multiplier = (
            None if elite_multiplier is None else _check_float("elite_multiplier", elite_multiplier, 0.0)
        )

        if self.use_elite_ants and elite_start_iteration is None:
            raise ValueError("elite_start_iteration is required when use_elite_ants=True")
        self.elite_start_iteration = _check_int("elite_start_iteration", elite_start_iteration, 0, allow_none=True)

        if (
            self.use_elite_ants
            and self.elite_start_iteration is not None
            and self.elite_start_iteration >= self.n_iterations
        ):
            warnings.warn(
                f"elite_start_iteration={self.elite_start_iteration} >= "
                f"n_iterations={self.n_iterations}: elite ants will never activate.",
                stacklevel=2,
            )

        tau_min = _check_float("tau_min", tau_min, 0.0)
        tau_max = _check_float("tau_max", tau_max, 0.0)
        if tau_min >= tau_max:
            raise ValueError(f"tau_min must be < tau_max, got tau_min={tau_min}, tau_max={tau_max}")

        self.alpha = _check_float("alpha", alpha, 0.0)
        self.pheromone_deposit = _check_float("pheromone_deposit", pheromone_deposit, 0.0)
        self.initial_pheromone = _check_float("initial_pheromone", initial_pheromone, 0.0)
        self.tau_min = tau_min
        self.tau_max = tau_max
        self.use_no_return = _check_bool("use_no_return", use_no_return)

        self.random_state = random_state
        self.warmup = _check_bool("warmup", warmup)
        self.verbose = _check_bool("verbose", verbose)

        self.pheromone_matrix_: csr_matrix | None = None
        self._graph: csr_matrix | None = None
        self._N: int = 0

        self._precomputed_weights: np.ndarray | None = None
        self._precomputed_density: np.ndarray | None = None
        self._indptr: np.ndarray | None = None
        self._indices: np.ndarray | None = None

        self._rng = np.random.default_rng(random_state)

    def _log(self, msg: str) -> None:
        if self.verbose:
            tqdm.write(msg)

    def _warmup(self) -> None:
        indptr = np.array([0, 1, 2, 3], dtype=np.intp)
        indices = np.array([1, 2, 0], dtype=np.intp)
        pheromone_data = np.ones(3, dtype=np.float64)
        weight_data = np.ones(3, dtype=np.float64)
        density = np.empty(0, dtype=np.float64)
        current_nodes = np.zeros(2, dtype=np.intp)
        prev_nodes = np.full(2, -1, dtype=np.intp)
        is_elite = np.zeros(2, dtype=np.bool_)
        alive = np.ones(2, dtype=np.bool_)
        rng_states = np.zeros(2, dtype=np.float64)

        rows, cols, vals = _step_ants(
            indptr=indptr,
            indices=indices,
            pheromone_data=pheromone_data,
            weight_data=weight_data,
            density=density,
            current_nodes=current_nodes,
            prev_nodes=prev_nodes,
            is_elite=is_elite,
            alive=alive,
            alpha=1.0,
            use_no_return=True,
            use_density=False,
            pheromone_deposit=0.1,
            elite_multiplier=5.0,
            rng_states=rng_states,
        )
        _update_edges(indptr, indices, pheromone_data, rows, cols, vals)

    def fit(self, graph: csr_matrix) -> Self:
        if self.n_ants is None:
            raise ValueError("n_ants is required: set it explicitly, e.g. n_ants=len(X) to start")
        if self.n_ants <= 0:
            raise ValueError(f"n_ants must be > 0, got {self.n_ants}")

        if graph.shape is None or graph.shape[0] != graph.shape[1]:
            raise ValueError(f"graph must be square (N, N), got shape {graph.shape}")
        if graph.shape[0] == 0:
            raise ValueError("graph is empty: a non-empty similarity graph is required")
        if graph.nnz == 0:
            raise ValueError("graph has no edges: ants have nowhere to go")
        if not np.isfinite(graph.data).all():
            raise ValueError("graph contains NaN or inf: clean the edge weights before running ACO")
        if (graph.data < 0).any():
            raise ValueError("graph contains negative weights: similarities must be >= 0")

        t_start = perf_counter()

        self._rng = np.random.default_rng(self.random_state)

        self._N = graph.shape[0]
        self._graph = graph.tocsr(copy=True)
        assert self._graph is not None
        self._graph.sum_duplicates()
        self._graph.eliminate_zeros()
        self._graph.sort_indices()

        self._indptr = self._graph.indptr.astype(np.intp)
        self._indices = self._graph.indices.astype(np.intp)

        self.pheromone_matrix_ = self._graph.copy().astype(np.float64)
        assert self.pheromone_matrix_ is not None
        assert self.pheromone_matrix_.data is not None
        self.pheromone_matrix_.data[:] = self.initial_pheromone
        self._clamp_pheromones()

        self._precomputed_weights = self._graph.data.astype(np.float64) ** self.beta

        if self.use_node_density:
            raw_density = np.asarray(self._graph.sum(axis=1)).flatten().astype(np.float64)
            max_d = raw_density.max()
            if max_d > 0:
                raw_density /= max_d
            # Re-checked here, not only in the constructor: the flags are public
            # attributes and may be flipped on an already-built instance.
            if self.node_density_gamma is None:
                raise ValueError("node_density_gamma is required when use_node_density=True")
            self._precomputed_density = raw_density**self.node_density_gamma
        else:
            self._precomputed_density = np.empty(0, dtype=np.float64)

        heuristics = []
        if self.use_elite_ants:
            heuristics.append("elite")
        if self.use_node_density:
            heuristics.append("density")
        if self.use_no_return:
            heuristics.append("no return")
        heur = ", ".join(heuristics) if heuristics else "none"

        self._log(
            f"[aco] run on graph ({self._N} nodes, {self._graph.nnz:,} edges) "
            f"n_ants={self.n_ants}, n_iterations={self.n_iterations}, "
            f"path_length={self.path_length}, heuristics={heur}"
        )

        if self.warmup:
            t0 = perf_counter()
            self._warmup()
            self._log(f"  njit warmup in {perf_counter() - t0:.2f}s")

        is_elite = np.zeros(self.n_ants, dtype=np.bool_)
        n_elite = 0
        if self.use_elite_ants:
            if self.elite_ratio is None:
                raise ValueError("elite_ratio is required when use_elite_ants=True")
            n_elite = round(self.n_ants * self.elite_ratio)
            if n_elite == 0:
                warnings.warn(
                    f"elite_ratio={self.elite_ratio} with n_ants={self.n_ants} yields 0 elite "
                    f"ants: elite is effectively off, but use_elite_ants=True",
                    stacklevel=2,
                )
            is_elite[:n_elite] = True

        no_elite = np.zeros(self.n_ants, dtype=np.bool_)

        t_run = perf_counter()
        elite_logged = False
        for iteration in tqdm(range(self.n_iterations), disable=not self.verbose):
            elites_active = (
                self.use_elite_ants
                and self.elite_start_iteration is not None
                and iteration >= self.elite_start_iteration
            )
            if elites_active and not elite_logged:
                self._log(f"  elite activated at iteration {iteration}")
                elite_logged = True
            self._run_iteration(is_elite if elites_active else no_elite)
            self._clamp_pheromones()
        self._log(f"  swarm run in {perf_counter() - t_run:.2f}s")

        self._log(
            f"[aco] done: pheromone range "
            f"[{self.pheromone_matrix_.data.min():.3f}, {self.pheromone_matrix_.data.max():.3f}], "
            f"total {perf_counter() - t_start:.2f}s"
        )

        return self

    def _run_iteration(self, is_elite: np.ndarray) -> None:
        assert self.pheromone_matrix_ is not None
        assert self.pheromone_matrix_.data is not None
        assert self._graph is not None
        assert self._precomputed_weights is not None
        assert self._precomputed_density is not None
        assert self._indptr is not None
        assert self._indices is not None
        assert self.n_ants is not None

        current_nodes = self._rng.integers(0, self._N, size=self.n_ants, dtype=np.intp)
        prev_nodes = np.full(self.n_ants, -1, dtype=np.intp)
        alive = np.ones(self.n_ants, dtype=np.bool_)

        for _ in range(self.path_length):
            if not alive.any():
                break

            rng_states = self._rng.random(self.n_ants)

            rows, cols, vals = _step_ants(
                indptr=self._indptr,
                indices=self._indices,
                pheromone_data=self.pheromone_matrix_.data,
                weight_data=self._precomputed_weights,
                density=self._precomputed_density,
                current_nodes=current_nodes,
                prev_nodes=prev_nodes,
                is_elite=is_elite,
                alive=alive,
                alpha=float(self.alpha),
                use_no_return=self.use_no_return,
                use_density=self.use_node_density,
                pheromone_deposit=float(self.pheromone_deposit),
                # Neutral 1.0 when elite is off: is_elite is all-False there, so
                # the multiplier is never applied and the value is unobservable.
                elite_multiplier=1.0 if self.elite_multiplier is None else float(self.elite_multiplier),
                rng_states=rng_states,
            )

            self.pheromone_matrix_.data *= 1.0 - self.evaporation_rate

            if len(rows) > 0:
                _update_edges(
                    self._indptr,
                    self._indices,
                    self.pheromone_matrix_.data,
                    rows,
                    cols,
                    vals,
                )

    def _clamp_pheromones(self) -> None:
        assert self.pheromone_matrix_ is not None
        assert self.pheromone_matrix_.data is not None

        np.clip(
            self.pheromone_matrix_.data,
            self.tau_min,
            self.tau_max,
            out=self.pheromone_matrix_.data,
        )
