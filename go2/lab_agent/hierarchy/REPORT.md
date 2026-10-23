# Small/large model hierarchy for the lab agent: overnight 2026-10-23

Built and run with no dog. Nothing was sent to the real console except about 10 read-only `GET /frame.jpg` to time
them. No file outside `hierarchy/` was changed. The agent used 37 of its 40 `claude -p` (Opus) calls. The lead session
re-ran both test scripts after the agent finished: all pass (`tests/test_hierarchy.py` 10/10,
`tests/test_integration.py` 5/5).

Models: Qwen3-VL-8B-Instruct-FP8 on `127.0.0.1:8301` (tmux `vlm8b`, `serve_8b.sh`, utilisation 0.20, 19.5 GB; needs
`VLLM_USE_DEEP_GEMM=0`) as the small model, Qwen3.8-27B on `:8300` as the middle tier, and Opus via `claude -p` as the
big model.

## Results

| question | answer |
|---|---|
| Can the 8B watch the camera and stop the dog? | Yes. On 150 hand-labelled frames, "a person in a teal t-shirt" was right on 20/20 target frames with 0/114 false yes, at 25-57 ms per frame. Against the fake console, stop arrived 0.36 s after the first target frame while `go_to` was still blocking. |
| Can the 8B take stop and named-place moves? | Yes. Stop is a keyword path with no model (0.02 s). The 8B chose the right first action on all 3 logged named-place turns, and on `no_route` it hands the turn up after one `go_to`. |
| Can the 8B answer memory questions alone? | Not yet. On 30 questions checked by eye it scores 0.43, against 0.67 for the 27B and 0.83 for Opus. |
| Does a router help? | Yes, over random escalation at the same Opus rate. Rules plus signals score 0.73 using Opus on 53% of questions (random at that rate: 0.65), with mean time 17 s against 29 s for always-Opus. |

### Watch loop (`watch.py`, `tools.py`, `watch_eval.py`, `fake_console.py`)

- **How it works.** Polls `/frame.jpg` at 3 Hz while `go_to` runs in another thread. Each frame gets one yes/no
  question to the 8B; P(yes) comes from the first token's log-probabilities. It stops the dog when 2 of the last 3
  frames say yes, and returns the hit frames so the big model can confirm. The console URL is required, and the real
  control PC is refused unless `allow_real` is set.
- **Labels** (`watch_data/labels.json`, 150 frames from 16:05-16:27): 20 show the teal shirt; 16 show the person with
  the shirt hidden (left out of per-frame scores); 114 show neither.
- **Per frame:** teal 20/20 with 0/114 false yes at a P(yes) threshold of 0.5 (also 0 at 0.3; 4 at 0.1).
- **Over the sequence:** 2-of-3 gave 9 triggers, 0 false. It caught 4 of 7 target segments, one frame after each
  started; the 3 missed segments never showed the shirt.
- **Control query** ("red t-shirt", which nobody wore): 8/150 false yes and 3 false stops. Five of those frames are the
  same still view of red bags, which a k-of-n gate can't filter. Requiring "Is there a person?" as well cut it to 1
  false stop; the 27B confirm step did not catch that last one (a distant person in navy with an orange print).
- **Timing:** the real `/frame.jpg` takes 3.5-22 ms per GET. The stored frames are 0.5-2.5 s apart, sparser than a live
  3 Hz stream. Only one query was tested, on one afternoon.

### Memory questions (`replay/`)

Test cases:
- **Logged:** 17 turns and 78 tool calls. Memory at each turn is frozen as a prefix of an index snapshot. 23 of 24
  logged `search_memory` / `people_seen` calls reproduce exactly. The 2026-10-22 search code is pinned in
  `replay/memory_2026_10_22.py`, because `memory.py` is changing tonight.
- **Generated:** 30 questions with "now" set to Thu 16:40, answers checked on contact sheets (`replay/sheets/`): 20
  find/attribute, 3 people, 6 negatives and 1 trap (descriptions say "robot arm"; the pictures show an open equipment
  case). Negatives were checked against descriptions only.

How the models are run:
- **Small agent:** one JSON action per step (`{thought, tool, args}`), constrained by the decoding schema; 0 invalid
  actions in all runs.
- **Opus:** `claude -p` with memory-only MCP tools, memory frozen, no console, results cached, call budget enforced.
- **Judge:** the 27B compares the main facts against a reference. Opus re-run against its own logged answers scores
  0.70, which is about the ceiling. A spot check of 12 answers agreed with the judge's direction; it was harsher on 2.

