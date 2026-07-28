# Search log

Per LITERATURE.md: every query run, what it returned, including nothing useful.
Databases used: Google-backed web search (via the assistant's WebSearch tool,
which aggregates general web + indexed preprint/publisher pages), arXiv direct
fetch, CyberLeninka (blocked, see Category G). ACM Digital Library, IEEE Xplore
and Scopus were NOT queried directly - only reached indirectly through pages
that surfaced them via web search. This is a gap, noted at the end.

Date run: 2026-07-28.

## Category A - novelty (pheromone-threshold clustering)

Question: has anyone already built the exact mechanism this project uses -
pheromone accumulates on kNN-graph edges, no objective function, clusters read
off by thresholding the pheromone field?

| Query | Returned |
|---|---|
| `ant colony optimization graph clustering pheromone threshold` | Hu 2015 "Multiple Pheromone Table ACO for Clustering" (Wiley) - uses a pheromone threshold to split patterns, but pheromone update is driven by a clustering objective (compactness/variance), and ants operate on a complete graph over *patterns*, not a sparse kNN graph. Also KohonAnts (SOM-hybrid), L-NNACO, ant K-means - all objective-driven variants. |
| `ACO community detection pheromone density edges` | ACODIG and multi-objective ACO community detection - explicit objective functions (density/purity, modularity). Sadi/Etaner-Uyar/Gunduz-Oguducu 2009 (full text retrieved, see Sources) - ants find cliques, pheromone reflects clique-membership score, output feeds a modularity-maximizing algorithm afterward. Not a raw pheromone-threshold read. |
| `ant colony algorithm k-nearest neighbor graph clustering` | L-NNACO (Gao 2016) restricts ant moves to each point's L nearest neighbors but keeps the objective-function ACO loop (cluster variance) - closest kNN-graph-based ACO found, still not thresholded. Ant K-means: pheromone updates driven by total cluster variance. |
| `pheromone-based edge weighting community detection` | PGPPR (pheromone-guided personalized PageRank) - different diffusion mechanism (PageRank, not ant walks), and a random-walk edge-centrality pre-processing step feeding a separate community algorithm - not itself a threshold-and-read scheme. |
| `swarm intelligence graph partitioning pheromone accumulation` | AntPaP (Elazar & Bruckstein) - pheromone marks encode idle-time/cover-time to partition a graph among patrolling agents; no objective function, but the read-out is territorial ownership, not a scalar pheromone-density threshold, and there is no kNN-graph construction stage. Closest "no-objective-function + pheromone" hit found in the whole search; recorded in full under Sources. |

**Interim finding**: no source found where (a) the input graph is an explicit
kNN neighborhood graph over embeddings/points, (b) all ants deposit pheromone
identically, with no per-ant or per-solution quality score, and (c) the
cluster read-out is "threshold the scalar pheromone value per edge, take
connected components." Every ACO-for-clustering paper found retains a
fitness/objective term (cluster variance, modularity, density-purity) that
selects which pheromone updates count. This is a negative result across five
queries plus their citation trails (see Category E/D for the trails followed);
recorded as a finding, not a certainty - four databases (ACM DL, IEEE Xplore,
Scopus, Web of Science) were not queried directly, only surfaced incidentally.

## Category B - MCL and random-walk relatives

