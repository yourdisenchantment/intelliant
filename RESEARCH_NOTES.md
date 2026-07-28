# Research Notes: Multilevel Graph Clustering via ACO

Research ideas that are deliberately outside [ROADMAP.md](ROADMAP.md) but
matter to the project long-term. **Working notes, not a work plan**: nothing
here is a commitment to implement, there is no formal justification structure,
and no literature review has been conducted. The purpose is to keep the
reasoning recoverable rather than to defend it.

The multilevel scheme below is a second algorithm that uses the flat one as a
building block. It is expected to become a separate dissertation chapter or a
second paper, and is deliberately not started until the flat version is
published - see "When to return to this idea".

---

## Concept: Hierarchical Clustering via Multilevel ACO

### Basic idea

After completing a standard ACO run and obtaining a flat partition, the
proposed approach is to **recursively apply the algorithm** to a coarsened
graph representation. Each cluster found at level L is physically collapsed
into a single point (a virtual super-node) at level L+1. All edges that
previously connected internal cluster points to external ones (noise or
other clusters) move to the centroid. Pheromones are fully reset between
levels. ACO is restarted on the reduced graph.

The process continues until one of the stopping conditions is met: complete
noise absorption, cluster invariance between levels, or collapse into a
single super-cluster (a pathological case).

### Centroid as absorber

To prevent erroneous merging of centroids via parasitic inter-centroid edges
(see "Open questions" below), a unified ant behavior rule is introduced: the
centroid is an absorption point, not a source and not a transit node.
Specifically, this means three constraints:

- Ants do not land on centroids during initialization (the starting position
  is always a regular node).
- An ant that reaches a centroid during its path does not take the next step
  - the path terminates, pheromone is deposited on the leading edge in the
  standard manner, the ant is reborn at a new random graph point.
- Inter-centroid edges may exist in the graph (for informativeness and
  potential meta-connection construction), but are never used for
  transitions.

This is an implementation of the "black hole" physical metaphor in
graph-space: the high degree of the centroid makes it an attractor for
incoming noise, and the structural prohibition on exiting the centroid
guarantees that two adjacent centroids do not merge via a direct ant
transition between them.

An additional effect - centroids accumulate pheromone only on leading
(incoming) edges, which strengthens the connection of surrounding points to
the center without diluting it via further transitions.

### Label history as the primary result representation

After completing the multilevel run, each original point receives not a
single label, but a **label vector of length L+1**, where L is the number of
executed levels. Essentially this is the **coordinate of the point in the
hierarchy tree**: each array position is its "address" at the corresponding
level of abstraction.

Stored as an array of shape `(N, L+1)` with type `int32`. A value of `-1`
means "the point was noise at this level".

Semantically, the history represents a **path of the point through parent
clusters**. Reading it left to right, we see which entities the point
belonged to at each level of generalization:

Example history of a point absorbed at the third level:

```
[-1, -1, -1, 7, 12, 2]
                ^   ^  ^
                |   |  +- super-cluster of level 5
                |   +- parent cluster of level 4
                +- absorption core of level 3
```

Example history of a point that was a core from the start and merged into a
super-cluster only at the top level:

```
[7, 7, 7, 7, 7, 2]
```

Example of "true" noise that never found a place at any level:

```
[-1, -1, -1, -1, -1, -1]
```

