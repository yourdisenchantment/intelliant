"""test_absorb_edge_cases.py
# In-depth testing of absorb_pheromone and absorb_centroid:
# empty cores, zero clusters, batch size.
"""

import warnings

import numpy as np
import pytest
from conftest import make_clusterer, make_extractor, make_graph_builder
from scipy.sparse import csr_matrix


def section(title):
    print(f"\n=== {title} ===")


def _setup():
    rng = np.random.default_rng(42)
    X = rng.standard_normal((20, 4))
    gb = make_graph_builder(n_neighbors=5, verbose=False, random_state=42, mutual=False)
    G = gb.build(X)
    pe = make_extractor(n_ants=10, n_iterations=5, verbose=False, random_state=42)
    pe.fit(G)
    return X, pe.pheromone_matrix_


# 1. extract_cores with a threshold_value so high that cores_ is empty
def test_threshold_cuts_all_edges_empty_cores():
    section("threshold_value cuts all edges -> cores_ is empty")
    _, G_full = _setup()
    for thresh in [0.5, 5.0, 50.0, G_full.data.max() + 1.0]:
        print(f"  threshold_value={thresh}:")
        cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
        cores = cc.extract_cores(G_full, threshold_value=thresh)
        print(f"    cores_={cores}, n_cores={len(np.unique(cores[cores >= 0]))}")
        # at a threshold above the maximum all edges are cut -> cores_ all -1
        if thresh >= G_full.data.max():
            assert (cores == -1).all()


# 2. extract_cores with min_cluster_size greater than the number of points
def test_min_cluster_size_greater_than_n():
    section("min_cluster_size > N")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=50, batch_size=5, verbose=False)
    cores = cc.extract_cores(G_full, threshold_value=0.01)
    print(f"  cores_: unique={np.unique(cores)}, n_noise={(cores == -1).sum()}")
    assert (cores == -1).all()
    # absorb_pheromone should fail afterwards
    print("  absorb_pheromone with empty cores:")
    with pytest.raises(ValueError, match="no cores to absorb"):
        cc.absorb_pheromone(G_full)


# 3. absorb_pheromone with batch_size > N
def test_absorb_pheromone_batch_size_greater_than_n():
    section("absorb_pheromone with batch_size > N")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=1000, verbose=False)
    cc.extract_cores(G_full, threshold_value=0.01)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        labels = cc.absorb_pheromone(G_full)
    print(f"  labels: unique={np.unique(labels)}")


# 4. absorb_pheromone with batch_size=1
def test_absorb_pheromone_batch_size_one():
    section("absorb_pheromone with batch_size=1")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=1, max_iterations=3, verbose=False)
    cc.extract_cores(G_full, threshold_value=0.01)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        labels = cc.absorb_pheromone(G_full)
    print(f"  labels: unique={np.unique(labels)}")


# 5. fit_predict twice on the same clusterer
def test_fit_predict_twice_same_clusterer():
    section("fit_predict 2 times in a row on the same CoreClusterer")
    X, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    labels1 = cc.fit_predict(G_full, threshold_value=0.01, X=X)
    print(f"  1st time: unique={np.unique(labels1)}")
    labels2 = cc.fit_predict(G_full, threshold_value=0.05, X=X)
    print(f"  2nd time: unique={np.unique(labels2)}")
    # Labels may differ (threshold), but cores_, labels_pheromone_, labels_ are overwritten


# 6. absorb_pheromone with max_iterations=0
def test_absorb_pheromone_max_iterations_zero():
    section("absorb_pheromone with max_iterations=0")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, max_iterations=0, verbose=False)
    cc.extract_cores(G_full, threshold_value=0.01)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        labels = cc.absorb_pheromone(G_full)
    print(f"  labels: unique={np.unique(labels)}, n_noise={(labels == -1).sum()}")


# 7. extract_cores + absorb_centroid with external labels (cache scenario)
def test_absorb_centroid_with_explicit_labels():
    section("absorb_centroid with explicit labels (cache)")
    X, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(G_full, threshold_value=0.01)
    labels = cc.absorb_centroid(X, labels=cc.cores_.copy())  # pass cores directly as labels
    print(f"  labels: unique={np.unique(labels)}")


