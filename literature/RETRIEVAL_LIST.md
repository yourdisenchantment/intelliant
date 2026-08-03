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
| A3 | Chen, L.; Tu, L.; Chen, H.-J. (2005). Data clustering by ant colony on a digraph. ICMLC vol. 3, 1686-1692 | `10.1109/ICMLC.2005.1527216` | [verified] |
| A4 | Chen, L.; Tu, L.; Chen, H. (2005). A Novel Ant Clustering Algorithm with Digraph (A3CD). ICNC, LNCS 1218-1228 | `10.1007/11539117_163` | [verified] |
| A5 | Chen, L.; Tu, L.; Chen, Y. (2006). An Ant Clustering Method for a Dynamic Database. LNCS | `10.1007/11739685_18` | [verified] |
| A6 | Chen, L.; Xu, X.-H.; Chen, Y.-X. (2004). An Adaptive Ant Colony Clustering Algorithm (A4C) | see entry P2-10 | [held, secondhand] |

**A3-A5 are the primary target of this whole list.** They decide whether the
mechanism "pheromone on arcs -> threshold -> components" dates from 2014 or
from 2005. That changes how novelty is stated, not which footnote is used.
A2 was found on 2026-08-03 and is of the same class.

---

## B. The ant-based clustering branch, which this work is not

Ants carrying objects on a grid. The paragraph that separates this project
from that branch currently rests on secondary description.

| # | Work | Identifier | Status |
|---|---|---|---|
| B1 | Deneubourg, J.-L. et al. (1991). The dynamics of collective sorting. SAB 1, 356-365, MIT Press | no DOI | [lead, print] |
| B2 | Lumer, E.; Faieta, B. (1994). Diversity and adaptation in populations of clustering ants. SAB 3, 501-508, MIT Press | no DOI | [lead, print] |
| B3 | Handl, J.; Meyer, B. (2007). Ant-based and swarm-based clustering. Swarm Intelligence 1(2), 95-113 | `10.1007/s11721-007-0008-7` | [verified] |
| B4 | Boryczka, U. (2009). Finding groups in data: Cluster analysis with ants. Applied Soft Computing 9(1) | `10.1016/j.asoc.2008.03.002` | [verified] |
| B5 | Boryczka, U. (2013). **Corrigendum** to B4 | `10.1016/j.asoc.2013.07.012` | [verified] |
| B6 | Boryczka, U. (2006). Finding Groups in Data: Cluster Analysis with Ants. ISDA 2006 (earlier conference version) | `10.1109/isda.2006.151` | [verified] |

**B3 and B4 are different papers by different authors.** Pass 1 merged them;
the error is recorded in the Corrections block of `SOURCES.md` and both must
be fetched separately.

**B5 is not optional.** Citing a paper that has a published corrigendum
without having read the corrigendum is an avoidable finding at a defence.

B1 and B2 are MIT Press proceedings volumes and are usually not open. Try, in
order: ResearchGate, the ACM DL record, any later reprint, and forward
citations in surveys that quote the primary text at length. If neither turns
up, both are recorded as not retrieved and the differentiation paragraph is
marked as resting on a secondary source.

---

## C. Non-ant relatives

What a reviewer asks first: how is this different from Walktrap, or from
evidence accumulation? Only MCL is on record so far.

| # | Work | Identifier | Status |
|---|---|---|---|
| C1 | van Dongen, S. (2000). Graph Clustering by Flow Simulation. PhD, Utrecht | - | [held] |
| C2 | Pons, P.; Latapy, M. (2006). Computing Communities in Large Networks Using Random Walks (Walktrap). JGAA 10(2) | `10.7155/jgaa.00124` | [verified] |
| C3 | Pons, P.; Latapy, M. (2005). Same work, conference version. LNCS | `10.1007/11569596_31` | [verified] |
| C4 | Rosvall, M.; Bergstrom, C. (2008). Maps of random walks on complex networks reveal community structure (Infomap). PNAS 105(4) | `10.1073/pnas.0706851105` | [verified] |
| C5 | Blondel, V. et al. (2008). Fast unfolding of communities in large networks (Louvain). JSTAT | `10.1088/1742-5468/2008/10/p10008` | [verified] |
| C6 | Traag, V.; Waltman, L.; van Eck, N. (2019). From Louvain to Leiden. Scientific Reports 9 | `10.1038/s41598-019-41695-z` | [verified] |
| C7 | Campello, R.; Moulavi, D.; Sander, J. (2013). Density-Based Clustering Based on Hierarchical Density Estimates (HDBSCAN). LNCS | `10.1007/978-3-642-37456-2_14` | [verified] |
| C8 | Fred, A.; Jain, A.K. (2005). Combining multiple clusterings using evidence accumulation. IEEE TPAMI 27(6) | `10.1109/tpami.2005.113` | [verified] |

