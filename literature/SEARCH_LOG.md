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
| `ant colony algorithm k-nearest neighbor graph clustering` | **[CORRECTED in pass 2: L-NNACO is Tseng, Chiang & Yang, ICMLC 2013, not Gao 2016]** L-NNACO restricts ant moves to each point's L nearest neighbors but keeps the objective-function ACO loop (cluster variance) - closest kNN-graph-based ACO found, still not thresholded. Ant K-means: pheromone updates driven by total cluster variance. |
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


---
---

# Pass 2 - 2026-07-29


Date run: 2026-07-29. Appends to `literature/SEARCH_LOG.md`; does not
overwrite it. Per LITERATURE.md: every query, and what it returned, including
the ones that returned nothing.

## Which databases were actually reached, and which were not

This is the part pass 1 could not write. Stated plainly.

| Database | Reached directly? | How, or why not |
|---|---|---|
| **IEEE Xplore** | **yes** | Searched directly in the maintainer's Chrome, seven queries, results and abstracts read on the publisher's own pages. Search and abstracts are open; **full text is not** - no institutional session is active on that browser ("Institutional Sign In" / "Personal Sign In" are both offered, and `stamp.jsp` bounces back to the record page for subscription content). |
| **OpenAlex** | **yes** | REST API, unauthenticated. Used for title/abstract field search and for forward citation tracing. Indexes Crossref, PubMed, DOAJ, arXiv and MAG; comparable in scale to Scopus, and it is the database that produced the decisive hit. |
| **Crossref** | **yes** | REST API. Used for DOI verification and for authoritative bibliographic fields. |
| **Semantic Scholar** | **partly** | Graph API worked for per-DOI lookups; the search endpoint returned HTTP 429 (rate limit) and was not retried. |
| **Unpaywall** | **yes** | REST API, used to establish open-access status for each paywalled item rather than guessing. |
| **SpringerLink** | **abstracts only** | Chapter pages fetched successfully (via the redirect chain through `idp.springer.com`); full text paywalled. Refused by the browser extension's navigation policy. |
| **ACM Digital Library** | **NO** | Blocked on every available route. `WebFetch` → HTTP 403. `curl` with a browser user agent → HTTP 403 (Cloudflare bot protection). The browser extension refuses `dl.acm.org` with "Navigation to this domain is not allowed". **Still not queried directly. This gap is unchanged from pass 1.** |
| **Scopus** | **NO** | `www.scopus.com` refused by the extension's navigation policy. Requires an institutional session in any case. |
| **Web of Science** | **NO** | `www.webofscience.com` refused by the extension's navigation policy. Same. |
| **CyberLeninka** | **NO** | `cyberleninka.ru` refused by the extension's navigation policy - so this pass did not even reach the CAPTCHA that stopped pass 1. |
| **eLibrary.ru** | **NO** | Not reached; same navigation policy. |
| **Google Scholar** | **NO** | `scholar.google.com` refused by the extension's navigation policy. |
| **arXiv** | **NO (browser)** | `arxiv.org` refused by the extension; not needed this pass, since the target literature is not on arXiv. |
| **Wiley Online Library** | **NO** | HTTP 402 to `WebFetch`; `onlinelibrary.wiley.com` refused by the extension. Hindawi's own `downloads.hindawi.com` returns 403 to curl and WebFetch. |

**On the maintainer's browser.** It is connected and working - one Chrome
instance, macOS, local. But its navigation allowlist currently permits only
`ieeexplore.ieee.org` out of every domain this search needed. Every other
publisher, index and Russian-language database was refused at the extension
level before any page load, so none of them ever presented a login or a
CAPTCHA. **No CAPTCHA was attempted and no credential was entered anywhere.**

## Category A - novelty (pheromone-threshold clustering). IEEE Xplore, direct.

Run against IEEE Xplore's own search, results read on the publisher's pages.

