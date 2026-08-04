# Sources

Per-source record, per LITERATURE.md format. `Answers` states what the source
says; `Bearing` states what it means for this project - never merged.

Three fixed questions applied to every ACO-family source (per the task):

- Q1. What deposits pheromone - all agents or a selected subset, by what
  criterion?
- Q2. What is the result - a found solution, or a state of the environment?
- Q3. What parameters, and why - for the transferred/not-transferred/
  not-applicable table.

---

## Corrections carried by pass 2

Read before any entry below. Pass 2 (2026-07-29) retrieved primary texts that
contradict three things pass 1 recorded. The wrong statements are left in
place rather than edited away, so that a reader who saw them elsewhere can
find out they were withdrawn.

1. **L-NNACO is not "Gao 2016".** It is Tseng, S.-P.; Chiang, M.-C.; Yang,
   C.-S., ICMLC 2013, DOI `10.1109/ICMLC.2013.6890869`. Gao 2016 (Comput.
   Intell. Neurosci. 2016:4835932) is an unrelated grid-based method with no
   pheromone update at all. Affects the Category A table in `SEARCH_LOG.md`.
2. **Entry 7 below conflates two different papers by different authors.** The
   survey is Handl, J. & Meyer, B., *Ant-based and swarm-based clustering*,
   Swarm Intelligence 1(2):95-113, 2007, DOI `10.1007/s11721-007-0008-7`. The
   title *Finding groups in data: Cluster analysis with ants* belongs to
   Boryczka, U., Applied Soft Computing 9(1), 2009, DOI
   `10.1016/j.asoc.2008.03.002` - which additionally has a published
   corrigendum, DOI `10.1016/j.asoc.2013.07.012`. Both are real; they are not
   the same work.
3. **Hu et al. 2015 does not threshold pheromone to split patterns.** The
   publisher's abstract describes a second pheromone table for search
   diversification. Nothing in any retrieved document supports the threshold
   reading pass 1 gave it. Withdrawn.

---

## 1. van Dongen, S. (2000). *Graph Clustering by Flow Simulation*. PhD thesis, Utrecht University / CWI Amsterdam.

- **Venue**: PhD dissertation (unpublished thesis, CWI technical report basis).
- **Identifier**: mirrored PDF, https://datajobs.com/data-science-repo/Markov-Clustering-%5Bvan-Dongen%5D.pdf (no DOI found for the thesis itself; the CWI technical reports it is based on are [45],[46] in its own bibliography, not separately tracked down here).
- **Retrieved**: full text (PDF, 169 pages).
- **Depth**: read (Introduction, Ch. 1 in full; table of contents and chapter summaries for Ch. 2-12 read; the algebraic proofs in Ch. 6-8 not read in depth).
- **Answers**:
  - Not an ACO/pheromone method at all - no agents. The "flow" is the literal Markov transition matrix of the graph, iterated by two matrix operators: expansion (matrix squaring - spreads flow along paths) and inflation (elementwise power + column renormalization - sharpens flow toward already-strong entries).
  - Result is the **limit matrix itself**: the process is proven (under the stated parametrization) to converge to an idempotent matrix whose nonzero-block structure directly **is** the clustering. No external threshold or connected-components step is described as part of the core algorithm.
  - No objective function anywhere. The thesis explicitly frames cluster analysis as a domain where "optimization approaches" are effectively ruled out (Sec. 1.1), and lists as a benefit of MCL that clusters are read from matrix structure "without high-level procedural instructions for assembling, joining, or splitting groups."
  - Parameters: the inflation exponent (granularity control - higher = finer clusters) and a pruning threshold used only for scalability (dropping near-zero matrix entries so the algorithm stays sparse), not for defining cluster boundaries.
- **Bearing**: this is the single closest structural relative to this project's algorithm found in the whole search - both discard an objective function and read the result directly from a converged field state rather than from a "best" trajectory. But the mechanism is fundamentally different in a way worth stating precisely: MCL operates deterministically on the *exact* transition matrix of the *full* graph and needs no threshold because idempotency does the separating work for it; this project samples a *sparse kNN* graph *stochastically* with actual ant walks, keeps pheromone as a quantity separate from the transition probabilities, and therefore *needs* an explicit threshold + connected-components step because there is no convergence-to-block-diagonal guarantee. This comparison belongs in the dissertation's related-work section as the strongest and most honest "closest relative, and here is exactly how it differs" argument found.

---

## 2. Stutzle, T. & Hoos, H.H. (2000). *MAX-MIN Ant System*. Future Generation Computer Systems 16(8), 889-914. (Preprint version retrieved.)

- **Venue**: journal (Future Generation Computer Systems), preprint PDF retrieved.
- **Identifier**: no DOI captured; preprint mirror https://lia.disi.unibo.it/Courses/SistInt/articoli/max-min-ant.pdf.
- **Retrieved**: full text (preprint PDF).
- **Depth**: read (Abstract, Introduction, Sec. 2.1-2.2 read in full; the TSP/QAP experimental sections not read).
- **Answers**:
  - Q1: only the **iteration-best** ant or the **best-so-far** ant deposits pheromone at each update (implementations commonly alternate the two) - a small, explicitly selected subset, never all ants.
  - Q2: the result is the best-so-far *solution* (a concrete tour/assignment), not the pheromone field - the field is a search-control mechanism, not the deliverable.
  - Q3 / mechanisms and why: (a) best-only update, to concentrate search near known-good solutions; (b) explicit trail limits [tau_min, tau_max], to guarantee no edge's selection probability ever reaches exactly zero (avoids premature convergence); (c) trails initialized at tau_max, to favor exploration early; (d) full reinitialization on stagnation (no improvement for N iterations).
- **Bearing**: every one of these four mechanisms is meaningless without a way to rank ant solutions - "best-so-far" presupposes a solution quality ordering. This is the primary-source evidence for the project's own claim ("no objective function, and this is the main thing... 'best ant' is not defined") - MMAS is the textbook counterexample showing what canonical ACO needs and does not have here. For the parameter-transfer table: tau_min/tau_max limits are already present in this project (`tau_min`, `tau_max` constructor args per AGENTS.md); best-only update and stagnation reinitialization are NOT applicable, because there is no per-ant solution to rank.

---

## 3. Sadi, S., Etaner-Uyar, S., Gunduz-Oguducu, S. (2009). *Community Detection Using Ant Colony Optimization Techniques*. Proceedings, MENDEL 2009 (15th Int. Conf. on Soft Computing).

- **Venue**: conference proceedings (MENDEL), full text hosted at the authors' institution.
- **Identifier**: https://web.itu.edu.tr/etaner/mendel09_2.pdf (no DOI captured).
- **Retrieved**: full text (PDF).
- **Depth**: read in full.
- **Answers**:
  - Q1: MMAS variant used - only the best-so-far ant deposits pheromone, weighted by a **points** score (sum of squares of clique sizes found). ACS variant also tested (local + global update, both restricted to best-so-far edges for the global step).
  - Q2: result is a set of maximal cliques found by the ants, which are then collapsed into meta-nodes and handed to a *separate*, conventional modularity-maximization algorithm (Clauset-Newman-Moore greedy method) - the ACO stage is a graph-reduction preprocessor, not the clustering step itself.
  - Q3: gives the exact transition-probability equation (pheromone^alpha * heuristic^beta, normalized over neighbors) and the exact AS/MMAS/ACS pheromone-update equations side by side, plus the parameter table used (alpha=1, beta=2, rho=0.5, m=25 ants, q0 in {0, 0.4, 0.8}).
- **Bearing**: useful as a single, freely-available primary text that lays out AS vs. MMAS vs. ACS mechanics in one place with worked equations - used as the base for the "canon of parameters" cross-check in Category C, alongside the MMAS paper directly. Also directly on-topic for Category A: confirms that even an ACO application that "finds cliques via pheromone" still routes the actual clustering decision through a downstream objective-function algorithm (modularity), reinforcing the negative finding that no source combines pheromone-threshold-only clustering with an explicit kNN-type graph.

---

## 4. Elazar, G. & Bruckstein, A.M. (2016 arXiv preprint; originally ANTS 2016). *AntPaP: Patrolling and Fair Partitioning of Graphs by A(ge)nts Leaving Pheromone Traces*.

- **Venue**: conference paper (ANTS - International Conference on Swarm Intelligence), arXiv preprint retrieved.
- **Identifier**: arXiv:1608.04511.
- **Retrieved**: full text (arXiv PDF/HTML).
- **Depth**: read in full.
- **Answers**:
  - Q1: **every** agent deposits pheromone identically on its own patrol route - no selection, no quality comparison between agents at all.
  - Q2: result is a **state of the environment** - a balanced partition of the graph into disjoint regions, one per agent, that emerges as a byproduct of each agent's local patrolling/conquest rule. There is no separate "solution" object; the partition just *is* the set of regions marked by each agent's pheromone at the point the system stabilizes.
  - Q3: parameters are a conquest probability `rho_c` and a vertex-loss probability `rho_l` (a simulated-annealing-like escape from local traps), plus pheromone "age"/decay used only to encode elapsed time (idle-time), not to weight a transition-probability formula the way alpha/beta/rho do in classical ACO. Explicitly contrasted by the authors against classical Dorigo-Maniezzo-Colorni ACO/TSP ants (which they describe accurately, including the alpha/beta/pheromone-bias mechanics) as a fundamentally different, objective-function-free mechanism.
- **Bearing**: the single closest-in-spirit "no objective function, pheromone is the answer" example found in this entire search. Still structurally distant from this project: no kNN/similarity graph construction stage (it operates on a graph given as-is, framed as a physical patrol area); the read-out is agent territorial ownership, not a scalar pheromone value compared to a threshold; and it solves *fair partitioning into k regions* (k = number of agents, chosen in advance), not *cluster discovery* (unknown number of dense regions). Worth citing directly as the nearest analogue under section D of the task ("ACO without a target function") precisely because it is not a clustering method and does not compete with this project's contribution - it demonstrates the pattern exists elsewhere, without preempting the claim.

---

## 5. Deneubourg, J.L. et al. (1991). *The Dynamics of Collective Sorting: Robot-like Ant and Ant-like Robot*. In: Proc. 1st Conf. on Simulation of Adaptive Behavior (SAB90/91), MIT Press.