| Query | Returned |
|---|---|
| `Markov Clustering algorithm van Dongen graph` | Primary source found and retrieved: van Dongen, PhD thesis, "Graph Clustering by Flow Simulation" (2000), full text via datajobs.com mirror. Read in depth (intro + organization sections; the expansion/inflation formalism is in Ch. 5-7, not fully read). |
| `random walk based graph clustering survey` | Confirms family: LRW, PPC (personalized PageRank clustering), Walktrap, mixing-time methods - all random-walk-based, all with an explicit stopping/objective criterion (modularity, mixing time) except MCL itself. |
| `Walktrap community detection random walks Pons Latapy` | Walktrap (Pons & Latapy) - hierarchical agglomerative merge driven by a random-walk distance measure, complexity O(N^2 log N); abstract/secondary description only, primary paper not fetched. |
| `diffusion based community detection random walks` | Confirms MCL is grouped with PageRank/Walktrap/Infomap as the standard "diffusion" family; Synwalk (2021) reframes community detection as fitting a random-walk model - abstract only. |
| `"flow simulation" graph clustering Markov` | Same van Dongen thesis (also found via CWI technical report page and a UCSB course slide deck secondary summary) - confirms expansion=matrix power, inflation=elementwise power+renormalize, no fitness function, clusters read directly from the idempotent limit matrix's block structure - no external threshold step. |

**Interim finding**: MCL is the closest structural relative under Handl &
Meyer's own framing that pheromone-threshold ACO should be checked against -
both discard an explicit objective function and read the answer from a
converged field/matrix state. The mechanism differs sharply: MCL's "field" is
the transition matrix itself, deterministically iterated (expansion/inflation
on the *exact* Markov matrix), and its stopping point is a mathematically
idempotent matrix whose block structure *is* the clustering - no external
threshold or connected-components step is needed. This project's pheromone
field is a separate quantity from the transition probabilities, built by
finite noisy ant sampling on a sparse kNN graph (not the complete transition
matrix), and requires an explicit threshold + connected-components step
because there is no idempotency guarantee. Worth stating explicitly in the
dissertation as the nearest-relative comparison.

## Category C - canonical ACO parameter set

| Query | Returned |
|---|---|
| `MAX-MIN Ant System Stutzle Hoos pheromone trail limits` | Primary source retrieved (Stutzle & Hoos, MMAS, preprint PDF, lia.disi.unibo.it mirror). Read in depth: MMAS = (1) pheromone update restricted to iteration-best or best-so-far ant only, (2) trail values clamped to [tau_min, tau_max], (3) trails initialized at tau_max, (4) reinitialization on stagnation. |
| `Ant Colony System Dorigo Gambardella pseudo-random proportional rule q0` | ACS (Dorigo & Gambardella 1997) - pseudo-random-proportional rule with q0 (exploit vs. explore), local pheromone update on every edge traversal (with its own evaporation), global update restricted to best-so-far edges only. Secondary description, primary not fetched in full. |
| `rank-based ant system Bullnheimer Hartl Strauss` | Bullnheimer, Hartl & Strauss 1999, rank-based AS - only the sigma best ants deposit pheromone, weighted by rank; secondary description only. |
| `ACO parameter tuning survey alpha beta rho evaporation rate` | Generic confirmation of alpha (pheromone weight), beta (heuristic/distance weight), rho (evaporation) as the canonical triple, plus number of ants and iteration count; nothing beyond a standard tutorial-level description. |
| (full text) Sadi, Etaner-Uyar, Gunduz-Oguducu, "Community Detection Using ACO Techniques" (Mendel 2009) | Retrieved in full (web.itu.edu.tr, open PDF). Gives the exact AS/MMAS/ACS transition-probability and pheromone-update equations side by side, and the parameter table used in their own experiment (alpha=1, beta=2, rho=0.5, m=25, q0 in {0, 0.4, 0.8}). Used as the working cross-reference for building the "transferred / not transferred / not applicable" table, alongside the two primary sources above. |

**Interim finding**: enough primary + one full secondary source to build the
requested column honestly. Not yet fetched in full: the Dorigo & Stutzle 2004
MIT Press book itself (only ever available as a purchase, not found as an open
PDF in this search) and the original ACS/rank-based-AS papers. Every mechanism
above (best-only update, trail limits, pseudo-random-proportional q0,
rank-weighted deposit, local vs. global update) implicitly *requires* a way to
rank or compare ant solutions - i.e., an objective function. None of them has
an operational meaning without one, which is itself the direct evidence for
point 1 in the project's own differentiation list ("no target function, and
that is the main thing").