| # | Query (IEEE Xplore syntax) | Hits | What came back |
|---|---|---|---|
| A1 | `("ant colony" AND clustering AND pheromone AND threshold)` | 27 | Mostly image thresholding by ACO, WSN routing, and grid-based ant clustering. **One structural hit: "Data clustering by ant colony on a digraph" (Chen, Tu, Chen, ICMLC 2005).** Also "A Novel Ant-based Clustering Algorithm with an Attractive Force Field" (Zhang & Cao 2010), "Clustering PPI Data Based on ACO" (Lei et al. 2013), "Automatic threshold selection based on ACO" (Ye et al. 2005, image thresholding). |
| A2 | `("ant colony" AND ("nearest neighbor graph" OR "k-nearest neighbor graph" OR "knn graph") AND clustering)` | **2** | "Beyond Predefined Clusters: A Comprehensive Review of Clustering Methods for Unknown Numbers of Clusters" (TKDE 2026, a review) and "Hierarchical Laplacian Score for unsupervised feature selection" (IJCNN 2018). **Neither is an ACO method operating on a kNN graph.** |
| A3 | `(pheromone AND "connected components" AND clustering)` | **1** | Exactly one document in the whole database, and it is the Chen/Tu/Chen digraph paper again. |
| A4 | `("ant colony" AND "community detection" AND pheromone)` | 7 | He et al. 2011, Javadi et al. 2014, Mu et al. 2014, Chang et al. 2013, Song et al. 2014 - all modularity- or fitness-driven, consistent with pass 1. One new item of interest: **"Clustering Social Networks Using Competing Ant Hives" (Held, Dockhorn, Krause, Kruse, ENIC 2015)** - hive-specific pheromone on nodes, no objective function evident. Recorded as source #11. |
| A5 | `(pheromone AND ("graph clustering" OR "graph partitioning") AND "ant")` | 8 | Mesh partitioning (Korošec et al. 2003), vertex bisection (Feng 2025), Blum's ACO tutorial, a patrolling paper (Doi 2013), the Held hive paper again, and a fusion/fission partitioning metaheuristic (Bichot 2006). **No pheromone-threshold read-out.** |
| A6 | (earlier, exploratory) `("ant colony" AND clustering AND pheromone AND threshold)` restricted follow-ups on individual records | - | Abstracts read for: `document/1527216` (digraph), `document/6890869` (L-NNACO). Both full texts blocked by sign-in. |

**Finding for Category A, and it is not the finding pass 1 recorded.**
IEEE Xplore, queried directly rather than incidentally, returns the mechanism
this project describes as new. It returns it from a 2005 conference paper, and
query A3 returns *nothing else in the database*. Following that paper forward
(Category H below) reached the 2014 journal paper that implements the full
pipeline on a kNN graph.

## Category B - the digraph line, traced forward. OpenAlex.

Forward citation tracing on the two 2005 digraph papers, since LITERATURE.md
asks for citations followed both ways.

| Query | Returned |
|---|---|
| OpenAlex `filter=cites:W2104268471` (cites the ICMLC 2005 digraph paper) | 7 works. Six are unrelated applications. The seventh is **Kang, M.-S. & Choi, Y.-S. (2014), "Ant Colony Hierarchical Cluster Analysis", Journal of Internet Computing and Services 15(5):95-105, DOI 10.7472/jksii.2014.15.5.95, open access.** |
| OpenAlex `filter=cites:W1515003038` (cites the ICNC 2005 A3CD paper) | 14 works. Nanda & Panda's 2014 survey in Swarm and Evolutionary Computation; **Handl & Meyer (2007), "Ant-based and swarm-based clustering", Swarm Intelligence 1(2):95-113** - which corrects pass 1's bibliographic record for that survey; Zhang & Cao's kernel and Rényi-entropy ant clustering papers; the Marinakis GRASP/ACO cluster; "A Graphic Clustering Algorithm Based on MMAS" (Yang, Li, Bo, CEC 2006). |
| OpenAlex `title_and_abstract.search:pheromone AND "connected components"` | **8 works worldwide.** Three of them are the Chen/Tu/Chen trilogy (ICMLC 2005, ICNC 2005 A3CD, LNCS 2006 dynamic database); one is Kang & Choi 2014; two are a 2026 Zenodo duplicate pair unrelated to clustering; the remaining two are a GPU-ACO paper and a cognitive-radio routing paper. **That eight-item set is the entire visible field for this phrasing.** |
| OpenAlex `title_and_abstract.search:pheromone AND threshold AND clustering AND graph` | 9. Kang & Choi 2014 again; "Telecommunication calling circles detecting algorithm based on ant colony optimization", Journal of Yangzhou University 2009 (same institution as Chen/Tu - possibly a Chinese-language sibling of the digraph work, **not retrieved**); the rest are eLife editorial records with no bearing. |
| OpenAlex `title_and_abstract.search:ant AND "similarity graph" AND clustering` | 2, neither relevant (a 2003 ISMIS proceedings volume; a Greek-language thesis). |
| OpenAlex `title_and_abstract.search:"pheromone" AND "k-nearest"` | 30, all feature selection, TSP or classification hybrids. **No ACO clustering that walks a kNN graph.** |
| OpenAlex `title_and_abstract.search:ants AND clustering AND "no objective function"` | 94, none matching - the phrase matches loosely and the results are ordinary objective-driven ACO clustering. |
| OpenAlex `search=ant colony pheromone threshold graph clustering connected components` (relevance search) | 919, dominated by rule-induction and routing ACO. Relevance ranking is citation-weighted and did not surface the digraph line; the field-restricted `title_and_abstract.search` above did. Recorded because it shows why a generic search misses this. |
| OpenAlex `search=pheromone accumulation edges k-nearest neighbor graph clustering ants` | 76, nothing relevant. |
| OpenAlex `search=ant colony clustering without objective function pheromone field` | 3099, nothing relevant - generic swarm-optimisation results. |