This representation is dual to the reverse mapping table ("which points are
in which centroid") - one is recovered from the other. Choosing history as
the primary representation is justified because typical user queries are
naturally expressed through point attributes, not cluster attributes:

- Final labels at any level of abstraction are a column of the history
  matrix.
- "When did the point stop being noise" is the position of the first
  non-`-1` element in its history.
- Finding points with similar coarse-level semantics but different
  fine-level - group by column `L_high`, split by `L_low`.
- Lowest common ancestor of two points is the leftmost position where labels
  in their histories match.

Repeated labels between levels (e.g. `7, 7, 7` in a row) are **meaningful
information**, not duplication: they encode the fact that the corresponding
cluster did not merge with anyone at these levels and retained its identity.
Points in "stable cores" have long repeats; points in clusters that entered
large mergers early have short ones.

Label numbering convention: labels at each level form an **independent
identifier space** (label 7 at level 1 and label 7 at level 2 are unrelated
entities, do not conflate). An alternative is prefix numbering (`"2_7"`
instead of `7`) - ensures uniqueness at the cost of compactness. The choice
is deferred until implementation.

Considered and rejected alternative representations:

- **Absorption moment only** (a single number `absorbed_at` + one final
  label) - loses information about intermediate mergers, does not allow
  recovering the parent path.
- **Moment + trajectory** (storage starting from the absorption level) -
  saves ~50% memory but complicates vectorized numpy operations. At
  realistic scales (3M points x 10 levels = 120 MB for full history), the
  savings do not justify the complexity.

### "Apple cross-section" structure

The multilevel label history gives rise to an interpretable nested cluster
structure. Inside are the "pips" - the initial dense cores found at level 0.
Around them, successive layers of "flesh" grow - points absorbed at later
levels. Each flesh point has a label at all levels starting from its
absorption level.

Useful diagnostic statistics derived from this structure:

- Distribution of "absorption age" of points across levels. A sharp peak at
  level 0 means the algorithm found everything at once, multilevel
  processing is redundant. A spread distribution means hierarchical
  structure is present.
- Proportion of points remaining noise up to the topmost level. This is
  "true" unstructured noise.
- Label stability of a point between levels. Jumping points are boundary
  points between clusters and are informative for analysis.

These statistics become direct analogs of the condensed tree and stability
score from HDBSCAN, but obtained through an emergent ACO process, not
through analytical MST.

### Multitask output from a single run

A single multilevel ACO run produces a **history matrix**, from which
several different products are extracted depending on the user query. This
fundamentally distinguishes the scheme from flat clustering methods: the
user should not decide in advance at what level of detail they operate -
they get all levels and choose a slice per task.

Possible products from one matrix:

- **Fine thematic cores.** Flat slice of the bottom level (column
  `history[:, 0]`). Pure, narrowly specialized clusters with a large amount
  of noise. Suitable for tasks requiring maximum semantic precision on
  narrow topics.
- **Coarse macro-topics.** Flat slice of the top level (column
  `history[:, -1]` or close to it). Few clusters, low noise fraction, broad
  thematic categories. Suitable for aggregation, classification into a
  small number of categories, overview analysis.
- **Intermediate generalizing categories.** Slice at any middle level. A
  compromise between purity and coverage.
- **Hierarchical structure.** Analyze matrix rows as tree paths. Suitable
  for building a dendrogram, finding the nearest common ancestor for a pair
  of points, estimating semantic distance.
- **Absorption dynamics.** Analyze transitions between columns - at which
  level which cores merged, which points remained noise until the very end.
  Suitable for exploratory analysis of the data structure itself.

This multitask capability becomes a strong comparative argument against flat
methods. Not "my algorithm gives 5% higher ARI than HDBSCAN", but "my
algorithm produces five different user products from a single run, for
which a flat method needs to be restarted with different parameters".

### Noise as structure: the semantic fabric between cores

In flat clustering, noise is a category of "points outside clusters",
without internal structure. In the multilevel scheme, noise acquires
structural meaning: what remains noise at level 0 may **form its own
clusters** at subsequent levels, consisting not of original points but of
former noise.

Semantically, these clusters differ from the original cores. They do not
represent narrow topics but form a **connecting fabric between cores** -
low-density diffuse regions that are simply discarded in flat clustering.
Example from the text domain: at level 0, cores "AI startups", "quantum
computing", "CPU releases" may be found. Points that fit none of them may
form a cluster at level 2 - "technology news in a broad sense" - a
generalizing category absent from the first-level cores.

This effect is a natural consequence of the architecture. At each level,
coarsening frees the graph from already-found structure; what remains is
re-evaluated from scratch and may turn out to be clusterable under new
conditions. What was perceived as noise in the presence of strong
attractors, after they are moved to absorber-centroids, becomes its own
structure.

Semantically, such "noise clusters" represent **semantic bridges between
cores**. They are less defined than the cores themselves, but not random -
they have their own center of gravity and thematic content. For tasks where
not only classification matters but also understanding intermediate
categories (topic modeling, collection exploration), this is a potentially
valuable product.

### Granularity trade-off as a known problem

The observation "many pure clusters and lots of noise OR few dirty clusters
without noise" is the **stability vs granularity trade-off**, a fundamental
dilemma of hierarchical clustering. It has no universal solution, because
the "right level of detail" is task-dependent.

HDBSCAN solves it via `cluster_selection_method` (`leaf` for fine
granularity, `eom` for coarse). These are not two different algorithms but
two ways of extracting a flat partition from a single hierarchy. Multilevel
ACO offers a similar handle - choosing the history matrix slice level - but
with more transparent semantics (literally "at what level of generalization
we look").

### Relation to literature

The approach belongs to the family of **multilevel graph clustering** /
**hierarchical graph coarsening**, known since the late 1990s (METIS,
Karypis & Kumar 1998). Modern representatives are Louvain (2008), Leiden
(2019). The basic coarsening idea is not new.

What is potentially new is the **collapse mechanism via ACO** with
preservation of pheromone structure between levels (through graph
compression, not through the pheromone values themselves). A systematic
literature review of this aspect has not been conducted; a confident claim
of novelty requires searching the ACO-clustering branch and hybrid ACO +
hierarchical methods.

### Gravity analogy - refinement

The initial intuition was: in the compressed graph, the centroid has an
extremely high degree, which creates asymmetry in ant navigation. Merging
is impeded by the topology itself.

**This intuition was partially wrong.** The correct picture:

The centroid does pull noise points toward itself - this works. A noise
point with an edge to the centroid will likely traverse that edge due to
the high density of the target node. Noise absorption through multilevel
ACO works via this mechanism.

But between two centroids the effect is opposite to what was expected: if
there is even one connecting edge, it becomes a **highway** for ants, not a
rare connection. Without a structural prohibition on inter-centroid
transitions, the scheme leads to guaranteed merging.

The correct formulation of the metaphor: the centroid is not just a
gravitational well, but a **black hole with an event horizon**. Points are
attracted to it, but do not exit back - this is what ensures isolation of
centroids from each other. The implementation of this metaphor is the
absorption mechanism described above.

### Merging as hierarchical information

If, despite protection via absorption, a situation arises where two level
L+1 clusters semantically merge (e.g. through statistical union of their
noise boundaries at L+2), this is **not information destruction**. Level L
labels are preserved in each point's history. Merging at the top level
enriches the data with a meta-connection: "these two clusters are similar
at a coarser level of abstraction".

From the perspective of hierarchical clustering, such behavior is a
feature, not a bug. This is the natural way of building a dendrogram through
an emergent process: at each level, exactly the degree of detail supported
by the current graph structure is discovered.

### Open questions

**1. Centroid merging: resolved architecturally via the absorption
mechanism.**

Initially it was believed that node degree asymmetry by itself prevents
merging. **This is incorrect.** Correct analysis:

The neighbour selection rule as implemented: `p(i->j) ~ tau^alpha *
weight^beta * density`, where the density factor enters linearly and is
switched on by `use_density` - there is no separate exponent for it. At a
`beta` of around 3, an inter-centroid edge has:

- High **weight** (connection between dense regions is usually strong).
- Extremely high **density** of the target node.
- Growing **tau** upon any visit.

Comparison in numbers:

```
inter-centroid edge: 0.85^3 * 500_000 ~= 3*10^5
noise edge:          0.4^3  * 1       ~= 6*10^-2
```

Without protection, ants would avalanche between centroids, **guaranteeing**
a merge.

**Solution** integrated into the architecture (see "Centroid as absorber"
section): the centroid is structurally deprived of outgoing transitions.
This eliminates the problem at the level of ant behavior rules, without
needing to intervene in graph topology or apply heuristic penalties.

Alternative options considered and rejected:

- Physically removing inter-centroid edges during coarsening - loses
  information about inter-cluster connection strength.
- A penalty in the selection rule - requires coefficient calibration,
  semi-heuristic.
- A "non-traversable" flag on an edge - a special case of the absorber, less
  general.

The chosen approach (centroid as absorber) is the most general: one rule
solves three tasks simultaneously (merge protection, correct initialization,
directed pheromone accumulation).

**2. Absorption of weak cores by strong ones.**

If there is a weak dense sub-core in the noise, it may not have time to form
at the second level, because ants are pulled toward existing centroids with
extreme degree. This is treated by choosing the edge aggregation function
during coarsening (`mean` vs `max`), but only an experiment can answer
definitively: synthetic data of N strong clusters + one weak one, checking
whether the weak cluster is detected at subsequent levels.

**3. Detecting merged cores before compression.**

In the flat version, a hyper-cluster (parasitic merge of two real cores) is
a bad label, reversible via absorption. In the multilevel version, it is an
**irreversible error**: after coarsening, the original points disappear,
separating the cores retroactively is impossible.

This requires diagnostics before each coarsening step: does the
centroid-candidate represent a single cluster or a merge? Possible
approaches - spectral check of the cluster subgraph, a bimodality test on
the intra-cluster distance distribution, subgraph modularity check. This is
an independent research question with direct value for the flat version too
(where it enhances giant handling).

**4. Stopping criterion.**

Greedy stopping (down to a single super-cluster) is meaningless. A rule
analogous to the critical point in hierarchical methods is needed: the
level after which new compressions yield no informative gain. One option is
tracking the change in centroid density between levels and stopping when a
plateau is reached.

**5. Computational cost.**

Each level is a full ACO run. On 120k points, a base run is ~30 seconds, 4
levels is ~2 minutes. On 3M - ~20 minutes instead of 5. Coarsening gives
exponential graph size reduction, so upper levels are substantially faster
than lower ones. But the exact savings depend on how aggressively the graph
is compressed at each step.

### What needs to be decided in advance, before implementation

- Edge weight aggregation function during coarsening (max, mean,
  sum-with-cap, something else).
- Storage of the "level L centroid -> level L-1 points" mapping for final
  recovery of original labels.
- Pheromone reset strategy between levels (full reset, partial reset
  preserving only intra-cluster traces, other options).
- ACO parameters for upper levels (same `n_ants` as at the base level, or
  adaptive to graph size).

### When to return to this idea

After publishing the first article on the flat version of the algorithm.
The multilevel version is a **new algorithm** that uses flat ACO as a
building block, and warrants a separate dissertation chapter or a second
paper. Doing it in parallel with bringing the flat version to a publishable
state risks finishing neither.

The comparative narrative for the scientific work is not "my method is
better than HDBSCAN by ARI at one level", but **"my method yields several
different products from a single run"**. On pure ARI at the fine slice,
parity is acceptable; on multitask capability, hierarchy interpretability,
and intermediate category analysis, there are structural advantages.

---

## Adjacent idea: detecting merged cores in the flat version

Arose as a byproduct of discussing the multilevel scheme. The flat version
detects giants by size distribution - `GiantDiagnostics` reports the largest
ratio between neighbouring ranks and whether it sits near the head, tuned by
`gap_ratio` and `max_gap_rank`. Detection is deliberately separate from
intervention there, and that separation is the right one, but the underlying
signal is still size: a large cluster may be a single dense core, while a
medium one may be two merged cores.

A possible mechanism is a **unimodality check** of the intra-cluster
distance distribution or **spectral diagnostics** of the cluster subgraph
(ratio of lambda_2 / lambda_1 of the Laplacian). High bimodality or close
first two eigenvalues is an indicator that the cluster is composite.

This direction has value independently of the multilevel version: it gives
the giant check a criterion based on structure rather than on size, and feeds
the threshold work already in the roadmap. Worth promoting to a roadmap item
once the real-data baseline exists.
