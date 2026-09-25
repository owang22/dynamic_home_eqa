# How published agent memories stop growing, and what they leave room for

Checked against the papers on 2026-09-24 by the research agent, at my request, because
this project was about to pick a number for how much memory is allowed and I did not
want to pick another unexplained eight. Every row was verified against a primary
source. Read this before changing any limit in `write_the_notes.py`.

Three limits get confused under the one phrase "how much memory". They are independent
and this project has already been caught mixing two of them up:

1. **how much it may hold** - the total size of the store;
2. **how much it may change in one step** - our eight-edits-a-night limit;
3. **how much of it may be read when answering** - the eight-line window, removed
   2026-09-24.

| system | limits the WRITE step? | limits total SIZE with a number? | tells a contradiction from a repeat? | reports its growth over time? | evidence that a bigger memory answers worse? |
|---|---|---|---|---|---|
| ACE, arxiv 2510.04618 | no | no. Removes near-duplicates by comparing embeddings, either as it goes or only when the context window is exceeded | no. Deduplication is about redundancy; contradiction is not discussed | no. Its token-growth figure is for the rewrite baseline it is beating, not for its own store | not addressed |
| Generative Agents, Park et al. 2023 | no | no, and explicitly says the stream does not fit in the context window | no, nothing about supersession | no | no controlled result |
| MemGPT / Letta | **yes, the one real exception.** A fixed-size working context, written through function calls that error on overflow, flushed by a fraction once a fill threshold is hit | working context: fixed. Archival store: no number | no. Its only edit is `replace`, which overwrites - their own example rewrites "boyfriend named James" into "ex-boyfriend named James" | no | **yes, figure 5.** Baseline accuracy peaks near 25 retrieved documents and falls away through 200, attributed to distraction rather than cost. Its own curve stays flat because it pages instead of pouring everything in |
| MemoryBank | no | no number. Items decay on a forgetting curve unless they are used again, which is down-weighting rather than confirmed deletion | no. Decay is the same whatever made an item stale | not confirmed | not confirmed |
| Mem0 | no | no number | **yes, the only clear answer.** A tool call chooses add, update, delete or do nothing, where delete is for new information that CONTRADICTS the old. Its graph version does not remove a contradicted link, it marks it invalid, stated to be for reasoning about time | not found | not found; reports cost and latency only |
| Reflexion | one reflection per trial by construction, not a chosen limit | **yes, one to three**, justified purely as fitting the context window | no. Oldest drops, no merging | not found | not found |
| Voyager | no | **no, "an ever-growing skill library"** | no | no | no |
| Recursive summarisation, Wang et al. 2308.15022 | no | no explicit ceiling | no. It regenerates one unified memory each step, which is overwriting - the same thing our wholesale arm does | no | not found |

## What follows for this study

**Nobody limits the write step the way we did.** One system of eight bounds writing at
all, and it ties the bound to an actual overflow rather than to a constant. Our eight
edits a night, applied equally to prompt conditions that cost different numbers of
edits per fact, has no precedent here. It was raised to two per object the robot is
asked about on 2026-09-24, with the measurement behind it in
`write_the_notes.edits_schema`.

**Almost nobody puts a number on total size, and the two who do say "we ran out of
context".** So there is no precedent to borrow and no shame in having none. Our own
data answers the question better than a borrowed constant would: the control's memory
saturates at about one line per object after four nights, and the arms told to keep
rival beliefs grow one to three lines a night, reaching roughly 3,000 characters by day
31. The ceiling is set by the house - objects times the number of states each object
has, which we measured at no more than three.

**Only Mem0 separates "the same thing said twice" from "two beliefs that disagree
because the world changed", and its graph version marks the loser invalid instead of
removing it.** That is a published precedent for the rule this study already had for
its own reasons, so it is worth citing: a claim is never deleted, only stopped from
being shown. It also names a gap in our third arm - the prompt offers joining and
setting aside but never contrasts them as answers to those two different situations.

**Nobody reports memory size against time as a result.** If we plot ours, that is a
small point of novelty rather than following a template.

**One real warning.** MemGPT's figure 5 is evidence that an unlimited read window can
cost accuracy through distraction, not only through compute. We removed the read limit
on 2026-09-24 to fix a genuine confound, and that fix moves us toward the setup where
that effect was measured. Our memories are fifteen to sixty short lines against their
twenty-five to two hundred documents, so we are probably near the peak rather than past
it, and `claims_in_reading_order` ranks by relevance rather than pouring everything in.
It is still worth measuring on our own data rather than assuming: re-answer one fixed
set of questions from the same frozen notes with the window at eight, at sixteen and at
everything. Oliver chose to keep the window unlimited and report the cost, so that
measurement is a check on the choice, not a reason to put the limit back.
