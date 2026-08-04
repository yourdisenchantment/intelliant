# Retrieval list

What still has to be obtained, and how far each identifier has been verified.
Assembled 2026-08-03 from `SOURCES.md` (passes 1 and 2) and from leads in two
third-party reviews of this repository.

Status means exactly this:

- `[verified]` - the identifier was confirmed against Crossref, OpenAlex or
  arXiv. Title, year and authors are what the index returned, not what anyone
  remembered.
- `[lead]` - a name that came from a review or a conversation and **matched
  nothing in any index**. It may not exist. Search by hand; if it does not
  turn up, that is recorded as an absence, not left as a gap.
- `[held]` - already retrieved in pass 1 or 2. Do not fetch again.

The rule from `LITERATURE.md` applies to every line here: until the document
is open, nothing on this page may be cited. A verified DOI proves the work
exists, not that it says what a review claimed it says.

---

## A. Direct predecessors of the mechanism

Pheromone on edges, a threshold, connected components. This is the section
that decides the novelty question, and it comes first.

| # | Work | Identifier | Status |
|---|---|---|---|
| A1 | Kang, Mun-Su; Choi, Young-Sik (2014). Ant Colony Hierarchical Cluster Analysis | see entry P2-1 | [held] |
| A2 | He, Y.; Hui, S.C.; Sim, Y. (2006). A Novel Ant-Based Clustering Approach for Document Clustering. LNCS | `10.1007/11880592_43` | [verified] |
| A3 | Chen, L.; Tu, L.; Chen, H.-J. (2005). Data clustering by ant colony on a digraph. ICMLC vol. 3, 1686-1692 | `10.1109/ICMLC.2005.1527216` | [held, full text - retrieved 2026-08-03 via maintainer's library, SOURCES.md P4-1] |
| A4 | Chen, L.; Tu, L.; Chen, H. (2005). A Novel Ant Clustering Algorithm with Digraph (A3CD). ICNC, LNCS 1218-1228 | `10.1007/11539117_163` | [held, full text - retrieved 2026-08-03 via maintainer's library, SOURCES.md P4-2. **Near-duplicate of A3 - see note below.**] |
| A5 | Chen, L.; Tu, L.; Chen, Y. (2006). An Ant Clustering Method for a Dynamic Database. LNCS | `10.1007/11739685_18` | [held, full text - retrieved 2026-08-03 via maintainer's library, SOURCES.md P4-3] |
| A6 | ~~Chen, L.; Xu, X.-H.; Chen, Y.-X. (2004). An Adaptive Ant Colony Clustering Algorithm (A4C)~~ **MOVED to Section B, see B7** | see entry P2-10 | **reclassified 2026-08-03, see note below - no longer belongs in Section A** |
| A7 | Qin, L.; Chen, Y.; Pan, Y.; Chen, L. (2006). A novel approach to phylogenetic tree construction using stochastic optimization and clustering. BMC Bioinformatics 7(S4):S24 | `10.1186/1471-2105-7-S4-S24` | [held, full text, open access - SOURCES.md P3-13] |
| A8 | Tu, L.; Chen, L.; Shen, J. (2007). Adaptive Clustering Algorithm by Ants' Optimization. J. Systems Science & Information | not in Crossref | [lead, weak - maintainer's library search found nothing 2026-08-03; independent WebSearch/Crossref/Chinese-language search also found nothing beyond the original snippet. Do not chase further without a better citation, see SOURCES.md P3-13 addendum.] |
| A9 | Qin, L.; Luo, J.; Chen, Z.; Guo, J.; Chen, L.; Pan, Y. (2006). Phylogenetic tree construction using self adaptive ant colony algorithm. IEEE Computer Society, proceedings-article `04021071`, conf. code `ichit/2006` | DOI not yet found | [lead, confirmed to exist but no full text - maintainer searched by title and title+combinations 2026-08-03, found no PDF anywhere (IEEE Computer Society paywalls it, as expected for CSDL). What this project has is **a search-engine snippet, not a verified publisher abstract** - weaker footing than P3-13's "abstract only" tier. Do not cite beyond what the snippet states; see SOURCES.md P3-13 addendum.] |

**A7 is not a substitute for A3-A5, but it closes most of the practical
citation gap.** Found 2026-08-03 via a Google Scholar search run directly in
the maintainer's browser (the maintainer asked whether Chrome could reach
CyberLeninka/Scholar - it could, no CAPTCHA, no block, this session). Same
research group (Ling Chen), fully open access (BMC/BioMed Central, CC-BY),
full text read. It gives, in complete equations, the same
digraph/acceptance-weight/pheromone/threshold/strong-connected-components
construction A3-A5's abstracts only summarise - with one caveat that must
travel with any citation: in *this* paper the clusters feed a second-stage,
fitness-driven genetic-algorithm loop over whole candidate phylogenetic
trees, so the outer system is not free of an objective function the way
A3-A5 are believed to be from their abstracts alone. The digraph-clustering
sub-step itself has no fitness term. See `SOURCES.md` P3-13 for the full
account, including the two further unverified leads (A8, A9) the same search
turned up.

**A3-A5 are the primary target of this whole list.** They decide whether the
mechanism "pheromone on arcs -> threshold -> components" dates from 2014 or
from 2005. That changes how novelty is stated, not which footnote is used.
A2 was found on 2026-08-03 and is of the same class.

**Pass 3 (2026-08-03) re-checked A3-A5: no new access found.** IEEE (A3) and
Unpaywall confirm no open copy exists anywhere for any of the three DOIs.
A5's abstract was newly retrieved verbatim this pass (SOURCES.md P2-4's
"not obtained" note now has the text, via SEARCH_LOG.md pass 3, Category A).
The full texts of all three still require the maintainer's own institutional
session - unchanged from pass 2's conclusion.

**Pass 4 (2026-08-03, same day): all three retrieved, full text, via the
maintainer's own library.** This is the single largest resolution in the
whole retrieval effort - A3, A4, and A5 are no longer paywalled gaps. Read in
full: SOURCES.md P4-1 (A3), P4-2 (A4), P4-3 (A5).

**New finding that changes how "three papers" should be counted: A3 and A4
are, to a first approximation, the same paper.** Same three authors, same
year, same algorithm equations, and - checked directly - the same
experimental result tables to the decimal (Table 1's 300/600-item runs,
Table 2's Glass results, Table 3's Soybean results are identical between the
two). They differ only in venue (ICMLC vs. ICNC, both 2005) and title. This
reads as one experiment published twice, not two independent confirmations
of the mechanism. A5 is the one member of the trio with a genuinely distinct
contribution (Section 4's incremental maintenance under insert/delete).
**Flagged as a question for the maintainer in `QUESTIONS.md`** - whether to
treat Section A's "three Chen/Tu/Chen papers" as two contributions (A3=A4,
plus A5) rather than three when the dissertation states its prior-art
picture, is not decided here.

**Pass 5 (2026-08-03): A6 was misfiled here and is moved to Section B.**
Full text (SOURCES.md P5-1) shows Chen/Xu/Chen 2004 has no pheromone, no
digraph, and no edge-threshold-into-components step at all - it is a
grid/agent density-and-activation-probability method (the "Ants Sleeping
Model"/A⁴C) squarely in the Deneubourg/Lumer-Faieta lineage, citing both as
its own ancestry. The secondhand description this project had before pass 5
apparently over-fitted the superficial "ant colony clustering" title
resemblance to the real digraph line (A1-A5). This does not touch the
novelty finding A3-A5 carry, since A6 was never one of those three. See B7
below and SOURCES.md P5-1's Bearing.

**Pass 5 also adds a new sub-line, A6a: fitness-driven, solution-
construction ACO retargeted at clustering (Yang/Sun/Huang 2002).** This is
architecturally distinct from A1-A5 (no digraph, no threshold, an explicit
tour-length fitness drives the pheromone update) but is early and
influential enough to be worth recording near Section A rather than folding
silently into Section H. See the new row below and SOURCES.md P5-3.

| # | Work | Identifier | Status |
|---|---|---|---|
| A6a | Yang, X.-b.; Sun, J.-g.; Huang, D. (2002). A New Clustering Method Based on Ant Colony Algorithm. 4th World Congress on Intelligent Control and Automation, Shanghai, pp.2222-2226 | no DOI captured | [held, full text - retrieved 2026-08-03 via maintainer's own PDF, SOURCES.md P5-3. New source, not previously on any list.] |

---

## B. The ant-based clustering branch, which this work is not

Ants carrying objects on a grid. The paragraph that separates this project
from that branch currently rests on secondary description.

| # | Work | Identifier | Status |
|---|---|---|---|
| B1 | Deneubourg, J.-L. et al. (1991). The dynamics of collective sorting. SAB 1, 356-365, MIT Press | no DOI | [held, full text - retrieved 2026-08-03 via maintainer's library (OCR scan), SOURCES.md P4-4] |
| B2 | Lumer, E.; Faieta, B. (1994). Diversity and adaptation in populations of clustering ants. SAB 3, 501-508, MIT Press | no DOI | [held, full text - retrieved 2026-08-03 via maintainer's own PDF (MIT CogNet excerpt), SOURCES.md P5-2. Closes a gap open since pass 1.] |
| B3 | Handl, J.; Meyer, B. (2007). Ant-based and swarm-based clustering. Swarm Intelligence 1(2), 95-113 | `10.1007/s11721-007-0008-7` | [held, see SOURCES.md P2-12] |
| B4 | Boryczka, U. (2009). Finding groups in data: Cluster analysis with ants. Applied Soft Computing 9(1) | `10.1016/j.asoc.2008.03.002` | [held, full text - SOURCES.md P3-2] |
| B5 | Boryczka, U. (2013). **Corrigendum** to B4 | `10.1016/j.asoc.2013.07.012` | [held, full text - retrieved 2026-08-03 via maintainer's library, SOURCES.md P4-6. Authorship-only correction, adds Marcin Budka as co-author.] |
| B6 | Boryczka, U. (2006). Finding Groups in Data: Cluster Analysis with Ants. ISDA 2006 (earlier conference version) | `10.1109/isda.2006.151` | [verified, metadata + reference list only - SOURCES.md P3-4] |
| B7 | Chen, L.; Xu, X.-H.; Chen, Y.-X. (2004). An Adaptive Ant Colony Clustering Algorithm - Ants Sleeping Model / A⁴C **(moved here from Section A, pass 5)** | see entry P2-10 | [held, full text - retrieved 2026-08-03 via maintainer's own PDF, SOURCES.md P5-1] |
| B8 | El-Feghi, I.; Errateeb, M.; Ahmadi, M.; Sid-Ahmed, M.A. (2009). An Adaptive Ant-Based Clustering Algorithm with Improved Environment Perception (AACA). IEEE SMC 2009, pp.1476-1483 | no DOI captured | [held, full text - retrieved 2026-08-03 via maintainer's own PDF, SOURCES.md P5-4. New source, not previously on any list - hybrid grid+pheromone method, see note below.] |

**B7 and B8 are pass-5 additions.** B7 is A6, moved here (see Section A's
note above) - a grid/agent method with no pheromone at all. B8 is new to
this project and is the first genuine **hybrid** found between Section A's
pheromone-accumulation idea and Section B's grid-relocation mechanism: it
keeps Lumer-Faieta's grid and density-based pick/drop probabilities but adds
an actual evaporating pheromone field over grid positions (its own eq 5-6),
which none of B1-B7 have. Worth a sentence in the related-work section as
evidence the two branches are not hermetically separate in the literature.
See SOURCES.md P5-4's Bearing.

**B3 and B4 are different papers by different authors.** Pass 1 merged them;
the error is recorded in the Corrections block of `SOURCES.md` and both must
be fetched separately.

**B5 is now read** (pass 4, SOURCES.md P4-6) - it is a one-page authorship
correction only (adds Marcin Budka as co-author), nothing substantive.
Boryczka 2009 (B4) should now be cited as Boryczka & Budka.

**B1 is now read in full** (pass 4, SOURCES.md P4-4) - a library OCR scan,
confirming from the primary text that this ancestral mechanism uses no
pheromone at all (local-memory density estimate only). **B2 is now also
read in full** (pass 5, SOURCES.md P5-2) - closes the last gap in this
section that had been open since pass 1. Confirms directly from the primary
text: no pheromone here either, just the density function `f(i)` and two
explicit extensions over B1 (population diversity in ant "pace," short-term
memory of drop locations).

---

## C. Non-ant relatives

What a reviewer asks first: how is this different from Walktrap, or from
evidence accumulation? Only MCL is on record so far.

| # | Work | Identifier | Status |
|---|---|---|---|
| C1 | van Dongen, S. (2000). Graph Clustering by Flow Simulation. PhD, Utrecht | - | [held] |
| C2 | Pons, P.; Latapy, M. (2006). Computing Communities in Large Networks Using Random Walks (Walktrap). JGAA 10(2) | `10.7155/jgaa.00124` | [verified; abstract retrieved via arXiv long version physics/0512106, see SOURCES.md P3-5] |
| C3 | Pons, P.; Latapy, M. (2005). Same work, conference version. LNCS | `10.1007/11569596_31` | [verified] |
| C4 | Rosvall, M.; Bergstrom, C. (2008). Maps of random walks on complex networks reveal community structure (Infomap). PNAS 105(4) | `10.1073/pnas.0706851105` | [verified; abstract retrieved, GREEN OA at arXiv:0707.0609 - SOURCES.md P3-6] |
| C5 | Blondel, V. et al. (2008). Fast unfolding of communities in large networks (Louvain). JSTAT | `10.1088/1742-5468/2008/10/p10008` | [verified; abstract retrieved, GREEN OA at arXiv:0803.0476 - SOURCES.md P3-7] |
| C6 | Traag, V.; Waltman, L.; van Eck, N. (2019). From Louvain to Leiden. Scientific Reports 9 | `10.1038/s41598-019-41695-z` | [verified; abstract retrieved, Gold OA full text at nature.com - SOURCES.md P3-8] |
| C7 | Campello, R.; Moulavi, D.; Sander, J. (2013). Density-Based Clustering Based on Hierarchical Density Estimates (HDBSCAN). LNCS | `10.1007/978-3-642-37456-2_14` | [held, full text - retrieved 2026-08-03 via maintainer's library, SOURCES.md P4-7. Journal companion (TKDD 2015) also held, 20/51 pages read, SOURCES.md P4-8.] |
| C8 | Fred, A.; Jain, A.K. (2005). Combining multiple clusterings using evidence accumulation. IEEE TPAMI 27(6) | `10.1109/tpami.2005.113` | [held, full text - retrieved 2026-08-03 via maintainer's library, SOURCES.md P4-5] |
| C9 | Gupta, G.; Liu, A.; Ghosh, J. (2006). Hierarchical Density Shaving (HDS). ICDMW 2006 | no DOI captured | [held, full text - retrieved 2026-08-04 via maintainer's own PDF, SOURCES.md P6-1. Kang & Choi's own comparison baseline - see note below.] |

**C8 is the most underrated line on this page - and is now confirmed, not
assumed.** Full text (pass 4, SOURCES.md P4-5) confirms the co-association-
matrix/threshold/single-link read-out this project had previously only
inferred from metadata. The pheromone matrix is a count of how often
stochastic processes crossed an edge; thresholding it and taking components
is structurally the move evidence accumulation makes with a co-association
matrix built from many weak partitions - the resemblance holds up under the
full text, with the caveat (see SOURCES.md P4-5's Bearing) that Fred & Jain's
evidence source is an ensemble of independent full clusterings, not a single
stochastic process walking one graph.

**C9, 2026-08-04: resolved.** The HSE research-proposal draft flagged HDS
(cited by Kang & Choi as one of their own baselines) as "primary source not
independently identified" - the maintainer then supplied the actual paper.
Full text confirms it: a density-shaving hierarchy over a full n x n
distance matrix (not a sparse graph), which clusters only the densest
subset of points at each level and explicitly discards the rest, rather
than covering every point the way this project's absorption step does. See
SOURCES.md P6-1.

C5-C7 are also the comparison set roadmap phase 4 needs. C7's journal
companion (SOURCES.md P4-8) is partially read (20/51 pages) - finishing it
(the semi-supervised extraction and GLOSH outlier-detection sections) is
optional, not required for anything currently claimed.

---

## D. Theory: self-reinforcing walks

A branch nobody has searched. It is also the most plausible home for the
theoretical component whose absence both external reviews named as the main
gap.

| # | Work | Identifier | Status |
|---|---|---|---|
| D1 | Pemantle, R. (2007). A survey of random processes with reinforcement. Probability Surveys 4 | `10.1214/07-ps094` | [held, partial - pp.1-35 of 79 read via arXiv:math/0610076, 2026-08-03, SOURCES.md P4-9. **Section 5 (pp.48-55), the ERRW/VRRW-on-general-graphs part, is the one still unread and most relevant.**] |
| D2 | Merkl, F.; Rolles, S. (2005). Edge-reinforced random walk on a ladder. Annals of Probability | `10.1214/009117905000000396` | [held, partial - read via arXiv:math/0501137, 2026-08-03, SOURCES.md P4-10; deep proof (Sections 3-5) not read, not needed for citation] |
| D3 | Merkl, F.; Rolles, S. (2011). Correlation Inequalities for Edge-Reinforced Random Walk | `10.1214/ecp.v16-1683` | [not retrieved - Gold OA but the only host, projecteuclid.org, returned an Incapsula bot-challenge to this session's tool, 2026-08-03; a normal browser may fare better, see SOURCES.md P4-11] |

**D1 update, 2026-08-03**: read pages 1-35 of 79 via arXiv (the
projecteuclid.org host this list originally pointed to now sits behind an
Incapsula bot-detection challenge - not attempted further, per this
project's own rule against routing around access barriers; the arXiv copy is
identical and open). Confirms the vocabulary point below directly: this
project's mechanism is formally an **edge-reinforced random walk (ERRW)**,
Coppersmith & Diaconis's term, not classical ACO - transition probability
proportional to 1 + (times this edge has been traversed), no fitness
anywhere. Section 5 (pp.48-55), covering ERRW/VRRW on general graphs rather
than trees, is still unread and is the part likely most worth finishing -
see SOURCES.md P4-9. D2-D3 remain unfetched; per the survey's own citation
practice they are exactly the "fetch on the survey's guidance" follow-up
once Section 5 is read.

The terminology point sits here too: what this project runs is closer to a
pheromone-reinforced random walk than to ACO - the trajectory is not a
solution, there is no objective function, and pheromone grows from traversal
alone.

---

## E. The multilevel line - bears on the third stage

| # | Work | Identifier | Status |
|---|---|---|---|
| E1 | Liu, X.; Ji, J.; Yang, C. et al. (2014). Ant Colony Clustering Approach Combined with Multilevel Framework for Functional Module Detection. WI-IAT 2014 | `10.1109/wi-iat.2014.145` | [verified] |
| E2 | **MABA, Multi-layer Ant-Based Algorithm** | `10.1142/S0219525912500361` (= arXiv:1303.4711) | [**resolved 2026-08-03: E2 is E3.**] |
| E3 | An Ant-Based Algorithm with Local Optimization for Community Detection in Large-Scale Networks (2013) | `arXiv:1303.4711` | [held, full text - confirmed identical to E2, see SOURCES.md P3-1] |
| E4 | Multilevel ACO for graph partitioning, 2000s, Springer | not identified | [lead] |

**E2 mattered more than every other lead combined, and it is now resolved.**
Full text read 2026-08-03 (SOURCES.md P3-1): MABA is not a separate paper -
it is E3 itself (He, Liu, Yang, Huang, Liu & Jin, *Advances in Complex
Systems* 15(8):1250036, 2012; self-archived arXiv:1303.4711, 2013). The paper
describes, under the name "layer and rule," exactly the planned scheme: run
the base method, take each found community as a vertex of a new graph, repeat
until modularity stops improving. **This does not threaten the base
mechanism** (MABA has no pheromone and is driven throughout by modularity as
an explicit objective function - Kang & Choi, P2-1, remains the mechanism-level
predecessor there) **but it does mean the coarsen-and-repeat structure planned
for stage 3 is not new, and is not new even relative to MABA**: Louvain (see
Section C, C5) performs the identical structural step in 2008, four years
earlier. See `QUESTIONS.md` pass 3 for the question this raises for the
roadmap.

E3 was found on arXiv and flagged as an unconfirmed match to the E2 lead;
reading it (this pass) confirms it is the same work - the arXiv listing gives
its own journal reference, so this is not an inference from search results.

---

## F. Thresholding

| # | Work | Identifier | Status |
|---|---|---|---|
| F1 | Otsu, N. (1979). A Threshold Selection Method from Gray-Level Histograms. IEEE TSMC 9(1) | `10.1109/TSMC.1979.4310076` | [held, full text] |
| F2 | Zelnik-Manor, L.; Perona, P. (2004). Self-Tuning Spectral Clustering. NIPS 17 | no DOI | [held, full text - retrieved 2026-08-03, SOURCES.md P3-12] |

F2 is not indexed by DOI, but this was never actually a paywall problem - NIPS
(NeurIPS) proceedings are freely hosted at `papers.nips.cc` /
`proceedings.neurips.cc`, no login. Retrieved in full in pass 3.

---

## G. Russian-language sources

Three titles were recorded in pass 1 and none retrieved; pass 2 never reached
the sites. A Russian-language document and a VAK review both need them.

```
муравьиный алгоритм кластеризация графа
роевой интеллект кластеризация данных обзор
муравьиная колония кластеризация феромон порог
метод муравьиной колонии кластер анализ порог
эвристические алгоритмы кластеризации муравьи
кластеризация графа случайные блуждания
ансамблевая кластеризация матрица совстречаемости
выявление сообществ в графах обзор
```

Where: CyberLeninka, eLibrary, Google Scholar with `site:cyberleninka.ru` and
`site:elibrary.ru`, and the proceedings of Russian conferences in the area.

**Update 2026-08-03: CyberLeninka opened without a CAPTCHA this session** (see
`SOURCES.md`, pass 3 addendum). Searching directly for the four titles pass 1
recorded as "surfaced by CyberLeninka" returned **zero results for all
four** - none could be found by title or by a shortened core phrase. This
does not prove they don't exist, but it means they should be treated as
**unconfirmed leads, not as real papers that a CAPTCHA is blocking** - pass 1
only ever had a general-purpose search tool's paraphrase of what CyberLeninka
"surfaced," never a confirmed hit against the index itself. A fresh,
well-formed query on the actual mechanism (`муравьиная колония кластеризация
феромон порог`) returned 6 real, readable results, none a close mechanism
match - recorded in `SEARCH_LOG.md` pass 3 addendum. eLibrary itself still
has not been searched directly in any pass.

---

## H. Fitness-driven, solution-construction ACO retargeted at clustering - a contrast case, not a predecessor

New in pass 5. Every source in Sections A and B shares this project's
no-objective-function property; these do not. Ants here construct a
complete candidate clustering (an assignment string or a tour), the
construction is scored by an explicit objective, and pheromone is deposited
in proportion to that score. This is mainstream Dorigo-style combinatorial
ACO (the TSP/QAP family) pointed at the clustering problem, not a relative
of the pheromone-threshold-components mechanism. Useful for the
dissertation precisely as the thing this project's mechanism is *not*,
stated explicitly rather than left implicit.

| # | Work | Identifier | Status |
|---|---|---|---|
| H1 | Zhao, B.-J. (2007). An Ant Colony Clustering Algorithm. ICMLC 2007, Hong Kong, pp.3933-3938 | `10.1109/ICMLC.2007.4370848` (unverified against Crossref) | [held, full text - retrieved 2026-08-03 via maintainer's own PDF, SOURCES.md P5-7] |
| H2 | Shelokar, P.S.; Jayaraman, V.K.; Kulkarni, B.D. (2004). An ant colony approach for clustering (WHACO). Analytica Chimica Acta 509, 187-195 | not yet checked | [lead - cited as H1's own comparison baseline (its ref 14), not independently retrieved or verified this pass] |

**H1** builds a complete cluster-assignment string per ant, scores it by
sum-of-squared-errors (eq 1), and lets only the single best-so-far ant
deposit pheromone in proportion to `1/objective` (eq 8-9) - the most
directly fitness-tied deposit rule found anywhere in this project's search.
Also borrows a GA uniform-crossover operator to refine solutions, a
cross-pollination absent from every other source on this list. Full Q1/Q2/Q3
answers and the head-to-head numbers against WHACO and a plain GA are in
SOURCES.md P5-7.

**H2 is a lead, not yet retrieved.** It surfaces only because H1 cites and
benchmarks against it; the title and journal look genuine (Analytica
Chimica Acta, a real analytical-chemistry journal that also published
Fernandez Pierna & Massart 2000, cited independently by H1's own ref [1]),
but this project has not searched for or read it directly. Worth a normal
retrieval pass if the dissertation wants the WHACO baseline as a primary
source rather than through H1's secondhand description of it.

---

## Already held - do not fetch again

van Dongen 2000 (MCL); Stutzle & Hoos 2000 (MMAS); Otsu 1979 (full text);
Kang & Choi 2014; Sadi et al. 2009; Elazar & Bruckstein 2016 (AntPaP); Hu et
al. 2015; Tseng, Chiang & Yang 2013 (L-NNACO, `10.1109/ICMLC.2013.6890869`);
Lucky & Girsang 2020 (NNACOC); Gao 2016; Held et al. 2015; arXiv 2108.05525;
Handl & Meyer 2007 (P2-12); Boryczka 2009 full text (`10.1016/j.asoc.2008.03.002`,
P3-2, retrieved 2026-08-03 - eprints.bournemouth.ac.uk mirror); He et al.
2012/2013 / MABA (arXiv:1303.4711 = E2 = E3, P3-1, retrieved 2026-08-03).
**Pass 4, 2026-08-03, via the maintainer's own library** - A3 (P4-1), A4
(P4-2), A5 (P4-3), Deneubourg 1991/B1 (P4-4), Fred & Jain 2005/C8 (P4-5),
Boryczka 2013 corrigendum/B5 (P4-6), Campello et al. 2013/C7 (P4-7), Campello
et al. 2015/C7's journal companion, partial (P4-8) - all full text.
**Pass 5, 2026-08-03, second batch of maintainer-supplied PDFs** - Chen/Xu/Chen
2004/A6=B7 (P5-1, reclassified out of Section A into Section B), Lumer &
Faieta 1994/B2 (P5-2, closes the last Section-B gap), Yang/Sun/Huang 2002/A6a
(P5-3, new), El-Feghi et al. 2009/B8 (P5-4, new hybrid), Blum 2007 (P5-5,
background/definitional reference, not clustering), Gong et al. 2009 (P5-6,
false lead - not a clustering paper), Zhao 2007/H1 (P5-7, new, fitness-driven
contrast case), Sinha & Jana 2025 (P5-8, false lead - PSO+Affinity
Propagation, no ants at all, partial 16/31 pages) - all full text except
where noted.

---

## Two notes on method

**Kang & Choi 2014 is not indexed in OpenAlex.** Tracing who has cited it in
twelve years cannot be done through the API - it needs Google Scholar by
hand. That trace is what answers whether someone has already built the
hierarchical collapse this project plans as its third stage.

**A lead is not a source.** Of nine names that arrived from external reviews,
seven were confirmed against an index and two were not. That is an ordinary
ratio, and it is also the reason each one is checked: a plausible title with a
plausible year is worth exactly as much as a nonexistent one until the
document is open.

---

## Where the PDFs go

```
literature/pdf/     gitignored - these files have rights holders and do not
                    belong in a public repository
```

File name: `<surname><year>_<key>.pdf`, e.g. `kang2014_achc.pdf`,
`chen2005_digraph_icmlc.pdf`. The mapping from file name to the entry in
`SOURCES.md` is written into the entry when the entry is added, so that
nobody has to match them up by title six months later.

**Eight PDFs are sitting in `tmp/pdf/`, not `literature/pdf/`, as of pass 4
(2026-08-03).** They are identified and recorded in `SOURCES.md` (P4-1
through P4-8), but not yet renamed/moved into the gitignored directory this
project actually uses, since their current filenames are actively misleading
(see SOURCES.md pass 4's "READ THIS FIRST" - `lingchen2005.pdf` is A3,
`chen2005.pdf` is A4, not the reverse). Suggested mapping, for whoever moves
them:
- `tmp/pdf/lingchen2005.pdf` → `literature/pdf/chen2005_digraph_icmlc.pdf` (A3)
- `tmp/pdf/chen2005.pdf` → `literature/pdf/chen2005_a3cd_icnc.pdf` (A4)
- `tmp/pdf/chen2006.pdf` → `literature/pdf/chen2006_dynamicdb.pdf` (A5)
- `tmp/pdf/VX-001986_30-11-2016_11-27-20_abbyy.pdf` → `literature/pdf/deneubourg1991_collectivesorting.pdf` (B1)
- `tmp/pdf/fred2005.pdf` → `literature/pdf/fred2005_evidenceaccumulation.pdf` (C8)
- `tmp/pdf/boryczka2013.pdf` → `literature/pdf/boryczka2013_corrigendum.pdf` (B5)
- `tmp/pdf/campello2013.pdf` → `literature/pdf/campello2013_hdbscan_pakdd.pdf` (C7)
- `tmp/pdf/campello2015.pdf` → `literature/pdf/campello2015_hdbscan_tkdd.pdf` (C7 companion)

**A second batch of eight distinct PDFs (nine uploads, one duplicate)
arrived in pass 5 (2026-08-03)**, also still in `tmp/pdf/`. Recorded in
`SOURCES.md` P5-1 through P5-7. Suggested mapping:
- `tmp/pdf/An Adaptive Ant Colony Clustering Algorithm.pdf` → `literature/pdf/chen2004_asm_a4c_icmlc.pdf` (A6=B7)
- `tmp/pdf/Diversity and adaptation in populations of clustering ants.pdf` → `literature/pdf/lumerfaieta1994_sab.pdf` (B2)
- `tmp/pdf/a-new-clustering-method-based-on-ant-colony-algorithm.pdf` → `literature/pdf/yang2002_aco_clustering.pdf` (A6a)
- `tmp/pdf/an-adaptive-ant-based-clustering-algorithm-with-improved-198iq5b9l1.pdf` → `literature/pdf/elfeghi2009_aaca.pdf` (B8)
- `tmp/pdf/blum2007.pdf` (and its duplicate `blum2007 (1).pdf`, not separately kept) → `literature/pdf/blum2007_aco_intro_his.pdf` (background reference, not numbered)
- `tmp/pdf/gong2009.pdf` → not moved - false lead, not relevant to the retrieval list (see SOURCES.md P5-6)
- `tmp/pdf/zhao2007.pdf` → `literature/pdf/zhao2007_accа_icmlc.pdf` (H1)
- `tmp/pdf/Improved-affinity-propagation-clustering-algorithms-a-PSO-based-approach.pdf` → not moved - false lead, out of scope (PSO + Affinity Propagation, no ants, no pheromone; see SOURCES.md P5-8)

**Pass 6 (2026-08-04):**
- `tmp/pdf/gupta2006.pdf` → `literature/pdf/gupta2006_hds_icdmw.pdf` (C9)

**2026-08-04: all sixteen files above moved.** `tmp/pdf/` is empty of source PDFs;
`literature/pdf/` now holds every retrieved full text under its mapped name.
Nothing left to file.