- **Venue**: conference proceedings, MIT Press.
- **Identifier**: no DOI or stable URL found; identified only via secondary description (ResearchGate listing page).
- **Retrieved**: NOT retrieved - abstract/description only, via tertiary summaries, not the source itself.
- **Depth**: abstract only (and, more precisely, second-hand: no abstract of the original was read either, only later papers' descriptions of it).
- **Answers** (as reported by secondary sources, flagged accordingly): ants move randomly on a lattice, picking up or dropping physical objects (originally: ant corpses) based on the local density of similar objects around their current position; small clusters of objects self-reinforce by attracting more deposits. No pheromone is involved in the original mechanism at all - the "signal" other ants respond to is the physical arrangement of objects itself, not a separate chemical field.
- **Bearing**: this is the foundational model the project must not be confused with (per the task's explicit warning about "ant-based clustering" in the Deneubourg/Lumer-Faieta sense). Key distinguishing fact worth stating precisely in the dissertation: the original Deneubourg mechanism does not even use pheromone - agents relocate the data itself. **Flagged**: this claim rests entirely on secondary description; the primary 1991 conference paper was not accessible in this search and should be tracked down (likely only in a physical MIT Press proceedings volume or via institutional access) before citing it as anything stronger than "reported by X."

---

## 6. Lumer, E.D. & Faieta, B. (1994). *Diversity and Adaptation in Populations of Clustering Ants*. In: Proc. 3rd Int. Conf. on Simulation of Adaptive Behavior (SAB94), vol. 3, MIT Press, pp. 501-508.

- **Venue**: conference proceedings, MIT Press.
- **Identifier**: ACM DL listing https://dl.acm.org/doi/10.5555/645301.648386 (no working DOI resolved beyond the ACM record ID).
- **Retrieved**: NOT retrieved - full text paywalled/not found freely; identified via ACM DL and SCIRP reference-listing pages plus later papers' descriptions.
- **Depth**: abstract only, and again second-hand (via secondary sources describing its content, not the original abstract).
- **Answers** (as reported by secondary sources): generalizes Deneubourg's model from physical corpse-sorting to numerical data analysis - data objects are placed on a 2D grid, ants pick up and carry an object based on a similarity function computed over the objects in its local neighborhood on the grid, and drop it where local similarity is high. The final spatial arrangement of objects on the grid encodes the clustering. One later analysis paper (cited only secondhand here, not itself retrieved) reportedly shows this scheme is formally related to Kohonen's Self-Organizing (Batch) Map.
- **Bearing**: the direct ancestor of the whole "ant-based clustering" branch that must be disambiguated from this project. Same core distinction as Deneubourg: agents carry and relocate *data* on a spatial substrate; there is no fixed underlying similarity graph and no pheromone trail on graph edges at all - the grid position is the memory. **Flagged**: primary text not retrieved in this search; a VAK-level differentiation paragraph should not rest solely on secondary description of this specific paper without at least the original abstract, which was not accessible here (SAB94 proceedings are not open-access).

---

## 7. [CORRECTED - see Corrections, item 2] Handl, J. & Meyer, B. *Finding groups in data: Cluster analysis with ants.* Applied Soft Computing (ScienceDirect), and earlier survey chapters extending Lumer-Faieta.

- **Venue**: journal (Applied Soft Computing / Swarm Intelligence, exact venue/year not disambiguated in this pass - the search surfaced the ScienceDirect abstract page without a clear single citation resolving to one canonical version).
- **Identifier**: https://www.sciencedirect.com/science/article/abs/pii/S1568494608000331 (abstract page only).
- **Retrieved**: NOT retrieved - abstract page reached, full text paywalled.
- **Depth**: abstract only (and the abstract page itself did not display readable abstract text in the fetch - title and metadata only; treat as title-level identification, weaker than typical "abstract only").
- **Answers**: per secondary/citing sources - Handl & Meyer proposed modifications to both Deneubourg's model and the Lumer-Faieta algorithm, and applied the resulting method to web-document classification; a recognized survey/extension point for the whole ant-based-clustering branch.
- **Bearing**: the standard citation point for "the ant-based clustering branch, surveyed" - useful as the single reference to cite when telling a reader "this is the branch we are not part of, see Handl & Meyer for its own literature." **Flagged, same as #5/#6**: not retrieved beyond a title/metadata page; needs the maintainer's own journal access to confirm venue/year precisely and read the actual differentiation the authors themselves draw against non-agent-carrying approaches (which would strengthen this project's own differentiation section if it exists).

---

## 8. kNN graph construction and thresholding sources

### 8a. (arXiv 2108.05525) "Clustering with UMAP: Why and How Connectivity Matters"

- **Venue**: preprint (arXiv), UMAP-related.
- **Identifier**: arXiv:2108.05525.
- **Retrieved**: search-snippet level only (not fetched in full in this pass).
- **Depth**: abstract only.
- **Answers**: discusses mutual-kNN graphs as a way to reduce distance concentration/hub effects in high dimension, at the cost of disconnected components; discusses path-based repair strategies to restore connectivity.
- **Bearing**: directly relevant to this project's `GraphBuilder` design (kNN with exact/pynndescent backends) and to any future decision about mutual-vs-directed kNN; flagged as a candidate for a deeper read if the graph-construction stage of the calibration work needs literature backing, but not fetched in full here - time/scope boundary of this pass.

### 8b. Otsu, N. (1979). *A Threshold Selection Method from Gray-Level Histograms*. IEEE Trans. Systems, Man, and Cybernetics.

- **Venue**: journal (IEEE SMC), classic paper.
- **Identifier**: not fetched in this pass; commonly cited as DOI 10.1109/TSMC.1979.4310076 - **not verified against a retrieved document in this search**, flagged, should be confirmed before citing since LITERATURE.md's rule is "never cite from memory."
- **Retrieved**: NOT retrieved in this pass.
- **Depth**: not applicable (not retrieved) - what is stated in `SEARCH_LOG.md` about Otsu's method comes from secondary/tertiary web descriptions (Wikipedia, tutorial pages), not the original 1979 paper.
- **Answers**: per secondary sources - maximizes between-class variance (equivalently minimizes intra-class variance) over a histogram, assuming a roughly bimodal distribution; degrades when the distribution is not cleanly bimodal or intra-class variance exceeds inter-class variance.
- **Bearing**: this project already uses Otsu as its fixed extraction method (`find_threshold`, per AGENTS.md/TASK.md). No example of a non-image application of Otsu to a pheromone-like scalar distribution was found in this search - worth stating as a further (mild) originality point about the threshold stage, but weakly supported since the primary Otsu paper itself was not retrieved here.

---

## Not-retrieved summary (per LITERATURE.md, recorded plainly, not filled in)

- Dorigo, M. & Stutzle, T. (2004). *Ant Colony Optimization*. MIT Press. (book; not found as an open PDF; only cited secondhand by source #3 and others).
- Dorigo, M. & Gambardella, L.M. (1997). *Ant Colony System: A Cooperative Learning Approach to the TSP*. IEEE Trans. Evolutionary Computation. (secondary description only, not fetched in full).
- Bullnheimer, B., Hartl, R.F., Strauss, C. (1999). *A New Rank-Based Version of the Ant System*. Central European J. Operations Research. (secondary description only).
- Deneubourg et al. 1991, Lumer & Faieta 1994, Handl & Meyer - see #5/#6/#7 above, all flagged not-retrieved.
- Three CyberLeninka articles (Category G) - blocked by CAPTCHA, titles/URLs recorded in SEARCH_LOG.md only.
- Otsu 1979 original paper - not retrieved (see 8b).


---
---

# Pass 2 - 2026-07-29

Appended, not merged into the numbering above: pass-1 entries keep their
numbers, pass-2 entries are prefixed `P2-`. Where a pass-2 entry upgrades a
pass-1 one, it says so.


## READ THIS FIRST

**Source #1 below (Kang & Choi 2014) is prior work that implements the
mechanism this project describes as new.** It is not adjacent, not "in the
same spirit" - it is a kNN directed graph, ants walking it and depositing on
arcs, a pheromone threshold, connected components as clusters, k-NN
reassignment of the removed points, and a threshold sweep that produces a
hierarchy. There is no objective function anywhere in it. It was published in
a peer-reviewed journal in 2014 and the full text was read in this session.

Everything else in this file is secondary to that.

---

## P2-1. Kang, Mun-Su & Choi, Young-Sik (2014). *Ant Colony Hierarchical Cluster Analysis* (개미 군락 시스템을 이용한 계층적 클러스터 분석).

- **Venue**: journal - Journal of Internet Computing and Services (JICS,
  한국인터넷정보학회논문지), Korean Society for Internet Information, vol. 15,
  no. 5, October 2014, pp. 95-105. ISSN 1598-0170 (print) / 2287-1136 (online).
- **Identifier**: DOI 10.7472/jksii.2014.15.5.95. Open access PDF retrieved
  from https://koreascience.kr/article/JAKO201433752159566.pdf (also listed as
  the OA location in OpenAlex).
- **Retrieved**: full text (PDF, 11 pages). Body is Korean; abstract, all
  equations, both algorithm listings, the results table and the reference list
  are readable directly.
- **Depth**: read. Sections 1-4 read in full via text extraction (Korean);
  equations (1)-(9), Algorithm 1 (`Ant Colony Clustering`), Algorithm 2
  (`Ant Colony Hierarchical Clustering`), the parameter discussion in 4.1, the
  evaluation functions in 4.2 and the reference list read directly. The
  discussion of individual figures was skimmed.
- **Answers**:
  - **Graph.** "a weighted directed graph of k-nearest neighborhood obtained
    from a given dataset" (English abstract, verbatim). Formally: dataset
    X = {x_i} ⊆ R^d, each x_i maps to a node v_i, and a directed edge e_ij
    exists iff x_j is one of the k nearest neighbours of x_i. Out-degree is
    the same for every node, in-degree varies - i.e. a directed, non-mutual
    kNN graph. Edge weight is a normalised distance
    ξ_ij = ((d(x_i,x_j) - d_min) / (d_max - d_min)) * Q + 1, with Q = 100, so
    distances are rescaled to [1, 101].
  - **Density heuristic.** A per-node density ρ_i = exp(ω * μ_k / d(x_i, x_i^k))
    where x_i^k is the k-th nearest neighbour and μ_k the mean over the k
    nearest neighbours; ω = 0.5. Cited to a kNN-graph density definition
    (their ref [15], Lee et al., IEEE TNN 2007).
  - **Node pheromone.** π_j = Σ_{i ∈ Ω_j} τ_ij (eq. 3) - the sum of arc
    pheromone on all arcs entering v_j, where Ω_j is the set of source nodes.
    Described as "a relative density measure in a local region": a node whose
    neighbourhood is denser than its own neighbours' pulls a larger π.
  - **Transition rule.** p_ij = π_j^β / Σ_{k ∈ N_i} π_k^β (eq. 4), or with the
    density heuristic included, p_ij = ρ_j^α π_j^β / Σ_{k ∈ N_i} ρ_k^α π_k^β
    (eq. 5), zero for non-neighbours. α weights the heuristic, β the
    pheromone. Cited to Dorigo & Stützle 2004 (their ref [16]).
  - **Q1.** Every ant that traverses an arc contributes. The deposit is
    Δτ_ij = log2(o_ij) * (1 / ξ_ij) (eq. 7), where **o_ij is the number of ants
    that moved along e_ij**; the log is taken explicitly to damp the influence
    of any one heavily-used arc. Evaporation: τ_ij ← (1-θ) τ_ij + Δτ_ij
    (eq. 6), θ = 0.95 in their runs. **There is no fitness, cost, quality or
    objective term anywhere in the update, and no ranking of ants.** Ants
    instead carry a *lifetime*: a fixed number are generated at each node,
    lifetime decrements per move, an ant at lifetime 0 is removed and ants are
    regenerated at every node - stated to be there so that ants do not get
    permanently trapped in high-density regions.
  - **Q2.** The result is a state of the environment. `compute_np` returns π,
    the node-pheromone vector, and nothing else. A second, entirely separate
    procedure `remove_labeling(G, π, threshold)` deletes every node with
    π_j < threshold (deleting its in- and out-arcs with it) and returns the
    strongly connected components of the remainder as the clusters. No ant's
    trajectory appears in the output.
  - **Noise handling.** "제거된 노드는 k-NN 규칙[18]을 이용하여 얻어진 클러스터 중
    하나로 할당한다" - the removed nodes are assigned to one of the obtained
    clusters using the k-NN rule (their ref [18] = Duda, Hart & Stork). In
    section 4.2 they add that this reassignment "is not always necessary for
    all applications."
  - **Hierarchy.** Algorithm 2 sorts π once, then sweeps the threshold by
    percentile - `h_level = 99`, `step = 1%` - calling `remove_labeling` at
    each level and building a tree, with the nesting guarantee stated as
    eq. (9): D_j ⊆ C_i for all D_j whenever t_C ≤ t_D. Each cluster in the
    tree carries a start threshold (when it appeared) and an end threshold
    (when it vanished). The visualisation is percentile on x, cluster size on
    y, colour persisting while a cluster does not split.
  - **Q3 / parameters.** k (neighbours), ant lifetime, number of iterations,
    node-removal percentage, α, β, plus ω = 0.5 and Q = 100. Their own
    sensitivity statement, section 4.1: ant lifetime and iteration count "do
    not greatly affect node pheromone" (lifetime 10, iterations 100 used);
    **k does** - too small and π does not reflect the local density
    distribution, too large and it stops representing a local region. They set
    k = sqrt(n) following their ref [9] (the Chen/Tu digraph paper, #2 below).
    α and β are tested only at three corners: (1,0), (1,1), (0,1).
  - **Evaluation.** F-measure, Dunn index, intra-cluster variance, on
    synthetic data and UCI sets, against HDS (Hierarchical Density Shaving,
    Gupta/Liu/Ghosh) and k-means. Reported F-measure e.g. Wisconsin: ACHC
    0.9673 / 0.9620 / 0.9617 for the three (α,β) cases against HDS 0.8766 and
    k-means 0.9192; Wine: 0.8756 / 0.9111 / 0.9114 against HDS 0.7446 and
    k-means 0.9495. The three (α,β) settings differ by less than the gap to
    either baseline on every dataset in the table.
- **Bearing**: this covers what AGENTS.md and the task brief describe as the
  project's four distinguishing properties. All four are present here:
  no objective function; the pheromone field is the answer rather than a
  search aid; a sparse kNN graph rather than a complete problem graph; and a
  staged pipeline in which the threshold is an argument to a separate
  procedure taking the field as input, which is exactly the "public
  intermediate state" contract. It further anticipates two roadmap items:
  phase 2's `scan_thresholds` (their percentile sweep) and the multilevel
  scheme in RESEARCH_NOTES.md (their cluster tree, obtained by sweeping the
  threshold rather than by coarsening the graph). Their finding that lifetime
  and iteration count barely move the field while k dominates it is the same
  shape as this project's "five of six parameters were flat" and "the graph
  bounds everything downstream".
  The differences that remain are real but narrow: (a) they threshold **nodes**
  by summed in-arc pheromone, this project thresholds **edges** by edge
  pheromone - node pheromone is a derived local density, edge pheromone is the
  primitive quantity; (b) they take strongly connected components of a
  digraph, this project takes connected components of a (optionally
  symmetrised) graph; (c) their deposit is a batched log of the traversal
  count with no trail limits, this project deposits per ant with MMAS
  [tau_min, tau_max] clamps and two evaporation schedules; (d) they choose the
  cut by percentile sweep, this project chooses it by Otsu; (e) they never
  measure what the kNN graph alone gives before the ants run, which is the
  `baseline_ARI` column this project added on 2026-07-28.
  This entry needs a decision from the maintainer, not a citation slot. See
  QUESTIONS_PASS2.md #1.

---

## P2-2. Chen, Ling; Tu, Li; Chen, Hong-Jian (2005). *Data clustering by ant colony on a digraph*.

- **Venue**: conference - Proceedings of the 2005 International Conference on
  Machine Learning and Cybernetics (ICMLC 2005), Guangzhou, China, 18-21
  August 2005, vol. 3, pp. 1686-1692. Publisher IEEE. Print ISBN
  0-7803-9091-1.
- **Identifier**: DOI 10.1109/ICMLC.2005.1527216. IEEE Xplore document
  4310076-analogue: https://ieeexplore.ieee.org/document/1527216. Page range
  taken from the reference list of source #1 (their ref [9]), which was
  retrieved in full this session.
- **Retrieved**: **abstract only** - the publisher's own abstract, read
  directly on the IEEE Xplore record page in the maintainer's browser. Full
  text is behind "Sign in to Continue Reading"; the maintainer's Chrome has no
  IEEE institutional session (the page offers "Institutional Sign In" /
  "Personal Sign In" and `stamp.jsp` redirects back to the record). Not
  open-access per Unpaywall; no OA copy found.
- **Depth**: abstract only. Everything below is what the abstract states, not
  what the paper shows.
- **Answers**:
  - Verbatim from the abstract: "we assign acceptance rates on the directed
    edges of a pheromone digraph in ant-cluster system. The pheromone on the
    edges of the digraph is adaptively updated by the ants passing it. Some
    edges with less pheromone are progressively removed under a list of
    certain thresholds in the process. Strong connected components of the
    final digraph are extracted as clusters."
  - Compared against k-means and "ACO clustering algorithm LF" (Lumer-Faieta)
    on real datasets and clustering benchmarks; claimed faster, better quality
    and easier to implement.
  - Q1: "updated by the ants passing it" - no selection criterion is
    mentioned, but the abstract does not settle whether a quality term
    multiplies the deposit.
  - Q2: the abstract implies the environment - the clusters are read off the
    final digraph, not off any ant's trajectory.
  - Q3: not stated in the abstract beyond "a list of certain thresholds".
- **Bearing**: this is the earlier statement of the same idea as #1, on a
  general pheromone digraph rather than an explicit kNN graph, thresholding
  **edges** (which is what this project does) rather than nodes. It is the
  paper source #1 cites for its choice of k = sqrt(n). Whether it carries an
  objective function cannot be settled from the abstract and needs the full
  text; that is the single most valuable retrieval left in this search.
  **Flagged for the maintainer's institutional access.**

---

## P2-3. Chen, Ling; Tu, Li; Chen, Hongjian (2005). *A Novel Ant Clustering Algorithm with Digraph*.

- **Venue**: conference - Advances in Natural Computation (ICNC 2005),
  Lecture Notes in Computer Science, Springer Berlin Heidelberg, pp. 1218-1228.
- **Identifier**: DOI 10.1007/11539117_163.
- **Retrieved**: **abstract only** - the publisher's abstract, retrieved from
  the SpringerLink chapter page this session. Metadata cross-checked against
  the CrossRef registry (authors, container title, page range, year all
  agree). Not open access per Unpaywall.
- **Depth**: abstract only.
- **Answers**: verbatim - "in A3CD we assign acceptance weights on the
  directed edges of a pheromone digraph. The weights of the digraph is
  adaptively updated by the pheromone left by ants in the seeking process.
  Finally, strong connected components are extracted as clusters under a
  certain threshold." Compared against k-means and LF.
- **Bearing**: the companion paper to #2, same mechanism, same year, same
  authors, different venue. Its value is that it states the read-out in one
  sentence - threshold, then strongly connected components - which is the
  project's `CoreClusterer` in outline. Same open question about an objective
  function; same need for institutional access.

---

## P2-4. Chen, Ling; Tu, Li; Chen, Yixin (2006). *An Ant Clustering Method for a Dynamic Database*.

- **Venue**: book chapter, Lecture Notes in Computer Science, Springer.
- **Identifier**: DOI 10.1007/11739685_18.
- **Retrieved**: **metadata only** (CrossRef / Semantic Scholar / OpenAlex
  records). Abstract not obtained; not open access per Unpaywall.
- **Depth**: not retrieved beyond bibliographic fields.
- **Answers**: none recorded - nothing was read.
- **Bearing**: recorded because it is the third member of the digraph line and
  appears in the same OpenAlex `pheromone AND "connected components"` result
  set (see SEARCH_LOG_PASS2.md). Listed so it is not rediscovered as new.

---

## P2-5. Otsu, Nobuyuki (1979). *A Threshold Selection Method from Gray-Level Histograms*.

**Upgrade of pass-1 entry 8b, which was recorded as NOT retrieved with an
unverified DOI. Both are now fixed: the DOI is verified and the full text was
read.**

- **Venue**: journal - IEEE Transactions on Systems, Man, and Cybernetics,
  vol. SMC-9, no. 1, January 1979, pp. 62-66. Published as a Correspondence
  item. ISSN 0018-9472 / 2168-2909.
- **Identifier**: **DOI 10.1109/TSMC.1979.4310076 - VERIFIED**, three ways:
  (a) the CrossRef registry record for that DOI returns exactly this title,
  author "Nobuyuki Otsu", container "IEEE Transactions on Systems, Man, and
  Cybernetics", volume 9, issue 1, pages 62-66, published-print 1979-01,
  publisher IEEE; (b) `https://doi.org/10.1109/TSMC.1979.4310076` resolves
  (302) to `ieeexplore.ieee.org/document/4310076`, whose record page shows the
  same fields and echoes the same DOI; (c) the retrieved PDF's own running
  heads read "IEEE TRANSACTIONS ON SYSTEMS, MAN, AND CYBERNETICS, VOL. SMC-9,
  NO. 1, JANUARY 1979" with page numbers 62-66.
- **Retrieved**: full text (5-page scanned PDF with an OCR text layer).
  Downloaded independently from three mirrors that returned byte-identical
  files: `web-ext.u-aizu.ac.jp/course/bmclass/documents/otsu1979.pdf`,
  `cw.fel.cvut.cz/wiki/_media/courses/a6m33bio/otsu.pdf`,
  `engineering.purdue.edu/kak/computervision/ECE661.08/OTSU_paper.pdf`. The
  file carries the IEEE Xplore stamp "Authorized licensed use limited to:
  Purdue University. Downloaded on October 7, 2008".
- **Depth**: read in full (all five pages; the figures themselves are scans
  and were not inspected).
- **Answers**:
  - Method: dichotomise the L-level histogram at k into C_0 = [1..k] and
    C_1 = [k+1..L]; maximise the between-class variance σ_B²(k), equivalently
    the normalised criterion η(k) = σ_B²(k)/σ_T². Only the zeroth and first
    cumulative moments ω(k) and μ(k) are needed:
    σ_B²(k) = [μ_T ω(k) - μ(k)]² / (ω(k)[1 - ω(k)]).
  - **On non-bimodal distributions - and this contradicts what pass 1 recorded
    from secondary sources.** The passage about "a flat and broad valley,
    imbued with noise, or when the two peaks are extremely unequal in height,
    often producing no traceable valley" is in the Introduction and describes
    the failure of **valley-seeking** methods; it is the motivation for
    Otsu's method, not a limitation of it. Otsu's own claims run the other
    way. Section III.C reports Fig. 2 as textures "where the histograms
    typically show the difficult cases of a broad and flat valley (c) and a
    unimodal peak (g)" and presents both as successful. Stated advantage 3)
    in the Conclusion: the threshold is selected "not based on the
    differentiation (i.e. a local property such as valley), but on the
    integration (i.e., a global property) of the histogram."
  - **The limitation Otsu does state** is about multithresholding, section
    III.B: "It should be noticed that the selected thresholds generally become
    less credible as the number of classes to be separated increases. This is
    because the criterion measure (σ_B²), defined in one-dimensional
    (gray-level) scale, may gradually lose its meaning as the number of
    classes increases." He considers M = 2 and 3 to "cover almost all
    practical applications".
  - **A separability diagnostic comes free with the method.** Section III.A:
    the maximum criterion value η* = η(k*) "can be used as a measure to
    evaluate the separability of classes (or ease of thresholding) for the
    original picture or the bimodality of the histogram." It is invariant
    under affine transformation of the value scale (g' = a·g + b), lies in
    [0, 1], attains 0 only for a single-constant-level picture and 1 only for
    a two-valued one. Numeric η* values appear beside each experiment
    (0.894, 0.853, 0.887, 0.767, 0.873, 0.893).
  - **Non-image use is licensed by the paper itself.** Conclusion: "The range
    of its applications is not restricted only to the thresholding of the
    gray-level picture ... but it may also cover other cases of unsupervised
    classification in which a histogram of some characteristic (or feature)
    discriminative for classifying the objects is available."
  - Section III.D notes that η(k) was "always smooth and unimodal" in their
    experiments but that "the rigorous proof of the unimodality has not yet
    been obtained."
  - References are five items: Prewitt & Mendelsohn 1966; Weszka, Nagel &
    Rosenfeld 1974; Watanabe/CYBEST 1974; Chow & Kaneko 1972; Fukunaga 1972
    pp. 260-267.
- **Bearing**: three things change for this project.
  (1) The citation is now safe to use - author, title, venue, volume, issue,
  pages, year and DOI are all verified against retrieved documents, so the
  dissertation's most certain citation no longer rests on recollection.
  (2) The sentence "Otsu degrades on non-bimodal distributions" should not be
  attributed to Otsu. He asserts the opposite and shows a unimodal-histogram
  example. If the project wants that claim it needs its own measurement or a
  later source; ROADMAP.md's own evidence (Otsu landing mid-plateau on
  synthetic data, and at p97 over active edges on real data) is a measurement
  the project owns and should cite as its own rather than as Otsu's caveat.
  (3) η* is directly actionable. It is one extra scalar out of the same two
  cumulative moments `find_threshold` already computes, it is affine-invariant
  so it is comparable across configurations and datasets, and it is exactly a
  measure of how bimodal the pheromone histogram was. Both failure faces in
  ROADMAP.md - the dominant middle plateau on synthetic data and the tau_min
  spike on real data - are hypotheses about the shape of that histogram, and
  η* would turn them into a number that every run reports. See
  QUESTIONS_PASS2.md #4.

---

## P2-6. Hu, Kai-Cheng; Tsai, Chun-Wei; Chiang, Ming-Chao; Yang, Chu-Sing (2015). *A Multiple Pheromone Table Based Ant Colony Optimization for Clustering*.

**Correction to pass 1.** SEARCH_LOG.md Category A recorded this as "Hu 2015
'Multiple Pheromone Table ACO for Clustering' (Wiley) - uses a pheromone
threshold to split patterns". The publisher-registered abstract does not
support the threshold description; the paper is about a second pheromone table
for search diversification.

- **Venue**: journal - Mathematical Problems in Engineering, vol. 2015,
  article 158632, 11 pages. Originally Hindawi, now hosted by Wiley.
- **Identifier**: DOI 10.1155/2015/158632.
- **Retrieved**: **abstract only** - the full abstract as registered with the
  publisher (via OpenAlex, which stores the publisher-supplied abstract).
  Full text not retrieved: Wiley returns HTTP 402 to WebFetch, the Hindawi
  `downloads.hindawi.com` PDF returns 403 to both curl and WebFetch, and
  `onlinelibrary.wiley.com` is refused by the browser extension's navigation
  policy.
- **Depth**: abstract only.
- **Answers**:
  - Verbatim: "Ant colony optimization (ACO) is an efficient heuristic
    algorithm for combinatorial optimization problems, such as clustering.
    Because the search strategy of ACO is similar to those of other well-known
    heuristics, the probability of searching particular regions will be
    increased if better results are found and kept. ... In addition to the
    'original' pheromone table used to keep track of the promising
    information, a second pheromone table is added to the proposed algorithm
    to keep track of the unpromising information so as to increase the
    probability of searching directions worse than the current solutions."
  - Q1: not resolved by the abstract, but the framing is explicitly
    solution-quality-driven ("better results are found and kept", "worse than
    the current solutions").
  - Q2: a solution. The clustering is the best solution found, evaluated
    "in terms of quality" against ACO and other clustering algorithms.
  - Q3: not stated in the abstract.
- **Bearing**: this is a search-diversification variant inside the ACOC
  lineage (see #8), not a pheromone-threshold read-out. It does not compete
  with this project's claim. The pass-1 note describing it as thresholding
  pheromone should be withdrawn - no retrieved document supports it.

---

## P2-7. Tseng, Shih-Pang; Chiang, Ming-Chao; Yang, Chu-Sing (2013). *L-nearest neighbors ant colony optimization for data clustering* (L-NNACO).

**Correction to pass 1.** SEARCH_LOG.md Category A recorded L-NNACO as
"Gao 2016". It is not: Gao 2016 is a different paper (see #9) and does not
contain the algorithm. L-NNACO is Tseng, Chiang & Yang, ICMLC 2013.

- **Venue**: conference - 2013 International Conference on Machine Learning
  and Cybernetics (ICMLC 2013), Tianjin, China, 14-17 July 2013, vol. 1,
  pp. 1684-1690. Publisher IEEE. Electronic ISBN 978-1-4799-0260-6.
- **Identifier**: DOI 10.1109/ICMLC.2013.6890869,
  https://ieeexplore.ieee.org/document/6890869.
- **Retrieved**: **abstract only** - the publisher's abstract, read on the
  IEEE Xplore record page in the maintainer's browser. Full text behind
  "Sign in to Continue Reading"; no OA copy.
- **Depth**: abstract only.
- **Answers**:
  - Verbatim: "It is based on the assumption that there are at least one or
    more neighbors belong to the same cluster in the L nearest neighbors of
    each instance. It modifies the operation of constructing solution to
    reduce the computation time of Euclidean distance. The experimental
    results show that the L-NNACO is faster than ACO about 38% to 54%. In
    addition, the L-NNACO is with greater or equal accuracy to the ACO for the
    various datasets of real world."
  - Q1/Q2: not stated directly, but "constructing solution" and "accuracy"
    place it squarely in the ACOC family - each ant builds a complete
    assignment which is then scored. Source #8 gives that family's objective
    function verbatim.
  - Q3: L, the number of nearest neighbours consulted; everything else
    inherited from ACO.
- **Bearing**: pass 1 recorded this as one of the two nearest competitors. It
  is not close. The nearest neighbours are used to skip probability
  computations while building an assignment vector; they never form a graph
  the ants walk on, and the algorithm keeps the objective function. Same
  research group (NSYSU) as #6. **This one can be set aside.**

---

## P2-8. Lucky, Lucky & Girsang, Abba Suganda (2020). *Hybrid Nearest Neighbors Ant Colony Optimization for Clustering Social Media Comments* (NNACOC).

- **Venue**: journal - Informatica (Slovenia), vol. 44, no. 1 (2020),
  pp. 63-74. Open access.
- **Identifier**: DOI 10.31449/inf.v44i1.2672. PDF:
  http://www.informatica.si/index.php/informatica/article/download/2672/1384
- **Retrieved**: full text (PDF, 12 pages).
- **Depth**: read (sections 1.1-1.4, 2.1-2.4 and the parameter tables read;
  the Twitter-dataset results skimmed).
- **Answers**:
  - **This is the ACOC family stated explicitly**, and it settles what
    #6 and #7 leave open about their lineage. ACOC is attributed to Shelokar:
    "The basic idea of this technique is to represent the solution into a
    string containing cluster number assigned to each data."
  - Q1: **elitist selection, verbatim** - "ACOC also implements the elitist
    ant strategy, which means that only n-best ants or solutions will be
    permitted to deposit the pheromone. The value of n is usually 20% from the
    total number of ants." Restated in 3.2: "only the elitist ants (m ants
    with best solution) are permitted to deposit pheromone."
  - Q2: a solution - a cluster-number string per ant, improved by a local
    search that is "similar to mutation in Genetic Algorithm".
  - **The objective function, verbatim**: deposit is Δτ_ij^k = 1 / F^k, where
    "F^k is the fitness function of the solution generated by k-th ant", and
    the fitness is "the minimal SSE of euclidean distances" between objects
    and their cluster centroids; for text they substitute the sum of cosine
    distances. The pheromone table is object × cluster, not edge-indexed:
    "The bigger the value of the pheromone between an object and certain
    cluster, the bigger the chance that the object will be assigned to that
    cluster."
  - The one "threshold" in the paper is unrelated to pheromone - it is a
    mutation probability in the local search.
  - Q3 / parameters (Table 8): number of ants m = 25, elitist ants e = 5,
    evaporation rate 0.1, local-search probability p_ls = 0.01; NNACOC adds
    nn = 20 nearest neighbours and q1 = 0.3. **k must be supplied**: for the
    Twitter sets "the number of hashtags is assumed as the number of
    clusters."
- **Bearing**: the clean primary-source demonstration that the whole
  ACOC/L-NNACO/MPTACO branch - the one pass 1 flagged as the nearest
  competitor - is objective-driven assignment search with a fixed k, a
  best-20% deposit rule and an object×cluster pheromone table. It answers all
  three questions in one place and is freely available, which makes it the
  better citation for "this is what ACO-for-clustering normally means" than
  either paywalled paper. It also confirms that this branch is **not** the
  threat to the novelty claim - #1 is.

---

## P2-9. Gao, Wei (2016). *Improved Ant Colony Clustering Algorithm and Its Performance Study*.

- **Venue**: journal - Computational Intelligence and Neuroscience, vol. 2016,
  article 4835932. Open access (PMC4709600).
- **Identifier**: DOI 10.1155/2016/4835932.
- **Retrieved**: full text page fetched and read by summarising fetch; not
  itself extracted to a local file.
- **Depth**: skimmed (via a targeted read of the PMC full text).
- **Answers**: it is a "data reactor" model in the Lumer-Faieta lineage where
  ants combine and split data objects by dissimilarity; the read of it in this
  session found **no pheromone update mechanism at all** - selection is by
  similarity and probability functions. Parameters reported: M, kp, kc, α, N,
  s (and a variant with α1, v_max, c). Cluster read-out is a recursive
  same-label flood over neighbours within a local region.
- **Bearing**: recorded only to close the pass-1 misattribution: this is not
  L-NNACO and does not restrict ant moves to L nearest neighbours. It answers
  none of the three questions usefully and should not be cited for anything in
  this project.

---

## P2-10. Chen, Ling; Xu, Xiao-Hua; Chen, Yi-Xin (2004). *An Adaptive Ant Colony Clustering Algorithm* (ASM / A4C).

- **Venue**: conference - Proceedings of the Third International Conference on
  Machine Learning and Cybernetics, Shanghai, 26-29 August 2004, pp. 1387-1392.
  Publisher IEEE.
- **Identifier**: no DOI captured; open PDF at
  https://www.cse.wustl.edu/~yixin.chen/public/a4c.pdf (author's own page).
- **Retrieved**: full text (PDF, 6 pages).
- **Depth**: skimmed (abstract, introduction and the Ants Sleeping Model
  definitions read; the experimental section not read).
- **Answers**: a 2-D grid model in the Deneubourg/Lumer-Faieta lineage. Each
  agent **is** a data object sitting on a cellular-automaton grid with two
  states, active and sleeping; a fitness function measures an ant's similarity
  to its grid neighbours and decides whether it moves. No pheromone anywhere.
  Explicitly framed against BM and LF, whose weakness they identify as
  separating the ants from the data so that "the data movements have to be
  implemented indirectly through the ants' movements".
- **Bearing**: by the same first author as #2/#3/#4 and one year earlier, but
  a completely different mechanism - grid, no graph, no pheromone. Useful for
  two things only: it is a freely readable primary description of what the
  Deneubourg/LF branch actually does (the branch this project must
  disambiguate itself from), and it shows that the digraph papers were a
  deliberate departure by that group rather than a variation on their own
  earlier work.

---

## P2-11. Held, Pascal; Dockhorn, Alexander; Krause, Benjamin; Kruse, Rudolf (2015). *Clustering Social Networks Using Competing Ant Hives*.

- **Venue**: conference - 2015 Second European Network Intelligence Conference
  (ENIC). Publisher IEEE.
- **Identifier**: DOI 10.1109/ENIC.2015.18.
- **Retrieved**: **abstract only** (publisher-registered abstract via
  OpenAlex; the IEEE record was reached through search but the full text is
  behind sign-in).
- **Depth**: abstract only.
- **Answers**:
  - Verbatim: "multiple ant colonies are competing for the available nodes.
    Each hive creates ants, which will explore nearby graph structures and
    drop hive-specific pheromones on visited nodes. Over time, hives will
    collect nodes and will be relocated to the center of all collected nodes.
    In case of dynamic graph clustering, pheromone values can be reused in
    consecutive iterations."
  - Q1: all ants of a hive deposit; no per-ant ranking is mentioned.
  - Q2: a state of the environment - node ownership is decided by which hive's
    pheromone is on the node.
  - Q3: not stated in the abstract. The number of hives is evidently a
    parameter.
  - Reported "on a par with the k-median algorithm and performs worse than
    Louvain clustering", with "the advantage of implicit noise detection ...
    at the cost of longer computation times."
- **Bearing**: a second example, after AntPaP in pass 1, of pheromone-as-answer
  with no objective function - and this one is actually a clustering method on
  a graph, which AntPaP is not. It is still distant from this project: the
  pheromone is per-hive and lives on nodes, the read-out is ownership rather
  than a scalar threshold, the number of hives is set in advance, and there is
  no similarity-graph construction stage. Worth citing as a companion to
  AntPaP under "ACO without a target function". Abstract-only; flagged.

---

## P2-12. Handl, Julia & Meyer, Bernd (2007). *Ant-based and swarm-based clustering*.

**Correction to pass-1 entry #7.** Pass 1 recorded "Handl, J. & Meyer, B.,
*Finding groups in data: Cluster analysis with ants*, Applied Soft Computing"
at title-level depth. That conflates two different works. The Handl & Meyer
survey is in *Swarm Intelligence*, and the Applied Soft Computing paper with
that title is by Urszula Boryczka (see the note at the end of this file).

- **Venue**: journal - Swarm Intelligence, vol. 1, no. 2 (2007), pp. 95-113.
  Springer.
- **Identifier**: DOI 10.1007/s11721-007-0008-7.
- **Retrieved**: **metadata only**. Not open access; no abstract is registered
  in OpenAlex and no free copy was found at the authors' pages.
- **Depth**: not retrieved.
- **Answers**: none - nothing was read.
- **Bearing**: still the standard survey citation for the branch this project
  must disambiguate itself from, and pass 1's bibliographic record of it was
  wrong. The corrected record is what is above. Full text needs the
  maintainer's Springer access. Note that the *related* Handl & Meyer paper
  that source #1 cites is a different one again: "Improved ant-based clustering
  and sorting in a document retrieval interface", PPSN VII, LNCS 2439,
  pp. 913-923, 2002.

---

## P2-13. Deneubourg, J.-L.; Goss, S.; Franks, N.; Sendova-Franks, A.; Detrain, C.; Chretien, L. (1991). *The dynamics of collective sorting: Robot-like ants and ant-like robots*.

**Bibliographic upgrade of pass-1 entry #5. The primary text is still not
retrieved; only the citation is now firm.**

- **Venue**: conference - Proceedings of the First International Conference on
  Simulation of Adaptive Behavior: From Animals to Animats 1, 1991,
  pp. 356-365, MIT Press, Cambridge, MA.
- **Identifier**: no DOI. The full author list and page range above are taken
  from the reference list of source #1 (their ref [3]), a peer-reviewed paper
  retrieved in full in this session - so the citation itself is now traceable
  to a document rather than to recollection.
- **Retrieved**: NOT retrieved. Still no primary text.
- **Depth**: not retrieved. Pass 1's description of the mechanism remains
  second-hand and is not restated here.
- **Bearing**: pass 1 flagged that a VAK reviewer would expect this citation to
  be readable. That is unchanged - what has changed is that the reference line
  itself (six authors, exact pages, exact proceedings title) is now supported.
  A physical or institutional copy of the SAB-1 volume is still needed before
  anything is said about what the paper argues.

---

## P2-14. Lumer, E. & Faieta, B. (1994). *Diversity and adaptation in populations of clustering ants*.

**Bibliographic confirmation of pass-1 entry #6. Not retrieved.**

- **Venue**: conference - Proceedings of the Third International Conference on
  Simulation of Adaptive Behavior: From Animals to Animats 3, pp. 501-508,
  MIT Press, Cambridge, MA. (1994.)
- **Identifier**: no DOI; ACM DL record 10.5555/645301.648386 per pass 1.
  The venue and page range are independently confirmed by the reference list
  of source #1 (their ref [4]), retrieved this session, and agree with what
  pass 1 recorded.
- **Retrieved**: NOT retrieved.
- **Depth**: not retrieved.
- **Bearing**: the page range and proceedings title recorded in pass 1 are
  correct. The content description in pass 1 remains second-hand.

---

## Named in retrieved documents, not themselves retrieved

Recorded so they are not rediscovered as new, and so the citation trail is
visible. All of these are reference-list entries in source #1, which was read
in full; none of the papers themselves was obtained.

- Kuntz, P. & Snyers, D. (1994). *Emergent colonization and graph
  partitioning*. Proc. Third Int. Conf. on Simulation of Adaptive Behavior
  (SAB3), pp. 494-500, MIT Press. **Ant-based graph partitioning, same
  proceedings volume as Lumer & Faieta - worth a look in a later pass.**
- Kuntz, P. & Snyers, D. (1999). *New results on an ant-based heuristic for
  highlighting the organization of large graphs*. Proc. CEC 1999,
  pp. 1451-1458, IEEE Press.
- Gupta, G.; Liu, A.; Ghosh, J. (2006). *Hierarchical Density Shaving: A
  clustering and visualization framework for large biological datasets*.
  Proc. 6th IEEE Int. Conf. on Data Mining workshops, pp. 89-93. And Gupta,
  Liu & Ghosh (2010), *Automated hierarchical density shaving*, IEEE/ACM
  Trans. Comput. Biol. Bioinform. 7(2):223-237. **HDS is the baseline source
  #1 compares against and is the density-based hierarchical method closest to
  the threshold-sweep idea.**
- Lee, K.; Kim, D.-W.; Lee, K. H.; Lee, D. (2007). *Density-Induced Support
  Vector Data Description*. IEEE Trans. Neural Networks 18(1):284-289. The
  source of the kNN-graph density definition used in #1.
- Handl, J.; Knowles, J.; Dorigo, M. (2006). *Ant-based clustering and
  topographic mapping*. Artificial Life 12(1):35-62.
- Chircop, J. & Buckingham, C. D. (2013). *A Multiple Pheromone Ant Clustering
  Algorithm*. NICSO 2013, Studies in Computational Intelligence, Springer.
  DOI 10.1007/978-3-319-01692-4_2. Surfaced independently in the OpenAlex
  sweep as well.
- Azzag, H.; Venturini, G.; Oliver, A.; Guinot, C. (2007). *A hierarchical ant
  based clustering algorithm and its use in three real-world applications*.
  European Journal of Operational Research 179(3):906-922.
- Dorigo, M. & Stützle, T. (2004). *Ant Colony Optimization*. MIT Press. Still
  not retrieved (as in pass 1); cited by #1 for the transition-probability and
  evaporation forms.
- Boryczka, U. (2009). *Finding groups in data: Cluster analysis with ants*.
  Applied Soft Computing 9(1). This is the paper behind the ScienceDirect page
  pass 1 recorded under Handl & Meyer's name. An open copy exists at
  `eprints.bournemouth.ac.uk/20910/1/Boryczka2009.pdf`; every fetch route
  available in this session failed on it (see SEARCH_LOG_PASS2.md). Not
  retrieved. **Retrieved in pass 3, see P3-2 below - the same URL succeeded
  from this session's environment.**

---
---

# Pass 3 - 2026-08-03

Run from `tmp/COWORK_BRIEF.md`. Order followed: Section A first (re-confirmed,
no new access), then E2/E3 (resolved), then B, C, D per
`literature/RETRIEVAL_LIST.md`. Numbering is prefixed `P3-` and does not
renumber pass 1 or pass 2 entries.

## READ THIS FIRST (pass 3)

**E2 is resolved, and it changes what stage 3 of this project can claim.**
"MABA" is not a separate undiscovered paper - it is the same paper as E3
(arXiv:1303.4711 / *Advances in Complex Systems* 15(8):1250036, He, Liu, Yang,
Huang, Liu & Jin, 2012/2013), read in full this session (P3-1). It describes,
by name ("layer and rule"), exactly the coarsen-and-repeat scheme planned as
this project's third stage: run the base method, take each found community as
a single vertex of a new graph, repeat. It is not this project's base
mechanism (no pheromone, driven throughout by modularity as an explicit
objective function) - but the *hierarchical-collapse structure itself* is not
new even setting MABA aside: Louvain (P3-7, 2008) does the identical
community-becomes-vertex-of-next-level-graph step four years earlier, and is
the most-cited method in the entire field. See P3-1's Bearing and the pass-3
entry in `QUESTIONS.md`.

---

## P3-1. He, Dongxiao; Liu, Jie; Yang, Bo; Huang, Yuxiao; Liu, Dayou; Jin, Di (2012/2013). *An Ant-Based Algorithm with Local Optimization for Community Detection in Large-Scale Networks* (MABA).

- **Venue**: journal - *Advances in Complex Systems*, vol. 15, no. 8 (2012),
  art. 1250036. Self-archived as arXiv:1303.4711 (submitted 19 Mar 2013),
  cs.SI / physics.soc-ph; the arXiv listing states the journal reference
  itself, so the E2/E3 identity is not an inference from search results but
  from the retrieved document's own header.
- **Identifier**: DOI 10.1142/S0219525912500361 (journal of record);
  arXiv:1303.4711 (open text).
- **Retrieved**: full text (arXiv PDF, 18 pages, fetched directly - no
  paywall, no login).
- **Depth**: read. Sections 1-4 (Introduction, Related Works, Algorithm,
  Experiments) read in full; Section 4.5 (convergence analysis) and the
  figures were not transcribed here.
- **Answers**:
  - **Q1.** Nothing deposits pheromone - there is none. Verbatim: "Unlike most
    of those methods where ants correspond with each other through pheromone,
    our ants (or called mobile-agents) communicate with one another by a
    particular underlying interactive mechanism which makes the actions of
    the current ants affected by that of all the previous ones... This
    special interactive mechanism, which does not employ pheromone,
    significantly reduces the running time." Each "ant" instead does
    simulated-annealing label propagation: it moves to a neighbour and
    probabilistically adopts that neighbour's community label, accepting with
    probability 1 if the move raises the vertex's local modularity
    contribution f(i), else with probability exp(-(f_cur - f'_cur)/T).
  - **Q2.** The result is an explicit partition maximising modularity Q - a
    found solution, not a state of an environment. SABA (the single-layer
    routine) runs "until no further improvement on modularity can be
    achieved" (a local maximum of Q); MABA explicitly returns "the partition
    corresponding to the maximal Q-value" among the levels visited.
  - **Q3.** Parameters: T (initial annealing temperature, reported value 500),
    c_T (cooling coefficient, T <- c_T x T per iteration, reported 0.1), p
    (fraction of vertices carrying an ant, n' = p x n, reported 0.6). None of
    these correspond to this project's tau_min/tau_max/rho/evaporation
    parameters - there is no pheromone trail to clamp or evaporate. Not
    applicable, in the sense the task's Q3 column intends.
  - **The multilevel mechanism, verbatim**: "we firstly run SABA on the
    original network as the first level... Once the communities are
    obtained, SABA is reapplied to a higher level network, where each
    detected community is regarded as a new vertex and the sum of the weights
    of edges between any two communities as the weight between the new
    vertices. The aforementioned process is repeated iteratively until no
    further improvement on modularity can be achieved, which corresponds to
    MABA." Presented as the paper's central contribution (Sec. 3.4), with a
    worked three-level hierarchy example (US college football network,
    Fig. 6) and an argument that repeated coarsening is what lets the method
    escape modularity's resolution limit (verified against a second
    synthetic-network test, Table 3, where MABA alone recovers the exact
    clique count as clique number grows past the point FN and SA both fail).
- **Bearing**: **resolves E2.** The base mechanism does not compete with this
  project - it has no pheromone, no similarity-graph construction stage
  (operates on an already-given network), and is driven throughout by an
  explicit objective function this project's stated position rules out. Kang
  & Choi (P2-1) remains the mechanism-level predecessor. But the *coarsen the
  graph by treating each found cluster as one node of the next level, and
  repeat* device - this project's planned stage 3 - is exactly MABA's "layer
  and rule", published 2012/2013, and (see P3-7) is not new even relative to
  MABA: Louvain does the same structural move in 2008. **What stage 3 can
  still claim as new, if anything, is doing this coarsening on top of a
  pheromone-threshold-components base rather than a modularity-optimizing
  one - not the coarsen-and-repeat structure itself.** Flagged as a question,
  not decided here; see `QUESTIONS.md` pass 3.

---

## P3-2. Boryczka, Urszula (2009). *Finding groups in data: Cluster analysis with ants.* [full text now obtained - upgrades the "named, not retrieved" listing at the end of Pass 1/2]

- **Venue**: journal - *Applied Soft Computing*, vol. 9, no. 1 (2009),
  pp. 61-70. Elsevier.
- **Identifier**: DOI 10.1016/j.asoc.2008.03.002. Open-access mirror:
  `eprints.bournemouth.ac.uk/20910/1/Boryczka2009.pdf` - the same URL pass 2
  tried and failed on twice ("Socket is closed", curl exit 000); this
  session's fetch tool reached it without incident, on the first try, no
  credential involved either time.
- **Retrieved**: full text (PDF; OCR artefacts in the header/running text -
  some ligatures and symbols are garbled - but the body, equations and tables
  are intact and readable).
- **Depth**: read in full.
- **Answers**: this is a Lumer-Faieta-lineage, grid/data-carrying method - it
  belongs in Section B ("the branch this project is not"), confirming the
  placement `RETRIEVAL_LIST.md` already gives it. Q1/Q2/Q3 do not apply in
  their ACO-family form: there is no pheromone and no digraph. Ants ("agents")
  occupy a toroidal 2D grid seeded with data items and pick up/drop items
  based on a local-density function f*(i) over a fixed-radius neighbourhood,
  with pick/drop probabilities of the same k1/k2-threshold form Deneubourg and
  Lumer-Faieta use. The paper's own contributions (ACA, and its refinement
  ACAM) are: (a) Euclidean/Cosine/Gower dissimilarity measures in place of
  Lumer-Faieta's fixed Euclidean distance, and (b) a simulated-annealing-style
  cooling schedule for the neighbourhood-scaling parameter alpha in place of a
  fixed value. No pheromone appears anywhere in the method - the paper's own
  conclusion lists "different communication strategies via pheromone" as
  *future* work, not something ACA/ACAM does.
- **Bearing**: confirms correct filing as a Lumer-Faieta-branch relative,
  structurally unrelated to this project's edge-pheromone/threshold/
  components mechanism and to the digraph line (Section A). No bearing on the
  novelty question. Standard citation, alongside Handl & Meyer 2007 (P2-12),
  for "the branch this project is not."

---

## P3-3. Boryczka, Urszula (2013). *Corrigendum to "Finding groups in data: Cluster analysis with ants"* [Appl. Soft Comput. 9(1) (2009) 61-70].

- **Venue**: journal - *Applied Soft Computing*, vol. 13, issue 10 (2013),
  p. 4229. Elsevier.
- **Identifier**: DOI 10.1016/j.asoc.2013.07.012.
- **Retrieved**: metadata only. Crossref confirms a single-page item, single
  author, explicitly linked via Crossref's own `associatedlink` relation to
  DOI 10.1016/j.asoc.2008.03.002 (P3-2 above). The abstract field is elided
  by the publisher in the Semantic Scholar record and no open-access location
  is listed by Unpaywall; the ScienceDirect article page did not return
  readable body text to this session's fetch tool.
- **Depth**: not retrieved beyond bibliographic confirmation - what the
  corrigendum actually corrects is unknown from this session.
- **Answers**: none - content not read.
- **Bearing**: exists, is real, one page long (consistent with an errata
  notice, but that is an inference from length, not from reading it).
  `RETRIEVAL_LIST.md` calls reading this "not optional" before citing P3-2 -
  it is still not read. If the maintainer opens the ScienceDirect page in
  their own session, this is a one-page read.

---

## P3-4. Boryczka, Urszula (2006). *Finding Groups in Data: Cluster Analysis with Ants* (ISDA 2006, earlier conference version of P3-2).

- **Venue**: conference - Sixth International Conference on Intelligent
  Systems Design and Applications (ISDA 2006), Jinan, China, 16-18 October
  2006, pp. 404-409. IEEE.
- **Identifier**: DOI 10.1109/isda.2006.151. IEEE Xplore document 4021473.
- **Retrieved**: metadata + reference list only (Crossref record, 18
  references). The IEEE Xplore document page returned no body content to
  this session's fetch tool - same client-rendered-shell behaviour seen on
  the Chen/Tu/Chen IEEE record (P2-2).
- **Depth**: not retrieved beyond title, venue, page range and reference
  list.
- **Answers**: none directly, but the reference list overlaps heavily with
  P3-2 (ref [5] Deneubourg 1991, ref [14] Lumer & Faieta 1994, ref [11] Handl
  & Meyer 2002), confirming this is the earlier, conference-length statement
  of the same ACA method, single-authored, three years before the journal
  version.
- **Bearing**: same placement as P3-2 - Lumer-Faieta branch, not this
  project's mechanism. Recorded so it is not mistaken for a fourth,
  independent source; per `RETRIEVAL_LIST.md`, it is the conference precursor
  to P3-2 and must not be conflated with it.

---

## P3-5. Pons, Pascal & Latapy, Matthieu (2006). *Computing Communities in Large Networks Using Random Walks* (Walktrap).

- **Venue**: journal - *Journal of Graph Algorithms and Applications* 10(2),
  191-218. Long/preprint version self-archived on arXiv.
- **Identifier**: DOI 10.7155/jgaa.00124 (journal of record); arXiv:physics/0512106
  (long version).
- **Retrieved**: abstract (arXiv abstract page fetched directly and read
  verbatim; JGAA's own page returned no content to this session's fetch
  tool). Full text is at the same arXiv URL but not transcribed in this pass.
- **Depth**: abstract only.
- **Answers**: proposes a vertex-similarity measure derived from random
  walks, used in an agglomerative algorithm ("Walktrap") to build communities
  bottom-up; O(mn^2) worst case, O(n^2 log n) typical. No pheromone, no ants -
  a random-walk-based hierarchical agglomerative method whose central device
  is a computed distance, not a threshold-and-read mechanism.
- **Bearing**: comparison-set entry, "non-ant relatives, random-walk family."
  This project's own mechanism is also a random walk, though
  pheromone-reinforced rather than distance-computing; structurally distant
  since Walktrap's read-out is agglomerative merging by computed distance,
  not thresholding an accumulated scalar field.

---

## P3-6. Rosvall, Martin & Bergstrom, Carl T. (2008). *Maps of Random Walks on Complex Networks Reveal Community Structure* (Infomap).

- **Venue**: journal - *Proceedings of the National Academy of Sciences*
  105(4), 1118-1123.
- **Identifier**: DOI 10.1073/pnas.0706851105. Open-access preprint
  arXiv:0707.0609 (GREEN OA per Semantic Scholar/Unpaywall).
- **Retrieved**: abstract (Semantic Scholar Graph API, cross-checked against
  the arXiv listing).
- **Depth**: abstract only.
- **Answers**: uses the probability flow of random walks as a proxy for
  real information flow, and decomposes the network into modules by
  minimising the description length of that flow (the "map equation" - an
  explicit information-theoretic objective), not by thresholding an
  accumulated field.
- **Bearing**: comparison-set entry for ROADMAP.md phase 4 (C5-C7 form the
  baseline set). Objective-function-driven, unlike this project.

---

## P3-7. Blondel, Vincent D.; Guillaume, Jean-Loup; Lambiotte, Renaud; Lefebvre, Etienne (2008). *Fast Unfolding of Communities in Large Networks* (Louvain).

- **Venue**: journal - *Journal of Statistical Mechanics: Theory and
  Experiment* 2008(10), P10008.
- **Identifier**: DOI 10.1088/1742-5468/2008/10/p10008. Open-access preprint
  arXiv:0803.0476 (GREEN OA).
- **Retrieved**: abstract (Semantic Scholar Graph API / arXiv listing).
- **Depth**: abstract only.
- **Answers**: a two-phase heuristic - (1) locally move nodes between
  neighbouring communities to greedily maximise modularity gain, (2) build a
  new, coarser network where each found community becomes a single node,
  weighted by the summed inter-community edge weight, and repeat on that
  coarser graph. Iterated until modularity stops increasing.
- **Bearing**: **the general-case predecessor of the "hierarchical collapse"
  this project plans as stage 3** - communities become vertices of the next
  level, repeat - published 2008, four years before MABA (P3-1) restates the
  same device inside an ant-labelled framework. Whatever stage 3 claims as
  new, it is not the coarsen-and-repeat structure itself; that is Louvain's
  second phase, the most-cited method in the field. See P3-1's Bearing and
  `QUESTIONS.md` pass 3.

---

## P3-8. Traag, V.A.; Waltman, L.; van Eck, N.J. (2019). *From Louvain to Leiden: Guaranteeing Well-Connected Communities.*

- **Venue**: journal - *Scientific Reports* 9, art. 5233.
- **Identifier**: DOI 10.1038/s41598-019-41695-z. Gold OA (CC-BY), full text
  at nature.com.
- **Retrieved**: abstract (Semantic Scholar Graph API; Gold OA confirmed -
  full text available but not transcribed in this pass).
- **Depth**: abstract only.
- **Answers**: shows Louvain can produce arbitrarily badly connected or even
  disconnected communities (up to 25% badly connected, 16% disconnected in
  their experiments, worse under iteration), and introduces Leiden, which
  guarantees connected communities and, iterated, local optimality of every
  subset of every community, while running faster than Louvain via a fast
  local-move approach.
- **Bearing**: comparison-set entry, ROADMAP.md phase 4. Also a caution for
  this project's own stage-3 design: Louvain's connectivity failure mode is a
  documented risk for any coarsen-and-repeat scheme, including a
  pheromone-based one.

---

## P3-9. Campello, Ricardo J.G.B.; Moulavi, Davoud; Sander, Joerg (2013). *Density-Based Clustering Based on Hierarchical Density Estimates* (HDBSCAN).

- **Venue**: conference - Pacific-Asia Conference on Knowledge Discovery and
  Data Mining (PAKDD 2013), Lecture Notes in Computer Science.
- **Identifier**: DOI 10.1007/978-3-642-37456-2_14.
- **Retrieved**: metadata only. Abstract elided by the publisher in the
  Semantic Scholar record (CLOSED, no open-access PDF per Unpaywall).
- **Depth**: not retrieved beyond bibliographic fields.
- **Answers**: none - abstract not obtained this session.
- **Bearing**: comparison-set entry, ROADMAP.md phase 4. **Flagged**: no
  description beyond common knowledge has been retrieved in any pass. The
  companion journal paper (ACM TKDD 2015) or the HDBSCAN authors' own
  documentation may be open where this conference version is not - worth a
  targeted retrieval before the comparison table is finalized.

---

## P3-10. Fred, Ana L.N. & Jain, Anil K. (2005). *Combining Multiple Clusterings Using Evidence Accumulation.*

- **Venue**: journal - *IEEE Transactions on Pattern Analysis and Machine
  Intelligence* 27(6), 835-850.
- **Identifier**: DOI 10.1109/tpami.2005.113.
- **Retrieved**: metadata only. Abstract elided by the publisher (Semantic
  Scholar CLOSED record); not open access per Unpaywall; the IEEE Xplore
  record page returned no content to this session's fetch tool.
- **Depth**: not retrieved beyond bibliographic fields. **This is a gap, not
  a finding** - `RETRIEVAL_LIST.md` calls this "the most underrated line" in
  Section C.
- **Answers**: none obtained this session. The co-association-matrix
  description in `RETRIEVAL_LIST.md` is the project's own prior
  characterisation of this paper, not something re-verified against the text
  here - restated as a gap, not as a freshly confirmed finding.
- **Bearing**: **unresolved.** The claim that thresholding a co-association
  matrix and taking components is structurally the move this paper makes
  could not be checked against the primary text in this session. Needs
  institutional access or a library copy before the dissertation leans on
  this comparison - right now it rests on the project's own prior reading,
  which is exactly the risk `LITERATURE.md` calls "citing from memory."
  **Flagged to the maintainer.**

---

## P3-11. Pemantle, Robin (2007). *A Survey of Random Processes with Reinforcement.*

- **Venue**: journal - *Probability Surveys*, vol. 4 (indexed as 2006 in
  some registries; the journal issue itself is dated 2007).
- **Identifier**: DOI 10.1214/07-ps094. Gold OA (CC-BY) at
  projecteuclid.org; self-archived as arXiv:math/0610076.
- **Retrieved**: abstract (Semantic Scholar Graph API, cross-checked against
  the Gold-OA publisher record). Full text is freely available at the DOI
  but not transcribed in this pass.
- **Depth**: abstract only.
- **Answers**: surveys generalised Polya urns, reinforced random walks,
  interacting urn models and continuous reinforced processes, emphasising
  methods and proof sketches, with applications noted in statistics, biology
  and economics.
- **Bearing**: **not yet exploited.** `RETRIEVAL_LIST.md` flags this survey
  as the source of vocabulary for describing this project's mechanism as a
  pheromone-reinforced random walk rather than canonical ACO (no objective
  function; pheromone grows from traversal alone). The abstract confirms the
  survey covers the right branch; which sections and theorems actually
  transfer requires reading the full text - which is open and free, so this
  is the next natural retrieval, not something blocked by access.

---

## P3-13. Qin, Ling; Chen, Yixin; Pan, Yi; Chen, Ling (2006). *A novel approach to phylogenetic tree construction using stochastic optimization and clustering.*

- **Venue**: journal - *BMC Bioinformatics* 7(Suppl 4):S24. BioMed Central
  (fully open-access publisher, CC-BY license).
- **Identifier**: DOI 10.1186/1471-2105-7-S4-S24.
- **Retrieved**: full text (bmcbioinformatics.biomedcentral.com /
  link.springer.com mirror, no paywall, no login - found via a Google Scholar
  search the maintainer asked to be run in-browser, then fetched directly).
- **Depth**: read in full.
- **Answers**: not one of the three digraph-line targets (A3-A5) itself, but
  by an overlapping author group (Ling Chen is the last author here, as on
  A3-A5) and describing, in complete mathematical detail, the same
  construction those three papers' abstracts only summarise. Verbatim
  structure: a weighted digraph is built where vertices are the objects to be
  clustered and edge weights are an "acceptance rate" between object pairs
  (their own term - matches A3-A5's abstracts exactly); ants traverse the
  digraph and deposit pheromone on traversed edges per the standard ACO
  evaporate-then-increment update (Eq. 2 in the paper, tau_ij(t+1) = rho *
  tau_ij(t) + delta_tau_ij); after 50 iterations, edges with pheromone below
  a threshold epsilon are omitted from the digraph, and the **strong
  connected components of what remains are the clusters** - the read-out
  step is identical, in words and structure, to A3-A5's abstracts. Where this
  paper diverges from a pure Kang&Choi/A3-A5-style method: the clusters
  produced this way become **candidate phylogenetic trees**, which a
  separate, second-stage genetic-algorithm-style loop (crossover, mutation,
  and "global pheromone updating operation according to the fitness value of
  the constructed phylogenetic trees") then optimises. So the outer loop of
  *this specific paper* is fitness/objective-driven - but that fitness
  operates on whole candidate trees, one level up from the digraph-threshold
  clustering step itself, which remains exactly the no-fitness,
  pheromone-accumulate-then-threshold mechanism the task is checking for.
- **Bearing**: this does not replace A3-A5 - it is a different paper, a
  different application (phylogenetics, not general data clustering), and it
  is not itself under `RETRIEVAL_LIST.md`'s Section A. But it is the
  **strongest indirect confirmation available of what A3-A5's abstracts only
  summarise**, from the same research group, fully open, with exact formulas.
  It closes most of the practical gap left by A3-A5 being paywalled: the
  digraph-pheromone-threshold-strong-connected-components mechanism, in
  complete technical detail, is now citable from an open primary source. It
  should be cited as itself (Qin, Chen, Pan & Chen 2006), not as a stand-in
  for A3-A5, and the caveat above (fitness enters one level up, over whole
  trees, not over the clustering step) should travel with any citation of it.

**Two further leads surfaced by the same Google Scholar query, not yet
verified against an index (per `RETRIEVAL_LIST.md`'s "a lead is not a
source" rule):**

- Tu, L.; Chen, L.; Shen, J. (2007). "Adaptive Clustering Algorithm by Ants'
  Optimization." *Journal of Systems Science & Information*. Seen only via
  Google Scholar snippet and an EBSCO openurl record; **no DOI found, not in
  Crossref** under this title/author search. Likely a further paper in the
  same digraph-clustering lineage (snippet: "Strong connected components of
  the final digraph are... adaptive clustering algorithm with ants'
  optimization on a digraph... whose pheromone value is less than a certain
  threshold"). Not retrieved; recorded so it is not rediscovered as new.
- Qin, L.; Luo, J.; Chen, Z.; Guo, J.; Chen, L. (2006). "Phylogenetic tree
  construction using self adaptive ant colony algorithm." First International
  Multi-Symposium on..., IEEE. Snippet is nearly identical to P3-13's own
  digraph/threshold/strong-connected-components description - likely a
  conference-length sibling or earlier version of P3-13, by an overlapping
  author list. Not retrieved; recorded, not conflated with P3-13.

**Update, pass 4 (2026-08-03): the maintainer searched their own university
library for both leads above (A8, A9) and found neither.** Per this
project's own "a lead is not a source" rule, that result was checked further
rather than taken as final, with two different outcomes:

- **A9 (Qin, Luo, Chen, Guo, Chen 2006) is real and better-specified than
  before.** A `WebSearch` this session found a matching IEEE Computer
  Society CSDL record - proceedings-article ID `04021071`, conference coded
  `ichit/2006` - and a fuller author list than previously recorded: **Ling
  Qin, Jianli Luo, Zhimin Chen, Jing Guo, Ling Chen, and Yi Pan** (six
  authors, not five - `Yi Pan` was missing from the pass-3 record). The
  CSDL page itself would not render its metadata to this session's fetch
  tool (client-rendered shell, same failure mode as other IEEE/ACM pages
  this project has hit before) and Crossref/DBLP queries for it returned
  empty, so the DOI is still not confirmed - but the paper's existence and
  full author list are now corroborated independently of the original
  Google Scholar snippet. **The maintainer's library search likely missed it
  because the recorded venue/author list was incomplete, not because the
  paper doesn't exist.** Worth a second library attempt with the corrected
  author list and the CSDL proceedings-article ID above.
- **A8 (Tu, Chen, Shen 2007) could not be corroborated by anything beyond
  the original Google Scholar snippet.** `WebSearch` (plain and in Chinese,
  since "Journal of Systems Science and Information" is the English name of
  a Chinese journal) and a Crossref bibliographic-query both returned
  nothing matching this title/author combination. Combined with the
  maintainer's own library miss, and pass 3's note that it was already
  "not in Crossref," this is now a **materially weaker lead than A9** - the
  same "lead is not a source" caution this project applied to the four
  unconfirmed CyberLeninka titles in Section G. **Recommendation: do not
  spend further library time chasing A8 unless a more specific citation
  (a DOI, or a CNKI/Chinese-database record) surfaces first.**

---

## Addendum: CyberLeninka and Google Scholar opened without CAPTCHA in this session

The maintainer asked whether Chrome could reach CyberLeninka and Google
Scholar directly (having been blocked by CAPTCHA in pass 1 and refused by a
browser-extension navigation allowlist in pass 2). In this session, both
opened normally - no CAPTCHA, no allowlist refusal.

**Google Scholar** immediately surfaced P3-13 above and the two further leads
just listed, none of which had turned up in the OpenAlex/Crossref/IEEE
sweeps of passes 2 and 3. This is a genuine gap in earlier passes' database
coverage, not a duplicate confirmation - worth noting for future searches:
Google Scholar's ranking surfaced author self-citations and related
applications (phylogenetics) that field-restricted API queries missed
because they don't share exact terminology with the original query.

**CyberLeninka**, searched directly, returned real results for a fresh query
(6 hits on `муравьиная колония кластеризация феромон порог`, none a close
mechanism match - general ACO/swarm-intelligence applications, listed in
`SEARCH_LOG.md`). **None of the four titles pass 1 recorded as "surfaced by
CyberLeninka" could be found by searching for them directly** - not the full
title, not a shortened core phrase. This does not prove they don't exist
(CyberLeninka's search may not be exhaustive, and titles can be mistyped),
but it is a materially different situation from "blocked by CAPTCHA": pass 1
never actually confirmed these four titles against the index either, only
against a general-purpose WebSearch tool's summary of what CyberLeninka
"surfaced" - the same "a lead is not a source" risk `RETRIEVAL_LIST.md`
already flags elsewhere. **These four should be treated as unconfirmed
leads, not as "known real papers blocked by CAPTCHA," until someone finds
them by browsing CyberLeninka directly rather than trusting the earlier
search summary.**

---

## Environment note for this pass

This session's fetch tool retrieved at least one document pass 2's
browser-based tool could not, from the identical URL, with no credential
involved either time: `eprints.bournemouth.ac.uk/20910/1/Boryczka2009.pdf`
(P3-2) succeeded here on the first attempt after failing twice in pass 2
("Socket is closed", `curl` exit 000 - connection-level failures, not
access-control ones). IEEE Xplore document pages
(`ieeexplore.ieee.org/document/*`) and ResearchGate publication pages, by
contrast, returned empty, client-rendered shells to this session's fetch
tool on every attempt (A3 re-check, P3-4) - consistent with those specific
pages needing JavaScript execution rather than being access-blocked.
Unpaywall, Crossref and the Semantic Scholar Graph API were reachable
throughout this pass and did most of the verification work; no CAPTCHA was
encountered and no credential was entered anywhere.

## P3-12. Zelnik-Manor, Lihi & Perona, Pietro (2004). *Self-Tuning Spectral Clustering.*

- **Venue**: conference - *Advances in Neural Information Processing Systems*
  17 (NIPS 2004).
- **Identifier**: no DOI. Free, official host: `papers.nips.cc/paper/2004/hash/40173ea48d9567f1f393b20c855bb40b-Abstract.html`,
  full text PDF at `proceedings.neurips.cc/paper_files/paper/2004/file/40173ea48d9567f1f393b20c855bb40b-Paper.pdf`.
- **Retrieved**: full text (PDF, fetched directly from the official NeurIPS
  proceedings mirror - no login, no paywall). **This entry was never actually
  blocked**; `RETRIEVAL_LIST.md`'s `[lead]` status reflected only that no DOI
  exists for it, not that it was inaccessible - it had simply not been fetched
  in an earlier pass.
- **Depth**: read in full.
- **Answers**: proposes a per-point local scaling parameter sigma_i (distance
  to the K-th nearest neighbour, K=7 in their experiments) in place of a
  single global scale for the spectral affinity matrix, so that clusters at
  different densities/scales are handled without hand-tuning; and a second
  method that estimates the number of clusters automatically by rotating the
  top eigenvectors of the normalized affinity matrix to align them with the
  canonical coordinate axes, choosing the largest group count with minimal
  alignment cost.
- **Bearing**: relevant to this project's own threshold-selection stage as a
  worked example of "let the data set its own local scale/cut rather than a
  single global parameter" - a different mechanism (spectral eigen-alignment,
  not a pheromone histogram), but the same underlying design move Otsu (P2-5)
  and this project's own `find_threshold` make: replace a hand-tuned global
  constant with something computed from the data's own structure. Useful as a
  second citation, alongside Otsu, for "automatic parameter selection is an
  established value in this kind of pipeline," not as a structural relative
  of the clustering mechanism itself.

---

**PDFs were not saved to `literature/pdf/` this pass.** The full texts of
P3-1 (arXiv:1303.4711) and P3-2 (eprints.bournemouth.ac.uk) were read via this
session's fetch tool, which returns extracted text, not the underlying file.
This session's separate shell environment sits behind a network allowlist
that blocks `arxiv.org` directly (`curl` returns HTTP 403,
`X-Proxy-Error: blocked-by-allowlist`), so the two PDFs could not be
downloaded to disk from here. Both are freely open, no login: `arxiv.org/pdf/1303.4711`
→ `he2013_maba.pdf`, and `eprints.bournemouth.ac.uk/20910/1/Boryczka2009.pdf`
→ `boryczka2009_aca.pdf`, per the naming rule at the bottom of
`RETRIEVAL_LIST.md`. Saving them is a two-download task for the maintainer,
not a retrieval question.

---

# Pass 4 - 2026-08-03

## READ THIS FIRST (pass 4)

**Source: the maintainer's own university library, not a web query.** Eight
PDFs were placed in `tmp/pdf/` this pass, retrieved by the maintainer directly
from institutional access, following the priority order this project handed
back after pass 3. This pass's job was to identify each file (filenames are
**not reliable** - see below), read it in full, and record it. All eight were
opened and read directly in this session; nothing here is restated from an
earlier pass's description.

**The single biggest finding this pass: A3 and A4 are, to a first
approximation, the same paper.** Full text of both is now in hand
(`lingchen2005.pdf` = A3, `chen2005.pdf` = A4), and they share: the identical
three authors (Chen, Tu, Chen), the same year (2005), the same algorithm
(`Ant-Cluster`, definitions 1-4, equations for acceptance rate/probability
function/heuristic/pheromone update/adaptive alpha-beta all numerically
identical up to renumbering), and - the clinching detail - **the exact same
experimental result tables, to the decimal** (Table 1's 300/600-item error
rates and timings; Table 2's Glass results; Table 3's Soybean results are
byte-for-byte identical between the two papers). What differs is only the
venue (ICMLC 2005 vs. ICNC 2005, i.e. two different 2005 conferences), the
title ("Data clustering by ant colony on a digraph" vs. "A Novel Ant
Clustering Algorithm with Digraph"), and cosmetic prose rewording. This reads
as one experiment published twice, not two independent confirmations. **This
is a question for the maintainer** (see `QUESTIONS.md`), not something
resolved here: whether to cite both, cite one and note the duplicate, or treat
"the Chen/Tu/Chen digraph line" as two contributions (A3=A4, and A5) rather
than three.

**Filenames in `tmp/pdf/` do not match paper identity.** Confirmed by reading,
not inferred:
- `lingchen2005.pdf` → **A3** (not A5, despite the name suggesting "Ling
  Chen 2005" generically)
- `chen2005.pdf` → **A4** (not A3, despite the name)
- `chen2006.pdf` → **A5** (the paper is dated 2005 conference / 2006
  Springer print, so the filename's year is defensible, but it is not the
  same paper as `chen2005.pdf`)
- `VX-001986_30-11-2016_11-27-20_abbyy.pdf` → **B1** (an ABBYY OCR scan
  filename, no relation to the paper's own identity)
- `fred2005.pdf` → Fred & Jain 2005 (this one's filename does match)
- `boryczka2013.pdf`, `campello2013.pdf`, `campello2015.pdf` → filenames match

Second major finding: **B1 (Deneubourg et al. 1991) is now full text**,
closing a gap that survived passes 1-3 unresolved ("NOT retrieved," "lead,
print"). Confirms from the primary source, not second-hand, that the
ancestral mechanism has no pheromone of any kind.

---

## P4-1. Chen, Ling; Tu, Li; Chen, Hong-Jian (2005). *Data clustering by ant colony on a digraph.* [FULL TEXT - upgrades P2-2]

- **Venue**: conference - Proceedings of the Fourth International Conference
  on Machine Learning and Cybernetics (ICMLC 2005), Guangzhou, China, 18-21
  August 2005, pp. 1686-1692. IEEE. Print ISBN 0-7803-9091-1.
- **Identifier**: DOI 10.1109/ICMLC.2005.1527216 (unchanged from P2-2).
- **Retrieved**: full text, PDF supplied by the maintainer from their
  university library (file `lingchen2005.pdf` in `tmp/pdf/` - the filename
  does **not** match the paper; confirmed by reading the header/footer on
  every page, which reads "Proceedings of the Fourth International Conference
  on Machine Learning and Cybernetics, Guangzhou, 18-21 August 2005").
- **Depth**: read in full, all 7 pages, including every numbered equation,
  the full pseudocode listing, all three result tables, and the full
  reference list.
- **Answers**:
  - Q1 (what deposits pheromone, by what criterion): every ant that traverses
    edge (i,j) deposits Δτ_ij^k = Q·Sim(i,j) (eq. 3.10), else 0. There is
    **no fitness/quality term tied to a complete tour or solution** - the
    increment is a fixed function of the static similarity of the two data
    points the edge connects, not of anything about the ant's path as a
    whole. Any ant that passes the edge deposits the same amount; "selection"
    only happens through the probability function (eq. 3.6-3.7), which biases
    which edges get walked, not how much gets deposited once walked.
  - Q2 (result = solution or environment state): the environment. Clusters
    are read off as the strong connected components of the pheromone digraph
    after thresholding (algorithm line 20) - no ant's individual path is ever
    treated as a candidate solution.
  - Q3 (parameters, transferred/not/N-A): m = n/2 ants; ρ = 0.05 (evaporation,
    eq. 3.9); q0 = 0.95 (exploit/explore split, eq. 3.6); Q (deposit scale
    constant, unspecified numeric value in the text); α, β - **not fixed**,
    adaptively recomputed every 10 iterations from the pheromone-distribution
    weight ψ (eq. 3.11-3.13: α = e^(-ψ), β = 1/α); a **list** of increasing
    thresholds {g0, g1, ... gh}, one new threshold applied every 10
    iterations (not a single global threshold applied once); maxnum = 500
    iterations. Initial pheromone τ_ij(0) is **not zero** (departure from
    classical ACO) - it is set to accept(i,j) itself (eq. 2.4 in the
    original numbering here, "acceptance rate"), which the paper argues
    removes the usual ACO cold-start problem.
- **Bearing**: this is the fullest and clearest statement of the mechanism
  this project's own pheromone-threshold-clustering idea most closely
  resembles - digraph, per-edge pheromone scaled by a static similarity, no
  objective/fitness function anywhere, strongly connected components as the
  read-out. The paper explicitly cites Deneubourg (P4-4/B1, their ref [14])
  and Lumer-Faieta (their ref [15]) as the prior "corpse-piling" lineage it
  is *not* building on directly - it presents Ant-Cluster as a departure from
  that branch (graph/pheromone-based, not grid/spatial-based). **This closes
  the single most-flagged gap in the entire retrieval list.** See P4-2 for
  the near-duplicate finding that qualifies how this should be cited.

---

## P4-2. Chen, Ling; Tu, Li; Chen, Hongjian (2005). *A Novel Ant Clustering Algorithm with Digraph* (A3CD). [FULL TEXT - upgrades P2-3]

- **Venue**: conference - Advances in Natural Computation (ICNC 2005),
  Lecture Notes in Computer Science vol. 3611, pp. 1218-1228. Springer Berlin
  Heidelberg, 2005. Eds. L. Wang, K. Chen, Y.S. Ong.
- **Identifier**: DOI 10.1007/11539117_163 (unchanged from P2-3).
- **Retrieved**: full text, PDF supplied by the maintainer from their
  university library (file `chen2005.pdf` in `tmp/pdf/` - again, the filename
  does not disambiguate this from P4-1; confirmed by reading the running
  header "L. Chen, L. Tu, and H. Chen" and the page footer "1218-1228, 2005").
- **Depth**: read in full, all 11 pages (originally hit a page-count limit on
  the reading tool; re-read with an explicit page range).
- **Answers**: **identical mechanism to P4-1/A3** - same Definitions 1-4
  (difference, similarity, acceptance rate - eq. 2.1-2.5 here vs. 3.1-3.5 in
  P4-1, same formulas), same probability function (2.4-2.5, wording
  identical to P4-1's), same heuristic function η_ij = Sim(i,j), same
  pheromone update Δτ_ij^k = Q·Sim(i,j) (eq. 2.9), same adaptive α = e^(-ψ),
  β = 1/α (eq. 2.13). Q1/Q2/Q3 answers are therefore the same as P4-1's,
  verbatim.
  - **The experimental section is, as far as this session could tell,
    identical in its numeric content to P4-1's**: the same five-type/50-item
    benchmark (Figs. 1-4, same normal-distribution parameters), the same
    Table 1 (300/600-item synthetic data: LF 0/135.08s, 1.98%/322.55s;
    K-Means 0/112.30s, 2.57%/243.12s; Ant-Cluster 0/53.27s, 0.38%/101.73s),
    the same Table 2 (Glass, 214 instances/9 attributes/6 classes: K-Means
    5.67%/92.42s, LF 4.68%/115.54s, Ant-Cluster 3.65%/40.24s), and the same
    Table 3 (Soybean, 47 instances/35 attributes/4 classes: K-Means
    5.27%/29.37s, LF 6.83%/38.25s, Ant-Cluster 1.66%/9.33s). These numbers
    match P4-1's Tables 1-3 to the last decimal place.
- **Bearing**: **this is the finding flagged at the top of this pass.** A3
  and A4 are not two independent statements of the mechanism - they are one
  experiment, reported at two 2005 venues under two titles, by the same three
  authors. This does not change anything about what the mechanism *is* (the
  Q1/Q2/Q3 answers are unaffected), but it changes what "three Chen/Tu/Chen
  papers exist" should be taken to mean for a novelty/prior-art argument: it
  is closer to two distinct contributions (this shared experiment, and A5's
  separate dynamic-database extension) than three. **Flagged to the
  maintainer in `QUESTIONS.md` - not resolved here.**

---

## P4-3. Chen, Ling; Tu, Li; Chen, Yixin (2006). *An Ant Clustering Method for a Dynamic Database.* [FULL TEXT - upgrades P2-4]

- **Venue**: book chapter - D.S. Yeung et al. (Eds.), *ICMLC 2005*, Lecture
  Notes in Artificial Intelligence vol. 3930, pp. 169-178. Springer-Verlag
  Berlin Heidelberg, 2006. (Conference held 2005; Springer print dated 2006 -
  both years appear on the paper's own first page.)
- **Identifier**: DOI 10.1007/11739685_18 (unchanged from P2-4).
- **Retrieved**: full text, PDF supplied by the maintainer from their
  university library (file `chen2006.pdf` in `tmp/pdf/` - this is the one
  filename in the batch that is roughly defensible, though it names the
  Springer print year, not the conference year).
- **Depth**: read in full, all 10 pages.
- **Answers**: same core mechanism as P4-1/P4-2 (Definitions 1-4, probability
  function, heuristic, pheromone update, adaptive α/β - equations 2.1-2.11
  here, same formulas). Q1/Q2/Q3 as in P4-1. The **third author differs**
  (Yixin Chen, Washington University in St. Louis, in place of Hong-Jian
  Chen) and this paper adds a genuinely new fourth section absent from P4-1/
  P4-2: **Section 4, "Maintaining the Clustering in a Dynamic Data Base."**
  Insertions/deletions to the database are not re-clustered from scratch;
  a running `change_num` counter triggers a full re-cluster only once it
  exceeds a threshold `thresh`, and in between, Algorithm 2 patches the
  existing digraph directly (remove a vertex and its edges on deletion; on
  insertion, compute the new record's distances to existing records, assign
  it to the cluster with least average distance, and add it as a new vertex
  with directed edges to the rest of the graph). The stated justification is
  that most existing pheromone information remains valid after a small
  change, so a full re-run is wasteful.
  - The Table 1 experimental numbers (300/600-item synthetic data) are
    **again identical** to P4-1 and P4-2's Table 1, to the decimal. This
    paper does **not** repeat the Glass/Soybean tables (P4-1/P4-2's Tables 2-
    3) - it stops after Table 1 and moves directly to the dynamic-database
    section.
- **Bearing**: this is the one paper of the three with a genuinely distinct
  contribution (incremental maintenance under insert/delete), not a
  restatement of P4-1/P4-2. If this project's own mechanism has (or will
  have) anything to say about updating a clustering incrementally rather than
  recomputing from scratch, this is the direct prior-art citation for that
  specific claim - not P4-1 or P4-2.

---

## P4-4. Deneubourg, J.-L.; Goss, S.; Franks, N.; Sendova-Franks, A.; Detrain, C.; Chrétien, L. (1991). *The Dynamics of Collective Sorting: Robot-like Ants and Ant-like Robots.* [FULL TEXT - upgrades P2-13, closes a gap open since pass 1]

- **Venue**: conference - Proceedings of the First International Conference
  on Simulation of Adaptive Behavior: From Animals to Animats 1 (SAB90-1),
  pp. 356-365. MIT Press, Cambridge, MA, 1991. Eds. J.A. Meyer, S. Wilson.
- **Identifier**: no DOI (matches P2-13; pre-DOI-era proceedings volume).
- **Retrieved**: full text, PDF supplied by the maintainer from their
  university library (file `VX-001986_30-11-2016_11-27-20_abbyy.pdf` in
  `tmp/pdf/` - an ABBYY FineReader OCR output filename, evidently a scanned
  library copy; confirmed by reading the title page, which carries the
  handwritten annotation "In 'Simulation of Animal Behaviour: From Animals to
  Animats' J.A. Meyer and S. Wilson (eds.), MIT Press").
- **Depth**: read in full, all 8 pages. OCR quality is imperfect - French
  diacritics and some ligatures are garbled throughout (e.g. "générâtes" for
  "generates", "expriment" for "experiment") - but the body text, equations,
  and figures are legible and the argument is intact.
- **Answers**: Q1/Q2/Q3 do not apply in ACO-family form - **there is no
  pheromone, no digraph, and no graph at all.** The mechanism: ant-like
  robots (ALRs) move randomly on a 2D grid of points. Each ALR keeps only a
  short-term memory of the last m objects it has personally encountered (not
  a shared field). The probability of *picking up* an object is
  p(pick up) = (k+/(k+ + f))^2, and the probability of *putting down* a
  carried object is p(put down) = (f/(k- + f))^2, where f is the fraction of
  the last m encounters that were objects of the same type (eq. in section
  2) - i.e., an object is picked up when it is locally rare and put down
  when it is locally common. This is a purely local, individually-estimated
  density signal, sampled from personal history, not laid down in the
  environment for others to read - the opposite design choice from
  pheromone. A continuous PDE model (their eqs. 1-4, section 4) formalizes
  the same dynamic and shows the clustered state emerges as a Turing-type
  instability of the homogeneous distribution once density crosses a
  threshold. Validated against both simulation (Figs. 1, 3, 4) and real ant
  colonies (Pheidole pallidula corpse-piling, Fig. 2; Leptothorax
  unifasciatus larva-sorting, Fig. 5).
- **Bearing**: this is the true root of the "ants + clustering" citation
  tree - the paper every other Section B source (Lumer-Faieta 1994, Handl &
  Meyer 2007, Boryczka 2009/2013) cites as their starting point, and the
  paper P4-1/P4-2/P4-3 themselves cite (their ref [14]/[22]) as the lineage
  they are explicitly *not* extending. Confirms, now from the primary text
  rather than second-hand, that "ant colony clustering" splits cleanly into
  two unrelated mechanisms from the start: this memory/density-based
  grid-relocation branch (Section B, not this project) and the
  pheromone/digraph/threshold branch (Section A, P4-1/P4-2/P4-3, closest to
  this project). No pheromone appears anywhere in this paper, confirming
  Boryczka 2009's own statement (P3-2) that "different communication
  strategies via pheromone" was still *future work* as of nearly twenty years
  after this paper.

---

## P4-5. Fred, Ana L.N. & Jain, Anil K. (2005). *Combining Multiple Clusterings Using Evidence Accumulation.* [FULL TEXT - upgrades P3-10, closes the gap flagged as "the most underrated line" in Section C]

- **Venue**: journal - *IEEE Transactions on Pattern Analysis and Machine
  Intelligence* 27(6), 835-850, June 2005.
- **Identifier**: DOI 10.1109/tpami.2005.113 (unchanged from P3-10).
- **Retrieved**: full text, PDF supplied by the maintainer from their
  university library (file `fred2005.pdf` in `tmp/pdf/`; 16 pages, initially
  hit a page-count limit on the reading tool, re-read with an explicit page
  range).
- **Depth**: read in full.
- **Answers**: not ACO-family, Q1/Q2/Q3 do not apply. The paper's mechanism,
  now confirmed against the primary text rather than restated from this
  project's prior characterisation (per P3-10's own flag): given N different
  clustering partitions of the same n patterns (a "clustering ensemble" -
  produced by running K-means repeatedly with different k or different
  initializations), build an n×n **co-association matrix** C(i,j) = n_ij/N,
  where n_ij counts how often patterns i and j land in the same cluster
  across the N partitions (eq. in section 3.2). This matrix is then itself
  treated as a new similarity measure between patterns, and a single-link
  (or average-link) hierarchical clustering is run over it; the final
  partition is chosen from the resulting dendrogram by the "cluster
  lifetime" criterion (the threshold range over which a given number of
  clusters persists, section 3.3). A nearest-neighbour approximation (p
  nearest neighbours per pattern, Table 1's algorithm) avoids the full
  O(n²) matrix in practice. Extensive comparison against K-means, single-
  link, complete-link, spectral clustering, and three graph-based ensemble
  methods (CSPA/HPGA/MCLA, Strehl & Ghosh) across nine real/synthetic
  datasets (Table 2).
- **Bearing**: confirms the project's own prior characterisation of this
  paper (co-association matrix, then threshold/component-style read-out) was
  correct - this is no longer resting on memory, per `LITERATURE.md`'s core
  rule. The structural parallel this project should draw carefully: co-
  association counts (how often two patterns are grouped together across
  many *partitions*) versus this project's own pheromone (how much two
  *directly connected* items reinforce a single edge across many ant
  passes) are analogous but not identical accumulation mechanisms - both are
  "let repeated evidence build up a pairwise strength, then threshold and
  take connected structure," but Fred & Jain's evidence source is an
  ensemble of independent full clusterings, not a single stochastic process
  walking a graph. Worth citing as the clearest non-ACO articulation of
  "accumulate pairwise co-occurrence evidence, then threshold" as a general
  design pattern - this project's mechanism is one instance of that pattern,
  not the only one.

---

## P4-6. Boryczka, Urszula (2013). *Corrigendum to "Finding groups in data: Cluster analysis with ants"* [Appl. Soft Comput. 9(1) (2009) 61-70]. [FULL TEXT - upgrades P3-3]

- **Venue**: journal - *Applied Soft Computing*, vol. 13 (2013), p. 4229.
  Elsevier.
- **Identifier**: DOI 10.1016/j.asoc.2013.07.012 (unchanged from P3-3).
- **Retrieved**: full text, PDF supplied by the maintainer from their
  university library (file `boryczka2013.pdf` in `tmp/pdf/`; one page, as
  P3-3 already inferred from length alone).
- **Depth**: read in full (it is one page).
- **Answers**: the corrigendum's entire content, verbatim: "The author wants
  to add an author to the following publication: The correct authorship for
  this article should be Urszula Boryczka and Marcin Budka. The author would
  like to apologise for any inconvenience caused." Nothing else - no
  technical correction, no retraction of any result, no change to the
  paper's content. Budka is affiliated with Bournemouth University, UK.
- **Bearing**: resolves P3-3's open flag completely. The corrigendum is
  purely an authorship correction (a co-author omitted from the original
  2009 print), not a substantive correction to the ACA/ACAM method or
  results described in P3-2. Any citation of Boryczka 2009 (P3-2) for this
  project's purposes should now credit both Boryczka and Budka as authors.
  No bearing on this project's own mechanism or novelty question beyond
  correct attribution.

---

## P4-7. Campello, Ricardo J.G.B.; Moulavi, Davoud; Sander, Joerg (2013). *Density-Based Clustering Based on Hierarchical Density Estimates* (HDBSCAN). [FULL TEXT - upgrades P3-9]

- **Venue**: conference - Pacific-Asia Conference on Knowledge Discovery and
  Data Mining (PAKDD 2013), Part II, Lecture Notes in Artificial Intelligence
  vol. 7819, pp. 160-172. Springer-Verlag Berlin Heidelberg, 2013.
- **Identifier**: DOI 10.1007/978-3-642-37456-2_14 (unchanged from P3-9).
- **Retrieved**: full text, PDF supplied by the maintainer from their
  university library (file `campello2013.pdf` in `tmp/pdf/`; 13 pages).
- **Depth**: read in full.
- **Answers**: not ACO-family, Q1/Q2/Q3 do not apply - no pheromone, no
  agents, no stochastic construction process at all. HDBSCAN redefines
  DBSCAN (as "DBSCAN*") on core-object connectivity alone (no border
  objects), then builds a **mutual reachability graph** - a complete graph
  where edge weight between two objects is
  max(d_core(x_p), d_core(x_q), d(x_p,x_q)) - and computes its minimum
  spanning tree, extended with a self-loop per vertex weighted by that
  vertex's own core distance. The complete density-based hierarchy is
  obtained by removing MST edges in decreasing weight order (a divisive,
  single-linkage-equivalent construction - Proposition 1 in the paper proves
  this equivalence formally), simplified to a small tree of only the levels
  where a cluster genuinely splits or disappears (not just shrinks). A
  cluster "stability" measure based on excess-of-mass (eq. 3, integrating
  1/ε_min - 1/ε_max over each cluster's member lifetimes) is then optimized,
  via a bottom-up dynamic-programming pass over the tree (Algorithm 3, O(κ)
  in the number of clusters), to extract the single globally-optimal flat
  partition. Overall complexity O(a·n²) (a = dimensionality). Benchmarked
  against AUTO-HDS and OPTICS(AutoCl) on 9 real datasets plus 2 image-
  descriptor collections, outperforming both on ARI/F-score in most cases.
- **Bearing**: comparison-set entry (ROADMAP.md phase 4), not a structural
  relative - deterministic MST-based construction and an exact,
  globally-optimal extraction via dynamic programming, versus this project's
  stochastic multi-agent construction with a single, hand-set threshold.
  Useful as the sharpest possible contrast for the "how is the read-out
  decided" question in this project's own methodology section: HDBSCAN
  proves a global optimum is computable in low-order polynomial time for its
  stability objective, which is a fair challenge this project's own
  threshold-selection method should be able to answer (why not compute an
  analogous optimal cut, rather than a single hand-tuned threshold?).

---

## P4-8. Campello, Ricardo J.G.B.; Moulavi, Davoud; Zimek, Arthur; Sander, Joerg (2015). *Hierarchical Density Estimates for Data Clustering, Visualization, and Outlier Detection.* [NEW - journal companion to P4-7/P3-9]

- **Venue**: journal - *ACM Transactions on Knowledge Discovery from Data*
  (TKDD) 10(1), Article 5, July 2015, 51 pages.
- **Identifier**: DOI 10.1145/2733381.
- **Retrieved**: partial, PDF supplied by the maintainer from their
  university library (file `campello2015.pdf` in `tmp/pdf/`; 51 pages total -
  the reading tool's per-request page cap was used to read pages 1-20 only).
- **Depth**: **skimmed (20 of 51 pages)** - introduction, related work,
  DBSCAN*/HDBSCAN* redefinition (sections 2-3, matches P4-7 exactly, same
  algorithm and propositions), hierarchy simplification, computational
  complexity, visualization (reachability/silhouette plots), and the start
  of the cluster-stability/optimal-extraction section (5.1, matches P4-7's
  section verbatim with figure numbers renumbered). **Not yet read**:
  section 5.2 onward (the semi-supervised extraction variant using
  should-link/should-not-link constraints - new relative to P4-7), section 6
  (GLOSH, the new global-and-local outlier detection method built on the
  same hierarchy - the paper's other major addition beyond P4-7), and the
  experimental section.
- **Answers**: as far as read, identical to P4-7 for the core HDBSCAN*
  algorithm - no pheromone, no ACO-family answers apply. The two genuinely
  new contributions this journal version adds beyond the PAKDD paper (per
  its own section 1.3, "Contributions") are the semisupervised cluster-
  extraction framework and GLOSH; neither has been read this pass.
- **Bearing**: same comparison-set role as P4-7. Recorded as a **partial**
  read rather than "not retrieved" so a future pass does not re-fetch it -
  finishing pages 21-51 (semi-supervised extraction and GLOSH) is a
  straightforward follow-up if the maintainer wants the outlier-detection
  angle for the comparison chapter, but is not needed for anything this
  project currently claims.

---

## P4-9. Pemantle, Robin (2007). *A Survey of Random Processes with Reinforcement.* [PARTIAL - upgrades P3-11]

- **Venue**: journal - *Probability Surveys*, vol. 4 (2007), pp. 1-79.
  Institute of Mathematical Statistics.
- **Identifier**: DOI 10.1214/07-PS094; arXiv:math/0610076 (Gold OA, no
  login - the projecteuclid.org host P3-11 pointed to returned an Incapsula
  bot-detection challenge this session and was not pursued further, per this
  project's own rule against routing around access barriers; arXiv served the
  identical paper without any such barrier).
- **Retrieved**: partial. Fetched directly from arXiv this session (not from
  the maintainer's library - a same-day, unprompted follow-up, since this was
  the one remaining item in the retrieval list that was openly accessible but
  had never actually been opened). The fetch tool's own extraction was cut
  off partway through - the saved text runs to page 35 of 79, ending mid-
  Section 4.4 ("Learning"), not the full document.
- **Depth**: read, pages 1-35 of 79 (Introduction; Section 2, "Overview of
  models and methods" in full, including the formal definitions of ERRW and
  VRRW; Section 3, "Urn models: theory," in full; Section 4, "Urn models:
  applications," through 4.4). **Not read**: the remainder of Section 4
  (4.5-4.7: evolutionary game theory, agent-based modeling, miscellany), and
  critically, **Section 5, "Reinforced random walk" (pp. 48-55)** - the
  section on ERRW/VRRW on general (non-tree) graphs, which is the part of
  this survey most directly relevant to this project's own mechanism. Also
  unread: Section 6 (continuous processes, self-avoiding walks).
- **Answers**: not ACO-family, Q1/Q2/Q3 do not apply directly, but this
  survey supplies exactly the vocabulary `RETRIEVAL_LIST.md` flagged it for.
  The formal definition of **edge-reinforced random walk (ERRW)**, due to
  Coppersmith & Diaconis [CD87] (eq. 2.1-2.3 in the survey): a walk on a
  locally finite graph where the transition probability from the current
  vertex to a neighbor is proportional to a_n(x,y) = 1 + (number of times
  edge {x,y} has been traversed so far, in either direction). **Vertex-
  reinforced random walk (VRRW)**, due to Pemantle himself [Pem88b] (eq.
  2.4), is the analogous scheme reinforcing by visits to the destination
  vertex rather than traversals of the edge. Both are presented as a
  departure from plain generalized Pólya urns precisely because, on a graph
  with cycles, the reinforced walk cannot be decomposed into independent or
  even generalized Pólya urn processes - "one may find embedded urn processes
  that interact nontrivially" (p.7). For trees specifically, Lemma 2.4 (from
  Pemantle's own 1988 thesis) shows the occupation measures at each vertex,
  sampled at return times, *do* form independent Pólya urns - a special-case
  simplification not available on general graphs.
- **Bearing**: this is the load-bearing citation `RETRIEVAL_LIST.md` already
  anticipated - ERRW, not classical ACO, is the correct formal family for
  what this project's mechanism actually is: a walk (or population of walks)
  whose transition probabilities are driven purely by accumulated traversal
  counts on edges, with no objective function, no candidate-solution
  evaluation, and no fitness. That is precisely ERRW's definition, adapted to
  a weighted/directed graph and closed off by a threshold-and-components
  read-out step that is specific to this project (ERRW itself has no
  clustering read-out - it is studied purely for its own long-run behavior,
  e.g. whether the walk localizes on a finite set of edges). **This still
  needs Section 5 to be complete**: that section is where the survey's own
  treatment of ERRW/VRRW *beyond trees* lives, including (per the table of
  contents) "5.2 Other edge-reinforcement schemes" and open problems - likely
  the single most relevant few pages in the entire 79-page survey for this
  project's own theory chapter, and they are exactly the pages not yet read.
  **Flagged as the natural next step, not urgent** - finishing pages 36-55
  (roughly) closes this properly; the vocabulary already extracted (ERRW,
  VRRW, the Coppersmith-Diaconis and Pemantle 1988 citations) is usable now.

**Follow-up same day: the page-35 cutoff is a tooling limit, not a paywall,
and does not resolve by retrying.** Re-fetching `arxiv.org/pdf/math/0610076`
(including with a `#page=36` fragment, which has no effect on a text
extractor) returned byte-for-byte the same truncated output (98,723
characters, 1,758 lines, ending mid-page-35) both times. The bash sandbox
cannot reach `arxiv.org` directly to download the PDF for page-ranged
reading (`blocked-by-allowlist` via the sandbox's proxy, same restriction
noted in pass 3). Semantic Scholar's record points only back to the same
arXiv copy and the Incapsula-gated projecteuclid host - no third copy found.
**Getting pages 36-79 needs either the maintainer downloading the PDF
directly (arXiv has no bot-gate for a browser or a plain download) or a
future session whose fetch tool does not cap PDF extraction this way** -
this is not something the maintainer needs to search a library for, since
the paper itself is fully open.

---

## P4-10. Merkl, Franz & Rolles, Silke W.W. (2005). *Edge-Reinforced Random Walk on a Ladder.* [PARTIAL]

- **Venue**: journal - *The Annals of Probability* 2005, vol. 33, no. 6,
  pp. 2051-2093.
- **Identifier**: DOI 10.1214/009117905000000396; arXiv:math/0501137 (bronze
  OA per Unpaywall - a submitted-version copy, freely fetched, no barrier).
- **Retrieved**: partial. Fetched from arXiv this session (same-day follow-up
  to P4-9, unprompted - checking whether D1's own citations, D2/D3, were
  open before asking the maintainer to hunt them). The fetch tool's
  extraction again cut off partway through (856 lines / 67,579 characters,
  ending mid-Section 3.2 of 5) - the same tooling limit noted in P4-9, not a
  paywall.
- **Depth**: read, roughly the first third (Introduction; Section 1.1-1.2,
  the formal ERRW definition and both main theorems; Section 2.1, the
  random-walk-in-random-environment representation; start of Section 3). Not
  read: the bulk of the technical proof (remainder of Section 3, Sections 4
  "transfer operator technique," and 5 "proof of recurrence").
- **Answers**: not ACO-family. Gives the **general-graph** formal definition
  of ERRW (eq. 1.1-1.4): edge weights start at a constant a, a walker moves
  to a neighbor with probability proportional to the traversed edge's
  current weight, and every traversal increments that edge's weight by
  exactly 1 - i.e., pure count-based reinforcement, no similarity/quality
  scaling at all (contrast with this project's own mechanism, and with
  P4-1/P4-2/P4-3's Δτ = Q·Sim(i,j), both of which scale the increment by a
  static similarity rather than using a flat +1). Establishes that Diaconis
  posed ERRW recurrence/transience on Z^d as an open problem in the late
  1980s, still open for d≥2 as of this paper (2005); proves recurrence for
  one specific two-row "ladder" graph via a heavy machinery of Gibbs
  measures and transfer operators - this is very deep, narrow pure-math
  territory, not method engineering.
- **Bearing**: confirms Pemantle's survey vocabulary (P4-9) against a second,
  independent primary source, and sharpens one useful contrast: **classical
  ERRW reinforces by raw traversal count; this project's mechanism (and the
  whole Chen/Tu/Chen line) reinforces by count weighted by a fixed
  similarity value.** That distinction - "is the deposit uniform per
  traversal, or scaled by an external quality/similarity signal" - is a
  cleaner way to locate this project's mechanism relative to the
  reinforcement-random-walk literature than "ERRW" alone. The deep proof
  technique (Sections 3-5, unread) is unlikely to be load-bearing for a
  clustering methods chapter; what matters for citation purposes - the
  definition and the "recurrence is still open in d≥2" framing - is already
  in hand.

---

## P4-11. Merkl, Franz & Rolles, Silke (2011). *Correlation Inequalities for Edge-Reinforced Random Walk.* [NOT RETRIEVED THIS SESSION - access barrier, not a paywall]

- **Venue**: journal - *Electronic Communications in Probability*, vol. 16
  (2011), pp. 753-763. A fully open-access (Gold, CC-BY, diamond-model)
  journal per Unpaywall and DOAJ.
- **Identifier**: DOI 10.1214/ecp.v16-1683.
- **Retrieved**: attempted, not obtained. The only host (Unpaywall confirms
  no arXiv or repository mirror exists, unlike P4-9/P4-10) is
  `projecteuclid.org`, which returned an Incapsula bot-detection challenge
  to this session's fetch tool - the same barrier P4-9 hit for the Pemantle
  survey's own primary host. Not pursued further, per this project's own
  rule against routing around access barriers.
- **Depth**: not retrieved - title, venue, and abstract (from the WebSearch
  snippet, not the paper itself) only.
- **Answers**: none obtained directly. Per the search snippet only (**not
  verified against the primary text - do not cite beyond this caveat**): the
  paper proves correlation inequalities for linearly edge-reinforced random
  walk concerning the "first entry tree" (the tree of edges used to first
  reach each vertex) and the asymptotic time-fraction on particular edges,
  using FKG-type inequalities and negative association for determinantal
  processes.
- **Bearing**: unresolved. If the maintainer can reach projecteuclid.org
  directly (a normal browser session, not this tool's fetch path, may not
  trip the same bot-challenge), this is a short paper (11 pages) and a quick
  read. Not urgent - D1/P4-9 and D2/P4-10 already supply the vocabulary and
  the main open-problem framing this project needs; D3 would only add a
  further technical refinement.

---
---

# Pass 5 - 2026-08-03

## READ THIS FIRST (pass 5)

**Source: a second batch of PDFs the maintainer placed in `tmp/pdf/`,
partly from library retrieval and partly (by the maintainer's own account)
from Sci-Hub for the maintainer's own use.** This project did not use
Sci-Hub or any similar site itself at any point - the files simply arrived
in the shared folder, exactly as pass 4's library batch did, and were
identified by reading them, not by trusting filenames or by asking how they
were obtained. Eight distinct files (nine uploads, one exact duplicate:
`blum2007.pdf` / `blum2007 (1).pdf`) were found; all eight are now read and
recorded below.

**Second major reclassification finding this pass, on top of the A3=A4 one
from pass 4: A6 does not belong in Section A.** `RETRIEVAL_LIST.md` has
carried A6 (Chen, Xu, Chen 2004) under "Section A - direct predecessors of
the mechanism: pheromone on edges, a threshold, connected components" since
pass 2, on the strength of a secondhand description. The full text (P5-1,
below) has **no pheromone, no digraph, and no edges at all** - it is a
grid/agent density-and-activation-probability method in the Deneubourg/
Lumer-Faieta line, i.e. exactly the "ant-based clustering branch this work
is not" that Section B exists to describe. This is corrected in
`RETRIEVAL_LIST.md` below; nothing about the mechanism-novelty finding
itself changes, since A6 was never one of the three digraph papers (A3-A5)
that finding rests on - only its shelf location was wrong.

**A genuinely new category surfaces this pass: fitness-driven,
solution-construction ACO applied to clustering (P5-7, Zhao 2007).** Every
ACO-clustering paper read so far - Section A's digraph line, Kang & Choi,
Sadi et al. - either has no fitness function (Section A/D) or uses one only
in a separate post-processing stage (Sadi et al.'s modularity step). Zhao
2007 is different in kind: each ant constructs a *complete candidate
clustering* (an explicit object-to-cluster assignment string), the
assignment is scored by an explicit sum-of-squared-errors objective, and
only the best-scoring ant deposits pheromone, in proportion to
`1/objective`. This is classical Dorigo-style combinatorial ACO (the same
family as TSP/QAP solvers) retargeted at the clustering problem by treating
it as an assignment problem - structurally the polar opposite of this
project's own no-objective, no-constructed-solution mechanism. Recorded as
a new bucket, Section H, in `RETRIEVAL_LIST.md`.

---

## P5-1. Chen, Ling; Xu, Xiao-Hua; Chen, Yi-Xin (2004). *An Adaptive Ant Colony Clustering Algorithm.* [FULL TEXT - upgrades P2-10/A6, and reclassifies it]

- **Venue**: Proceedings of the Third International Conference on Machine
  Learning and Cybernetics (ICMLC 2004), Shanghai, 26-29 August 2004, pp.
  1387-1392. IEEE, ISBN 0-7803-8403-2.
- **Identifier**: no DOI captured from the PDF itself (pre-Crossref-DOI era
  for this venue); IEEE catalog number is on the first page but not
  transcribed as a separate field previously - see `RETRIEVAL_LIST.md` A6.
- **Retrieved**: full text, 6 pages, via the maintainer's own PDF
  (`tmp/pdf/An Adaptive Ant Colony Clustering Algorithm.pdf`).
- **Depth**: read in full.
- **Answers**:
  - This is **not** a pheromone/digraph method. It is the **Ants Sleeping
    Model (ASM)** combined with an **Adaptive Artificial Ants Clustering
    Algorithm (A⁴C)** - a two-dimensional-grid, agent-based method squarely
    in the Deneubourg (B1) / Lumer & Faieta (B2) lineage, which the paper's
    own reference list cites explicitly (refs 6 and 7) as the BM/LF
    ancestry it extends.
  - Mechanism: each data object is an "agent" placed on a 2D grid. A
    fitness function (Definition 5) is computed over a local
    neighbourhood: `f(agent_i) = 1/[(2s_x+1)(2s_y+1)] · sum_j alpha_i^2 /
    (alpha_i^2 + d(agent_i, agent_j)^2)`, summed over agents currently in
    the (2s_x+1)x(2s_y+1) window. An **activation probability** (Definition
    6), `p_a(agent_i) = cos^lambda(pi/2 · f(agent_i))`, decides whether the
    agent moves this step. Both `alpha` (the similarity scale) and `lambda`
    (the activation-curve steepness) are adapted during the run (eqs
    8-10), which is the paper's "adaptive" contribution over plain
    BM/Lumer-Faieta.
  - Q1 (pheromone/selection criterion) - **does not apply**: there is no
    pheromone variable anywhere in the algorithm. The closest analogue is
    the per-agent fitness `f(agent_i)`, which every agent computes for
    itself from its local neighbourhood, not a quantity deposited on
    edges by a subset of agents.
  - Q2 (solution vs. environment state): the result is the **spatial
    configuration of agents on the grid** after convergence (agents of the
    same "kind" physically clustered together) - an environment-state
    read-out, not a constructed solution string, and in that respect it
    resembles this project's own read-from-state approach more than Q1
    might suggest. But there is still no pheromone and no graph in the
    sense this project uses those terms.
  - Q3 (parameters and why): grid size (implicit, tied to dataset), window
    half-widths `s_x, s_y` (neighbourhood radius for the fitness sum),
    `alpha` (adapted, controls how sharply similarity falls off with
    distance), `lambda` (adapted, controls the activation-probability
    curve's steepness - higher lambda makes agents "settle" more
    decisively once locally satisfied). Tested on a synthetic 4-type
    random dataset and on Iris, benchmarked against Lumer-Faieta and
    (implicitly) a k-means-adjacent baseline; reports A⁴C reaching 1.31%
    error vs. LF's 4.45%, and 1.42s vs. LF's 56.81s runtime.
- **Bearing**: **A6's shelf location in `RETRIEVAL_LIST.md` Section A was
  wrong and is corrected in this pass.** This paper has no pheromone, no
  digraph, and no edge-threshold-into-components read-out - it belongs with
  B1/B2 as a Deneubourg/Lumer-Faieta descendant, not with A1-A5's
  pheromone-on-arcs line. It does *not* touch the novelty argument A3-A5
  carry (A6 was never counted among those three), but it does mean any
  prior draft text that cited A6 as evidence for "prior pheromone-digraph
  clustering existing since 2004" would have been wrong and should be
  checked. As a Section-B source in its own right, it is useful precisely
  because of the adaptive-parameter contribution (alpha, lambda both
  self-tuning) - a detail the earlier secondhand description did not
  surface.

---

## P5-2. Lumer, Erik D.; Faieta, Baldo (1994). *Diversity and Adaptation in Populations of Clustering Ants.* [FULL TEXT - upgrades B2 from "lead, print" to held, closes a gap open since pass 1]

- **Venue**: Proceedings of the Third International Conference on
  Simulation of Adaptive Behavior: From Animals to Animats 3 (SAB 1994),
  pp. 501-508. MIT Press / Bradford Books.
- **Identifier**: no DOI (pre-DOI-era proceedings volume); MIT CogNet
  watermark on the scan confirms provenance.
- **Retrieved**: full text, 10 pages, via the maintainer's own PDF
  (`tmp/pdf/Diversity and adaptation in populations of clustering ants.pdf`
  - a MIT CogNet screen-viewable excerpt, legitimately supplied, not
  fetched by this project).
- **Depth**: read in full.
- **Answers**:
  - This is the direct extension of Deneubourg et al. 1991 (B1) that
    Section B's paragraph has described secondhand since pass 1 - now
    confirmed from the primary text. Grid-based, no pheromone, no digraph.
  - Mechanism: `P_pick(i) = (k_p/(k_p + f(i)))^2` (pick-up probability,
    higher when local density `f(i)` is low), `P_drop(i) = 2f(i)` if
    `f(i) < k_d`, else `1` (drop probability, higher when local density is
    high). `f(i)` is a local density/similarity function computed over a
    `d x d` neighbourhood using a dissimilarity scale `alpha` - the direct
    continuous-valued generalisation of Deneubourg's binary same/different
    rule.
  - Two extensions over Deneubourg's original BM, both explicit
    contributions of this paper: **population diversity** (ants move at
    varying "pace," some fast/coarse, some slow/fine-grained) and
    **short-term memory** of recently-dropped-item locations, which lets an
    ant that just dropped an item go pick up a *similar* item elsewhere and
    carry it back - a directed, non-random relocation the base BM lacks.
    Also introduces "behavioural switches" (agents alternate between a
    gathering mode and, more rarely, a destroying mode that breaks up
    poor clusters).
  - Q1/Q2/Q3 do not apply in the ACO sense - there is no pheromone at all,
    confirming what B1's full text (P4-4) already established for the
    ancestor. Result (Q2-equivalent) is the spatial arrangement of items on
    the grid, read directly, no threshold or connected-components step.
- **Bearing**: closes the last full-text gap in Section B. Confirms, from
  the primary source rather than a survey's paraphrase, that the entire
  Deneubourg-to-Lumer/Faieta-to-Handl/Meyer-to-Boryczka line never uses
  pheromone at all - it is memory/density-based throughout. This sharpens
  the contrast this project wants in its related-work section: "ant-based
  clustering" in the literature usually means this grid-relocation family,
  and this project's own pheromone-on-edges-then-threshold mechanism is a
  different lineage entirely (A1-A5, Kang & Choi), which is exactly the
  distinction Section B's heading already asserts - now with both ends of
  the citation chain (B1, B2) read in full rather than one.

---

## P5-3. Yang, Xin-bin; Sun, Jing-gao; Huang, Dao (2002). *A New Clustering Method Based on Ant Colony Algorithm.* [NEW - not previously on any retrieval list]

- **Venue**: Proceedings of the 4th World Congress on Intelligent Control
  and Automation, Shanghai, 10-14 June 2002, pp. 2222-2226. IEEE. Bilingual
  full text (English and Chinese in parallel).
- **Identifier**: no DOI captured from the PDF.
- **Retrieved**: full text, 5 pages, via the maintainer's own PDF
  (`tmp/pdf/a-new-clustering-method-based-on-ant-colony-algorithm.pdf`).
- **Depth**: read in full.
- **Answers**:
  - This is classical TSP/QAP-style Dorigo ACO retargeted at clustering by
    a **binary distance threshold**, not a similarity-scaled continuous
    weight: pheromone is initialised `tau_ij(0) = 1` if `d_ij <= r` else
    `0`, where `r` is a fixed neighbourhood radius chosen in advance - a
    coarser, cruder starting point than any of Section A's continuous
    acceptance-weight schemes.
  - Points are merged into the same cluster if the transition probability
    between them exceeds a fixed threshold `p0`; cluster centres are then
    recomputed as means (a k-means-like step), and the whole process
    iterates until a total-deviation error `epsilon <= epsilon_0`.
  - Q1: pheromone update follows the classical TSP-style rule,
    `tau_ij(t+n) = rho*tau_ij(t) + Delta tau_ij`, with `Delta tau_ij^k =
    Q/L_k` where `L_k` is the **length of the tour/path** constructed by
    ant `k` - i.e. **the deposit is explicitly tied to a path-quality
    (fitness) term**, the opposite of a no-objective mechanism. All ants
    that complete a tour deposit, weighted by how good that tour was.
  - Q2: result is a constructed solution (a path/tour whose quality is
    `L_k`) that is then converted into a clustering via the threshold-`p0`
    merge step and mean-recomputation - a hybrid of "constructed solution"
    and "state read-out," leaning toward solution-construction because the
    tour-length fitness is what actually drives the pheromone update.
  - Q3: threshold `r` (neighbourhood radius, fixed a priori - the paper
    does not state a principled method for choosing it), `p0` (merge
    threshold on transition probability), `epsilon_0` (convergence
    tolerance on total deviation). Tested on a 40-sample, 6-dimensional
    air-conditioning fault-diagnosis dataset; reports 8 clusters mapped to
    specific fault types, no comparison against a second method.
- **Bearing**: an early (2002), fitness-driven, classical-ACO-lineage
  clustering paper that predates every one of Section A's digraph papers by
  three years, but is architecturally unrelated to them - it constructs
  TSP-style tours scored by path length, not a walk that reads out from
  accumulated edge pheromone with no fitness anywhere. Worth citing as an
  early data point for "how ACO was first bent toward clustering," and as a
  contrast case for Q1/Q2/Q3: this paper answers "all completing ants,
  weighted by tour-length fitness" / "constructed solution, then
  post-processed" / "fixed a priori thresholds" - the opposite answer from
  this project's own mechanism on every axis. Added as Section A6a in
  `RETRIEVAL_LIST.md` pending a maintainer decision on where it best fits
  (see `QUESTIONS.md`).

---

## P5-4. El-Feghi, I.; Errateeb, M.; Ahmadi, M.; Sid-Ahmed, M.A. (2009). *An Adaptive Ant-Based Clustering Algorithm with Improved Environment Perception* (AACA). [NEW - not previously on any retrieval list]

- **Venue**: Proceedings of the 2009 IEEE International Conference on
  Systems, Man, and Cybernetics (SMC 2009), San Antonio, TX, October 2009,
  pp. 1476-1483.
- **Identifier**: no DOI captured from the PDF.
- **Retrieved**: full text, 8 pages, via the maintainer's own PDF
  (`tmp/pdf/an-adaptive-ant-based-clustering-algorithm-with-improved-198iq5b9l1.pdf`).
- **Depth**: read in full.
- **Answers**:
  - This is a genuine **hybrid** of Section A and Section B, and the first
    one found in this project's whole search. It is built on the
    Lumer-Faieta grid model (cites Lumer & Faieta 1994 as ref 16,
    Deneubourg 1991 as ref 14, Handl & Meyer 2002 as ref 20 - the standard
    Section-B ancestry) but **adds an actual grid-position pheromone field**
    `tau(i)` with its own evaporation rule (eqs 5-6), which did not exist in
    any of B1/B2/B3/B4.
  - The pheromone value at each grid position modulates the pick-up/drop
    probability functions (eqs 3-4) alongside the usual local-density term
    - so unlike B1/B2, this is not purely memoryless/density-based; a
    genuine accumulated-traversal quantity now sits in the update.
  - Also contributes: an adaptive/progressive "vision field" that grows
    over the run (ants perceive a larger neighbourhood as the process
    matures), an adaptive similarity-scaling parameter `alpha` (as in
    A⁴C/P5-1), and a modified density function `f*(i)` incorporating a
    per-ant "speed" parameter (fast ants sample sparser neighbourhoods).
  - Q1: pheromone is deposited **by every ant that occupies or passes
    through a grid cell**, decaying by evaporation - no fitness/quality
    weighting is applied to the deposit itself (unlike P5-3's tour-length
    weighting); in this respect it resembles A1-A5's no-fitness deposit
    rule, just applied to grid cells rather than graph edges.
  - Q2: result is the spatial arrangement of items on the grid (Section-B
    style state read-out), not a constructed solution.
  - Q3: pheromone evaporation rate, vision-field growth schedule, `alpha`
    (adaptive), and a per-ant speed distribution. Compared against k-means
    and average-link agglomerative clustering on synthetic (square/size)
    and four real UCI datasets (Iris, Yeast, Breast Cancer Wisconsin, Zoo),
    using F-measure, Rand index, intra-cluster variance and the Dunn
    index.
- **Bearing**: the closest thing found so far to a bridge between this
  project's edge-pheromone-and-threshold mechanism and the
  grid-relocation branch it explicitly distinguishes itself from - AACA
  keeps the grid/spatial-relocation read-out of Section B but borrows the
  "accumulate pheromone, let it evaporate" idea from the Section-A/ACO
  world. Worth a sentence in the related-work section precisely because it
  shows the two branches are not hermetically sealed from each other in
  the literature, even though this project's own mechanism sits
  unambiguously on the graph/edge/threshold side.

---

## P5-5. Blum, Christian (2007). *Ant Colony Optimization: Introduction and Hybridizations.* [NEW - background/definitional reference, not a clustering paper]

- **Venue**: Proceedings of the Seventh International Conference on Hybrid
  Intelligent Systems (HIS 2007), Kaiserslautern, Germany, pp. 24-29. IEEE.
- **Identifier**: DOI `10.1109/HIS.2007.36`.
- **Retrieved**: full text, 6 pages, via the maintainer's own PDF
  (`tmp/pdf/blum2007.pdf`; a duplicate upload, `blum2007 (1).pdf`, was not
  read separately).
- **Depth**: read in full.
- **Answers**:
  - Not a clustering paper at all - a tutorial companion piece (the paper
    itself says it is a short version of Blum, *Ant colony optimization*,
    Physics of Life Reviews 2(4), 2005) covering classical combinatorial
    ACO and its hybridizations with beam search, constraint programming,
    and multilevel schemes.
  - Gives the **canonical definition** this project's own Q1/Q2/Q3
    framework is implicitly contrasted against: solution constructed
    step-by-step from a component set `C`, transition probability `p(c_i|s)
    ∝ [tau_i]^alpha · [eta(c_i)]^beta` (eq 1), and a general pheromone
    update `tau_i <- (1-rho)*tau_i + rho * sum_{s in S_upd} w_s * F(s)` (eq
    2) where **`F` is explicitly required to be a quality/fitness function**
    monotonic in the objective (`f(s) < f(s') => F(s) >= F(s')`). Table 1
    catalogues the named ACO variants (EAS, RAS, MAX-MIN AS, ACS,
    Hyper-Cube Framework) purely by which pheromone-update rule they use.
  - Q1/Q2/Q3 in the textbook-definition sense: pheromone update always
    keyed to `S_upd`, a set of *ranked* solutions (iteration-best and/or
    best-so-far), always weighted by a fitness function `F`; result is
    always an explicitly constructed solution (a permutation, assignment,
    or sequence), never a raw state of the environment; parameters
    (`alpha`, `beta`, `rho`, trail limits) all exist to shape convergence
    toward that ranked-solution fitness signal.
  - Also surveys ACO applications and hybridizations broadly (TSP, QAP,
    scheduling, vehicle routing, bioinformatics, multi-objective and
    non-static problems, hybridization with beam search and constraint
    programming) - none touching clustering.
- **Bearing**: not a comparison target, but a citable primary source for
  *what canonical ACO is*, useful specifically because it makes explicit,
  in one general equation (eq 2), the fitness-function requirement this
  project's mechanism lacks. Citing this alongside Stutzle & Hoos (entry 2
  above) gives two independent textbook-level statements of the same
  point, which strengthens rather than duplicates the existing MMAS
  citation - Blum's eq 2 is the general framework MMAS's rule is one
  instance of.

---

## P5-6. Gong, Yue-jiao; Xu, Rui-tian; Zhang, Jun; Liu, Ou (2009). *A Clustering-based Adaptive Parameter Control Method for Continuous Ant Colony Optimization.* [NEW - false lead, off-topic despite the keyword overlap]

- **Venue**: Proceedings of the 2009 IEEE International Conference on
  Systems, Man, and Cybernetics (SMC 2009), San Antonio, TX, October 2009,
  pp. 1827-1832.
- **Identifier**: no DOI captured from the PDF.
- **Retrieved**: full text, 6 pages, via the maintainer's own PDF
  (`tmp/pdf/gong2009.pdf`).
- **Depth**: read in full.
- **Answers**:
  - **This paper is not an ant-colony clustering algorithm - it is the
    reverse.** It uses ordinary K-means clustering as an internal
    diagnostic inside a continuous-optimization ACO variant (the
    "continuous orthogonal ant colony," COAC): at each iteration, the
    candidate regions explored by the ants are K-means-clustered, and the
    size/rank of the cluster containing the current-best vs. current-worst
    region is used to classify the search into an "initial / maturing /
    matured" state, which then drives adaptive adjustment of COAC's own
    parameters (`q0`, `phi`, `shrink`).
  - Clustering here is a control-loop diagnostic for tuning a
    combinatorial optimizer; nothing about ants clustering data, and no
    pheromone-clustering mechanism to compare against this project's own.
  - Q1/Q2/Q3 do not meaningfully apply - the "clustering" is a classical
    K-means sub-routine, not part of any ACO/pheromone process; the ACO
    part (COAC itself) is a standard fitness-driven region-search method
    with pheromone deposited per eq 6, weighted by each region's rank and
    visit count, i.e. fitness-driven in the ordinary combinatorial-ACO
    sense described in P5-5.
- **Bearing**: a **false lead**, recorded so the "ant colony" + "clustering"
  keyword overlap that surfaced it is not mistaken for a hit in any future
  search. Not relevant to Sections A/B/H and not added as a new retrieval
  entry beyond this note.

---

## P5-7. Zhao, Bao-Jiang (2007). *An Ant Colony Clustering Algorithm.* [NEW - fitness-driven, solution-construction ACO clustering, distinct from every prior category found]

- **Venue**: Proceedings of the Sixth International Conference on Machine
  Learning and Cybernetics, Hong Kong, 19-22 August 2007, pp. 3933-3938.
  IEEE.
- **Identifier**: DOI `10.1109/ICMLC.2007.4370848` (catalog number
  1-4244-0973-X/07 on the PDF; not independently re-verified against
  Crossref this pass - treat as unconfirmed until checked).
- **Retrieved**: full text, 6 pages, via the maintainer's own PDF
  (`tmp/pdf/zhao2007.pdf`).
- **Depth**: read in full.
- **Answers**:
  - Recasts data clustering as the **quadratic assignment problem (QAP)**:
    each ant builds a complete solution string `S` of length `N` (one
    cluster label per data object, e.g. `(2,1,3,2,2,3,2,1)` for `N=8,
    K=3`), using pheromone-and-heuristic-guided assignment at each
    position (eq 6-7: exploitation with probability `q0` via `argmax
    [tau_ij]*[eta_ij]^beta`, otherwise roulette-wheel selection over
    `p_ij`). `eta_ij` is the inverse Euclidean distance from object `i` to
    cluster `j`'s current centre.
  - After all ants build strings, a **parameterized uniform crossover**
    (borrowed directly from genetic algorithms, threshold `p_ls = 0.7`) is
    applied to the best 20% of solutions, an explicit cross-pollination
    with GA absent from every other source in this project's list.
  - The clustering objective is explicit and stated as equation 1: `min
    F(w,m) = sum_j sum_i sum_v w_ij * ||x_iv - m_jv||^2` - ordinary
    sum-of-squared-errors, identical in spirit to k-means' own objective.
  - Q1: **only the single best-so-far ant deposits pheromone**, and the
    deposit amount is `Delta tau_ij^bs = 1/F_bs` if object `i` is assigned
    to cluster `j` in the best solution, else `0` (eq 8-9) - i.e. the
    deposit is **inversely proportional to the objective-function value of
    the best constructed solution**, the most explicit fitness-tied
    deposit rule found anywhere in this project's search so far (Section A
    and D sources have none; Kang & Choi has none; even P5-3's tour-length
    weighting is less directly tied to the clustering objective itself).
  - Q2: the result is unambiguously a **constructed solution** - the
    assignment string `S` itself, not a state of a graph or grid read out
    afterward. There is no threshold step and no connected-components (or
    equivalent) read-out anywhere in the algorithm.
  - Q3: number of ants `R=40`, `q0=0.8` (exploitation probability), `beta=2`
    (heuristic weight), `rho=0.1` (evaporation rate), crossover probability
    `0.7`, crossover applied to top 20% of solutions by fitness. Compared
    against WHACO (ant colony clustering without heuristic information,
    Shelokar, Jayaraman & Kulkarni 2004, *Analytica Chimica Acta* 509,
    cited as the paper's own ref [14] - not yet on this project's own
    retrieval list, see `QUESTIONS.md`) and a standard GA, on one synthetic
    Gaussian dataset and three UCI datasets (Iris, Wine, Glass). Reports
    ACCA finding the global optimum in all or most of 10 runs with
    substantially fewer function evaluations and less CPU time than either
    baseline.
- **Bearing**: this is the clearest possible **contrast case** for this
  project's own no-objective-function claim, and belongs in the
  related-work section specifically as that contrast rather than as a
  predecessor. Where Section A (Kang & Choi, A1-A5) shares this project's
  no-fitness, edge-pheromone-threshold-components architecture, and
  Section B (Deneubourg through Boryczka) shares its no-fitness but
  grid/spatial architecture, **this paper (and P5-3) demonstrate that a
  large parallel line of "ant colony clustering" work is explicitly
  fitness-driven, treats clustering as combinatorial assignment, and
  produces a constructed solution rather than reading one out of an
  environment state** - i.e. mainstream ACO applied to clustering the same
  way it is applied to TSP/QAP, with none of the four distinguishing
  properties this project's own mechanism has. Naming this contrast
  explicitly (rather than letting the dissertation imply "all ACO
  clustering has no objective function") is a more defensible framing.
  Recorded as a new Section H entry in `RETRIEVAL_LIST.md`.

---

## P5-8. Sinha, Ankita; Jana, Prasanta K. (2025). *Improved Affinity Propagation Clustering Algorithms: A PSO-Based Approach.* [NEW - false lead, no ants, no pheromone, out of scope]

- **Venue**: journal - Knowledge and Information Systems 67:1681-1711.
- **Identifier**: DOI `10.1007/s10115-024-02260-x`.
- **Retrieved**: partial, 16 of 31 pages, via the maintainer's own PDF
  (`tmp/pdf/Improved-affinity-propagation-clustering-algorithms-a-PSO-based-approach.pdf`).
- **Depth**: read (Abstract, Introduction, related-work survey of AP-tuning
  methods, full background on Affinity Propagation's message-passing
  algorithm, full description of both proposed algorithms PSO-AP*ver1* and
  PSO-AP*ver2*, and the mutant-PSO procedure). Sections 4.4 onward
  (complexity analysis, experimental results and datasets, statistical
  tests) not read - not needed to establish scope, see Bearing.
- **Answers**:
  - **No ants and no pheromone anywhere in this paper.** It combines two
    unrelated methods, neither of which is ACO: **Affinity Propagation**
    (Frey & Dueck's message-passing clustering algorithm, using
    responsibility/availability messages between data points, no swarm of
    any kind) and **Particle Swarm Optimization** (a different
    swarm-intelligence metaheuristic - particles with position/velocity,
    no pheromone, no graph traversal) used here purely to tune AP's two
    free parameters (preference `p` and damping factor `lambda`).
  - The paper's own contribution is a "mutant PSO" that evaluates each
    candidate parameter setting with two cluster-validity indices
    (silhouette score as `primary`, Davies-Bouldin index as `mutant`), then
    merges the two fitness signals to update the global best.
  - Q1/Q2/Q3 do not apply - there is no pheromone-depositing process of any
    kind in either AP or PSO. Both are explicitly fitness-driven in the
    ordinary metaheuristic sense (PSO particles chase a validity-index
    score; AP itself is deterministic message-passing, not stochastic).
- **Bearing**: **a false lead, recorded so the "swarm intelligence" +
  "clustering" keyword overlap that surfaced it alongside the genuine ACO
  papers in this batch is not mistaken for a hit in a future search.** Not
  ant colony optimization at all - a different swarm metaheuristic (PSO)
  applied to a different clustering algorithm (AP), with nothing resembling
  pheromone, digraphs, thresholds, or edge-reinforced walks. Not added to
  `RETRIEVAL_LIST.md` as a numbered entry; noted only in the pass-5 file
  mapping as "not moved - out of scope."

---
---

# Pass 6 - 2026-08-04

## P6-1. Gupta, Gunjan; Liu, Alexander; Ghosh, Joydeep (2006). *Hierarchical Density Shaving: A clustering and visualization framework for large biological datasets* (HDS). [NEW - resolves the maintainer-supplied lead flagged in the HSE research proposal draft]

- **Venue**: Sixth IEEE International Conference on Data Mining - Workshops
  (ICDMW'06). IEEE, ISBN/catalog 0-7695-2702-7/06.
- **Identifier**: no DOI captured from the PDF.
- **Retrieved**: full text, 5 pages, via the maintainer's own PDF
  (`tmp/pdf/gupta2006.pdf`). Not found by this project's own search - the
  maintainer supplied the file directly after this project flagged HDS as
  an unconfirmed comparison baseline (Kang & Choi cite it as one of theirs).
- **Depth**: read in full.
- **Answers**:
  - HDS builds on **Hierarchical Mode Analysis** (HMA, Wishart 1968, a
    density-based method the authors note had "gotten lost in time"). Input
    is a full n x n distance matrix (Euclidean, 1 - cosine similarity, or
    Pearson distance) - **not a sparse kNN graph**, a structural difference
    from this project's own mechanism and from HDBSCAN alike.
  - Density at a point is the count of points within a radius `r_eps`,
    equivalently parametrised by `n_eps` (how many neighbours must be
    within range to count as dense). **Density Shaving (DS)**, the
    non-hierarchical building block: given a "shave fraction" `f_shave`,
    keep only the `n_c = ceil(n(1-f_shave))` densest points as `G`, cluster
    them by chaining within `r_eps`, and label everything else "don't
    care" (`0`) - **HDS explicitly clusters only a subset of the data and
    discards the rest**, unlike this project's absorption step, which
    covers every point.
  - **Hierarchical DS (HDS)**: repeatedly shave a fraction `r_shave` of the
    remaining densest-point set, rerun DS, and relabel bottom-up so cluster
    identities persist across levels (a "compaction" step); clusters below
    size `n_part` are treated as spurious "particles" and pruned. This is
    the hierarchy-construction mechanism, and it is a **peeling/shrinking
    scheme on a shrinking dense core**, not a graph-coarsening scheme -
    structurally distinct from both Louvain/Leiden-style coarsening and
    from this project's own centroid-collapse mechanism. Time complexity
    `O(n^2 log n)` for the full hierarchy (`O(n^3)` naively).
  - No pheromone, no ants, no ACO framing anywhere - this is a pure
    density-based method, evaluated with ARI, and explicitly benchmarked
    (via a "MaxBall" procedure giving competitors the same k and coverage)
    against MaxBall-K-Means, MaxBall-Single-Link, and DBSCAN on a synthetic
    2D dataset (Sim-2, 1298 points, five Gaussians + uniform noise) and a
    real yeast gene-expression dataset (Gasch, 6151 genes x 173
    experiments, 11 classes).
- **Bearing**: confirms Kang & Choi's own comparison baseline is real and
  reads as described. Relevant to this project mainly as a **comparison-set
  candidate for the "coverage" question**: HDS's explicit design choice to
  cluster only the densest subset and discard the rest (`f_shave`) is the
  same problem this project's own graph-baseline-vs-full-coverage tension
  addresses differently (giant-component handling, two-level absorption).
  Worth citing in the related-work section as a second density-based
  hierarchical method distinct from HDBSCAN, and worth noting explicitly
  that it does **not** operate on a sparse graph the way this project,
  Kang & Choi, or HDBSCAN's mutual-reachability graph do.