## Category D - ACO without an objective function

| Query | Returned |
|---|---|
| `ant colony optimization without objective function exploratory` | No direct hit. Web search's own synthesis explicitly states standard ACO is formalized as a triplet (S, Omega, f) with f an objective function to minimize, and could not surface a variant lacking one. |
| `stigmergy self-organization pattern formation graph` | General stigmergy/self-organization literature (biofilms, robotics) - relevant conceptually (structure without central control) but not a graph-clustering-via-ACO instance. |
| `pheromone field emergent structure detection graph no fitness` | Surfaced "Ant colony clustering with fitness perception and pheromone diffusion for community detection" (ScienceDirect) - name notwithstanding, it uses an explicit fitness function per the abstract; not a counter-example. |

**Interim finding (negative, load-bearing for the novelty argument)**: across
these queries plus the AntPaP hit recorded under Category A/E, no ACO
application was found that discards an objective function entirely while
still producing a genuine partition/clustering read directly off a pheromone
field via a scalar threshold. AntPaP is the single closest analogue (no
fitness function at all), but it solves graph *patrolling* with a *balanced
territorial partition* as an explicit byproduct of the patrol rule, not a
kNN-similarity-graph clustering task, and its read-out is agent ownership, not
a thresholded scalar field. This gap is exactly the novelty claim in
AGENTS.md/LITERATURE.md's framing and should be reported to the maintainer as
a "found nothing" result worth stating plainly, not softened - per five plus
three queries here and the citation trails through Category B/E, not a larger
formal database sweep.

## Category E - Deneubourg / Lumer-Faieta branch (disambiguation)

| Query | Returned |
|---|---|
| `Deneubourg 1991 ant corpse clustering robots larval sorting model` | Deneubourg et al., "The Dynamics of Collective Sorting: Robot-like Ant and Ant-like Robot," Proc. 1st Conf. on Simulation of Adaptive Behavior (1991) - identified via secondary sources (ResearchGate abstract pages), original not fetched (not freely available in this search). Mechanism per secondary description: ants move randomly, pick up/drop physical objects based on local density of similar objects around them - agents carry data, data does not stay fixed. |
| `Lumer Faieta 1994 diversity adaptation clustering ants numerical data` | Lumer & Faieta, "Diversity and Adaptation in Populations of Clustering Ants," SAB94 vol. 3, MIT Press, pp. 501-508 (1994) - identified via secondary sources (ACM DL listing, SCIRP reference page); full text not freely accessible in this search, so depth is abstract-level via secondary description only. Generalizes Deneubourg's model to numerical (non-corpse) data: objects are placed on a 2D grid, ants pick up/carry/drop objects based on a similarity function of the local neighborhood, positions on the grid encode the final grouping. One secondary source (a later analysis paper) states this scheme is formally related to Kohonen's Self-Organizing Batch Map. |
| `Handl Meyer ant-based clustering survey Deneubourg Lumer Faieta` | Handl & Meyer, "Finding groups in data: Cluster analysis with ants" (Applied Soft Computing, ScienceDirect) - the direct survey/extension of the Lumer-Faieta line; abstract page reached, full text paywalled, not retrieved. Secondary sources confirm Handl & Meyer extended Lumer-Faieta and applied it to web-document classification. |

**Interim finding**: confirms the mechanism this project must explicitly
distance itself from - in the Deneubourg/Lumer-Faieta/Handl-Meyer branch,
mobile agents pick up and physically relocate data items on a 2D grid or
similar substrate; the grid position at the end of the run *is* the
clustering. In this project's algorithm, ants move but data points are fixed
graph nodes; only the pheromone value on a fixed edge changes. This is a
clean, defensible distinction, but two of the three foundational sources
(Deneubourg 1991, Lumer & Faieta 1994) were reached only through secondary
description, not the primary text - flagged for the maintainer, since a VAK
review would expect the primary citation to be readable, not just cited from
a listing page.

