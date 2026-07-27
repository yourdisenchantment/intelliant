# src/intelliant/pheromone_extractor.py
"""Stage 2: run the colony over the graph and read off the pheromone field.

Ants start at random vertices and walk, choosing each step by pheromone times
edge weight, depositing as they go. Dense regions get walked more often and
accumulate; sparse ones do not. The result is not a partition - it is a field
whose distribution the next stage cuts.

Unlike ACO for the travelling salesman, a walk here is not a solution and
there is no objective function. Nothing is optimised; the field is simply
where the ants have been. That difference is why parameter values from the
ACO literature do not transfer, most sharply for `evaporation_schedule`.
"""

import warnings
from time import perf_counter
from typing import Self

import numpy as np
from numba import njit
from scipy.sparse import csr_matrix
from tqdm.auto import tqdm

from ._validation import _check_bool, _check_float, _check_int


# fastmath permits float reassociation, which is why this is fast - and why
# results are only guaranteed bit-identical on one machine with one numba
# build. The determinism tests hold within a platform, not across them; treat
# cross-platform reproduction as approximate.
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
    """Advance every live ant by one step and collect the deposits.

    Compiled, and written as explicit loops rather than array operations
    because numba is faster that way and this is the hot path.

    An ant dies when it reaches a vertex with no edges, or when every
    available move has effectively zero probability - which happens when the
    only way back is banned by `use_no_return`. Dead ants are skipped for the
    rest of the iteration.

    Args:
        indptr: CSR row pointers of the graph.
        indices: CSR column indices, sorted within each row.
        pheromone_data: Current pheromone per edge, modified by the caller.
        weight_data: Edge weights already raised to `beta`.
        density: Per-vertex density factors, empty when unused.
        current_nodes: Where each ant stands. Updated in place.
        prev_nodes: Where each ant came from, -1 at the start. Updated in
            place.
        is_elite: Which ants take the greedy move and deposit more.
        alive: Which ants can still move. Updated in place.
        alpha: Exponent on pheromone. Above 1 sharpens the field toward what
            is already strong.
        use_no_return: Whether stepping straight back is forbidden.
        use_density: Whether to weight moves by vertex density.
        pheromone_deposit: Base deposit per traversed edge.
        elite_multiplier: Multiplier applied to elite deposits.
        rng_states: One uniform random draw per ant for this step.

    Returns:
        `(rows, cols, values)` for the deposits of this step, both directions
        of each traversed edge.
    """
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
) -> int:
    """Add deposits to the matrix in place, and count those that miss.

    Each target is found by binary search within its CSR row, which is why
    `sort_indices` is called before the run.

    An ant stepping i -> j deposits on both (i, j) and (j, i). On an
    asymmetric graph the reverse edge is not stored and that half has nowhere
    to go. Counting the misses is free - the lookup happens anyway - and it
    measures the actual damage rather than checking symmetry up front, which
    would cost an O(nnz) allocation on every fit.

    Args:
        indptr: CSR row pointers.
        col_indices: CSR column indices, sorted within each row.
        data: Pheromone values, modified in place.
        rows: Target rows.
        cols: Target columns.
        vals: Amounts to add.

    Returns:
        How many deposits fell on edges that do not exist.
    """
    missed = 0
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
        else:
            missed += 1

    return missed


