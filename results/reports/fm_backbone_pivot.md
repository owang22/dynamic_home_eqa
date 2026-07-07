# FM-backbone pivot: architecture decision record

**Decision (2026-07-07): the foundation model becomes the reasoning/
decision backbone. Classical tools (kernel/HSMM, spatial map) are
demoted to instruments the backbone consults for memory and geometry.**
This inverts L1's architecture, where the kernel was the backbone and
the LLM a bottom-level cold-start crutch (Role A) or a decision-time
consumer that never overwrote the posterior (Role B).

## What retires

**L1 T2-T5** — the cold-start Dirichlet backoff wiring (T2), the
cold-start payoff experiment (T3), the Role-B situation-reader policy as
originally scoped (T4), and the composed three-way decision (T5). None
of these were built past T1's interface; nothing is being thrown away
that had running code depending on it. Do not resume this line under
the L1 framing.

## What is kept, not deleted

- **T0's finding** (`l1_design.md`): the fitted kernel's location-axis
  win is real decay-dynamics modeling, not base-rate exploitation
  (2x pooled Brier advantage over a trivial "stay put" predictor, 7x at
  the 4h horizon). This remains true and reusable — it is evidence about
  the classical instrument's own quality, independent of which
  architecture consumes it.
- **T1's interface** (`l1_t1_dirichlet_interface.md`,
  `embodied/posterior.py`'s `shrink_hierarchical_with_llm`,
  `llm_prior/pseudo_counts.py`): shelved, not deleted. May inform B2's
  dynamics-tracking-over-FM-proposed-symbols instrument, which needs
  exactly this kind of "blend a prior with accumulating real data"
  mechanism, just over a different (FM-proposed, not fixed-anchor) state
  space.

## What survives unchanged

- The generation pipeline and validated dynamics — still the benchmark
  and the scoring ground truth.
- The belief/kernel machinery (`embodied/posterior.py`,
  `embodied/belief.py`) — now a consulted instrument the backbone reads,
  not the agent itself.
- Scoring, reports, and guards infrastructure (code_hash/fingerprint
  discipline, cached LLM calls, no-live-calls-in-tests) — unchanged
  conventions, now serving a different architecture.
- The negative results accumulated so far (L0: LLM priors lose to the
  fitted kernel on both axes tested; L1 T0: the kernel's win is real
  dynamics modeling). These are now load-bearing motivation, not just
  findings: a purely classical belief layer is insufficient on its own
  (L0/T0 measured its ceiling), which is part of why the FM must be the
  reasoner, not a bolt-on prior.

## New phase structure

- **Phase A** (known map, oracle perception): does an FM-as-decider beat
  the kernel-as-decider with the world held fixed? De-risking for B, not
  a headline — a modest or null A result does not veto B. A1 (decision
  backbone vs. decay_voi, open comparison, not a confinement), A2 (quick
  native-modality dynamics-reasoning check, explicitly not a rigorous
  study), A3 (scale A1 across the multi-scene pool).
- **Phase B** (unmapped environment, the actual contribution): the FM
  grounds its own state space from perception; classical tools track
  over FM-proposed symbols; no privileged anchor list. B0 (answer
  semantics without a fixed anchor set — blocking design, needs sign-off
  before any B code), B1 (perception/grounding, isolated and validated
  against the oracle before feeding the belief layer), B2 (classical
  memory over FM-proposed symbols), B3 (full loop vs. the strongest
  classical agent that still assumes the known map).

Full task list, standing rules, and sequencing discipline (A before B,
B0 gates all B code, no species-level LLM-capability claims below
multi-scene scale) live in the task list this record was created from,
not duplicated here.

## Status

Phase A, A1 in progress. See `INDEX.md` for the current report list;
L1's own reports remain at their original filenames
(`l1_design.md`, `l1_t1_dirichlet_interface.md`), now marked PAUSED
there rather than moved or edited.
