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
  retrieved.