## Category C - Otsu 1979, priority 1.

| Query / action | Returned |
|---|---|
| Crossref API `works/10.1109/TSMC.1979.4310076` | Resolves. Title "A Threshold Selection Method from Gray-Level Histograms", author Nobuyuki Otsu, container "IEEE Transactions on Systems, Man, and Cybernetics", vol. 9, issue 1, pp. 62-66, published-print 1979-01, publisher IEEE, ISSN 0018-9472 / 2168-2909, 32,967 citing works. **DOI verified.** |
| `https://doi.org/10.1109/TSMC.1979.4310076` via WebFetch | HTTP 302 to `ieeexplore.ieee.org/document/4310076`. **DOI resolution verified.** |
| IEEE Xplore record `document/4310076` in the maintainer's browser | Same fields displayed, same DOI echoed. **Publisher record verified.** |
| `ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4310076` | Served `04310076.pdf` in the browser's PDF viewer. (Note the contrast with the 2005 conference paper, which bounced back to its record page - IEEE evidently serves this legacy item without a subscription.) |
| WebSearch `Otsu 1979 "A Threshold Selection Method from Gray-Level Histograms" pdf` | Surfaced a Tel Aviv lecture-notes PDF that is *not* the paper (21 pages of slides) - discarded. |
| Direct probe of five candidate mirrors | Three returned byte-identical 5-page PDFs (3,152,839 bytes): `web-ext.u-aizu.ac.jp/course/bmclass/documents/otsu1979.pdf`, `cw.fel.cvut.cz/wiki/_media/courses/a6m33bio/otsu.pdf`, `engineering.purdue.edu/kak/computervision/ECE661.08/OTSU_paper.pdf`. Two 404'd. **Full text obtained and read.** |

**Finding.** The DOI is confirmed. The paper does **not** say Otsu's method
degrades on non-bimodal histograms - that claim, which pass 1 took from
secondary web sources, describes the valley-seeking methods Otsu is replacing.
His stated caveat is about multithresholding with many classes. He also
defines an affine-invariant separability measure η* ∈ [0,1] that falls out of
the same computation, and explicitly extends the method beyond images to "any
histogram of some characteristic (or feature) discriminative for classifying
the objects". Details in SOURCES_PASS2.md #5.

## Category D - the two "nearest competitors" from pass 1.

| Query / action | Returned |
|---|---|
| WebSearch `Hu 2015 "multiple pheromone table" ant colony optimization clustering Wiley` | Identified as Hu, Tsai, Chiang & Yang, "A Multiple Pheromone Table Based Ant Colony Optimization for Clustering", Mathematical Problems in Engineering 2015, art. 158632, DOI 10.1155/2015/158632. |
| Fetch attempts on Hu 2015 full text | `onlinelibrary.wiley.com/doi/10.1155/2015/158632` → 402. `downloads.hindawi.com/.../158632.pdf` → 403 (curl and WebFetch). `www.hindawi.com/journals/mpe/2015/158632/` → 402. Browser extension refuses the domain. **Abstract only**, obtained from the publisher-registered abstract via OpenAlex. |
| WebSearch `L-NNACO ant colony optimization clustering "nearest neighbors"` | **Pass 1's attribution was wrong.** L-NNACO is Tseng, Chiang & Yang, ICMLC 2013, DOI 10.1109/ICMLC.2013.6890869 - not Gao 2016. |
| IEEE Xplore `document/6890869` | Abstract read on the publisher page. Full text behind sign-in. |
| WebFetch `pmc.ncbi.nlm.nih.gov/articles/PMC4709600/` (Gao 2016) | Confirms Gao 2016 is a different algorithm ("data reactor" model, Lumer-Faieta lineage) with **no pheromone update mechanism** and no L-nearest-neighbour restriction. |
| WebFetch `informatica.si/.../download/2672/1384` (Lucky & Girsang 2020, NNACOC) | **Open access full text retrieved.** Gives the ACOC family's objective function verbatim - Δτ = 1/F, F = SSE of Euclidean distances (or sum of cosine distances for text) - plus the elitist deposit rule ("only n-best ants ... usually 20%"), the object×cluster pheromone table, and the requirement that k be supplied. |

