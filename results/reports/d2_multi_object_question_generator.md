# D2: multi-object question generator

**Question:** Can the question generator produce stems that reference
multiple (2-3) instances at once, each independently scoreable, as the
prerequisite for E3 (opportunistic routing) and for E1's eventual multi-leg
cost-ranking rerun?

**Setup:** Built `generate_multi_object_question` in `embodied/question.py`,
reusing the existing single-object generator per referenced instance
(no duplicated option/distractor logic), bundled into a new
`MultiObjectQuestion` type with a `TargetSpec` per instance.

## Headline numbers

| property | requirement | status |
|---|---|---|
| stems reference 2-3 instances | spec | enforced (`ValueError` outside 2-3, or on duplicate labels) |
| each target independently report-time resolvable | spec | verified identical to solo `generate_mcq_question` output, per target |
| per-instance distractor provenance | spec | each `TargetSpec` carries its own `distractor_provenance` |
| hazard_class = max over targets | spec | `"volatile"` if any target is volatile, else `"stable"` |
| `n_targets` field | spec | present on `MultiObjectQuestion` |
| blind-baseline chance test, extended | spec | new test passes: blind guesser scores within noise of chance per target, pooled across all generated multi-object questions |
| new tests | — | 10 passing (`tests/test_multi_object_question.py`) |

## What this means

The generator is a thin, correctness-preserving wrapper: each target's
options/correct_index/provenance are byte-identical to what a solo
question for that same label would produce, so nothing new needs
validating about single-target correctness — only the bundling logic
(hazard max, n_targets, stem construction, input validation) is new
surface, and it is what the new tests cover. This unblocks E3 (routing
needs multiple genuinely independent targets to route between) and gives
E1 a way to construct scenes where cost-ranking among several legs is
actually exercised (E1's own rehearsal never went past one resense leg —
see `e1_lambda_forensics.md`).

## What is NOT yet supported by these numbers

- **The runner and policies do not consume `MultiObjectQuestion` yet.**
  This batch built the generator only, per its stated scope ("sole
  remaining build blocker for E3," not E3 itself). `QuestionEpisodeRunner`
  and `DecayVoiRouting` still operate on single-target `MCQQuestion` only;
  wiring a multi-object episode loop (scoring each target, letting a
  routing policy choose an order) is E3's own build item, not done here.
- No real multi-object questions have been asked of any policy — this
  report validates the generator's construction properties, not any
  policy's behavior on multi-object questions.

**Traceability:** fingerprint `25e52eee014c3c72`, code_hash
`05102535c7dbb01b` (this batch touched `embodied/question.py`, not the four
behavior-bearing modules the hash covers — see `embodied/attribution.py`'s
`_BEHAVIOR_MODULES`). Tests: `tests/test_multi_object_question.py`.
