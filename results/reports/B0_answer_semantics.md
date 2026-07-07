# B0: what "the answer" means once there is no fixed anchor set

**This is a design document. No B1/B2/B3 code follows from this batch —
per the task list's own instruction, this is the STOP point pending
sign-off.**

## The problem, precisely

Today's scoring contract (`embodied/question.py`'s `MCQQuestion`,
`embodied/scoring.py`'s `Choice`) assumes a closed, pre-enumerated option
set: `options: tuple[str, ...]`, `correct_index: int`, and an answer is
`Choice(option_index, confidence)`. Correctness is
`option_index == correct_index` — a string-identity check against a menu
built at question-generation time from `category_anchor_history` (every
anchor a category was EVER observed at across the train days). This
menu is itself privileged information: it is built from the ground-truth
trace, not from anything the agent perceived.

In Phase B there is no such menu. The FM grounds objects and proposes
their locations from pixels; "where is the mug" cannot be answered by
picking a letter from a list the agent never built. Two design problems
follow directly: (1) what does a scoreable answer look like, and (2) how
does the agent (or the scorer) know it's talking about the SAME mug the
question means, when there might be two.

## 1. Answer semantics: recommendation

**Recommended: spatial-overlap scoring against ground truth, using the
agent's OWN discovered candidate set — not open-vocabulary text matching,
and not a disguised return to a fixed menu.**

### The three options, evaluated

