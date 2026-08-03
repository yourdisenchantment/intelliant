# Open questions for the maintainer

Newest pass first. A question stays here until it is answered or
withdrawn; answered ones move into ROADMAP or the backlogs, not into a
deleted file.

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
