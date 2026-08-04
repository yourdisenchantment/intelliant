# Open questions for the maintainer

Newest pass first. A question stays here until it is answered or
withdrawn; answered ones move into ROADMAP or the backlogs, not into a
deleted file.

---

# Pass 5 - 2026-08-03

You supplied a second batch of eight distinct PDFs in `tmp/pdf/` this pass
(partly library, partly - by your own account - Sci-Hub for your own use).
All eight are identified, read, and recorded (`SOURCES.md` P5-1 through
P5-8). This raises one correction that needs no action from you (informational
only) and one open question about scope.

---

## 1. INFORMATIONAL, no action needed. A6 was misfiled in Section A and has been moved to Section B.

Full text of Chen/Xu/Chen 2004 (`SOURCES.md` P5-1) shows it has no
pheromone, no digraph, and no edge-threshold-into-components step - it is a
grid/agent density method in the Deneubourg/Lumer-Faieta lineage, which its
own reference list cites as its ancestry. The secondhand description this
project carried since pass 2 apparently over-weighted the "ant colony
clustering" title resemblance to the real digraph line. **This does not
touch the novelty finding** - A6 was never one of the three papers (A3-A5)
that finding rests on - but if any earlier draft text cited A6 as evidence
of prior pheromone-digraph clustering work, that citation should be
corrected; A6 (now B7) belongs with the grid-based branch this project
explicitly distinguishes itself from, not with the branch it descends from.

---

## 2. NEW. A genuine fitness-driven "ant colony clustering" line exists (Section H) - is a contrast paragraph worth adding to the related-work chapter?

Two new sources this pass (Yang/Sun/Huang 2002, `SOURCES.md` P5-3, and
Zhao 2007, `SOURCES.md` P5-7) construct complete candidate clusterings with
an ant per solution, score them with an explicit objective (tour length or
sum-of-squared-errors), and deposit pheromone in proportion to that score -
classical Dorigo-style combinatorial ACO (the TSP/QAP family) pointed at
clustering, sharing none of this project's four distinguishing properties.
Nothing found before this pass made this contrast explicit; Sections A, B
and D all either lack an objective function entirely or use one only in a
separate post-processing stage.

This is not a threat to the novelty claim - if anything it strengthens the
contrast, since it shows the "no objective function" property is not the
default even within work that calls itself "ant colony clustering." The
question is only whether the related-work chapter should say this
explicitly (naming Zhao 2007 and Yang/Sun/Huang 2002 as the fitness-driven
counter-example to Sections A/B/Kang & Choi) or leave it implicit. A related,
smaller decision: a third such paper is cited by Zhao 2007 as its own
comparison baseline - Shelokar, Jayaraman & Kulkarni 2004, "An ant colony
approach for clustering" (WHACO), *Analytica Chimica Acta* 509 - and has not
been independently retrieved (`RETRIEVAL_LIST.md` H2, a lead only). Worth a
normal retrieval pass if the contrast paragraph is wanted with a primary
source for WHACO rather than Zhao's secondhand description of it.

---

## 3. INFORMATIONAL, no action needed. The Sci-Hub request is declined again, and will continue to be.

You asked directly this pass for this project to use Sci-Hub itself, arguing
it is useful for keyword search across both paywalled and open-access
papers, and separately noted you use it yourself for your own papers. This
project's position is unchanged from earlier in the conversation and does
not depend on the argument for usefulness: it will not access Sci-Hub or any
similar mirror/aggregator site, regardless of what you do with your own
access. Every source this project cannot retrieve through an open,
non-circumventing route continues to be recorded with the precise reason
(paywall, bot-detection barrier, or simply not found to exist), rather than
a generic "not found" - see, for example, D3's "access barrier, not
paywall" (`RETRIEVAL_LIST.md`) and A8/A9's distinct treatment
(`RETRIEVAL_LIST.md`, `SOURCES.md` P3-13 addendum). That precision is meant
to stand as the record of what was and was not achievable without
circumventing access controls.

---
---

# Pass 4 - 2026-08-03

You supplied eight PDFs from your own library retrieval this pass (in
`tmp/pdf/`), following the priority order this project handed back at the
end of pass 3. All eight are now identified, read, and recorded
(`SOURCES.md` P4-1 through P4-8). This closes pass 3's question #2 and both
gaps in question #3 below - see the withdrawal notes under each. It also
raises one new question that needs your judgment, not this project's.

---

## 1. NEW. A3 and A4 are, to a first approximation, the same paper published twice. How should "the Chen/Tu/Chen digraph line" be counted?