## Category F - kNN graph and thresholding

| Query | Returned |
|---|---|
| `mutual kNN graph connectivity clustering high dimensional` | Confirms mutual-kNN as a standard remedy for kNN hub effects / distance concentration in high dimension, at the cost of disconnected components; one hit (arXiv 2108.05525, UMAP paper) discusses connectivity trade-offs directly relevant to this project's graph-construction stage. |
| `Otsu thresholding non-image data distribution application` | Otsu's method confirmed as maximizing between-class variance on a value histogram (Fisher's-discriminant equivalent), originally for image intensity; no example found of a non-image application analogous to thresholding a pheromone-value distribution. Its stated failure mode (works badly when the distribution isn't cleanly bimodal, or intra-class variance exceeds inter-class variance) is directly relevant to calibrating `find_threshold` in this project. |

**Interim finding**: no queries run yet for "k-nearest neighbor graph
clustering high dimensional" (general, non-mutual) or "graph sparsification
edge weight thresholding clustering" as separate searches - folded into the
above two since results were already converging (saturation signal per
LITERATURE.md). Flagged as incomplete below rather than padded with repeat
queries.

## Category G - Russian-language sources

| Query | Returned |
|---|---|
| `муравьиный алгоритм кластеризация графа` | Surfaced CyberLeninka: "Кластеризация МРТ-изображений: биостохастический метод муравьиной колонии" (ant-colony clustering of MRI images) - relevant Russian-language ACO-clustering application. Also a machine learning wiki page on "Markov clustering algorithm" (Russian) and Habr popular-science articles (not academic, not recorded as sources). |
| `роевой интеллект кластеризация данных обзор eLibrary` | Surfaced CyberLeninka: "Алгоритмы роевого интеллекта и их применение для анализа образовательных данных" - swarm intelligence survey, but scoped to educational-data analysis, tangential. |
| `муравьиные алгоритмы обзор параметры КиберЛенинка` | Surfaced CyberLeninka: "Обзор эволюционных методов оптимизации на основе роевого интеллекта" (survey of evolutionary swarm-intelligence optimization methods) and "К вопросу о параметрической оптимизации роевых алгоритмов" (on parametric optimization of swarm algorithms) - both look directly relevant to the parameter-canon question (Category C) in Russian-language literature. |

**Not retrieved**: all three CyberLeninka articles above returned a CAPTCHA
("Вы точно человек?") wall on fetch and could not be read - title, URL and
abstract-from-search-snippet only, recorded as **not retrieved** per the one
rule in LITERATURE.md, not filled in from inference. eLibrary itself was not
reached directly at all (no eLibrary URLs surfaced by the search tool; it may
require direct navigation/login). This is the weakest-covered category in
this pass and needs the maintainer's own institutional access to CyberLeninka
and eLibrary to close - flagged explicitly, not papered over.

## Overall stop condition

Stopped after Categories A-D showed saturation (new queries returning sources
already implied by earlier ones: objective-function-bearing ACO variants,
random-walk community detection family, MCL). Category E and F each got one
round since the task specified a small, closed set of names/queries and they
converged immediately. Category G stopped at the CAPTCHA wall rather than
attempting to bypass it (see web-fetch restrictions).

**Databases actually used**: general web search (Bing/Google-backed, via the
WebSearch tool), arXiv (direct PDF fetch), CyberLeninka (search-snippet only,
full text blocked). **Not used**: ACM Digital Library, IEEE Xplore, Scopus,
Web of Science, Semantic Scholar API, eLibrary.ru direct search - each only
seen incidentally through pages that referenced them. This is a real gap
against LITERATURE.md's "a search that used one database is not a survey"
standard and should be closed with tool/access the maintainer has (e.g.
institutional Scopus/IEEE access) before this is treated as a complete search.