# 8. extract_cores + absorb_centroid with empty cores_ (all -1)
def test_absorb_centroid_all_noise_cores_raises():
    section("absorb_centroid when cores_ are all -1")
    X, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(G_full, threshold_value=G_full.data.max() + 1.0)  # cut everything
    print(f"  cores_: {cc.cores_}")
    assert (cc.cores_ == -1).all()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pytest.raises(ValueError, match="no labels for absorption"):
            cc.absorb_centroid(X)  # labels=None -> labels_pheromone_=None


# 9. absorb_centroid reassigns noise to cores
def test_absorb_centroid_reassigns_noise():
    """Checks that absorb_centroid assigns part of the noise (-1) to clusters (>= 0).

    We build 2 clear clusters + satellite points near one cluster; extract_cores
    leaves the satellites as -1, and absorb_centroid (by cosine to centroids) must
    assign them a label >= 0. Final -1 count after absorb_centroid must be smaller
    than in cores_.
    """

    section("absorb_centroid reassigns noise to cores")
    rng = np.random.default_rng(42)
    # Two dense clusters.
    c0 = rng.standard_normal((8, 4))
    c1 = rng.standard_normal((8, 4)) + np.array([10.0, 0.0, 0.0, 0.0])
    # Satellites near cluster 0 (weak link, become noise after cutoff).
    sats = rng.standard_normal((6, 4)) + np.array([0.0, 5.0, 0.0, 0.0])
    X = np.vstack([c0, c1, sats])
    N = len(X)

    gb = make_graph_builder(n_neighbors=5, mutual=False, verbose=False, random_state=42)
    G = gb.build(X)
    pe = make_extractor(n_ants=20, n_iterations=10, verbose=False, random_state=42)
    pe.fit(G)
    pheromone = pe.pheromone_matrix_
    assert pheromone is not None

    cc = make_clusterer(min_cluster_size=3, batch_size=5, verbose=False)
    cores = cc.extract_cores(pheromone, threshold_percentile=80.0)
    n_noise_cores = int((cores == -1).sum())
    print(f"  cores_: n_noise={n_noise_cores}/{N}, unique={np.unique(cores)}")

    # absorb_pheromone + absorb_centroid on embeddings.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cc.absorb_pheromone(pheromone)
        labels = cc.absorb_centroid(X)
    n_noise_final = int((labels == -1).sum())
    print(f"  labels_: n_noise={n_noise_final}/{N}, unique={np.unique(labels)}")

    # There must be progress: part of the noise is absorbed.
    assert n_noise_final < n_noise_cores


# 10. Giant cluster diagnostics: suspected=True on a clear size gap
def test_detect_giant_flagged():
    """Checks that _detect_giant marks suspected=True on a clear size gap.

    First runs extract_cores on synthetic data (large + small cluster) to make
    sure the diagnostics are computed on real core sizes. Then calls _detect_giant
    directly on a controlled array of sizes [30, 5]: gap 6.0 > gap_ratio=3.0 and it
    is at the head of the series, so suspected=True and max_gap/gap_pos are
    defined.
    """

    section("_detect_giant: suspected=True on a large size gap")
    rng = np.random.default_rng(42)
    # Large dense cluster + small one, well separated.
    big = rng.standard_normal((30, 4))
    small = rng.standard_normal((5, 4)) + np.array([50.0, 0.0, 0.0, 0.0])
    X = np.vstack([big, small])

    gb = make_graph_builder(n_neighbors=3, min_connections=3, mutual=False, verbose=False, random_state=42)
    G = gb.build(X)
    pe = make_extractor(n_ants=20, n_iterations=10, verbose=False, random_state=42)
    pe.fit(G)
    pheromone = pe.pheromone_matrix_
    assert pheromone is not None

    # Integration run: extract_cores computes diagnostics from core sizes.
    cc = make_clusterer(min_cluster_size=3, batch_size=10, gap_ratio=3.0, max_gap_rank=3, verbose=False)
    cores = cc.extract_cores(pheromone, threshold_percentile=80.0)
    sizes = np.unique(cores[cores >= 0], return_counts=True)[1]
    print(f"  cores_: unique={np.unique(cores)}, sizes={sizes.tolist()}")

    # Controlled gap: [30, 5] => gap=6.0 > gap_ratio=3.0, position 0 < max_gap_rank=3.
    diag = cc._detect_giant(np.array([30, 5]))
    print(f"  diag(controlled): {diag}")

    assert diag.max_gap is not None
    assert diag.gap_pos is not None
    assert diag.max_gap == 6.0
    assert diag.gap_pos == 0
    assert diag.suspected
    assert diag.n_clusters == 2
    assert diag.top_sizes == [30, 5]
    assert isinstance(diag.median, float)
    assert isinstance(diag.single, bool)
    assert diag.single is False

    # Case with no gap: [10, 9] => gap ~1.11 < gap_ratio=3.0 => suspected=False.
    diag_ok = cc._detect_giant(np.array([10, 9]))
    assert diag_ok.max_gap is not None
    assert not diag_ok.suspected

    # Single cluster: single=True, max_gap=None.
    diag_single = cc._detect_giant(np.array([7]))
    assert diag_single.single is True
    assert diag_single.max_gap is None
    assert diag_single.gap_pos is None
    assert not diag_single.suspected


