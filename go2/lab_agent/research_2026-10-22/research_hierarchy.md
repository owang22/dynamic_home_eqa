# Small-VLM-first hierarchy for the Go2 lab agent: research survey (2026-10-22)

Scope: how a small local VLM (Qwen3-VL-8B) can handle most requests and steps, pass harder decisions up to the
local Qwen3.8-27B or to Opus, and run a fast "watch frames and stop on X" loop. I checked arXiv IDs against the
arXiv API and read the abstracts. Items marked [U] are unverified: they come from memory or from secondary
summaries.

## 0. What our own logs show (go2/data/lab_agent/chats/, 6 sessions, 17 Oliver turns, ~78 tool calls)

- Requests split into three kinds:
  - memory-only questions: "computer tower with coloured lights", "people on Monday", "grey backpack", "near the sofa today", "oliver's shirt colour"
  - named-place driving: "walk to oliver's desk", "go to kang's desk", "walk to yuyang's desk"
  - perception-driven driving: "find oliver and stop", "move to the blue roll of tape", "back up to look at oliver"
- Tool counts: search_memory 20, go_to 13, show_pictures 9, move 6, release 6, turn 5, people_seen 4, stop 3, photo 3, locate 3, list_places 3, look_around 2, status 1.
- The "find oliver and stop" turn (16:18-16:19) used 5 blocking calls about 6-10 s apart: go_to blocked, then
  go_to no_route, then move blocked, then turn, then stop. Opus noticed the person in a photo returned by `move` and
  turned toward them. The dog only stopped because the motion primitives were short. A real "walk until you see X"
  needs a loop that runs faster than the planner.
- The console already has what such a loop needs:
  - `/frame.jpg` is proxied at about 4 Hz.
  - `/agent/stop` is accepted while another call is blocking. The phone STOP button already does this.
  - So a watcher thread can poll frames during a blocking `go_to` and stop the dog itself.
- 17 turns is enough for test cases. It is far too few to train on (see §3).

## 1. LLM cascades, routing and deferral: what escalation signals work

