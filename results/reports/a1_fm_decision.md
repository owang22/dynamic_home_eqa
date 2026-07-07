# Phase A, A1: FM decision backbone vs. decay_voi (first look, single scene)

**VERDICT: modest/null. On this scene, `fm_decision` does not beat
`decay_voi`.** At comparable travel cost (4.69m Llama / 4.10m Qwen vs.
`decay_voi`'s 4.69m), `fm_decision`'s accuracy matches or trails the
`answer_immediately` floor (0.356 all-questions accuracy, identical to
the floor; 0.696 accuracy-when-answered, actually below the floor's
0.727) for both models tested. `decay_voi` reaches 0.422 / 0.864 at the
same travel budget. This is exactly the kind of outcome Phase A's own
design anticipated as acceptable — de-risking for Phase B, not a
headline, and this result does not veto Phase B.

## Setup

Frozen scene (102343992_family_with_kids), oracle perception, location
axis, all 5 swept `wait_hours` values, all 9 `FROZEN_LABELS` — 45 trials
per policy. Policy set: `answer_immediately` (floor), `always_resense`
(ceiling), `decay_threshold`, `decay_voi` (at the validated binding
`latency_weight=0.01`, see `voi_boundary.md`), and `fm_decision` (A1's
new policy).

**Models:** `fm_decision` was run against BOTH:
- **Llama-3.3-70B-Instruct, AWQ INT4** (`casperhansen/llama-3.3-70b-instruct-awq`)
  — the clean cross-family arm. Meta lineage, genuinely different from
  Qwen (generator) and from Phi-3 (L0's own cross-family pick), and a
  real step up in capability class (70B vs. L0's 14B-class comparison).
- **Qwen3-14B-AWQ** (`Qwen/Qwen3-14B-AWQ`) — the same model that
  generated this pool's ground truth. **CONTAMINATED-REFERENCE**, not the
  headline number — included only to size any same-family advantage, per
  the same convention L0 established.

**Infrastructure note (real, load-bearing):** `FMDecisionPolicy.act()`
runs inside a live habitat_sim episode (`QuestionEpisodeRunner`, under
the `explore-eqa` conda env), which has no `vllm` installed; `vllm`'s own
env has no `habitat_sim`. Installing either into the other's env risked a
real CUDA/torch conflict neither was built to survive. Fixed by
decoupling, not merging: `scripts/serve_llm.py` launches vLLM's own
OpenAI-compatible server (bound to `127.0.0.1` ONLY — verified directly,
and the auto-mode permission layer independently caught and blocked a
first attempt that would have bound to `0.0.0.0` instead) from the env
that has vllm; `llm_prior/http_client.py`'s `HTTPLLMClient` talks to it
over plain HTTP from the habitat_sim env, using only `requests` — no
`vllm` import anywhere in that module. Response shape (`choices[0].
logprobs.content[0].top_logprobs`, a list of `{"token", "logprob"}`
entries) was verified against a real running server before being coded
against, not assumed. A real bug was caught and fixed in the same
pass: Qwen3's thinking-mode-disable flag
(`chat_template_kwargs: {"enable_thinking": false}`, L0's own fix for the
in-process client) was missing from the HTTP client's request body —
would have reproduced L0's exact "reasoning trace eats the completion
budget" failure for the Qwen contaminated-reference arm specifically
(Llama has no thinking-mode concept, so that arm was unaffected either
way). Fixed before the Qwen sweep ran, not after.

## Headline numbers

| policy | n | accuracy (all) | accuracy (answered) | abstain rate | mean travel | mean confidence |
|---|---|---|---|---|---|---|
| answer_immediately (floor) | 45 | 0.356 | 0.727 | 0.511 | 0.00m | 1.00 |
| decay_threshold | 45 | 0.378 | 0.773 | 0.511 | 9.96m | 0.65 |
| **decay_voi** | 45 | **0.422** | **0.864** | 0.511 | 4.69m | 0.61 |
| always_resense (ceiling) | 45 | 0.422 | 0.864 | 0.511 | 17.58m | 1.00 |
| fm_decision (Llama, clean) | 45 | 0.356 | 0.696 | 0.489 | 4.69m | 1.00 |
| fm_decision (Qwen, contaminated) | 45 | 0.356 | 0.696 | 0.489 | 4.10m | 0.99 |

`decay_voi` reaches the ceiling's accuracy (0.422/0.864, matching
`always_resense` exactly) at roughly a quarter of `always_resense`'s
travel — the VoI tradeoff this project has measured before, holding up
again here as the comparison target. `fm_decision`, at similar travel
cost to `decay_voi`, lands at or below the floor on both models. The two
models' accuracy numbers are identical (0.356/0.696) despite different
mean travel (4.69m vs. 4.10m) — read as evidence the two models'
resense/answer PATTERNS differ (different trials trigger resense) while
converging to a similar net accuracy on this small (n=45), single-scene
sample, not as evidence the two runs are secretly identical (the cache
key includes `model_id`; each model was queried independently — see
Setup).

**A real calibration finding, not yet acted on:** `fm_decision`'s mean
confidence (1.00 Llama / 0.99 Qwen) is far higher than its actual
accuracy-when-answered (0.696) — near-total confidence regardless of
correctness. This is confidence read directly off the chosen letter's
renormalized logprob mass among the real answer options (see
`llm_prior/fm_decision.py`'s own `confidence` computation) — when the FM
picks an answer over resense, it does so with very peaked next-token
probability almost every time, which is a known property of chat-tuned
LLM token-level confidence, not necessarily a property of the
underlying belief. This is reported as a measured fact about A1's
confidence signal, not diagnosed further here.

## What this means

On this one scene, the FM decision backbone's `answer-vs-resense` call is
not yet competitive with `decay_voi`'s VoI arithmetic — it travels a
similar distance but doesn't convert that travel into better accuracy
the way `decay_voi` does. This is a real, negative comparison point, not
a confound: the FM was shown the exact same posterior `decay_voi`
computes its own decision from (see Setup), so the gap is in decision
quality given identical information, not in what either policy knows.

Per Phase A's own design principle, this modest result is expected and
does not veto Phase B — Phase A holds perception fixed specifically to
isolate whether reasoning-over-a-known-posterior helps, and a null result
here is itself informative: it suggests the project's actual thesis
(perception-grounding in Phase B) is doing real work, not that an FM
backbone is a bad idea in general.

## What is too thin to call

- **One scene, n=45 per policy.** No confidence intervals are reported —
  matching this project's own established convention for a rehearsal-
  scale first look (see `e1_lambda_forensics.md`, `e2_preliminary.md`'s
  early iterations) rather than fabricating precision a single scene
  can't support. A3 is exactly the task that scales this across the
  pool; nothing here should be read as a stable ranking until that lands.
- Whether `fm_decision`'s underperformance is a prompt-design issue (the
  belief-summary rendering, the decision framing), a genuine reasoning
  gap, or noise at n=45 is not distinguishable from this one run.

## What is NOT yet supported by these numbers

- State axis: `fm_decision` only ran location questions this batch (see
  `llm_prior/fm_decision.py`'s own scope note) — a state-axis variant is
  future work.
- A2 (the FM-as-dynamics-reasoner quick check) has not run yet.
- No claim about LLM reasoning capability in general is made or
  supported here — one model family, one scale, one scene. Per this
  phase's own standing rule, no species-level claim is drawn.

**Traceability:** raw results:
`embodied_results/diagnostics/a1_fm_decision_{llama,qwen}_result.json`
(each stamped with `FrozenConfig.fingerprint()` and `code_hash` via
`write_result_manifest`, called internally by `rerun_frozen_e0`).
Reproduce: `scripts/serve_llm.py --model <model> --port <port>` (from the
vllm env), then `scripts/a1_fm_decision_sweep.py --base-url
http://127.0.0.1:<port>/v1 --model-family {llama,qwen}` (from an env with
habitat_sim, e.g. explore-eqa).

---

## Addendum (2026-07-07): reconciliation — which claim does the null actually support?

**VERDICT: (a) worse decisions on identical information, not (b) lower
abstention from miscalibration.** The two are distinguishable and only
one is what the headline numbers looked like at first read. Paired
per-question analysis, both models, logs only — no new runs.

**Abstain rates are not the story.** `fm_decision` abstains at 0.489
(Llama) / 0.489 (Qwen) vs. `answer_immediately`'s and `decay_voi`'s 0.511
— fractionally *lower*, not dramatically lower, and not the driver of the
accuracy gap by itself.

**`fm_decision` nearly reproduces `answer_immediately`'s behavior
outright.** Paired by question: on the 22 questions both policies commit
to an answer on, correctness matches on **22/22** for both models — not
one disagreement. The only difference from the floor is a single extra
question `fm_decision` chose to answer instead of abstain on (and got
wrong). This means A1, as run, mostly measured "does the FM's
answer/resense head degenerate to the floor's own behavior" — and the
answer is: almost exactly, yes.

**Resensing was attempted more than the top-line bucket count showed, and
essentially never paid off.** `fm_decision` actually resensed
(distance_traveled_m > 0) on 8/45 (Llama) and 7/45 (Qwen) trials, not the
1 the initial summary's bucket classification implied (that count
excluded trials that resensed AND THEN abstained, which is most of them —
7 of 8 for Llama). Of the resense attempts, only one ever converted into
an answer at all, and that one was wrong.

**The sharpest finding: on the exact 3 questions where `decay_voi`
resenses and corrects a wrong belief, `fm_decision` — shown the identical
posterior — answers immediately and is wrong, every time, on both
models.** `candle_1` at wait_hours 1.0, 2.0, and 4.0: `decay_voi`
resenses (2 invocations, 26.37m) and answers correctly; `fm_decision`
answers immediately (0 invocations beyond the first, 0m) and is wrong,
identically on Llama and Qwen. This is the concrete mechanism behind the
accuracy gap on the 22-question overlap (19/22 same correctness, 3/22
differ, all 3 in `decay_voi`'s favor by this exact pattern) — not
miscalibration inflating the answered set, but a real failure to
recognize when the belief summary it was shown warranted a resense that
would have paid off.

**Reading together with the near-1.0 confidence finding:** the picture is
consistent, not contradictory — a policy that is nearly always maximally
confident in its own belief has little internal signal telling it a
resense is worth the trip, which is exactly what "answers immediately and
wrong" on `candle_1` looks like from the inside. But the mechanism here
is a genuine decision-quality failure (declining a resense that would
have helped, given the same information `decay_voi` used correctly), not
merely "answers more often because it never doubts itself." Both are
real; this reconciliation shows the decision-quality failure is the one
actually visible in the paired data, not a hypothesis to accept on the
confidence pattern alone.

**Reproduce:** paired analysis reads only the two existing result files
(`a1_fm_decision_{llama,qwen}_result.json`); no new elicitation, no new
habitat_sim run.
