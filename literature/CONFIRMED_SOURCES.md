# Confirmed sources — exact titles for re-retrieval

A flat bibliography, pulled from `SOURCES.md`, of every paper this project
has actually opened and read (full text or a substantial partial read) and
confirmed bears on the project's mechanism — either as a predecessor, a
relative, or a deliberate contrast case. Titles are copied verbatim from the
paper itself (as transcribed into `SOURCES.md` when it was read), not
retyped from memory, so a title-search should reliably find the PDF again
if it is ever lost. Abstract-only entries are marked as such — the title is
still exact, but the paper itself was never opened.

Leads that were never confirmed to exist as citable primary sources (A8, A9,
D3, H2), and false leads that turned out to be off-topic despite surfacing
in a relevant-looking search (Gong et al. 2009, Sinha & Jana 2025), are
listed separately at the end, not mixed in here — see `RETRIEVAL_LIST.md`
and `SOURCES.md` for why each was set aside.

---

## Section A — pheromone on a digraph, threshold, connected components (the mechanism's direct predecessors)

1. Kang, Mun-Su; Choi, Young-Sik (2014). **"Ant Colony Hierarchical Cluster Analysis"** (개미 군락 시스템을 이용한 계층적 클러스터 분석). *Journal of Internet Computing and Services* 15(5):95-105. DOI `10.7472/jksii.2014.15.5.95`. Open access. Full text read (`SOURCES.md` P2-1).

2. Chen, Ling; Tu, Li; Chen, Hong-Jian (2005). **"Data clustering by ant colony on a digraph."** *Proceedings of the Fourth International Conference on Machine Learning and Cybernetics* (ICMLC 2005), Guangzhou, 18-21 August 2005, vol. 3, pp. 1686-1692. DOI `10.1109/ICMLC.2005.1527216`. Full text read (`SOURCES.md` P4-1).

3. Chen, Ling; Tu, Li; Chen, Hongjian (2005). **"A Novel Ant Clustering Algorithm with Digraph"** (A3CD). ICNC 2005, LNCS, pp. 1218-1228. DOI `10.1007/11539117_163`. Full text read (`SOURCES.md` P4-2). **Near-duplicate publication of #2 above** — same authors, same year, same experimental tables to the decimal; only venue and title differ. See `QUESTIONS.md` Pass 4 #1.

4. Chen, Ling; Tu, Li; Chen, Yixin (2006). **"An Ant Clustering Method for a Dynamic Database."** LNAI 3930, pp. 169-178. DOI `10.1007/11739685_18`. Full text read (`SOURCES.md` P4-3).

5. Qin, Ling; Chen, Yixin; Pan, Yi; Chen, Ling (2006). **"A novel approach to phylogenetic tree construction using stochastic optimization and clustering."** *BMC Bioinformatics* 7(Suppl 4):S24. DOI `10.1186/1471-2105-7-S4-S24`. Open access. Full text read (`SOURCES.md` P3-13).

6. Yang, Xin-bin; Sun, Jing-gao; Huang, Dao (2002). **"A New Clustering Method Based on Ant Colony Algorithm."** *Proceedings of the 4th World Congress on Intelligent Control and Automation*, Shanghai, 10-14 June 2002, pp. 2222-2226. IEEE. Bilingual English/Chinese full text. No DOI captured. Full text read (`SOURCES.md` P5-3). Architecturally distinct from #1-4 (classical tour-length-fitness ACO, not a no-objective digraph walk) but early and relevant — see Bearing in P5-3.

---

## Section B — grid/spatial ant-based clustering (the branch this project is not)

7. Deneubourg, J.-L.; Goss, S.; Franks, N.; Sendova-Franks, A.; Detrain, C.; Chrétien, L. (1991). **"The Dynamics of Collective Sorting: Robot-like Ants and Ant-like Robots."** *Proceedings of the First International Conference on Simulation of Adaptive Behavior* (SAB 1990/91), pp. 356-365. MIT Press. No DOI. Full text read (`SOURCES.md` P4-4).