| work | id | escalation signal | key result |
|---|---|---|---|
| FrugalGPT | [2305.05176](https://arxiv.org/abs/2305.05176) | learned scorer on (query, answer) gates a sequential cascade | matches GPT-4 at up to 98% lower cost on its benchmarks |
| AutoMix | [2310.12963](https://arxiv.org/abs/2310.12963) | few-shot self-verification by the small model, then a POMDP router (self-verification is noisy) | >50% cost cut at equal quality |
| Cascades w/ Mixture of Thoughts | [2310.03094](https://arxiv.org/abs/2310.03094) | answer consistency across samples (CoT vs PoT) | about GPT-4 quality at about 40% of the cost [U on the exact %]; consistency is a strong, training-free signal |
| Token-level cascades (Gupta et al.) | [2404.10136](https://arxiv.org/abs/2404.10136) | sequence log-prob has length bias; quantiles of per-token uncertainty, or a small learned head, work better | |
| Hybrid LLM | [2404.14618](https://arxiv.org/abs/2404.14618) | router predicts query difficulty before generating | 40% fewer large-model calls with no quality drop |
| RouteLLM | [2406.18665](https://arxiv.org/abs/2406.18665) | router trained on preference data | >2x cost cut; partly transfers when the model pair changes |
| RouterBench / LLMRouterBench | [2403.12031](https://arxiv.org/abs/2403.12031), [2601.07206](https://arxiv.org/abs/2601.07206) | benchmarks | **many routers, commercial ones included, do not reliably beat simple baselines**; large gap to the oracle |
| Zero-shot confidence for 7-8B | [2605.02241](https://arxiv.org/abs/2605.02241) | mean token log-prob vs RouteLLM-style supervised routers | log-prob AUROC 0.65-0.71 in-distribution and **0.72-0.83 OOD, vs 0.51-0.56 for supervised**; 1,000 labels never beat it |
| Escalation-signal pitfalls (Cisco) | [2610.07354](https://arxiv.org/abs/2610.07354) | semantic entropy | works on GSM8K (AUROC 0.87); on another benchmark a **question-only difficulty rule matched it**. Checklist: always compare against a question-type baseline; the cost of live sampling can exceed simply calling the big model |
| Disagreement-guided routing | [2610.22245](https://arxiv.org/abs/2610.22245) | weak-vs-strong (or weak-vs-weak) disagreement, no labels needed | beats correctness predictors even when labels exist; motivated by edge and robot settings |
| Step-level handoff (STEPGATE) | [2610.07816](https://arxiv.org/abs/2610.07816) | per-step uncertainty of the SLM's tool call | Qwen2.5 1.5B→7B multi-turn: 69% trajectory success with 30% cloud actions, vs 48% local-only, 60% random, 57% query-level routing, 82% strong-only; small scripted test sets |
| LEASH | [2610.22280](https://arxiv.org/abs/2610.22280) | small model's hidden states compared with those from past success/failure trajectories; also watches the strong agent after handoff | OSWorld: Qwen3.5-35B-A3B+escalation 73.7% vs always-Opus-5 72.9% at 19% lower cost; +6.6-11.9 pts over random escalation at matched rate |
| TACIT-Switch | [2608.27911](https://arxiv.org/abs/2608.27911) | learned permanent-handoff time from cumulative trajectory risk | beats task-, step- and fixed-prefix routing on ALFWorld/DABench |
| RSI-Router | [2609.34712](https://arxiv.org/abs/2609.34712) | subtask-level assignment + model-specific "skills" mined from trajectories | DeepSeek-Flash + Qwen3.5-9B at about 48% of the cost, with gains on ALFWorld/WebShop |
| Context-guided routing for stateful agents (Microsoft) | [2610.19292](https://arxiv.org/abs/2610.19292) | route at **user-turn boundaries** with session history | history-aware routing stays within 1 pt of always-expensive; switching models up mid-session breaks the prompt cache and never paid off |
| Bayesian self-escalation | [2608.24087](https://arxiv.org/abs/2608.24087) | escalate during generation via a competence posterior | theory, plus a small code-cascade check |
| Minions | [2502.15964](https://arxiv.org/abs/2502.15964) | the big model **decomposes the task into small local subtasks** | naive local/remote chat recovers 87% of quality; decomposition (MinionS) recovers 97.9% at 5.7x lower remote cost. The small model failed at following multi-step instructions |
| Online cascade learning | [2402.04513](https://arxiv.org/abs/2402.04513) | small model trained online on the LLM's own labels, plus a deferral policy | up to 90% cost cut on streams |
| Learning to defer | [2006.01862](https://arxiv.org/abs/2006.01862) | consistent surrogate loss for classifier+expert | the formal base; needs labels |

**Calibration of small models, which matters most for us**
- Verbalized confidence is overconfident ([2306.13063](https://arxiv.org/abs/2306.13063)).
- For 0.5-14B models, temperature scaling cannot fix models whose confidence stays above 0.5 while accuracy falls below it. A certified 10%-risk autonomy level was reached by no model-task pair ([2608.05064](https://arxiv.org/abs/2608.05064)).
- Stated confidence carries no item-specific self-knowledge beyond shared difficulty ([2605.24299](https://arxiv.org/abs/2605.24299)).
- A dissenting result: self-evaluation quality stays stable as models shrink ([2609.39478](https://arxiv.org/abs/2609.39478)). Large RLHF models verbalize better than they log-prob ([2305.14975](https://arxiv.org/abs/2305.14975)), but that finding does not carry over to 8B models.
- **Ranking for us, best first:**
  1. hard structural signals: tool error, REFUSED, blocked/no_route, invalid call, loops, step budget
  2. question-type rules
  3. mean or min token log-prob of the small model's tool call
  4. k-sample disagreement on the tool call
  5. a learned router or hidden-state probe, only after hundreds of labelled steps exist
  6. verbalized "I'm not sure", the weakest

## 2. Robotics hierarchies (fast/slow, ask-for-help, perception triggers)

**Fast/slow VLA stacks.** All of these pair a big slow VLM with a small fast policy.
- Helix (Figure, [blog](https://www.figure.ai/news/helix)): S2 is a 7B VLM at 7-9 Hz; S1 is an 80M policy at 200 Hz. S2 writes a latent vector to shared memory asynchronously, and the two are trained jointly with a matched latency offset.
- GR00T N1 ([2503.14734](https://arxiv.org/abs/2503.14734)): VLM S2 plus diffusion-transformer S1, trained end-to-end.
- Closely related designs: HiRT ([2410.05273](https://arxiv.org/abs/2410.05273)), RoboDual ([2410.08001](https://arxiv.org/abs/2410.08001)), Fast-in-Slow ([2506.01953](https://arxiv.org/abs/2506.01953)), Hume ([2505.21432](https://arxiv.org/abs/2505.21432)), SmolVLA async inference ([2506.01844](https://arxiv.org/abs/2506.01844)).
- AsyncVLA ([2602.13476](https://arxiv.org/abs/2602.13476)): a big remote model plus an onboard adapter for navigation. It tolerates up to **6 s** of delay to the big model, which is close to our 5-10 s per call.
- These systems hand down latents or actions, not tool calls, so we cannot copy them directly. The lesson that transfers: **the slow model sets a goal, and the fast loop owns reactivity and the stopping decision.**

**Language-level hierarchies.** These are closer to us: the slow model sends down text sub-goals.
- Hi Robot ([2502.19417](https://arxiv.org/abs/2502.19417)): a high-level VLM turns complex prompts and mid-task user feedback into atomic commands for a π0 low level, at about 1 Hz [U on the rate].
- π0.5 ([2504.16054](https://arxiv.org/abs/2504.16054)): one model first predicts a semantic subtask, then the actions.
- RT-H ([2403.01823](https://arxiv.org/abs/2403.01823)): "language motions" as the middle layer, so a human can correct the robot in language.
- Gemini Robotics 1.5 / ER 1.5 ([2510.03342](https://arxiv.org/abs/2510.03342)) is the closest analogue:
  - ER 1.5 is an **orchestrator that calls the VLA as a tool**, with natural-language steps ("pack the rain jacket").
  - The orchestrator does success detection to move to the next step, and it can call web search.
  - Success detection is a listed orchestrator failure mode.
- OneTwoVLA ([2505.11917](https://arxiv.org/abs/2505.11917)) and StreamVLA ([2602.01100](https://arxiv.org/abs/2602.01100)): one model that reasons only at sub-task transitions. StreamVLA skips slow decoding on 72% of steps.
- SayCan ([2204.01691](https://arxiv.org/abs/2204.01691)): LLM plus skill affordances.
- SwiftSage ([2305.17390](https://arxiv.org/abs/2305.17390)): a small model fine-tuned on oracle trajectories acts, and GPT-4 plans sub-goals when needed.

**Navigation.**
- NaVid ([2402.15852](https://arxiv.org/abs/2402.15852)) and Uni-NaVid ([2412.06224](https://arxiv.org/abs/2412.06224)): video-VLM next-step policies. Uni-NaVid covers following, search, QA and person tracking.
- DualVLN ([2512.08186](https://arxiv.org/abs/2512.08186)): the VLM predicts pixel waypoint goals, and a small diffusion policy executes them.
- Mobility VLA ([2407.07775](https://arxiv.org/abs/2407.07775)): a long-context VLM picks a goal frame from a tour video, and a topological graph executes the route. This is the same split as our `locate` → `go_to`.
- **Most relevant: "Structure over Reasoning" ([2610.25130](https://arxiv.org/abs/2610.25130), Go2 quadruped, off-board inference):**
  - Qwen3-VL-4B "can judge whether a single view looks like the goal, but its route reasoning is at chance, its distance estimates nearly constant, its stop votes unreliable".
  - They therefore ask the small model only narrow perceptual questions. They treat its answers as evidence, not actions, and put the stop decision behind a trail-consistency gate.
  - Termination was the dominant lever. Thirteen attempts to hand the small model more of the navigation produced no reliable gain.

**When to ask for help (conformal and introspective).**
- KnowNo ([2307.01928](https://arxiv.org/abs/2307.01928)): conformal prediction over multiple-choice next steps. Execute if the prediction set has one option, otherwise ask, with a coverage guarantee.
- Introspective planning ([2402.06529](https://arxiv.org/abs/2402.06529)) gives tighter sets. CoFineLLM ([2511.06575](https://arxiv.org/abs/2511.06575)) fine-tunes so the sets shrink.
- Explore-until-Confident ([2403.15941](https://arxiv.org/abs/2403.15941)) applies conformal calibration to the **EQA stopping decision**, which is directly relevant to dynamic_home_eqa.
- INSIGHT ([2510.01389](https://arxiv.org/abs/2510.01389)): the time series of token uncertainty predicts help requests much better than static scores.
- All of these need a **few hundred labelled calibration examples**, and the guarantee assumes the data are i.i.d.

**Monitors and triggers: the small model watches, the big model intervenes.**
- Spotter ([2609.36808](https://arxiv.org/abs/2609.36808)): the executor leads, a lightweight local screener watches, and the VLM intervenes only when it flags an error.
- Critic-in-the-Loop ([2603.05185](https://arxiv.org/abs/2603.05185)): a light visual critic hands control to the VLM on stagnation or failure, and uses rules to break retry loops.
- EAMP ([2606.25629](https://arxiv.org/abs/2606.25629)): a prompt-configurable event trigger runs over short clips and wakes a distilled VLM.
- Code-as-Monitor ([2412.04455](https://arxiv.org/abs/2412.04455)): the VLM writes monitor code once, and the code runs in real time.
- VLMs as success detectors: [2303.07280](https://arxiv.org/abs/2303.07280), AHA [2410.00371](https://arxiv.org/abs/2410.00371).
- Streaming video LLMs: VideoLLM-online ([2406.11816](https://arxiv.org/abs/2406.11816)).
- Open-vocabulary detectors fast enough for a 5-30 Hz gate: YOLO-World ([2401.17270](https://arxiv.org/abs/2401.17270)), OWLv2 ([2306.09683](https://arxiv.org/abs/2306.09683)).
- System Switch ([2610.09683](https://arxiv.org/abs/2610.09683)): deferring the least-confident 30% of a fast actor's decisions helps in proportion to the actor's AUROC. Calibration and accuracy are separate properties, so measure the AUROC before relying on a confidence gate.

## 3. Small VLMs as tool-calling agents

- **Capability profile.**
  - EmbodiedBench ([2502.09560](https://arxiv.org/abs/2502.09560)): MLLMs do well on high-level tasks and badly on low-level navigation and manipulation; small open models trail far behind.
  - Embodied Agent Arena ([2610.00854](https://arxiv.org/abs/2610.00854)): even frontier VLM agents often make partial progress and then miss the goal.
  - Agentic AI for robot control ([2602.13081](https://arxiv.org/abs/2602.13081)): the agent behaves non-deterministically and is very sensitive to the prompt, even with a reasoning LLM.
  - Qwen3-VL ([2511.21631](https://arxiv.org/abs/2511.21631)) ships 2/4/8/32B dense models with 256K context and agent and GUI training. I did not verify any published BFCL or tool-calling score for the 8B [U].
- **Failure modes to expect at 8B**, from Minions and LiteSearch-VL [2608.29357](https://arxiv.org/abs/2608.29357):
  - dropping steps from multi-step instructions
  - answering too early without opening pictures
  - picking the wrong tool, or repeating the same query
  - ignoring the image
  - malformed calls
  - hallucinating a sighting from a stored description
  - looping on blocked/no_route
  - weak metric reasoning: distances, yaw, triangulation
- **What helps:**
  - *Fewer tools / tool retrieval.* Cutting the toolset raises small-model accuracy (Less-is-More [2411.15399](https://arxiv.org/abs/2411.15399), RAG-MCP [2505.03275](https://arxiv.org/abs/2505.03275) with 3x better selection, TinyAgent [2409.00608](https://arxiv.org/abs/2409.00608)).
  - *Role split.* Separate planner, caller and summarizer, as in α-UMi [2401.07324](https://arxiv.org/abs/2401.07324). Small models call functions better when the call is framed as plain instruction-following ([2608.22472](https://arxiv.org/abs/2608.22472)).
  - *Constrained decoding.* XGrammar ([2411.15100](https://arxiv.org/abs/2411.15100)) or vLLM guided JSON removes malformed calls. JSONSchemaBench ([2501.10868](https://arxiv.org/abs/2501.10868)) measures coverage. Caveat: strict formats can hurt reasoning ([2408.02442](https://arxiv.org/abs/2408.02442)), so let the model think freely, then constrain only the call.
  - *Macros/skills.* Replace multi-call chains with one deterministic tool. RSI-Router shows model-specific skills are where much of the gain comes from.
  - *Distillation.* SFT on teacher trajectories: FireAct [2310.05915](https://arxiv.org/abs/2310.05915), AgentTuning [2310.12823](https://arxiv.org/abs/2310.12823), Agent Distillation [2505.17612](https://arxiv.org/abs/2505.17612).
    - LoRA-SFT is the strongest in-distribution method from 0.6B to 32B and beats full fine-tuning ([2609.17848](https://arxiv.org/abs/2609.17848)).
    - LiteSearch-VL found that SFT mainly transfers the "agent contract": it took Qwen3-VL-2B from almost always giving no answer to 28% Pass@1. Step-DPO on the five failure modes refined that further.
    - Our 78 calls are too few for this. We need hundreds to low thousands of trajectories (§4).

## 4. Recommendations for our setup

**Architecture: deterministic router → 8B front agent with a narrow toolset → escalation to 27B → Opus, plus a separate fast watch loop.**
This combines Minions-style decomposition, Gemini-ER's orchestrator-plus-tool split and STEPGATE/LEASH step-level escalation.

1. **Route at the turn boundary first** (per 2610.19292, and the 2610.07354 rule that a question-type baseline must be beaten). Use a cheap 8B classification call with constrained output, plus keyword rules:
   - **8B owns these:**
     - `stop` and any "stop"/"halt" (no model at all: a keyword fast path)
     - `status`, `list_places`, `release`
     - `go_to <named place>` when the place resolves by fuzzy match to a `list_places` id
     - "what did you see at/near <place> <time>" and "have you seen <object>": search_memory, with the answer drafted from descriptions plus picture ids
     - running `watch_for` (below)
   - **Goes straight to the big model:**
     - counting distinct people / busy-ness (needs cross-picture identity)
     - `locate` and "go to <a thing>" (triangulation, metric reasoning)
     - "find <person by description>"
     - relocalization, multi-step or ambiguous requests, anything about attributes ("what colour was his shirt")
     - any turn after a REFUSED
2. **Escalate within a turn on hard signals only at first:**
   - a tool returns REFUSED, blocked, no_route or an error
   - the same tool+args twice
   - more than 4 steps
   - a schema-invalid call twice
   - the 8B's final answer cites no picture id it actually opened
   - the 8B emits an `ask_expert` call (give it this tool; it costs little, even though self-reports are weak)

   After that, add mean token log-prob of the tool-call tokens (vLLM `logprobs`) with a threshold tuned on replay. Optionally add k=3 sampled tool calls and escalate on disagreement. Do not use verbalized confidence.
   **Escalate the whole remaining turn, not a single step**: an upward switch loses the prompt cache, and TACIT-Switch argues for permanent handoff. Pass on the transcript so far plus the pictures already opened.
3. **Big model hands sub-goals down as tools, not as chat** (Minions found small models fail at multi-step chat instructions). Opus or 27B plans, then calls *skill tools* that run the small model locally:
   - `watch_for(query, during="go_to|turn_scan|move", max_s, on_hit="stop")`
   - `verify_pictures(ids, question)`, which returns yes/no + box per picture from the 8B
   - `scan_for(query)`, which turns in 45° steps, runs the 8B on each view and stops on a hit

   The big model's calls then go from 5-8 (the "find oliver" turn) to 1-2.
4. **Fast watch loop (new code beside server.py, not a model-level change):**
   - A thread polls `/frame.jpg` at 2-4 Hz while `go_to`/`turn`/`move` blocks.
   - **Stage A** is an open-vocabulary detector (YOLO-World/OWLv2) for the noun ("person", "backpack") at camera rate.
   - **Stage B** runs only on Stage-A hits: Qwen3-VL-8B yes/no for the attribute part ("teal t-shirt"). Use the P("yes") logprob as the score, at about 0.3-1 s per frame on our GPU [U; measure].
   - **Trigger** when k of the last n frames pass (the trail-consistency gate from 2610.25130). The thread calls `/agent/stop` itself, which already works mid-call, and returns the hit frame.
   - The big model, or 27B, confirms on that frame before reporting "found". The 8B never makes the final claim alone; its stop votes are known to be unreliable.
5. **Draft-then-verify for memory questions.**
   - The 8B runs search_memory with multiple wordings and drafts an answer that cites ids.
   - The 27B (local, free) opens those 2-6 pictures and accepts or rejects the draft (AutoMix-style verification, done by a stronger model).
   - Only rejections go to Opus.
   - This keeps "answer from pictures, not descriptions" without Opus on every question.
6. **Shrink the 8B's toolset per route** to 3-5 tools (Less-is-More, RAG-MCP). Use constrained JSON for the call only. Keep the 8B system prompt short and rule-based: the SYSTEM.md style already suits this.

**Evaluation (before any training):**
- *Memory-only turns replay exactly.* The tools are read-only, so freeze the memory at the turn's timestamp (filter records to `t < turn time`) and rerun each logged question through 8B, 8B+27B-verify and full cascade. Measure:
  - final-answer agreement with Opus, judged by Opus or 27B against the opened pictures, with spot checks by eye
  - overlap of cited picture ids
  - rate of hallucinated sightings
  - tool-call validity, step count, wall-clock time
- *Driving turns: teacher-forced next-action agreement.* Give the model the Opus transcript prefix, including the returned photos, and compare its next call: same tool, args within tolerance (place id equal, x/y within 0.5 m, yaw within 30°). Then run a fixed set of 10-20 live tasks on the dog.
- *Escalation curves.*
  - Plot success vs escalation rate, compared with random escalation at the same rate and with the question-type-only rule (the 2610.07354 check).
  - Report time and Opus calls per *completed* task, not per call: per-step errors compound ([2610.19345](https://arxiv.org/abs/2610.19345)).
  - Report watch-loop false-stop and miss rates on recorded walks. The trail frames can serve as an offline video set.
- *Grow the test/training set cheaply.*
  1. Generate a few hundred synthetic memory questions from object names in the descriptions.
  2. Run Opus on them in memory-only mode (no dog needed).
  3. Keep the trajectories whose answers check out by eye or by 27B. These are both test cases and LoRA-SFT data for Qwen3-VL-8B.
  4. Later, add step-DPO on observed 8B failure modes (LiteSearch-VL recipe).

**Risks:**
- **Bad routing on motion is a safety issue, not a quality issue.** Keep STOP outside every model (it already is). Keep 8B moves to named places only, and keep `move` capped at 1.5 m.
- A small model gives confident wrong "not seen" answers. Require cited, opened ids, otherwise escalate.
- Learned routers and probes need labels and break under distribution shift (LLMRouterBench, 2610.07354). Start with rules.
- Conformal guarantees need i.i.d. calibration data. Ours shifts with time and layout.
- Sampling-based gates add latency: with 3 samples, an 8B call can cost more wall-clock time than one 27B call.
- Switching models mid-turn loses the prompt cache, and Claude Code adds overhead on every switch. An Opus "consult" may cost 10-20 s.
- Distillation:
  - Our transcripts hold Opus thinking blocks and tool calls. Check Anthropic's terms before training a model on outputs [U].
  - 78 calls will overfit.
  - Teacher trajectories show only Opus-style successes; there is no recovery data.
- The fast loop depends on `/frame.jpg` latency (cached at 0.25 s) and on the detector working at the dog's 0.4 m camera height. Validate on trail frames first.