# 11. absorb_pheromone: early termination when all points are already in cores
def test_absorb_pheromone_early_termination():
    """Checks the early termination branch of absorb_pheromone when there is no noise.

    We build a pheromone graph where all points belong to cores (cores_ without
    -1); absorb_pheromone must immediately enter the "all points resolved" branch
    (core_clusterer.py:374) without performing a single wave. The result
    labels_pheromone_ must match cores_ and contain no -1.
    """

    section("absorb_pheromone: early termination, no noise")
    # Fully connected graph on 6 vertices -> one component, the core covers all points.
    rows = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    cols = [1, 2, 0, 2, 0, 1, 4, 5, 3, 5, 3, 4]
    data = [2.0] * 12
    G = csr_matrix((data, (rows, cols)), shape=(6, 6))

    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cores = cc.extract_cores(G, threshold_value=0.01)
    assert (cores == -1).sum() == 0  # no noise

    labels = cc.absorb_pheromone(G)
    assert (labels == -1).sum() == 0
    assert np.array_equal(labels, cores)
    assert cc.labels_pheromone_ is not None
    assert (cc.labels_pheromone_ != -1).all()


# 12. absorb_pheromone: early stop on no progress
def test_absorb_pheromone_no_progress_stop():
    """Checks the "no progress - early stop" branch (core_clusterer.py:416).

    A core of 3 connected points + 3 isolated singletons (no edges). Noise points
    have no pheromone edges to the core, so nothing is resolved on the first wave;
    newly_resolved == 0 triggers early stop. The procedure terminates in finite
    time, and the isolates stay -1.
    """

    section("absorb_pheromone: early stop, isolates with no progress")
    rows = [0, 0, 1, 1, 2, 2]
    cols = [1, 2, 0, 2, 0, 1]
    data = [2.0] * 6
    G = csr_matrix((data, (rows, cols)), shape=(6, 6))

    cc = make_clusterer(min_cluster_size=2, batch_size=5, max_iterations=5, verbose=False)
    cores = cc.extract_cores(G, threshold_value=0.01)
    assert (cores[3:] == -1).all()  # points 3-5 are noise

    labels = cc.absorb_pheromone(G)
    # Isolates got no edges to the core -> stayed -1.
    assert (labels[3:] == -1).all()