**C8 is the most underrated line on this page.** The pheromone matrix is a
count of how often stochastic processes crossed an edge; thresholding it and
taking components is structurally the move evidence accumulation makes with a
co-association matrix built from many weak partitions. If the resemblance is
as close as it looks, this is a second predecessor after A1, and it is better
found here than by a reviewer.

C5-C7 are also the comparison set roadmap phase 4 needs.

---

## D. Theory: self-reinforcing walks

A branch nobody has searched. It is also the most plausible home for the
theoretical component whose absence both external reviews named as the main
gap.

| # | Work | Identifier | Status |
|---|---|---|---|
| D1 | Pemantle, R. (2007). A survey of random processes with reinforcement. Probability Surveys 4 | `10.1214/07-ps094` | [verified] |
| D2 | Merkl, F.; Rolles, S. (2005). Edge-reinforced random walk on a ladder. Annals of Probability | `10.1214/009117905000000396` | [verified] |
| D3 | Merkl, F.; Rolles, S. (2011). Correlation Inequalities for Edge-Reinforced Random Walk | `10.1214/ecp.v16-1683` | [verified] |

Start with D1; it maps the branch and supplies the right vocabulary. Fetch
D2-D3 on the survey's guidance rather than blind.

The terminology point sits here too: what this project runs is closer to a
pheromone-reinforced random walk than to ACO - the trajectory is not a
solution, there is no objective function, and pheromone grows from traversal
alone.

---

## E. The multilevel line - bears on the third stage

| # | Work | Identifier | Status |
|---|---|---|---|
| E1 | Liu, X.; Ji, J.; Yang, C. et al. (2014). Ant Colony Clustering Approach Combined with Multilevel Framework for Functional Module Detection. WI-IAT 2014 | `10.1109/wi-iat.2014.145` | [verified] |
| E2 | **MABA, Multi-layer Ant-Based Algorithm** | not found | [lead] |
| E3 | An Ant-Based Algorithm with Local Optimization for Community Detection in Large-Scale Networks (2013) | `arXiv:1303.4711` | [verified; correspondence to the lead not established] |
| E4 | Multilevel ACO for graph partitioning, 2000s, Springer | not identified | [lead] |

**E2 matters more than every other lead combined.** It is described as this
project's own planned scheme: one flat ant pass, each community becomes a
vertex of the next level, repeat on the coarsened graph. If it exists in that
form, the third stage cannot be claimed as a new framework. Neither Crossref
nor OpenAlex returned it; search arXiv by full title and by the acronym.

E3 was found on arXiv and fits one lead by year and topic, but the match is
unconfirmed. Reading it settles whether it is that work or a different one.

---

## F. Thresholding

| # | Work | Identifier | Status |
|---|---|---|---|
| F1 | Otsu, N. (1979). A Threshold Selection Method from Gray-Level Histograms. IEEE TSMC 9(1) | `10.1109/TSMC.1979.4310076` | [held, full text] |
| F2 | Zelnik-Manor, L.; Perona, P. (2004). Self-Tuning Spectral Clustering. NIPS 17 | no DOI | [lead] |

F2 is not indexed by DOI; NIPS 2004 proceedings live on the conference site
and on author pages. Needed for the section on choosing a cut in a sparse
graph.

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

---

## Already held - do not fetch again

van Dongen 2000 (MCL); Stutzle & Hoos 2000 (MMAS); Otsu 1979 (full text);
Kang & Choi 2014; Sadi et al. 2009; Elazar & Bruckstein 2016 (AntPaP); Hu et
al. 2015; Tseng, Chiang & Yang 2013 (L-NNACO, `10.1109/ICMLC.2013.6890869`);
Lucky & Girsang 2020 (NNACOC); Gao 2016; Held et al. 2015; arXiv 2108.05525.

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
