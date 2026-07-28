# Questions for the maintainer

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
