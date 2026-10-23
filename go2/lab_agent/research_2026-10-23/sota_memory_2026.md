# Robot memory and strategy memory: 2026 state of the art versus our Go2 setup (2026-10-23)

**Our task families are mostly standard, and our memory design trails 2026 work on three points.**

- **Task families:** finding objects, questions about the past and counting are well covered by 2026 benchmarks.
- **Memory design is behind** on object-centred positions, calibrated "still there" filters and when pictures get
  described.
- **Possible contributions:**
  - real-robot evaluation of change questions and never-seen questions;
  - how much change history survives compression;
  - strategy memory on a real mobile robot, compiled into tools for a small model.

Three research subagents compiled this on 2026-10-23. They opened each cited paper through alphaXiv or arXiv;
the lead session did not re-check them. Most entries are 2026 preprints, not peer reviewed. Model names are as the
papers report them.

## Benchmarks and task suites

| Work | Lab, date | arXiv | What it tests | Key number |
|---|---|---|---|---|
| Sequential-EQA | UMD / UT Austin / UIUC, Jul 26 | 2607.21571 | memory across questions; **real Unitree Go2** | 3D-Mem +33 pts; real robot 20→40% |
| MeMoREval | CMU / Dexmate, Oct 26 | 2610.12561 | 7 categories answered from memory only | frames 70%, descriptions 60%, text 39%, frames + graph 75% |
| EmbodiedMemory-Bench | Zhejiang U, Sep 26 | 2609.28236 | moved objects, failures, experience | Gemini-3-Flash 64.2% |
| DAAAM / OC-NaVQA | MIT, CVPR 26 | 2512.00565 | NaVQA re-annotated with object positions | 0.711 vs ReMEmbR 0.43–0.46 |
| Worth Remembering | MIT, Jun 26 | 2606.03787 | memory gated by surprise | 0.796; keeps 1.7% of frames |
| Spatial Memory by Agents | Princeton / CMU / JHU, Oct 26 | 2610.22736 | memory designed by coding agents | object positions explain 12 of 16 pts |
| S-EMBER | Meta FAIR, Jul 26 | 2607.02689 | streaming recall that must cite evidence | Gemini 3.1 Pro 42.9% vs human 91.4% |
| AbstainEQA | NTU / PKU, Dec 25 | 2512.04597 | questions it should decline | Claude Sonnet 4.5 declines correctly 1.0% of the time |
| EvoNav-Bench | BIGAI / Tsinghua, Sep 26 | 2609.08292 | navigation after objects move | 3D-Mem 92→40% after changes |
| NavHarness | Adelaide / CSIRO, Sep 26 | 2609.34276 | lifelong navigation with file memory | Opus 5 in Claude Code 58.9→81.5 |
| MessyMem | Stanford (Bohg), Sep 26 | 2609.15976 | properties learned by interacting, 3 h runs | 80% vs 51% |
| ECROM / LOOP-Bench | NUS, Sep 26 | 2610.00330 | where things usually are; visibility-weighted misses | 14/15 real-robot finds |
| GESTO | KTH / Google / TUM, Aug 26 | 2608.10886 | how objects were used over time | 0.70 time accuracy |

Evaluation practice to adopt:

1. **Typed answers:** a position within tolerance, a time window, an exact count, yes/no.
2. **Cited evidence:** a picture id, scored together with the answer.
3. **Balance:** about as many unanswerable or false-premise questions as answerable ones.
4. **Controls:**
    - no memory;
    - full information;
    - the key evidence removed;
    - a text-only model.
5. **Frozen-memory replay:** 3 seeds and a held-out set.
6. **Breakdowns:** by how long ago the evidence was seen and how well the spot was covered.
7. **Ground-truth audits:** NaVQA had leaks and wrong time windows.
8. **No raw history stuffed into context:** it lowers accuracy.

## Memory architectures

| Work | Lab, date | arXiv | Idea to borrow |
|---|---|---|---|
| Industrial ReMEmbR | NVIDIA, Oct 26 | 2610.28624 | no captions at storage time; describe only on retrieval (35× less GPU) |
| MEM | Physical Intelligence / Stanford / Berkeley / MIT, Mar 26 | 2603.03596 | two levels: dense video + a language summary updated on subtask success |
| UQ-DAAAM | MIT, Jun 26 | 2606.08277 | caption uncertainty from disagreement across views; re-query uncertain objects |
| RAVEN | Princeton / UPenn, Jun 26 | 2606.25206 | images, no captions; 0.12 fps keeps 90%; Go1 |
| SuperMap | CMU, Aug 26 | 2608.22896 | per-point log-odds, "seen through so it's gone" |
| FOCUS | Toronto, Oct 26 | 2610.05639 | persisted / replaced / removed filter, calibrated on a session with no changes |
| LT-Mem | DGIST, Aug 26 | 2608.19059 | Live / Delta (event log) / Meta stores; per-object volatility |
| PreSIST | UT Austin, Jul 26 | 2607.04057 | survival-time priors from a VLM |
| VideoReloc | TUM / Huawei, Sep 26 | 2609.21804 | relocalize from object boxes in a clip; single frames fail |
| DynaMem | NYU / Meta, Nov 24 | 2411.04999 | remove voxels the camera sees through; say "not found" |

## Strategy and experience memory