8. Lumer, Erik D.; Faieta, Baldo (1994). **"Diversity and Adaptation in Populations of Clustering Ants."** *Proceedings of the Third International Conference on Simulation of Adaptive Behavior: From Animals to Animats 3* (SAB 1994), pp. 501-508. MIT Press / Bradford Books. No DOI. Full text read (`SOURCES.md` P5-2).

9. Handl, Julia; Meyer, Bernd (2007). **"Ant-based and swarm-based clustering."** *Swarm Intelligence* 1(2):95-113. DOI `10.1007/s11721-007-0008-7`. Full text read (`SOURCES.md` P2-12).

10. Boryczka, Urszula (2009). **"Finding groups in data: Cluster analysis with ants."** *Applied Soft Computing* 9(1):61-70. DOI `10.1016/j.asoc.2008.03.002`. Full text read (`SOURCES.md` P3-2). Should be cited as Boryczka & Budka after the 2013 corrigendum below adds a co-author.

11. Boryczka, Urszula (2013). **"Corrigendum to 'Finding groups in data: Cluster analysis with ants'"** [*Appl. Soft Comput.* 9(1) (2009) 61-70]. DOI `10.1016/j.asoc.2013.07.012`. Full text read (`SOURCES.md` P4-6). One page; authorship correction only (adds Marcin Budka).