class PheromoneExtractor:
    """Run an ant colony over a graph and produce a pheromone field.

    Attributes:
        pheromone_matrix_: The field after `fit` - the same sparsity pattern
            as the input graph, with pheromone instead of similarity. Public
            and meant to be cut several ways; see `find_threshold` and
            `scan_thresholds`.

    Example:
        >>> aco = PheromoneExtractor(
        ...     n_ants=len(X),
        ...     n_iterations=20,
        ...     path_length=10,
        ...     beta=2.0,
        ...     alpha=1.0,
        ...     evaporation_rate=0.07,
        ...     evaporation_schedule="step",
        ...     pheromone_deposit=1.0,
        ...     initial_pheromone=1.0,
        ...     tau_min=0.01,
        ...     tau_max=10.0,
        ... )
        >>> aco.fit(graph)  # doctest: +SKIP
    """

    def __init__(
        self,
        *,
        n_iterations: int,
        path_length: int,
        beta: float,
        alpha: float,
        evaporation_rate: float,
        evaporation_schedule: str,
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
        """Configure the colony.

        Args:
            n_iterations: Colony runs. Each starts the ants afresh at random
                vertices; the field carries over.
            path_length: Steps per ant per iteration. Under the `"step"`
                schedule this also scales the effective decay - see
                `evaporation_schedule`.
            beta: Exponent on edge weight. Raises the pull of similarity
                against pheromone.
            alpha: Exponent on pheromone. Above 1 sharpens the field toward
                what is already strong, which converges sooner and commits
                to boundaries sooner.
            evaporation_rate: Fraction removed per decay event, in [0, 1].
                What "event" means depends on the schedule.
            evaporation_schedule: `"step"` decays once per ant step, so the
                effective per-iteration decay is
                `1 - (1 - rate) ** path_length` - 0.516 at rate 0.07 with
                path_length 10, and the tail of a walk outweighs its start.
                `"iteration"` decays once before the ants move, as Ant System
                and MMAS do. **No value from the ACO literature transfers to**
                **`"step"`.**
            pheromone_deposit: Added per traversed edge, both directions.
            initial_pheromone: Starting value on every edge.
            tau_min: Lower clamp, applied once per iteration. Keeps an edge
                from reaching zero and becoming permanently unreachable.
            tau_max: Upper clamp. Bounds runaway reinforcement - the MMAS
                idea.
            n_ants: Ants per iteration. Required by `fit`; the production
                recipe is one per point.
            use_node_density: Whether to bias moves toward high-degree
                vertices.
            node_density_gamma: Exponent on density. Required when the flag
                is on.
            use_elite_ants: Whether some ants take the greedy move and
                deposit more.
            elite_ratio: Share of ants that are elite. Required when the flag
                is on.
            elite_multiplier: Deposit multiplier for elite ants. Required
                when the flag is on.
            elite_start_iteration: Iteration from which elites activate.
                Required when the flag is on - delaying them lets the field
                form before anything sharpens it.
            use_no_return: Whether an ant may step straight back where it
                came from.
            random_state: Seed for ant placement and choices.
            warmup: Whether to compile the kernels on a toy graph first, so
                the first iteration is not dominated by compilation.
            verbose: Whether to report progress and timings.

        Raises:
            ValueError: If any argument is outside its valid range or of the
                wrong type, if `tau_min` is not below `tau_max`, if
                `evaporation_schedule` is not one of the two, or if a
                heuristic parameter is missing while its flag is on.

        Warns:
            UserWarning: If `elite_start_iteration` is at or beyond
                `n_iterations`, which means elites never activate.
        """
        self.n_ants = _check_int("n_ants", n_ants, 1, allow_none=True)

        self.n_iterations = _check_int("n_iterations", n_iterations, 0)

        self.path_length = _check_int("path_length", path_length, 1)

        self.beta = _check_float("beta", beta, 0.0)

        self.evaporation_rate = _check_float("evaporation_rate", evaporation_rate, 0.0, 1.0)

        # WHEN the whole pheromone matrix decays, which is not the same
        # question as by how much.
        #
        # "step" - decay once per ant step, so `path_length` times per
        #   iteration. The effective per-iteration decay is
        #   `1 - (1 - evaporation_rate) ** path_length`: at rate 0.07 and
        #   path_length 10 that is 0.516, not 0.07. It also weights the tail
        #   of a walk over its start, since a deposit made at step k is
        #   evaporated (path_length - k) more times before the iteration ends.
        #   This is what the algorithm has always done.
        #
        # "iteration" - decay once, before the ants move, as Ant System and
        #   MMAS do. Deposits within an iteration then carry equal weight.
        #
        # The two are NOT interchangeable and no value from the ACO
        # literature transfers to "step". Which one is better here is an open
        # question to settle by measurement on the synthetic datasets, not by
        # argument: unlike TSP, a walk here is not a solution, so the
        # iteration boundary carries no inherent meaning.
        if evaporation_schedule not in {"step", "iteration"}:
            raise ValueError(
                f"evaporation_schedule must be one of {{'step', 'iteration'}}, got {evaporation_schedule!r}"
            )
        self.evaporation_schedule = evaporation_schedule

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

        self.random_state = _check_int("random_state", random_state, 0, allow_none=True)
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
        """Write a progress message when verbose, via tqdm to avoid clobbering bars."""
        if self.verbose:
            tqdm.write(msg)

    def _warmup(self) -> None:
        """Compile the kernels on a toy graph before the real run.

        numba compiles on first call, so without this the first iteration
        carries the compilation cost and every timing above it is misleading.
        """
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
        """Run the colony over the graph.

        The input is copied and canonicalised - duplicates summed, explicit
        zeros dropped, indices sorted - so the caller's matrix is left alone
        and the binary search in the update kernel is valid.

        Args:
            graph: A square, symmetric similarity graph with finite,
                non-negative weights. `GraphBuilder` produces one; a
                hand-built graph must be symmetric, or half of every deposit
                is discarded.

        Returns:
            The instance, so the call can be chained. The field itself is in
            `pheromone_matrix_`.

        Raises:
            ValueError: If `n_ants` is unset or not positive, if the graph is
                not square, empty, edgeless, holds NaN or inf or negative
                weights, or if a heuristic parameter is missing while its flag
                is on.

        Warns:
            UserWarning: If deposits landed on edges absent from the graph -
                it is not symmetric - or if `elite_ratio` rounds to zero elite
                ants.
        """
        if self.n_ants is None:
            raise ValueError("n_ants is required: set it explicitly, e.g. n_ants=len(X) to start")
        # Not dead code, though it looks it: the constructor already enforces
        # >= 1, but the staged design makes every parameter a public attribute,
        # and assigning one after construction bypasses that check entirely.
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
        missed_deposits = 0
        for iteration in tqdm(range(self.n_iterations), disable=not self.verbose):
            elites_active = (
                self.use_elite_ants
                and self.elite_start_iteration is not None
                and iteration >= self.elite_start_iteration
            )
            if elites_active and not elite_logged:
                self._log(f"  elite activated at iteration {iteration}")
                elite_logged = True
            missed_deposits += self._run_iteration(is_elite if elites_active else no_elite)
            self._clamp_pheromones()
        self._log(f"  swarm run in {perf_counter() - t_run:.2f}s")

        # The ACO deposits on both directions of every traversed edge, so a
        # missing reverse edge silently swallows half the deposit. Rather than
        # verifying symmetry up front - an O(nnz) allocation on every fit, and
        # prohibitive on a graph with 10^8 edges - the kernel counts the
        # deposits that landed nowhere, which is the damage itself.
        if missed_deposits > 0:
            warnings.warn(
                f"{missed_deposits:,} pheromone deposits fell on edges missing from the graph and were "
                f"discarded: the graph is not symmetric. Ants deposit on both (i, j) and (j, i), so the "
                f"result understates the reverse direction. Build the graph with GraphBuilder, or "
                f"symmetrize it before fitting.",
                stacklevel=2,
            )

        self._log(
            f"[aco] done: pheromone range "
            f"[{self.pheromone_matrix_.data.min():.3f}, {self.pheromone_matrix_.data.max():.3f}], "
            f"total {perf_counter() - t_start:.2f}s"
        )

        return self

    def _run_iteration(self, is_elite: np.ndarray) -> int:
        """Place the ants and walk them `path_length` steps.

        Args:
            is_elite: Which ants take the greedy move this iteration. All
                False before `elite_start_iteration`.

        Returns:
            Deposits that fell on edges missing from the graph.
        """
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

        # Before the ants move, so every deposit made during this iteration
        # carries the same weight - the Ant System / MMAS ordering.
        if self.evaporation_schedule == "iteration":
            self.pheromone_matrix_.data *= 1.0 - self.evaporation_rate

        missed = 0
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

            if self.evaporation_schedule == "step":
                self.pheromone_matrix_.data *= 1.0 - self.evaporation_rate

            if len(rows) > 0:
                missed += _update_edges(
                    self._indptr,
                    self._indices,
                    self.pheromone_matrix_.data,
                    rows,
                    cols,
                    vals,
                )

        return missed

    def _clamp_pheromones(self) -> None:
        """Clamp the field into [tau_min, tau_max].

        Once per iteration rather than per step - a deliberate trade. Values
        may briefly leave the range within an iteration; clamping on every
        step would cost a full pass over the matrix `path_length` times over.
        """
        assert self.pheromone_matrix_ is not None
        assert self.pheromone_matrix_.data is not None

        np.clip(
            self.pheromone_matrix_.data,
            self.tau_min,
            self.tau_max,
            out=self.pheromone_matrix_.data,
        )