# 13. absorb(): direct call to the wrapper and a warning at X=None
def test_absorb_wrapper_directly():
    """Checks a direct call to absorb() and a warning at X=None + absorb_isolated.

    First absorb() is called with X: it must return final labels of the correct
    length (labels_). Then on a fresh clusterer absorb() is called with X=None and
    absorb_isolated=True: the wrapper must emit exactly one warning about skipping
    stage 2 and still return labels (isolates stay -1).
    """

    section("absorb(): direct call with X and with X=None + absorb_isolated")
    rng = np.random.default_rng(42)
    X = rng.standard_normal((15, 4))
    gb = make_graph_builder(n_neighbors=3, min_connections=3, verbose=False, random_state=42, mutual=False)
    G = gb.build(X)
    pe = make_extractor(n_ants=5, n_iterations=2, verbose=False, random_state=42)
    pe.fit(G)
    ph = pe.pheromone_matrix_
    assert ph is not None

    # Direct call to absorb() with X.
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(ph, threshold_value=0.1)
    labels = cc.absorb(ph, X)
    assert labels is not None
    assert len(labels) == 15
    assert cc.labels_ is not None

    # absorb() with X=None + absorb_isolated=True and remaining noise -> warning.
    # The isolated weak pair (2, 3) stays noise after the waves, so stage 2
    # actually has work to skip.
    G_iso = csr_matrix(
        (np.array([0.9, 0.9, 0.05, 0.05]), (np.array([0, 1, 2, 3]), np.array([1, 0, 3, 2]))),
        shape=(4, 4),
    )
    cc2 = make_clusterer(min_cluster_size=2, batch_size=5, absorb_isolated=True, verbose=False)
    cc2.extract_cores(G_iso, threshold_value=0.1)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        labels2 = cc2.absorb(G_iso, X=None)
    assert labels2 is not None
    assert len(labels2) == 4
    assert len(w) == 1
    assert "stage 2" in str(w[0].message)


# 14. extract_cores: overriding min_cluster_size via an argument
def test_extract_cores_min_cluster_size_arg_override():
    """Checks that the min_cluster_size argument in extract_cores overrides the constructor.

    make_clusterer(min_cluster_size=10) when calling extract_cores(..., min_cluster_size=2)
    uses threshold 2, not 10: more cores pass the component-size filter, so the
    number of cores with override >= the number of cores with the constructor
    value 10 (on synthetic data with small components override finds more cores).
    """

    section("extract_cores: min_cluster_size argument overrides the constructor")
    _, G_full = _setup()

    cc_ctor = make_clusterer(min_cluster_size=10, batch_size=5, verbose=False)
    cores_ctor = cc_ctor.extract_cores(G_full, threshold_value=0.01)
    n_cores_ctor = int(np.unique(cores_ctor[cores_ctor >= 0]).size)
    print(f"  constructor min_cluster_size=10: n_cores={n_cores_ctor}")

    cc_override = make_clusterer(min_cluster_size=10, batch_size=5, verbose=False)
    cores_override = cc_override.extract_cores(G_full, threshold_value=0.01, min_cluster_size=2)
    n_cores_override = int(np.unique(cores_override[cores_override >= 0]).size)
    print(f"  argument min_cluster_size=2: n_cores={n_cores_override}")

    # A smaller size threshold lets more components through as cores.
    assert n_cores_override >= n_cores_ctor
    # The constructor value must not have been clobbered by the override call.
    assert cc_override.min_cluster_size == 10


# 15. absorb_centroid directly with X=None and no noise left: no warning
def test_absorb_centroid_x_none_directly():
    """Checks a direct call to absorb_centroid(X=None) when no noise remains.

    Since polish round 1 the skip warning lives in absorb_centroid itself and
    fires only when there is actual noise left to absorb. Here the passed labels
    contain no noise, so stage 2 has nothing to skip: no warning is emitted and
    the labels stay equal to the passed labels.
    """

    section("absorb_centroid directly with X=None and no remaining noise: no warning")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, absorb_isolated=True, verbose=False)
    cores = cc.extract_cores(G_full, threshold_value=0.01)
    assert (cores >= 0).all()  # premise: nothing left for stage 2

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        labels = cc.absorb_centroid(X=None, labels=cores.copy())
    # No remaining noise -> nothing was skipped -> no warning.
    assert len(w) == 0
    # Without X the centroid fallback is not launched -> labels are unchanged.
    assert np.array_equal(labels, cores)
    assert cc.labels_ is not None
    assert np.array_equal(cc.labels_, cores)