| set | tier | score | median time |
|---|---|---|---|
| generated (30) | 8B v0 | 0.23 | 5 s |
| | 8B v1 (prompt rules) | 0.27 | 5 s |
| | 8B v2 (rules in the decoding schema) | 0.43 | 6.5 s |
| | 27B | 0.67 | 23 s |
| | Opus | 0.83 | 29 s, 7.5 tool calls |
| logged (9, against Opus's log) | 8B v0 / v1 / v2 | 0.28 / 0.50 / 0.44 | |
| | 27B | 0.61 | |
| | Opus re-run (5 turns) | 0.70 | |

Scores: agree = 1, partial = 0.5.

| tier | false "not seen" (of 20) | invented sightings (of 7) |
|---|---|---|
| 8B v2 | 6 | 1 |
| 27B | 1 | 1 |
| Opus | 0 | 0 |

The 8B's main failure is limiting its searches to today, which gives false "not seen" answers. Prompt rules didn't stop
it: in v1 it swapped `since: "00:00"` for `since: "today"`. Taking the choice away in the decoding schema did, cutting
false "not seen" from 17/20 to 6/20.

v2 scores lower than v1 on the logged set for two reasons:
- **L09** ("what colour was Oliver's shirt") names no day, so v2 searched all days and found Tuesday pictures of
  someone in grey.
- **L04** adds "not a busy day", which Opus declined to say.

The router sends both turns to the big model anyway. The 27B's times are inflated because it shared the GPU with the
description backfill.

### Driving turns (next action, given Opus's transcript so far; 52 decision points)

| model | tool right | tool and main argument right | lenient | time per decision |
|---|---|---|---|---|
| 8B | 23 | 17 | 19 | 1.0 s |
| 27B | 26 | 20 | 22 | 5.0 s |

Neither model reproduces any of Opus's 3 "stop now" decisions. That is the argument for letting the watch loop own
the stop.

### Router (`router.py`, `agent.py`)

Rules for the whole turn:
- "stop" or "halt" alone: no model.
- A move to a fuzzy-matched place id: 8B with 7 tools.
- "Have you seen" / "where is": 8B with the memory tools.
- Straight to the big model: people / who / busy, attributes, finding a person, relocalization, multi-step requests,
  going to a thing, and anything unmatched.

On the logged turns, 7 of 17 go to the 8B.

Within a turn, the whole turn goes up (with a handoff transcript) on:
- REFUSED / blocked / no_route / aborted / ERROR in a result
- a repeated call
- more than 4 tool calls
- 2 invalid actions
- an `ask_expert` call
- an answer citing pictures it didn't open

"Strict" also escalates any answer citing no opened picture. "neg_ok" lets a "not seen" answer stand after two
different searches with no time filter. An optional 27B check reviews the pictures the 8B opened; with no pictures it
invents scenes, so that case is forced to "cannot tell".

| policy (30 generated questions) | quality | share sent to Opus | random escalation at that share |
|---|---|---|---|
| always 8B | 0.43 | 0 | |
| always 27B | 0.67 | 0 | |
| always Opus | 0.83 | 1 | |
| question type only | 0.58 | 0.20 | 0.51 |
| rules + signals (strict) | 0.73 | 0.53 | 0.65 |
| rules + signals (neg_ok) | 0.63 | 0.27 | 0.54 |
| neg_ok + 27B check | 0.73 | 0.50 | 0.63 |
| escalate to the 27B only | 0.60 | 0 | |
| 8B, then 27B, then Opus | 0.68 | 0.30 | 0.55 |
| oracle at 0.53 | 0.85 | 0.53 | |

What the signals catch:
- **Strict fires on 11 of 28 turns routed to the 8B.** Only 5 of those answers are wrong; the other 6 are correct "not
  seen" answers.
- **It misses 14 of 19 wrong or partial answers,** because those cite pictures the 8B really opened. The 27B check
  catches some of them (G13, the G19 trap, L03).
- **The 3-tier chain is worse than going straight to Opus,** because the 27B's own signals rarely fire.
- **Escalated turns were scored cold:** the big model started the turn fresh. The live handoff transcript is
  implemented but not scored.

## Recommendations

1. **Register `watch_go_to` and `scan_for` for Opus now** (`integration.register(mcp, server_module)`). Use the
   person-AND rule for people queries and keep the 27B confirm. Test on the dog with Oliver walking past.
2. **Turn on the router only for stop and named-place `go_to`.** Everything else stays with Opus.
3. **Keep memory questions on Opus for now.** To hand them down, use v2 plus strict signals or the 27B check: about
   0.75 quality at about 55% of Opus calls.
   - Re-run `replay/` against tonight's new memory search (SigLIP), which may fix the misses caused by search
     coverage.
   - The other recurring error is giving "near <where the dog stood>" as the thing's location.
4. **For Khang:** use the JSON-action protocol with schema constraints (v2), and `VLLM_USE_DEEP_GEMM=0` for FP8 on this
   GPU.
5. **The 30 generated questions were used to design v2.** Write a fresh set checked by eye before trusting v2's
   numbers.

## Bugs found and fixed in the replay setup

- `claude -p` knows the real date, so in replay it called 10-22 "yesterday". Replays now state the replay time.
- Router rules: "Do not move the dog" counted as a move request, and "shirt" counted as an attribute word.

**Not yet known:** what the real console returns when a `go_to` is stopped mid-way. The fake returns `aborted`, and
`server.py`'s `agent()` raises Refused on that; the watcher handles it. Check on the dog.

## Files

| file | what it is |
|---|---|
| `llm.py` | OpenAI-compatible client |
| `memtools.py`, `mem_mcp.py` | memory tools over a frozen index with no console; the same as an MCP server for `claude -p` |
| `small_agent.py` | 8B agent loop, prompts v0/v1/v2, action schema |
| `router.py`, `agent.py` | turn rules, within-turn escalation, 27B check, `run_turn`, `ConsoleEnv` |
| `watch.py`, `tools.py` | the watch loop; `watch_go_to`, `scan_for`, `verify_pictures` |
| `integration.py` | `register()` for `server.py`, `ServerEnv`; integration notes in its docstring |
| `fake_console.py` | HTTP fake of the console agent API |
| `bigmodel.py` | `claude -p` runner with cache and budget |
| `serve_8b.sh` | 8B server launch script |
| `replay/` | cases, runners, analysis; results in `replay/results/` (earlier versions kept as `*_vN`) |
| `watch_data/` | labelled frames, contact sheets, results |
| `tests/` | end-to-end and integration tests (run as scripts, not with pytest) |
| `logs/` | run logs, `claude_calls.jsonl` |