Full text of both is now in hand. **A3** (Chen, Tu, Chen, *Data clustering by
ant colony on a digraph*, ICMLC 2005) and **A4** (Chen, Tu, Chen, *A Novel Ant
Clustering Algorithm with Digraph*, ICNC 2005) share: the same three authors,
the same year, the identical algorithm (same definitions, same equations for
acceptance rate/probability function/heuristic/pheromone update/adaptive
alpha-beta, only renumbered), and - checked directly, not inferred - **the
same experimental result tables to the decimal**: Table 1's 300/600-item
error rates and timings, Table 2's Glass results, and Table 3's Soybean
results are identical between the two papers. The only differences are the
venue (two different 2005 conferences) and the title/prose wording.

**A5** (Chen, Tu, Yixin Chen, *An Ant Clustering Method for a Dynamic
Database*) is different from both - same core algorithm, but with a
genuinely new fourth section (incremental re-clustering under insert/delete)
and a different third author.

This means "three independent papers confirm the pheromone-digraph mechanism
dates to 2005" is not quite the right description - it is closer to two
contributions (the shared A3/A4 experiment, and A5's separate extension),
one of which happens to have been published at two venues. This does not
weaken the novelty finding itself (the mechanism still dates to 2005, still
predates this project, still predates Kang & Choi 2014 by nine years); it
only affects **how you describe the prior-art count** in whatever chapter
states it. Options this project is not choosing between on your behalf:
cite both A3 and A4 as if independent (technically accurate but arguably
misleading about how much independent confirmation exists); cite one and
note in a footnote that the other is a near-duplicate publication; or
describe the line as "two contributions" rather than "three papers" from the
outset. Full comparison in `SOURCES.md` P4-2's Bearing.

---

## 2. WITHDRAWN (was pass 3, #2). The Chen/Tu/Chen 2005-2006 digraph papers are no longer paywalled.

You supplied full text of all three (A3, A4, A5) from your own library this
pass. All read in full; see `SOURCES.md` P4-1/P4-2/P4-3 and question #1
above for the one new finding this unlocked.

---

## 3. WITHDRAWN (was pass 3, #3). Both small gaps are closed.

- **Boryczka's 2013 corrigendum**: read in full (one page, `SOURCES.md`
  P4-6). It is an authorship-only correction (adds Marcin Budka as
  co-author) - nothing substantive to the 2009 method or results. Boryczka
  2009 should now be cited as Boryczka & Budka.
- **Fred & Jain 2005**: read in full (`SOURCES.md` P4-5). The resemblance
  this project proposed (co-association matrix ~ pheromone matrix, both
  thresholded and read out via connectivity/linkage) holds up under the full
  text - it is a genuine structural parallel, with the caveat that Fred &
  Jain's evidence source is an ensemble of independent full clusterings,
  not a single stochastic process walking one graph. The "second
  predecessor after Kang & Choi" framing in `RETRIEVAL_LIST.md` can stand,
  with that caveat attached.

As a bonus beyond the priority list: **B1 (Deneubourg et al. 1991)** was
also supplied and read in full, closing a gap open since pass 1 - confirms
from the primary text that the ancestral "ants sorting objects" mechanism
has no pheromone at all, just locally-sampled memory. And **C7 (HDBSCAN)**,
metadata-only since pass 3, is now full text for both the PAKDD and (20 of
51 pages) the TKDD journal version.

---
---

# Pass 3 - 2026-08-03

Run from `tmp/COWORK_BRIEF.md`, which named two findings that "would change
plans rather than citations" and asked for them to arrive as questions, not
buried in a table. Both were resolved this pass. This section is that
question.

---

## 1. E2 (MABA) is E3. The planned stage-3 "hierarchical collapse" is not new - and it is not new even setting MABA aside.

**He, Dongxiao; Liu, Jie; Yang, Bo; Huang, Yuxiao; Liu, Dayou; Jin, Di.
"An Ant-Based Algorithm with Local Optimization for Community Detection in
Large-Scale Networks."** *Advances in Complex Systems* 15(8):1250036 (2012);
self-archived arXiv:1303.4711 (2013). Full text read this session
(`SOURCES.md` P3-1).

The two leads (E2, described only as "this project's own planned scheme," and
E3, an unconfirmed arXiv match) are the same paper. Its own words: run a
single-layer ant-based routine (SABA) on the network, then "reapplied to a
higher level network where each detected community is regarded as a new
vertex and the sum of the weights of edges between any two communities as the
weight between the new vertices," repeated "until no further improvement on
modularity can be achieved." That is - node for node - the third stage
`RESEARCH_NOTES.md` proposes: cores contracted into absorbing supernodes,
repeat on the coarsened graph.