# 15a. absorb_centroid directly with X=None and remaining noise: exactly one warning
def test_absorb_centroid_x_none_with_noise_warns_once():
    """Checks that a direct absorb_centroid(X=None) call warns when noise remains.

    One strong core pair (0, 1) and an isolated weak pair (2, 3): after
    thresholding at 0.1 nodes 2 and 3 are noise, so stage 2 has actual work to
    skip. The direct call (no absorb() wrapper) must emit exactly one
    UserWarning, matching its docstring contract (REVIEW #4), and leave the
    noise points at -1.
    """

    section("absorb_centroid directly with X=None and remaining noise: one warning")
    G_iso = csr_matrix(
        (np.array([0.9, 0.9, 0.05, 0.05]), (np.array([0, 1, 2, 3]), np.array([1, 0, 3, 2]))),
        shape=(4, 4),
    )
    cc = make_clusterer(min_cluster_size=2, batch_size=5, absorb_isolated=True, verbose=False)
    cores = cc.extract_cores(G_iso, threshold_value=0.1)
    assert (cores[2:] == -1).all()  # premise: stage 2 has work to skip

    with pytest.warns(UserWarning, match="stage 2") as record:
        labels = cc.absorb_centroid(X=None, labels=cores.copy())
    assert len(record) == 1
    # Stage 2 skipped: the noise pair stays -1.
    assert np.array_equal(labels, cores)


# 15b. absorb_centroid: zero cores + external labels + X -> clean ValueError
def test_absorb_centroid_zero_cores_external_labels_raises():
    """Checks the "no cores to absorb" guard in absorb_centroid (REVIEW #3).

    extract_cores with a threshold above the maximum leaves cores_ all -1;
    calling absorb_centroid with external labels and X used to crash with a raw
    numpy "zero-size array to reduction operation" error from
    valid_clusters.max(). Now it must raise the same clean ValueError as
    absorb_pheromone.
    """

    section("absorb_centroid: zero cores + external labels + X -> ValueError")
    X, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(G_full, threshold_value=G_full.data.max() + 1.0)
    assert (cc.cores_ == -1).all()

    with pytest.raises(ValueError, match="no cores to absorb"):
        cc.absorb_centroid(X, labels=np.full(len(X), -1))


# 15c. extract_cores: per-call min_cluster_size type contract
def test_extract_cores_min_cluster_size_percall_type_contract():
    """Checks that the per-call min_cluster_size matches the constructor contract.

    Previously extract_cores checked only <= 0, so 2.5 and True slipped through
    while the constructor rejected them (REVIEW #10). Now both go through
    _check_int: float, bool and 0 raise ValueError; np.int64 is accepted and
    behaves like the plain int, without clobbering the constructor value.
    """

    section("extract_cores: per-call min_cluster_size 2.5 / True / 0 / np.int64(3)")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=10, batch_size=5, verbose=False)

    for bad in [2.5, True, 0]:
        with pytest.raises(ValueError, match="min_cluster_size must be int >= 1 or None"):
            cc.extract_cores(G_full, threshold_value=0.1, min_cluster_size=bad)

    cores_np = cc.extract_cores(G_full, threshold_value=0.1, min_cluster_size=np.int64(3))
    cores_int = cc.extract_cores(G_full, threshold_value=0.1, min_cluster_size=3)
    assert np.array_equal(cores_np, cores_int)
    # The constructor value is untouched by per-call overrides.
    assert cc.min_cluster_size == 10