**(a) Open-vocabulary text matching.** The agent states a free-text
answer; some process (necessarily another LLM call, since no
deterministic string-matcher can reliably equate "on the counter" with
"kitchen.counter") judges whether it's correct. **Rejected.** This
requires an LLM to grade the FM's own answer — exactly the
self-assessment pattern the calibration through-line (`INDEX.md`'s open
questions, fed by L0 and A1's reconciliation) has now measured as
unreliable in two independent roles. Introducing a third role where an
FM judges FM output, right after measuring the FM to be a poor judge of
its own correctness twice, is building on the least-trusted mechanism
this project has data on. It is also non-deterministic and expensive to
reproduce, unlike every other scoring path in this codebase.

**(b) Spatial-overlap scoring.** The agent's belief is a distribution
over PLACES it has itself discovered and tracked (via B2's classical
map — a place graph or occupancy structure built from real observed
geometry, not a symbolic menu). An answer is "the object is at place P
in my own map," resolved to P's real geometry. Correctness is a
deterministic geometric check: does the ground-truth object's real
position, at the time asked, fall within (or near, under a stated
tolerance) place P's region. **Recommended**, for three reasons:
deterministic and reproducible (matches every existing scoring path in
this codebase — Brier/ECE, `e2_headline_comparison.py`'s clustered
statistics, none of which assume anything about WHAT the candidate
labels mean, only that correctness is a boolean); no new self-assessment
vector; and it cleanly separates B1 (did perception find and track the
right region) from B3 (did the agent reason well about resensing) —
B1's own task description already demands this separation
("testable on its own... so a downstream null is attributable to the
agent, not to a perception bug"), and only spatial scoring delivers it,
because a text-matching judge conflates grounding quality and reasoning
quality into one opaque number.

**(c) Hybrid (fixed menu when expressible, open otherwise).** **Rejected
as stated.** Silently reintroducing the fixed anchor list for "easy"
cases undermines Phase B's own premise and creates a scoring
discontinuity (some questions scored one way, some another, with no
principled boundary). The useful part of this idea survives inside (b):
ground truth INTERNALLY keeps using its existing slot/anchor
representation for its own bookkeeping (unchanged, still generated the
same way) — it is only the AGENT-facing answer channel and the
correctness CHECK that change, from string-identity to spatial-overlap.
That is not really a hybrid; it's (b) done carefully, and is what
"recommended" above means concretely.

### What spatial-overlap scoring needs, verified against the current codebase

- `embodied/world.py`'s `viewpoint_for(anchor: str) -> Optional[Pose]`
  already resolves a symbolic ground-truth anchor to a real navigable
  3D position — confirmed by direct inspection, not assumed. This is
  enough to give ground truth's SIDE of the comparison real geometry
  today, at anchor-region granularity, with zero new tracking machinery.
- `env/state.py`'s `ObjectInstance` already HAS a `position: Optional[
  tuple[float, float, float]]` field in its dataclass — but confirmed
  (via `env/replay.py`, which contains no reference to `.position` at
  all) that nothing currently populates it; the location-change replay
  logic operates purely on symbolic `current_semantic` strings. A
  literal continuous per-instance position for Tier-2b clutter does not
  exist today.
- **Recommendation:** start scoring at anchor-region granularity (reuse
  `viewpoint_for`'s existing resolution, wrap its output as a scoring
  region with a stated radius), not literal-XYZ granularity. This is
  buildable now without touching generation. Finer-grained (literal
  position) scoring is a real future refinement if anchor-region proves
  too coarse (e.g. a large receptacle where "same anchor" doesn't mean
  "spatially close enough"), not a blocker for B1.

## 2. Instance identity: the aliasing problem

Today, `OracleDetection` carries the ground-truth instance label
directly (`label="mug_1"` vs. `"mug_2"`) — identity is never actually
solved, only handed to the agent. Once perception (not an oracle) must
distinguish two same-category objects across time and viewpoint, this
becomes a real, live problem with two distinct parts.

**Part 1 — associating a new detection with an existing tracked
instance, or starting a new one.** Recommended convention: standard
gated nearest-neighbor association — a new detection of category C is
matched to the closest EXISTING tracked instance of category C within a
distance/time-plausibility gate (informed by B2's own dynamics tracker:
an instance that hasn't been seen in a very long time, or whose fitted
kernel says it's unlikely to still be nearby, should require a tighter
spatial match to re-associate). Ambiguous cases (two untracked
candidates within the gate, or no confident match) should SPLIT into a
new provisional instance rather than force an association — under-
linking (more instances than truly exist) is the recoverable failure
mode; over-linking (conflating two real objects into one tracked
history) silently corrupts the dynamics-tracking history B2 is supposed
to maintain, with no way to detect or undo it later. This is the same
asymmetry classical SLAM/MOT systems already default to, not a new
argument invented for this project.

**Part 2 — a real, adjacent problem this batch's task list didn't name
but B0 should flag before B1 is built:** the QUESTION GENERATOR currently
disambiguates instances using oracle-only IDs ("mug_1" vs "mug_2" as
internal strings). Once the agent must resolve identity from its own
imperfect tracking, a question needs to reference a distinguishing
feature the AGENT could plausibly resolve too — e.g., "the mug near the
sink" or "the mug you saw this morning" — not an oracle ID string never
exposed to the agent in the first place (today's questions never expose
raw instance IDs to the agent either, so this is less a regression than
a previously-hidden requirement becoming visible: the CORRECT-INDEX
side of scoring used to secretly rely on the generator's own oracle
labeling being unambiguous, and Phase B needs the QUESTION TEXT itself
to carry enough of a distinguishing cue that a non-oracle agent has a
fair shot at resolving which instance is meant). Flagged as in-scope for
B0's aliasing convention, not deferred — a re-identification convention
that the question generator doesn't also respect is not a complete
convention.

## 3. What survives, what gets rewritten

**Survives unchanged:**
- Brier score / ECE machinery (`embodied/scoring.py`'s `compute_ece`,
  the `ScoringConfig.r_abstain` convention) — both are already generic
  over "a distribution over candidates, one of which may be correct";
  neither assumes anything about what a candidate IS.
- All of `scripts/e2_headline_comparison.py`'s clustered-bootstrap
  statistics — clustering is by scene-day, orthogonal to how a single
  question's correctness is defined.
- The kernel/HSMM machinery itself (`embodied/posterior.py`) — per the
  FM-backbone pivot, this becomes an instrument B2 consults; nothing
  about spatial-overlap scoring changes what it computes, only what
  state space it's asked to track (the agent's own discovered places,
  not a fixed anchor list — same shape of question D1's generalization
  work already had to answer for cross-scene pooling).
- `embodied/world.py`'s `viewpoint_for` — reused directly for ground
  truth's side of the comparison, per section 1 above.

**Rewritten:**
- `MCQQuestion`'s `options`/`correct_index` fields — replaced by
  something carrying a ground-truth POSITION/region (resolved via
  `viewpoint_for`, per section 1) instead of a menu, plus whatever
  distinguishing text the question needs for the aliasing problem
  (section 2, part 2).
- `Choice(option_index, confidence)` — replaced by an answer type
  referencing the agent's own place-node/region (or, if the agent has no
  discovered candidate at all, an `Abstain()` — that type is unaffected).
- `runner.py`'s `_score()` — from `option_index == correct_index` to a
  spatial-overlap check against `viewpoint_for`'s resolved region, using
  a stated tolerance (a new, explicit parameter — this project's own
  "guards fatal" convention says this tolerance belongs in a frozen
  config, versioned, not a magic number in the scoring function).

**New (does not exist today at all):**
- The re-identification/association module (section 2, part 1) — B2's
  own responsibility, not built here.
- A distinguishing-reference convention in question generation (section
  2, part 2) — touches `generation/` and the question factory, not
  scored here but flagged as a real dependency B1/B2 need resolved
  before question generation for Phase B can run.

## Open items this design doc does not resolve (for the sign-off conversation)

- The exact spatial tolerance for "close enough" (a receptacle-sized
  radius? A fixed meters value? Scaled by receptacle size?) — proposed
  as a frozen, versioned config value once B1 exists to measure real
  perception error against, not guessed here.
- Whether question generation for Phase B needs new distinguishing-
  reference logic before or alongside B1 — flagged, not scheduled.
- Whether anchor-region granularity (this doc's recommendation) proves
  too coarse in practice — a B1/B2-stage empirical question, not
  resolvable from a design doc alone.