**Finding.** Neither pass-1 "nearest competitor" is close. Both belong to the
Shelokar ACOC lineage: each ant constructs a complete cluster-assignment
string, the assignment is scored by an explicit objective, and only the best
20% of ants deposit. The kNN element in L-NNACO is a computation shortcut
inside solution construction, not a graph the ants walk. Neither thresholds a
pheromone field. **The threat to the novelty claim is Kang & Choi 2014, not
these.**

## Category E - Deneubourg / Lumer-Faieta.

| Query / action | Returned |
|---|---|
| Reference list of Kang & Choi 2014 (retrieved in full) | Ref [3]: Deneubourg, J.-L., Goss, S., Franks, N., Sendova-Franks, A., Detrain, C., and Chretien, L., "The dynamics of collective sorting: Robot-like ants and ant-like robots", Proc. First Int. Conf. on Simulation of Adaptive Behavior: From Animals to Animats 1, 1991, pp. 356-365, MIT Press. Ref [4]: Lumer, E. and Faieta, B., "Diversity and adaptation in populations of clustering ants", Proc. Third Int. Conf. SAB, pp. 501-508, MIT Press. **Both citations now traceable to a document read this session; neither primary text obtained.** |
| `cse.wustl.edu/~yixin.chen/public/a4c.pdf` | Open PDF of Chen, Xu & Chen (2004), "An Adaptive Ant Colony Clustering Algorithm", ICMLC 2004 pp. 1387-1392. Retrieved in full. A grid/cellular-automaton model in the Deneubourg-LF lineage, no pheromone. Useful as a freely readable primary description of that branch. |
| Attempt to list `cse.wustl.edu/~yixin.chen/public/` for the digraph papers | HTTP 403, no directory listing. |
| `eprints.bournemouth.ac.uk/20910/1/Boryczka2009.pdf` (Boryczka, "Finding groups in data: Cluster analysis with ants", Applied Soft Computing 2009 - the paper pass 1 attributed to Handl & Meyer) | Every route failed: `curl` returned exit code 000 twice (connection not established from this sandbox), `WebFetch` returned "Socket is closed" twice, the browser extension refuses the domain. **Not retrieved.** Recorded because the file is open access and one retrieval from the maintainer's own machine would close it. |
| Probes for a free Handl & Meyer 2007 survey PDF | Three guessed URLs at Manchester and CMU: all 404. Not open access per OpenAlex. **Not retrieved.** |

## Category F - Chinese and Korean language leads.

| Query | Returned |
|---|---|
| WebSearch `"ant colony" clustering digraph 陈崚 涂立 有向图 蚁群 聚类 强连通分量` | Nothing. General ACO blog posts and a TSP paper. CNKI was not reachable. |
| WebSearch `Chen Tu "ant-cluster" pheromone digraph "strong connected components" clustering algorithm pdf` | Only the two paywalled 2005 records again, plus the Chircop & Buckingham multiple-pheromone paper. |
| (incidental, via OpenAlex) | "Telecommunication calling circles detecting algorithm based on ant colony optimization", Journal of Yangzhou University, 2009 - same institution as Chen/Tu, no DOI, **not retrieved**. Possible Chinese-language sibling of the digraph work. |
| Korean: Kang & Choi 2014 | Retrieved in full from `koreascience.kr` (open access). Body is Korean; abstract, equations, both algorithm listings, results table and reference list all readable. This is the pass's principal source. |

## Category G - Russian-language sources.

**Nothing was run.** CyberLeninka, eLibrary and Google Scholar were all
refused by the browser extension's navigation policy before any page load, so
this pass got *less* far than pass 1, which at least reached CyberLeninka's
CAPTCHA. The three CyberLeninka titles pass 1 recorded remain unretrieved.
No CAPTCHA was attempted. This category is now the second-largest gap in the
record after ACM DL, and it needs the maintainer to open the pages.

## Stop condition

Stopped when the field-restricted OpenAlex searches, the IEEE Xplore searches
and the forward citation traces all converged on the same eight-work set
around `pheromone + connected components`, and when three consecutive
formulations returned nothing new. Saturation, not a count.

The one thing that would change the picture is the full text of the two 2005
Chen/Tu digraph papers, which would settle whether their pheromone update
carries a quality term. That is a retrieval, not another query.
