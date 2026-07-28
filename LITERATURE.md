# Literature protocol

How a search is run and what it must produce. The specific question comes from
the maintainer; this is the process that applies to any of them.

The output feeds a dissertation. That sets the standard: a claim about what
some paper says has to be traceable to that paper, by anyone, later.

## The one rule

**Never cite from memory.** Not a title, not a year, not "X showed that Y".
Every statement about a source must come from a document that was actually
retrieved during this search, and the record must say where it came from.

A plausible citation that turns out not to exist is worse than a gap. A gap
gets filled; a fabricated reference destroys the credibility of everything
around it, including the parts that were right.

If a source cannot be retrieved, that is recorded as not retrieved. It is
never filled in from recollection.

## Search for answers, not for papers

"Find papers about ant colony clustering" produces a pile. A search is aimed
at questions, and each source is read for whether it answers them.

The questions come with the task. Whatever they are, hold them fixed across
every source so the results form a table rather than a set of summaries. If a
source raises a question worth adding to the list, add it and say so - do not
answer it silently for that source alone.

## Where it goes

```
literature/SOURCES.md      cumulative, one entry per source
literature/SEARCH_LOG.md   cumulative, one dated section per pass
literature/QUESTIONS.md    what the current pass needs from the maintainer
```

Versioned, for the same reason results are: losing the search log costs more
than losing the sources, because the log is what makes a negative result an
argument rather than an assertion. A pass appends; it does not overwrite.

## Access, and what to do when a source is behind something

Most of what matters is not on the open web. Three cases, and they are
handled differently.

**Paywalled by a publisher.** The in-app browser has no institutional session.
Anything requiring one has to run through the maintainer's own browser, where
those sessions already exist. Say so and hand it over rather than settling for
the abstract - "abstract only" is a permanent weakness in the record, and one
retrieval fixes it.

**Behind a CAPTCHA.** Do not attempt it, do not route around it, and do not
look for a mirror that happens to skip it. Record the URL and the fact that it
was blocked, and hand it to the maintainer, who can open it in their own
session and pass back the text.

**Not digitised.** Pre-web conference proceedings often exist only on paper or
in a library system. Record what is known, mark the depth as second-hand, and
say plainly that a primary citation needs a library.

The rule underneath all three: an inaccessible source is recorded as
inaccessible. It is never approximated from what cites it and then written up
as though it had been read.

## What gets recorded, per source

```
Authors, year, title
Venue - journal, conference, preprint server, or "unpublished"
Identifier - DOI where one exists, otherwise a stable URL
Retrieved - what was actually obtained: full text, preprint, abstract only
Depth - read, skimmed, or abstract only
Answers - one line per question from the task
Bearing - what it means for this project, kept separate from what it says
```

**`Answers` and `Bearing` are different columns and never merge.** The first is
what the source states; the second is the inference drawn here. Mixing them is
how a project's own hypothesis ends up cited as someone else's finding.

**`Depth` is not optional.** An abstract supports "the paper claims X", never
"the paper shows X" - abstracts overstate, and methods sections are where the
disagreements live. Anything resting on an abstract is marked as such and
flagged for retrieval.

Capture the bibliographic fields when the source is found. Going back for them
later does not happen.

## Record the search, not only the findings

Every query run, and what it returned - including the ones that returned
nothing useful. This is the same rule the experiment protocol applies to
parameter grids, for the same reason: "we found nothing" is a claim about the
literature, and only the search record makes it credible.

For a novelty argument the negative result **is** the deliverable. "No prior
work was found" is worth nothing on its own; "these twelve queries across
these databases returned nothing matching this description" is an argument.

Record which databases were used. Google Scholar, the ACM and IEEE libraries,
arXiv, Semantic Scholar and the Russian-language indexes do not return the
same things, and a search that used one is not a survey.

## When to stop

Stop when new queries return sources already seen - saturation, not a count.
Two or three consecutive queries yielding nothing new is the signal.

Follow citations both ways while doing it: what a relevant paper cites, and
what cites it. A single well-placed survey usually gives more coverage than
another ten queries.

## When to come back with a question

- A source contradicts something the project has recorded as established.
- The search suggests the question itself was wrong - the field uses different
  terminology, or the thing being looked for is filed under another name.
- A promising source is paywalled and cannot be obtained.
- Something turns up that would change the project's direction rather than
  its citations.

The last one especially. A find that makes a planned contribution redundant is
the most valuable thing a literature search can produce, and it should arrive
as a question rather than buried in a table.

## What not to do

- Do not soften a find because it is inconvenient. If prior work covers what
  this project claims as new, say so plainly and early.
- Do not pad the record with sources that were found but answer nothing. A
  citation that supports no statement is noise.
- Do not translate a claim into stronger language than the source used.
  "Suggests" and "demonstrates" are different words in a paper for a reason.
- Do not treat a preprint as peer-reviewed, or an unpublished thesis as
  either. Record the venue and let the reader weigh it.