| Work | Lab, date | arXiv | Takeaway |
|---|---|---|---|
| ReasoningBank | Google Cloud + UIUC, Sep 25 / Mar 26 | 2509.25140 | lessons from successes and failures; up to +20% |
| SkillOS | UIUC / Google / MIT, May 26 | 2605.06614 | curator trained by RL on how later tasks turn out |
| More Memory, Worse Agents | Indiana / Tencent, Oct 26 | 2610.27406 | **stored lessons can hurt**; generating them per task and discarding after use wins by 3 to 28 pts |
| What Matters in Hi-VLA | Google DeepMind, Jun 26 | 2606.10267 | summaries across episodes +3.6 to 7.7 pp; history within an episode neutral; false "done" signals are costly |
| Reflective Test-Time Planning | Stanford, Feb 26 | 2602.21198 | reflections turned into LoRA weights; Franka 44 vs 21% |
| FAR | CMU, Jul 26 | 2607.01111 | failed attempts become preference data; +11.7% on the real robot |
| REM | Yale / Amazon, Oct 26 | 2610.27377 | full episode record shown only when the agent is struggling |
| SkillCommit | Nanjing / HKUST-GZ, Aug 26 | 2608.15165 | promote a skill only after replay passes |
| Agent Plasticity; Self-Evolving Agents | Berkeley / Meta; Mila / GDM, Oct 26 | 2610.08902; 2610.25858 | evaluation design; retrieval collisions; learning new things costs stability |

## What the major labs are doing

| Lab | System | How it fits ours |
|---|---|---|
| Google DeepMind | Gemini Robotics 1.5 / ER 1.5–1.6 | reasoner calls the action model as a tool, with success detection; same pattern as ours; no persistent memory |
| Physical Intelligence | MEM in π0.6; π0.7 | two-level memory inside the policy; minutes, not days |
| NVIDIA | ReMEmbR → Industrial ReMEmbR; GR00T N1.x | captions on demand, fleet scale |
| Anthropic | Project Fetch (Nov 25, Jun 26) | Claude writing control code for a quadruped; no memory |
| Meta, TRI, OpenAI, Tesla, Figure | | no 2026 robot-memory work found; could be a search gap |

University groups lead on long-term robot memory: MIT (Carlone), Stanford (Bohg), CMU, Princeton.

## Close read: "More Memory, Worse Agents" (arXiv 2610.27406, Indiana U / Tencent, 19 Oct 2026)

**Discarding lessons beat storing them, but the setup favours discarding in five ways, and the claimed mechanism
is barely evidenced.** I read the full text (2,592 lines).

### Setup

- **Benchmarks:** text benchmarks only (ALFWorld, WebShop, ScienceWorld).
- **Backbones:** Llama-4-Scout, Qwen3-Coder-Next, Gemma-4-31B.
- **Schedule:** 10 rounds of 50 training tasks, then held-out tasks with memory frozen, 3 seeds.

| Arm | What it does |
|---|---|
| trajectory memory | keeps raw episodes and their outcomes |
| abstraction memory | keeps lessons, append-only |
| joint memory | keeps both |
| anti-persistence | keeps episodes; writes a lesson for the current task on demand, then discards it |

Anti-persistence also picks among none / imitation / strategic / corrective with a bandit that charges for each
extra call.

### Results

| Measure | Result |
|---|---|
| Average held-out success | anti-persistence 59.9, trajectory 53.5, abstraction 49.0, joint 49.3 |
| Abstraction or joint vs trajectory | worse in 7 of 9 settings |
| Persist vs discard (Table 2, Llama) | +28.0 ALFWorld, +12.3 WebShop |
| Persist vs discard (Table 2, Qwen) | +3.3 ALFWorld, +6.7 WebShop |
| GPT-5.5 admission filter on abstraction memory | 38.7 → 46.0 |
| Filtered lessons added as a frozen layer to anti-persistence | 56 → 44 |
| AppWorld, controlled lesson content | none 23, useful 40, toxic 20 |

### Five ways the setup favours discarding

1. **Dense near-duplicate tasks.** ALFWorld has 6 task templates; there were 500 training episodes. The 5 nearest
   successful episodes nearly solve the new task by imitation, so abstraction adds little and loses detail. With
   sparse, varied episodes, as on a robot with about 50 runs, this may flip.
2. **Persistence is confounded with fitting the task.** Discarded guidance is written for the current task's
   instruction and starting state. Stored lessons were written for other tasks. Nobody tested stored lessons
   rewritten for the current task at retrieval time.
3. **Shared context budget.** Stored lessons take context away from raw evidence. That likely explains why even
   filtered lessons hurt (56 → 44).
4. **Append-only stored lessons with no conditions on when they apply** and no revision when contradicted.
   An admission filter alone recovers 7 points.
5. **Weak models are hurt most.** The gain from discarding shrinks as the backbone gets stronger (Llama +28, Qwen
   +3). The main table also bundles the bandit's mode choice with the discarding.

### Mechanism evidence

The "error reproduction" audit uses supplied aggregates that, in the paper's own words, were "not recomputed …
or verified against event-level provenance". It gives no counts and no uncertainty, so the mechanism is
hypothesised rather than shown. The persist-vs-discard result itself rests on 4 cells × 3 seeds.

### What this means for us

- **The 8B in the hierarchy** reading lessons written by Opus is exactly the vulnerable case: a weak backbone
  with stored guidance.
- **Robot data is sparse and varied,** with a world that changes, unlike their dense, unchanging text tasks.
- **Experiment to run:**
    - Arms: raw episodes; stored lessons; on-demand lessons; stored lessons that are verified, conditioned, and
      rewritten for the current task.
    - Vary the backbone: Opus vs the 8B.
    - Vary the data regime: dense vs sparse, and before vs after a staged routine shift.
