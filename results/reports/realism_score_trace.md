# Realism score trace: what `mean_realism_score` actually is

**FINDING: pure LLM self-grading, never validated against any external
judgment. Every existing "realism ~0.7" figure in this project is an
unvalidated self-assessment and should be read as such until a
correlation study exists.** This is not a hypothetical risk — it's the
same failure mode the calibration through-line (`INDEX.md`'s open
questions) has now measured directly in two other roles (L0's prior
elicitation, A1's decision confidence), and this is a third, more
consequential instance: the self-assigned score doesn't just get
reported, it determines what becomes "ground truth" for the whole
benchmark.

## Where it's computed

`generation/stages.py`'s `score_realism_batch` (lines ~483-547): for each
activity-window's pool of already-grounded displacement candidates, one
LLM call scores every candidate independently on "behavioral
plausibility" in [0, 1] — the `_REALISM_SYSTEM` prompt (same file, lines
~195-221) frames this explicitly as "a separate judgment" from grounding
("Grounding has already confirmed each candidate below is physically
placeable; your job is ... how behaviorally plausible is it").

**The model doing the judging is the same model that proposed the
candidates.** `score_realism_batch`'s own signature defaults
`model: str = DEFAULT_MODEL`, and its one call site
(`generation/pipeline.py`, ~line 314) passes `model=model` — the same
`model` parameter threaded through every other generation stage
(persona, activity trace, displacement proposal) for that run. No
separate judge model is ever configured; confirmed by reading the call
site directly, not inferred from the default alone. In practice this
means Qwen3-14B-AWQ (the pool's own generator — see `l0_rerun.md`'s Step
0 for how that was established) grades its own proposals.

## What the score controls

Not a passive metric — it's load-bearing. `generation/selection.py`'s
`select_displacements` weights candidate selection by
`exp(realism_score / temperature)`: a candidate's self-assigned realism
score directly determines its probability of being CHOSEN as a real
displacement event in the generated household's ground-truth trace.
`mean_realism_score` (written into every `generation_result.json`) is
the mean score of the candidates that were actually selected, not of the
full candidate pool.

## Has it ever been validated against anything external?

**No.** Repo-wide search for any correlation study, human rating, or
external validation of the realism score turned up nothing — the only
matches for "correlat/human judg/validat" near "realism" are unrelated
uses of the word "validate" as a generic function parameter name
elsewhere in the codebase (`generation/stages.py`'s own `validate=
_validate` kwarg, `scripts/e2_headline_comparison.py`'s prose about
statistical correlation, `scripts/yield_projector.py`'s prose about a
different correlation entirely). No human-annotation pass, no held-out
judge model, no comparison to any external plausibility signal exists
anywhere in this project's history.

## The actual numbers

Read directly from all 211 `generation_result.json` files currently on
disk (every scene-day generated so far, pool and frozen scene combined):
**mean_realism_score ranges [0.527, 0.883], mean 0.667** — matching the
"~0.68-0.72" figure already in circulation. This confirms the number is
real and consistently computed; it says nothing about whether 0.667
means "the generated households are behaviorally realistic" or "the
generator model is moderately generous grading its own homework." Those
are different claims and this report resolves neither — it only
confirms which one is currently being made without support.

## What this means for existing and future reports

**Every existing or future citation of a `mean_realism_score` number
must be labeled an unvalidated self-assessment, not evidence of
generation quality, until a correlation study exists.** This is not
asking anyone to distrust generation wholesale — the trace-only
mechanics (grounding, physical placeability, chain consistency,
`trace_validate.py`'s own checks) are unaffected and remain real,
deterministic, non-LLM-judged constraints. It is specifically the
BEHAVIORAL-plausibility layer on top of that — "would a person really do
this" — that has never been checked against anything but the same
model's own opinion of itself.

## What comes next (not this report)

The render tool and diversity/dwell instrumentation (this batch's
parallel items 6b/6c) are the prerequisites for an eventual correlation
study — rendering what the trace claims happened, and measuring whether
categories/profiles actually separate in the underlying dwell-time
distributions, are both necessary before any human-judgment comparison
is meaningful. The human-annotation harness itself is explicitly a later
phase, not built here.

**Traceability:** pure code reading + a direct scan of 211 committed
`generation_result.json` files, no new generation run, no model call.