**What does not survive.** The stage-3 coarsen-and-repeat *structure*, as a
contribution, cannot be claimed as new. And MABA is not even the earliest
prior art for it once found: **Louvain** (Blondel et al. 2008, `SOURCES.md`
P3-7) performs the identical step - community becomes vertex of the next
level, repeat - four years before MABA, and is one of the most-cited methods
in network science. Whatever this project's third stage does, "coarsen a
graph by contracting found clusters into supernodes and repeat" is now the
default move in the field, not a contribution.

**What might still survive - this is the question, not a recommendation.**
MABA's base mechanism has no pheromone and is driven throughout by an
explicit objective function (modularity), which this project's stated
position rules out; Louvain's does too. Kang & Choi (P2-1, pass 2) remains
the mechanism-level predecessor for the base stage - that finding is
unchanged. **What a narrowed stage-3 claim could rest on, if you want one, is
narrower than "we coarsen and repeat": specifically, doing that coarsening on
top of a pheromone-threshold-components base that has no objective function
anywhere, rather than on top of a modularity-optimizing base the way every
example found (MABA, Louvain, and Louvain's own descendant Leiden, P3-8) does
it.** Whether that narrower framing is worth keeping, or whether stage 3
should be reframed or dropped from the novelty claim entirely, is a decision
for you - not one this pass is making. Per `LITERATURE.md`'s own instruction,
a find that makes a planned contribution redundant should arrive as a
question rather than be buried in a table; this is that question.

**Second-order consequence for ROADMAP.md phase 4 and phase-3 planning.**
Louvain and Leiden were already on the comparison-table plan (`RETRIEVAL_LIST.md`
Section C, C5-C7); this finding is an argument for treating them as the direct
comparison for a coarsen-and-repeat stage specifically, not only as general
baselines. MABA itself is not implemented in any library found in this or any
prior pass, so adding it as a numeric baseline (rather than a cited related
work) would be new work and is your call.

---

## 2. The Chen/Tu/Chen 2005 digraph papers are still paywalled - unchanged from pass 2, re-confirmed this pass.

All three DOIs (`10.1109/ICMLC.2005.1527216`, `10.1007/11539117_163`,
`10.1007/11739685_18`) were re-checked against Unpaywall, Semantic Scholar and
IEEE/SpringerLink directly. No open copy exists anywhere. SpringerLink's own
abstract pages remain reachable (A5's abstract was retrieved fresh this pass,
confirming the edge-level threshold language already on file); IEEE's is not
- neither the document page nor Semantic Scholar's record exposes even the
abstract for the ICMLC paper. This remains, as pass 2 said, the single
highest-value retrieval left on the whole list, and it still requires your
own institutional session. Nothing in this pass changes that ask.

---

## 3. Two small gaps worth closing before the related-work chapter is final, neither urgent.

- **Boryczka's 2013 corrigendum** (`10.1016/j.asoc.2013.07.012`) to the 2009
  paper is a one-page notice on ScienceDirect that this session could not
  read (no open copy, publisher elides the abstract even in Semantic
  Scholar's metadata). `RETRIEVAL_LIST.md` calls reading it "not optional"
  before citing the 2009 paper, which is now read in full (`SOURCES.md`
  P3-2). If you open the ScienceDirect page yourself, it is a one-page read.
- **Fred & Jain 2005** (evidence accumulation, `10.1109/tpami.2005.113`) is
  still completely unread in every pass - no abstract, no full text, nothing
  beyond the DOI and author names. `RETRIEVAL_LIST.md` calls this "the most
  underrated line" in the non-ant-relatives section, on the strength of a
  resemblance (thresholding a co-association matrix ~ thresholding a
  pheromone matrix) that this project itself proposed and that has never
  actually been checked against the paper. That is worth flagging plainly:
  right now that comparison rests on this project's own hypothesis, not on
  anything read from Fred & Jain. If it turns out not to hold up, the
  "second predecessor after Kang & Choi" framing in `RETRIEVAL_LIST.md`
  should be softened.

Neither of these changes plans; both are recorded so they do not quietly
become "verified" citations they are not.

---
---

# Pass 2 - 2026-07-29


Per LITERATURE.md "When to come back with a question", and per its instruction
that a find which makes a planned contribution redundant should arrive as a
question rather than buried in a table.

---

## 1. The novelty claim, as currently framed, does not survive. Prior work implements the mechanism.

**Kang, Mun-Su & Choi, Young-Sik (2014), "Ant Colony Hierarchical Cluster
Analysis", Journal of Internet Computing and Services 15(5):95-105,
DOI 10.7472/jksii.2014.15.5.95.** Peer-reviewed, open access, full text read
in this session (SOURCES_PASS2.md #1).

Their algorithm, in their own words and equations:

- a **weighted directed k-nearest-neighbour graph** built from the dataset,
  edge weight a normalised distance;
- ants **hop from node to node along its arcs**, choosing the next node by
  `p_ij ∝ ρ_j^α · π_j^β` - a density heuristic times pheromone, the same shape
  as this project's transition rule and its `use_node_density` fork;
- **every traversal deposits**: `Δτ_ij = log2(o_ij) / ξ_ij`, where `o_ij` is
  the number of ants that used the arc. **No fitness, cost or quality term
  appears anywhere in the update, and no ant is ever ranked against another;**
- the field is then **thresholded** and the **connected components** (strongly
  connected, since the graph is directed) of what remains are the clusters;
- the **removed points are reassigned by a k-NN rule** afterwards - their
  noise absorption - with the explicit note that this step "is not always
  necessary for all applications";
- the threshold is **swept by percentile, 1% at a time over 99 levels**, and
  the nested clusterings form a hierarchy.

Against the four distinguishing properties in the task brief: no objective
function - present; the pheromone field is the answer rather than a search
aid - present; a sparse kNN graph rather than a complete problem graph -
present; a staged pipeline where the threshold is a separate argument to a
separate procedure over the finished field - present. It is not in the
Deneubourg/Lumer-Faieta sense either: the data are fixed graph nodes and only
the arc pheromone changes.

It also anticipates two things the roadmap treats as future work: the
threshold sweep is phase 2's `scan_thresholds`, and the resulting cluster tree
is the hierarchy that RESEARCH_NOTES.md proposes to reach by graph coarsening.

**What still differs, precisely** - this is what a narrowed claim would be
built from, and I am not deciding whether it is enough:

1. They threshold **nodes** by summed incoming-arc pheromone; this project
   thresholds **edges** by edge pheromone. Their node pheromone is a derived
   local density; edge pheromone is the primitive. Whether that difference is
   material is a research question, not a bibliographic one.
2. They take strongly connected components of a digraph; this project takes
   connected components, with a `mutual` symmetrisation fork.
3. Their deposit is a batched `log2(count)` per arc per iteration with no
   trail limits; this project deposits per ant with MMAS `[tau_min, tau_max]`
   clamps and two evaporation schedules.
4. They pick the cut by percentile sweep; this project picks it by Otsu, and
   the whole of phase 2 is about that choice.
5. They never compute what the kNN graph alone gives before the ants run.
   This project added `baseline_ARI` and `ARI_over_baseline` on 2026-07-28
   precisely because that number turned out to be the whole result on
   Gaussian blobs. **On their own reported comparison - ACHC beating HDS on
   F-measure while their three (α,β) settings differ from each other by less
   than the gap to the baselines - the same doubt applies to their numbers as
   to the July calibration here.** That is a genuine, defensible criticism of
   the prior work and a reason the project can still say something new about
   the same mechanism.

**The decision I am not taking.** Whether the dissertation reframes from
"a new mechanism" to "an independently arrived-at mechanism, calibrated" - the
contribution becoming the edge-level formulation, the automatic threshold, the
graph-baseline protocol and the human-in-the-loop staging - or whether you
judge one of the five differences above to be a mechanism-level distinction.
Either way this paper has to be cited and compared head-on; a VAK reviewer or
an arXiv reader will find it, and finding it in the related-work section is
much better than finding it in review.

**Second-order consequence for ROADMAP.md phase 4.** ACHC and HDS should
probably join HDBSCAN and Louvain/Leiden in the comparison table. ACHC is not
implemented in any library I found, so that is real work, and it is a decision
for you rather than a task I should start.

---

## 2. The Chen/Tu digraph papers are the one retrieval that could change the answer, and they are paywalled.

The 2014 paper above cites, and builds on, two 2005 papers by the same three
authors:

- Chen, L.; Tu, L.; Chen, H.-J. "Data clustering by ant colony on a digraph",
  ICMLC 2005, vol. 3, pp. 1686-1692, DOI 10.1109/ICMLC.2005.1527216.
- Chen, L.; Tu, L.; Chen, H. "A Novel Ant Clustering Algorithm with Digraph"
  (A3CD), ICNC 2005, LNCS, pp. 1218-1228, DOI 10.1007/11539117_163.

Their abstracts - retrieved from IEEE and Springer this session - say the
pheromone lives on the **directed edges**, that it is "adaptively updated by
the ants passing it", that "edges with less pheromone are progressively
removed under a list of certain thresholds", and that "strong connected
components of the final digraph are extracted as clusters". That is the
**edge-level** version, which is difference (1) above - the one thing that
currently separates this project from Kang & Choi.

I could not get either full text. IEEE requires an institutional or personal
sign-in (your Chrome has neither active), Springer likewise, neither is open
access per Unpaywall, and no mirror exists. **If you have institutional access
to IEEE Xplore or SpringerLink, these two PDFs are the highest-value
retrieval left in this whole search** - they decide whether difference (1)
survives, and whether their pheromone update carries a quality term.

A third member of the line, Chen, Tu & Chen (2006), "An Ant Clustering Method
for a Dynamic Database", DOI 10.1007/11739685_18, is also paywalled and worth
grabbing in the same session.

---

## 3. Two things pass 1 recorded are wrong and should be corrected in `literature/`.

Not urgent, but they will propagate into a chapter if left.

- **L-NNACO is not "Gao 2016".** It is Tseng, Chiang & Yang, ICMLC 2013,
  DOI 10.1109/ICMLC.2013.6890869. Gao 2016 (Comput. Intell. Neurosci.
  2016:4835932) is an unrelated grid-based method with no pheromone update at
  all. Pass 1's `SEARCH_LOG.md` Category A row should be amended.
- **Handl & Meyer's survey is "Ant-based and swarm-based clustering", Swarm
  Intelligence 1(2):95-113, 2007, DOI 10.1007/s11721-007-0008-7.** Pass-1
  entry #7 conflates it with an Applied Soft Computing paper titled "Finding
  groups in data: Cluster analysis with ants", which is by **Urszula
  Boryczka** (2009). Both exist; they are different papers by different
  authors.

Also worth withdrawing: the pass-1 characterisation of Hu 2015 as using "a
pheromone threshold to split patterns". The publisher's abstract describes a
second pheromone table for search diversification, and nothing in any
retrieved document supports the threshold reading.

---

## 4. Otsu says something useful that the project is not using, and does not say something the project has been attributing to him.

The 1979 paper was retrieved in full and the DOI 10.1109/TSMC.1979.4310076 is
verified three independent ways (SOURCES_PASS2.md #5). Two findings:

**(a) "Otsu degrades on non-bimodal distributions" is not Otsu's claim.** That
passage in his Introduction describes the *valley-seeking* methods he is
replacing. His own advantage 3) is that the threshold comes from "the
integration (i.e., a global property) of the histogram" rather than a local
valley, and Fig. 2 presents a unimodal-peak histogram as a successful case.
His stated caveat is different: thresholds "become less credible as the number
of classes to be separated increases", which is about M > 2, not about
bimodality. The project's own measurements (Otsu landing mid-plateau on
synthetic data, near p97 over active edges on real data) are perfectly good
evidence - they should just be cited as this project's finding rather than as
Otsu's caveat.

**(b) η* is free and would quantify both failure faces.** Otsu defines
η* = σ_B²(k*)/σ_T² ∈ [0, 1] as "a measure to evaluate the separability of
classes (or ease of thresholding) ... or the bimodality of the histogram",
invariant under affine rescaling of the value axis, 0 only for a constant
field and 1 only for a two-valued one. It comes out of the same two cumulative
moments `find_threshold` already computes. Both faces in ROADMAP.md - the
dominant middle plateau on synthetic data, and the `tau_min` spike covering
~97% of edges on real data - are claims about the shape of the pheromone
histogram, and η* turns them into one comparable number per run.

**Question:** do you want `find_threshold` to return η* alongside the cutoff
(it would fit `ThresholdResult`), and the protocol to record it per run
next to `baseline_ARI`? It is a small, well-grounded change with a primary
citation behind it, but it touches public API and a recorded value, so I am
not making it unasked. He also writes explicitly that the method's range "is
not restricted only to the thresholding of the gray-level picture" but covers
"other cases of unsupervised classification in which a histogram of some
characteristic ... is available" - which is the primary-source licence for
this project's non-image use, and closes the weak point pass 1 flagged in its
entry 8b.

---

## 5. The browser is reachable but almost nothing is.

Worth knowing before the next pass is planned. Your Chrome is connected and
working, and IEEE Xplore searches ran in it. But its navigation allowlist
currently permits **only `ieeexplore.ieee.org`**. Every one of these was
refused before any page load, so none of them even presented a login or a
CAPTCHA: `dl.acm.org`, `link.springer.com`, `onlinelibrary.wiley.com`,
`www.scopus.com`, `www.webofscience.com`, `cyberleninka.ru`, `elibrary.ru`,
`scholar.google.com`, `arxiv.org`, `eprints.bournemouth.ac.uk`.

Consequences for the negative-result sentence the dissertation wants to write:

- **IEEE Xplore can now be named.** Seven queries ran against it directly, and
  the results are in SEARCH_LOG_PASS2.md. So can OpenAlex, Crossref and
  Unpaywall, all queried through their public APIs.
- **ACM DL still cannot.** It refused every route available here - HTTP 403 to
  both WebFetch and curl (Cloudflare), and blocked in the extension. Pass 1's
  gap is unchanged.
- **Scopus and Web of Science still cannot**, and would need your institutional
  session in any case.
- **Category G went backwards.** Pass 1 at least reached CyberLeninka's
  CAPTCHA; this pass never reached the site. The three Russian-language titles
  pass 1 recorded are still unretrieved, and a VAK-level paper needs them.

If you can widen the allowlist (or open the pages yourself and hand back the
text), the order of value is: (1) the two 2005 Chen/Tu PDFs, (2) CyberLeninka
and eLibrary, (3) ACM DL for the Category A queries, (4) Handl & Meyer 2007
and the open Boryczka 2009 PDF, which failed here for network reasons rather
than access reasons.

No CAPTCHA was attempted and no credential was entered anywhere in this
session.


---
---

# Pass 1 - 2026-07-28 (resolved, kept for the record)


Per LITERATURE.md "When to come back with a question." Not buried in the
tables - flagged here explicitly.

1. **The novelty claim looks intact after this pass, but the pass was
   shallow on formal databases.** No source combining (kNN graph + pheromone
   accumulation + threshold-read clustering + no objective function) turned
   up across ~20 queries and their citation trails. That is a real negative
   result worth stating in the dissertation - but it used general web search,
   arXiv, and CyberLeninka (blocked) only. ACM DL, IEEE Xplore, Scopus, and
   Web of Science were never queried directly, only seen through pages that
   happened to reference them. Before this negative result is written down
   as "these N databases returned nothing," those four need a direct pass -
   likely needs your institutional access, which this session does not have.

2. **MCL (van Dongen 2000) is the closest structural relative found**, not
   anything in the ACO literature. Worth deciding: does the dissertation's
   related-work section want MCL positioned as "the nearest neighbor to
   compare against," ahead of the ACO-clustering papers? The comparison is
   clean (both skip an objective function and read the result from a
   converged field) and the difference is precise (idempotent deterministic
   matrix vs. sparse stochastic ant sampling + explicit threshold) - see
   `SOURCES.md` #1. This is exactly the kind of find LITERATURE.md flags as
   worth surfacing rather than leaving buried in a table.

3. **Two of the three foundational ant-based-clustering citations
   (Deneubourg 1991, Lumer & Faieta 1994) were not retrievable as primary
   text** - both are pre-web-era conference proceedings (MIT Press SAB
   volumes), reached only through secondary description. A VAK reviewer will
   expect a primary citation to be readable, not cited from a listing page.
   If you have institutional/library access to these proceedings (or a
   personal copy), it's worth pulling the primary text before the
   differentiation paragraph goes into a chapter - what is recorded now in
   `SOURCES.md` #5/#6 is accurate as far as it goes, but is explicitly
   flagged as second-hand.

4. **Category G (Russian-language sources) is the weakest in this pass.**
   CyberLeninka blocked every fetch behind a CAPTCHA; eLibrary was never
   reached at all (no eLibrary URLs surfaced by search). Three promising
   titles are recorded by URL/title only in `SEARCH_LOG.md`. This needs your
   own browser session (logged into CyberLeninka/eLibrary if you have an
   account) to actually read them - I cannot get past the CAPTCHA from here,
   and per the standing rules I should not try to route around it.

None of the four above changes the project's direction on its own - they are
gaps in *this pass's* coverage, not contradictions of anything recorded in
AGENTS.md, ROADMAP.md, or RESEARCH_NOTES.md.