# 15d. absorb_pheromone: graph shape / size / finiteness validation (R2-2, R2-8)
def test_absorb_pheromone_rejects_bad_graph():
    """Checks that absorb_pheromone validates its graph like extract_cores.

    Before round 2 a non-square or wrong-size graph slipped past validation (a
    smaller one crashed with a raw IndexError, a larger one was silently
    accepted against the wrong adjacency), and NaN weights were accepted
    silently. All four now raise a clean ValueError.
    """

    section("absorb_pheromone: non-square / smaller / larger / NaN graph -> ValueError")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(G_full, threshold_value=0.01)

    with pytest.raises(ValueError, match=r"pheromone graph must be square \(N, N\), got shape \(3, 5\)"):
        cc.absorb_pheromone(csr_matrix((3, 5)))

    edge = (np.array([0.5, 0.5]), (np.array([0, 1]), np.array([1, 0])))
    small = csr_matrix(edge, shape=(5, 5))
    with pytest.raises(ValueError, match=r"pheromone graph size \(5\) does not match the number of points in cores"):
        cc.absorb_pheromone(small)

    big = csr_matrix(edge, shape=(25, 25))
    with pytest.raises(ValueError, match=r"pheromone graph size \(25\) does not match the number of points in cores"):
        cc.absorb_pheromone(big)

    bad = G_full.copy()
    bad.data[0] = np.nan
    with pytest.raises(ValueError, match="pheromone graph contains NaN or inf"):
        cc.absorb_pheromone(bad)


# 15e. extract_cores: per-call threshold argument type contract (R2-3)
def test_extract_cores_percall_threshold_type_contract():
    """Checks that per-call threshold args go through _check_float.

    Before round 2, threshold_value="0.5" raised a raw TypeError from
    np.isfinite, threshold_percentile="50" a TypeError from a chained
    comparison, and True was accepted as 1.0 for both. A negative
    threshold_value stays legitimate (keeps every edge).
    """

    section("extract_cores: threshold_value / threshold_percentile bool and str -> ValueError")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)

    with pytest.raises(ValueError, match="threshold_value must be a number, got True"):
        cc.extract_cores(G_full, threshold_value=True)
    with pytest.raises(ValueError, match=r"threshold_value must be a number, got '0\.5'"):
        cc.extract_cores(G_full, threshold_value="0.5")
    with pytest.raises(ValueError, match="threshold_percentile must be a number, got True"):
        cc.extract_cores(G_full, threshold_percentile=True)
    with pytest.raises(ValueError, match="threshold_percentile must be a number, got '50'"):
        cc.extract_cores(G_full, threshold_percentile="50")

    # Negative cutoff is a valid way to keep all edges (weights are positive).
    cores = cc.extract_cores(G_full, threshold_value=-1.0)
    print(f"  threshold_value=-1.0: unique={np.unique(cores)}")
    assert (cores >= 0).any()


# 15f. absorb_centroid: 1-D X raises a clean ValueError (R2-7)
def test_absorb_centroid_1d_x_raises():
    """Checks that a 1-D X of matching length is rejected up front.

    len() of a 1-D array passes both length checks, so before round 2 the
    failure surfaced as a raw IndexError from X.shape[1] deep in stage 2.
    """

    section("absorb_centroid: 1-D X -> ValueError")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)
    cc.extract_cores(G_full, threshold_value=0.01)
    assert cc.cores_ is not None

    with pytest.raises(ValueError, match="X must be a two-dimensional array"):
        cc.absorb_centroid(np.zeros(len(cc.cores_)), labels=cc.cores_.copy())


# 16. extract_cores: reset of derived labels on a repeated call
def test_extract_cores_reset_state():
    """Checks that a repeated extract_cores resets labels_pheromone_ to None.

    After the first extract_cores, absorb_pheromone is called (fills
    labels_pheromone_). A second extract_cores with a different threshold must
    reset labels_pheromone_ and labels_ to None, and cores_ must reflect the new
    threshold.
    """

    section("extract_cores: reset of labels_pheromone_ on a repeated call")
    _, G_full = _setup()
    cc = make_clusterer(min_cluster_size=2, batch_size=5, verbose=False)

    # First run: extract_cores + absorb_pheromone (fills labels_pheromone_).
    cc.extract_cores(G_full, threshold_value=0.01)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cc.absorb_pheromone(G_full)
    assert cc.cores_ is not None
    assert cc.labels_pheromone_ is not None

    # Second run with a different threshold: derived labels are reset.
    cores2 = cc.extract_cores(G_full, threshold_value=G_full.data.max() + 1.0)
    assert cc.labels_pheromone_ is None
    assert cc.labels_ is None
    # cores_ reflects the new threshold: all edges cut -> all noise.
    assert (cores2 == -1).all()
    assert (cc.cores_ == -1).all()