12. Boryczka, Urszula (2006). **"Finding Groups in Data: Cluster Analysis with Ants."** ISDA 2006 (earlier conference version of #10). DOI `10.1109/isda.2006.151`. Metadata and reference list only, not full text (`SOURCES.md` P3-4).

13. Chen, Ling; Xu, Xiao-Hua; Chen, Yi-Xin (2004). **"An Adaptive Ant Colony Clustering Algorithm"** (Ants Sleeping Model / A⁴C). *Proceedings of the Third International Conference on Machine Learning and Cybernetics* (ICMLC 2004), Shanghai, 26-29 August 2004, pp. 1387-1392. IEEE, ISBN 0-7803-8403-2. No DOI captured. Full text read (`SOURCES.md` P5-1). **Reclassified 2026-08-03** — previously filed under Section A on a secondhand description; the full text shows no pheromone, no digraph.

14. El-Feghi, I.; Errateeb, M.; Ahmadi, M.; Sid-Ahmed, M.A. (2009). **"An Adaptive Ant-Based Clustering Algorithm with Improved Environment Perception"** (AACA). *Proceedings of the 2009 IEEE International Conference on Systems, Man, and Cybernetics* (SMC 2009), San Antonio, TX, October 2009, pp. 1476-1483. No DOI captured. Full text read (`SOURCES.md` P5-4). A hybrid — grid-based like #7-#13, but adds an actual evaporating pheromone field, the only source found that bridges Sections A and B.

15. Gao, Wei (2016). **"Improved Ant Colony Clustering Algorithm and Its Performance Study."** *Computational Intelligence and Neuroscience* 2016, article 4835932. DOI `10.1155/2016/4835932`. Open access (PMC4709600). Skimmed via full-text fetch (`SOURCES.md` P2-9). Grid/Lumer-Faieta-lineage "data reactor" model, no pheromone.

---

## Section A-adjacent — other surveyed pheromone-clustering variants (objective-driven, comparison-table candidates rather than direct predecessors)

16. Hu, Kai-Cheng; Tsai, Chun-Wei; Chiang, Ming-Chao; Yang, Chu-Sing (2015). **"A Multiple Pheromone Table Based Ant Colony Optimization for Clustering."** *Mathematical Problems in Engineering* 2015, article 158632. DOI `10.1155/2015/158632`. **Abstract only** — full text paywalled (Wiley/Hindawi), never obtained (`SOURCES.md` P2-6).

17. Tseng, Shih-Pang; Chiang, Ming-Chao; Yang, Chu-Sing (2013). **"L-nearest neighbors ant colony optimization for data clustering"** (L-NNACO). *2013 International Conference on Machine Learning and Cybernetics* (ICMLC 2013), Tianjin, vol. 1, pp. 1684-1690. DOI `10.1109/ICMLC.2013.6890869`. **Abstract only** — IEEE Xplore paywall, never obtained (`SOURCES.md` P2-7).

18. Lucky, Lucky; Girsang, Abba Suganda (2020). **"Hybrid Nearest Neighbors Ant Colony Optimization for Clustering Social Media Comments"** (NNACOC). *Informatica* (Slovenia) 44(1):63-74. DOI `10.31449/inf.v44i1.2672`. Open access. Full text read (`SOURCES.md` P2-8). The clearest primary-source statement of the whole ACOC/L-NNACO family: object×cluster pheromone table, elitist deposit, SSE fitness function.

19. Elazar, Gil; Bruckstein, Alfred M. (2016, arXiv preprint; originally ANTS 2016). **"AntPaP: Patrolling and Fair Partitioning of Graphs by A(ge)nts Leaving Pheromone Traces."** arXiv:1608.04511. Full text read (`SOURCES.md` entry 4). Closest-in-spirit "no objective function, pheromone is the answer" example found anywhere — but partitions into a pre-set number of regions, not cluster discovery.

20. Held, Pascal; Dockhorn, Alexander; Krause, Benjamin; Kruse, Rudolf (2015). **"Clustering Social Networks Using Competing Ant Hives."** 2015 Second European Network Intelligence Conference (ENIC). DOI `10.1109/ENIC.2015.18`. **Abstract only** — IEEE paywall (`SOURCES.md` P2-11).

---

## Section C — non-ant relatives (graph clustering / community detection without pheromone)

21. van Dongen, Stijn (2000). **"Graph Clustering by Flow Simulation."** PhD thesis, University of Utrecht. No DOI; mirror PDF at datajobs.com. Full text read (`SOURCES.md` entry 1). MCL — the single closest structural relative found in the whole search.

22. Pons, Pascal; Latapy, Matthieu (2006). **"Computing Communities in Large Networks Using Random Walks"** (Walktrap). *Journal of Graph Algorithms and Applications* 10(2). DOI `10.7155/jgaa.00124`. Abstract retrieved via the arXiv long version, physics/0512106 (`SOURCES.md` P3-5).

23. Pons, Pascal; Latapy, Matthieu (2005). Same work, conference version. LNCS. DOI `10.1007/11569596_31`.

24. Rosvall, Martin; Bergstrom, Carl T. (2008). **"Maps of random walks on complex networks reveal community structure"** (Infomap). *PNAS* 105(4). DOI `10.1073/pnas.0706851105`. Abstract retrieved; Green OA at arXiv:0707.0609 (`SOURCES.md` P3-6).

25. Blondel, Vincent D.; Guillaume, Jean-Loup; Lambiotte, Renaud; Lefebvre, Etienne (2008). **"Fast unfolding of communities in large networks"** (Louvain). *Journal of Statistical Mechanics: Theory and Experiment* 2008(10):P10008. DOI `10.1088/1742-5468/2008/10/p10008`. Abstract retrieved; Green OA at arXiv:0803.0476 (`SOURCES.md` P3-7).

26. Traag, V.A.; Waltman, L.; van Eck, N.J. (2019). **"From Louvain to Leiden: guaranteeing well-connected communities."** *Scientific Reports* 9:5233. DOI `10.1038/s41598-019-41695-z`. Gold OA — full text read at nature.com (`SOURCES.md` P3-8).

27. Campello, Ricardo J.G.B.; Moulavi, Davoud; Sander, Joerg (2013). **"Density-Based Clustering Based on Hierarchical Density Estimates"** (HDBSCAN). LNCS (PAKDD 2013). DOI `10.1007/978-3-642-37456-2_14`. Full text read (`SOURCES.md` P4-7).

28. Campello, Ricardo J.G.B.; Moulavi, Davoud; Zimek, Arthur; Sander, Joerg (2015). **"Hierarchical Density Estimates for Data Clustering, Visualization, and Outlier Detection."** *ACM Transactions on Knowledge Discovery from Data* (TKDD). Journal companion to #27. Partially read, 20 of 51 pages (`SOURCES.md` P4-8).

29. Fred, Ana L.N.; Jain, Anil K. (2005). **"Combining Multiple Clusterings Using Evidence Accumulation."** *IEEE Transactions on Pattern Analysis and Machine Intelligence* 27(6). DOI `10.1109/tpami.2005.113`. Full text read (`SOURCES.md` P4-5).

40. Gupta, Gunjan; Liu, Alexander; Ghosh, Joydeep (2006). **"Hierarchical Density Shaving: A clustering and visualization framework for large biological datasets"** (HDS). *Sixth IEEE International Conference on Data Mining - Workshops* (ICDMW'06). No DOI captured; IEEE catalog 0-7695-2702-7/06. Full text read (`SOURCES.md` P6-1). Kang & Choi's own comparison baseline - builds on Hierarchical Mode Analysis (Wishart, 1968), operates on a full distance matrix rather than a sparse graph, and clusters only the densest subset per level rather than covering every point.

---

## Section D — theory: self-reinforcing random walks

30. Pemantle, Robin (2007). **"A survey of random processes with reinforcement."** *Probability Surveys* 4:1-79. DOI `10.1214/07-ps094`. Also arXiv:math/0610076 (identical, open). Partially read, pp. 1-35 of 79 (`SOURCES.md` P4-9). Section 5 (pp. 48-55, ERRW/VRRW on general graphs) still unread.

31. Merkl, Franz; Rolles, Silke W.W. (2005). **"Edge-reinforced random walk on a ladder."** *Annals of Probability*. DOI `10.1214/009117905000000396`. Also arXiv:math/0501137 (identical, open). Partially read (`SOURCES.md` P4-10).

---

## Section E — the multilevel line

32. He, Dongxiao; Liu, Jie; Yang, Bo; Huang, Yuxiao; Liu, Dayou; Jin, Di (2012/2013). **"An Ant-Based Algorithm with Local Optimization for Community Detection in Large-Scale Networks"** (MABA). *Advances in Complex Systems* 15(8):1250036 (2012); self-archived as arXiv:1303.4711 (2013). DOI `10.1142/S0219525912500361`. Full text read (`SOURCES.md` P3-1).

---

## Section F — thresholding

33. Otsu, Nobuyuki (1979). **"A Threshold Selection Method from Gray-Level Histograms."** *IEEE Transactions on Systems, Man, and Cybernetics* 9(1). DOI `10.1109/TSMC.1979.4310076`. Full text read (`SOURCES.md` P2-5).

34. Zelnik-Manor, Lihi; Perona, Pietro (2004). **"Self-Tuning Spectral Clustering."** *Advances in Neural Information Processing Systems* 17 (NIPS 2004). No DOI; freely hosted at papers.nips.cc / proceedings.neurips.cc. Full text read (`SOURCES.md` P3-12).

35. (arXiv:2108.05525) **"Clustering with UMAP: Why and How Connectivity Matters."** Supporting technical reference for kNN-graph construction, not itself a clustering-mechanism comparison (`SOURCES.md` entry 8a).

---

## Section H — fitness-driven, solution-construction ACO retargeted at clustering (contrast case, not a predecessor)

36. Stützle, Thomas; Hoos, Holger H. (2000). **"MAX-MIN Ant System."** *Future Generation Computer Systems* 16(8):889-914. No DOI captured; preprint mirror at lia.disi.unibo.it. Full text read (`SOURCES.md` entry 2). Not clustering — the textbook definition of "best-so-far ant" that this project's mechanism has no equivalent of.

37. Sadi, S.; Etaner-Uyar, S.; Gündüz-Öğüdücü, Ş. (2009). **"Community Detection Using Ant Colony Optimization Techniques."** MENDEL 2009 (15th International Conference on Soft Computing). No DOI captured; full text hosted at web.itu.edu.tr/etaner/mendel09_2.pdf. Full text read (`SOURCES.md` entry 3).

38. Zhao, Bao-Jiang (2007). **"An Ant Colony Clustering Algorithm."** *Proceedings of the Sixth International Conference on Machine Learning and Cybernetics*, Hong Kong, 19-22 August 2007, pp. 3933-3938. IEEE. DOI unconfirmed against Crossref this pass (catalog number 1-4244-0973-X/07 on the PDF). Full text read (`SOURCES.md` P5-7). The clearest fitness-driven contrast case found: only the best-so-far ant deposits pheromone, in proportion to 1/objective.

39. Blum, Christian (2007). **"Ant Colony Optimization: Introduction and Hybridizations."** *Proceedings of the Seventh International Conference on Hybrid Intelligent Systems* (HIS 2007), Kaiserslautern, pp. 24-29. IEEE. DOI `10.1109/HIS.2007.36`. Full text read (`SOURCES.md` P5-5). Not a clustering paper — a canonical-ACO-definition reference, useful for citing the general fitness-function requirement (its eq. 2) that this project's mechanism lacks.

---

## Leads, not confirmed — do not expect a PDF to exist under these titles without further checking

- Tu, L.; Chen, L.; Shen, J. (2007). "Adaptive Clustering Algorithm by Ants' Optimization." *Journal of Systems Science and Information*. Not found in Crossref, DBLP, or by direct search in any language (`RETRIEVAL_LIST.md` A8).
- Qin, L.; Luo, J.; Chen, Z.; Guo, J.; Chen, L.; Pan, Y. (2006). "Phylogenetic tree construction using self adaptive ant colony algorithm." IEEE Computer Society, proceedings-article `04021071`, conference code `ichit/2006`. Confirmed to exist (IEEE CSDL record), but no PDF found anywhere — what this project has is a search-snippet, not a verified abstract (`RETRIEVAL_LIST.md` A9).
- Merkl, Franz; Rolles, Silke (2011). "Correlation Inequalities for Edge-Reinforced Random Walk." *Electronic Communications in Probability* 16:753-763. DOI `10.1214/ecp.v16-1683`. Gold OA, but the only host (projecteuclid.org) blocks this project's tools with a bot-detection challenge — never bypassed (`RETRIEVAL_LIST.md` D3).
- Shelokar, P.S.; Jayaraman, V.K.; Kulkarni, B.D. (2004). "An ant colony approach for clustering" (WHACO). *Analytica Chimica Acta* 509:187-195. Cited by #38 above as its own comparison baseline; never independently retrieved or verified (`RETRIEVAL_LIST.md` H2).

---

## False leads — surfaced by a relevant-looking search, confirmed on reading to be off-topic

- Gong, Yue-jiao; Xu, Rui-tian; Zhang, Jun; Liu, Ou (2009). "A Clustering-based Adaptive Parameter Control Method for Continuous Ant Colony Optimization." IEEE SMC 2009, pp. 1827-1832. Uses K-means *inside* an ACO optimizer — the reverse of ant-colony clustering (`SOURCES.md` P5-6).
- Sinha, Ankita; Jana, Prasanta K. (2025). "Improved Affinity Propagation Clustering Algorithms: A PSO-Based Approach." *Knowledge and Information Systems* 67:1681-1711. DOI `10.1007/s10115-024-02260-x`. PSO tuning Affinity Propagation — no ants, no pheromone at all (`SOURCES.md` P5-8).
