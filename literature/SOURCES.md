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

## 7. Handl, J. & Meyer, B. *Finding groups in data: Cluster analysis with ants.* Applied Soft Computing (ScienceDirect), and earlier survey chapters extending Lumer-Faieta.

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
