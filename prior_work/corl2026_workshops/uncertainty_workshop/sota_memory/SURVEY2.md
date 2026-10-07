# SURVEY2: five directions the first survey did not cover

Written 2026-09-23 by a survey agent, extending `results/sota_memory/SURVEY.md`. Read that first; this
document does not repeat it. Where a system is already covered there (Zep/Graphiti, Mem0, MemGPT/Letta,
A-MEM, Memory-R1, MemoryOS, MIRIX, HippoRAG 2, AriGraph, MemoryBank, MemOS, Mem-alpha, SeCom, Hindsight,
CUPMem/STALE, BeliefMem, MemStrata; benchmarks LongMemEval, MemoryAgentBench, LoCoMo, HaluMem, Memora;
and the whole multi-agent-debate literature) it appears here only by name.

Conventions, same as SURVEY.md:
- **[U]** = I did not verify this in the primary source. Everything not marked [U] was read in the paper
  itself (arXiv abstract page, arXiv HTML, or ar5iv HTML) during this survey.
- Citation counts are Semantic Scholar, 2026-09-23. `cites: n/a` means the API rate-limited me, not that
  the paper is uncited.
- **STORED / READ** on each method says whether it changes what the memory holds or what the answering
  model sees at answer time. Our measured failure is at READ: in 807 of 890 questions where the
  recent-sightings buffer was wrong during the disruption, the correct answer was already in its prompt.
  Methods that only change STORED are labelled *unlikely to help us* and the reason is given.

### If you read four things

1. **§0** — MemTrace (arXiv 2606.17328, June 2026) measured our 807-of-890 diagnosis independently, on 835
   knowledge points across 13 memory systems, and got the same 10× ratio. The read-time diagnosis is no longer
   ours. What is still ours is the A→B→A structure and the confidence measurement.
2. **§2.1 and §2.7** — prompting is a measured non-fix, with eight papers behind that claim; the one paper with
   our exact conflict type prices a conflict-aware instruction at **+1.2** on a temporal shift.
3. **§5.1b** — the correction I made to my own agents' "zero reversions" claim. Two unrefereed August 2026
   preprints do have a reversion (TEPA, TANGLE). The gap statement still holds, but only in its corrected form.
4. **§6** — three methods to build, two to avoid, and what the survey changed about the paper's framing.

### Contents

- §0 the diagnosis, already published
- §1 the accepted baselines, and what our five memories actually are
- §2 prompting before architecture
- §3 hypothesis reweighting and regime inference
- §4 memory as a tool, and multi-agent memory
- §5 non-stationarity and transfer, and how empty the gap really is
- §6 recommendation, framing, credibility hygiene, loose ends

---

## 0. Read this first: the diagnosis we thought was ours was published in June

### The single most important paper for us, found outside the five questions

**MemTrace — "Probing What Final Accuracy Misses in Long-Term Memory"** (Xianxuan Long, Zhikai Chen,
Shenglai Zeng, Shouren Wang, Kai Guo, Jiliang Tang, Michigan State; arXiv 2606.17328, 15 June 2026; 2 cites).
Verified in
the HTML. **Its headline finding is our 807-of-890 number, independently measured, and it was published three
months ago.**
- The unit of measurement is a **knowledge point** — one typed fact, not one question row. **835 knowledge
  points (635 substantive, 200 distractors), 20 users, 15,422 question rows, 200,453 scored answers.**
- Every fact is probed along three dimensions: **memory age** (how many sessions ago it appeared),
  **question type** (current state / earlier state / **trajectory of change**), and **evidence condition**
  (present / missing / contradicted-by-false-premise).
- **The number: "Of the 300 probes, 21 are reach misses (7.0%), 220 are retriever-reached but unsolved
  (73.3%)."** Evidence was reachable in about 93% of cases and unused in 73.3% of failures — roughly **10×
  more often reachable-and-unused than missing**. Our figure is 807/890 = 90.7% of our errors with the answer
  already in the prompt, i.e. about 9.7×. **The two numbers agree.**
- **Trajectory questions are where everything collapses**, at saturation (their windows 7-8):
  HippoRAG-v2 current 45.4 / historical 50.9 / **trajectory 13.4**; Mem-T 40.4 / 47.3 / **19.8**;
  best long-context (Gemini-3-Flash) 39.7 / 47.1 / **11.0**. Fresh-to-saturated gaps of **26 to 42 points**
  on trajectory questions for long-context systems.
- 13 configurations across 4 paradigms: long-context (Qwen3.5-35B, Gemini-3-Flash, GPT-5-nano); RAG (**BM25**,
  text-embedding-3-small, Qwen3-Emb, HippoRAG-v2); external memory (Mem0, **SimpleMem**, REMem, AMem);
  agentic memory (MIRIX, Mem-T). No open-weight model near 27B in the primary results.
- **It does not report any fact returning to a previously-held value.**

**One caveat on our own side of the comparison, from `results/confidence_shift_2026-09-20/uq/CLAIM_AUDIT.md`
item 14: our 807-of-890 is the recent-sightings list only, because it is the arm whose prompt can be read.
MemTrace's 10× is across 13 configurations and 4 paradigms. So the fair sentence is that our single arm
replicates their cross-system finding, not that we measured it more broadly than they did. The trial they make
available to us is to repeat the count for the same-hour lookup memory, which also enumerates its sightings —
that is already on our own trial list.**

**A third, weaker corroboration worth one citation.** MERIT / "When Does Memory Help? A Cost-Aware Evaluation
of Long-Term Memory in Tool-Using LLM Agents" (Shweta Mishra, Shashank Mishra; arXiv 2609.05441, July 2026;
cites n/a; two-author preprint, low authority). It asks whether remembered facts change what a tool-using agent
*does*, not what it answers. Memory lifts dependent-task success from 0.00 to 0.55–1.00; embedding retrieval is
unreliable (0.30–0.95 variance) where structured stores hold 0.70–1.00; the best condition per domain delivers
2.7–3.9× its marginal utility per dollar against full replay. **And the number for us: "agents acted on
correctly retrieved updated facts only 55% of the time."** A third independent measurement of the same gap, in
an action setting rather than a QA setting.

**What this does to our paper.** It is no longer novel to claim that memory failure is at the point of use —
MemTrace says it, with a 10× ratio, on 835 facts. Two things are still ours: (i) the **A→B→A** structure,
which MemTrace does not have and which no memory benchmark in this survey has; (ii) the **confidence /
answer-versus-ask** measurement, which MemTrace does not make. We must cite MemTrace up front and state
plainly that our 807/890 replicates its diagnosis in an embodied setting on a local model, rather than
presenting the diagnosis as new. Their "trajectory of change" question type is also the closest published
relative of our cold-question metric and we should say so.

### Two more cross-cutting results that bear on every recommendation below

**"Useful Memories Become Faulty When Continuously Updated by LLMs"** (Dylan Zhang, Yanshan Lin, Zhengkun Wu,
Yihang Sun, Bingxuan Li, Dianqi Li, Hao Peng; arXiv 2605.12978, 13 May 2026, rev. 29 Aug 2026; cites n/a).
Verified from the abstract page. An ARC-AGI Stream environment with three memory actions — **Retain, Delete,
Consolidate** — run over many rounds. **Memory utility rises, then degrades, and can fall below the
no-memory baseline.** "GPT-5.4 fails on **54%** of a set of ARC-AGI problems it had previously solved without
memory", *even when consolidating from ground-truth solutions*. Their recommendation, quoted: robust agent
memory "should treat raw episodes as **first-class evidence** and **gate consolidation explicitly** rather
than firing it after every interaction", and reliable memory needs consolidation "without overwriting the
evidence they depend on".
**This is a direct warning about three of our own arms.** `routine7`, `reflect` and the `facts_*` stores all
consolidate on a fixed nightly schedule with no gate, and we have already found our fact store corrupting
itself four ways before a question was answered (RESULTS.md). This paper is the citation that makes that
finding a contribution rather than an embarrassment, and it is the reason not to answer our problem with more
write-side machinery.

**BEAM — "Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs"** (arXiv 2510.27246;
**ICLR 2026**; cites n/a). 100 conversations of up to **10M tokens**, **2,000 probing questions**, **ten**
abilities including **updating information over time** and **resolving contradictions**. Even 1M-context
models, with and without retrieval, degrade as dialogues lengthen. Its proposed framework **LIGHT** adds a
long-term episodic store, a short-term working memory and a scratchpad of salient facts, for
**+3.5% to +12.69%** over the strongest baselines depending on backbone. I then read the HTML: the ten abilities
are **Abstention, Contradiction Resolution, Event Ordering, Information Extraction, Instruction Following,
Knowledge Update, Multi-hop Reasoning, Preference Following, Summarization, Temporal Reasoning**; knowledge
updates are built from "bullet pairs encoding an initial fact and its later revision", and contradiction
resolution from "three targeted bullet points" injected into the conversation plan. **No fact returns to a
previously-stated value.** Open-weight backbones include **Qwen2.5-32B-AWQ** and Llama-4-Maverick-fp8, so it is
runnable at our scale. Its per-category numbers are in §2.5, and they are brutal.


---

## 1. What are the accepted baselines?

### 1.1 What our five memories actually are

Read out of `src/baselines/patrol/llm.py:memory_lines` so the comparison below is against the code, not
against our own description of it:

| our name | what the answering prompt contains |
|---|---|
| `naive` "recent-sightings list" | the newest **60** sightings **of the queried object**, oldest first, plus up to 40 patrol listings since its last sighting that did not show it |
| `routine` / `routine7` "nightly summary table" | LLM-written notes rewritten each night from that day's movements **plus the previous notes** (routine7 over a 7-day window), plus the object's last **3** sightings, plus up to 6 negative listings |
| `retrieval` "same-time-of-day" | the last **8** sightings, plus up to **10** sightings within **90 minutes** of the query's time of day on other days, plus up to 10 negative listings |
| `reflect` "nightly self-written notes" | notes on **mistakes only**, written each night from that day's corrections, plus the last 10 sightings, plus 6 negative listings |
| `longcontext` "the whole log" | every sighting of the object, up to 200 negative listings, **and the household's entire movement log for every object** |

One thing to notice before the comparison: `naive` is not a buffer. It is filtered to the queried object,
which is a retrieval step with a perfect entity-level retriever. That is a strength for the paper, not a
weakness: it means our failure cannot be blamed on retrieval, which is what most of the memory literature
is actually measuring.

### 1.2 Closest named, published counterpart for each

**`naive` — no published counterpart. It is a control, not a method.**
There is no named method in the literature that is "keep the newest N raw observations about the queried
entity". The nearest citable things are (a) the *recency* term of Generative Agents' retrieval taken alone,
and (b) the fixed-context control that every memory paper runs. Generative Agents (Park, O'Brien, Cai,
Morris, Liang, Bernstein; **UIST 2023**; arXiv 2304.03442; **5637 cites**) scores each memory as
`score = α_recency·recency + α_importance·importance + α_relevance·relevance`, with **all α set to 1**,
recency an exponential decay with **factor 0.995** over sandbox hours since last retrieval, importance an
LLM rating on a 1-10 poignancy scale, and relevance the cosine similarity of embeddings (all verified in
the paper's Memory and Retrieval section). Our `naive` is that score with importance and relevance dropped
and an entity filter added. **Verdict: a variant of a standard control with no named counterpart.** Do not
present it as a method. Present it as what MemoryAgentBench calls a long-context agent with the history
pre-filtered — i.e. the floor. The honest name for the paper is "recency-truncated, entity-filtered
episodic buffer".

**`routine`/`routine7` — faithful instance of recursive summarisation; variant of Generative-Agents reflection.**
- **Recursive summarisation** (Wang, Liang, Zhang et al., "Recursively Summarizing Enables Long-Term Dialogue
  Memory in Large Language Models"; arXiv 2308.15022; **Neurocomputing**; **98 cites**). Verified from the
  abstract: the method "first stimulates LLMs to memorize small dialogue contexts and then **recursively
  produce new memory using previous memory and following contexts**". That is exactly our nightly rewrite.
  Our arm is a **faithful instance**, differing only in that the summary is schema'd (per-resident routine,
  per-object usual spots) rather than free text. The paper does **not** address contradictory or evolving
  facts (checked; the abstract and the evaluation are about consistency over long dialogues).
- **Generative-Agents reflection** (as above). Verified differences: their reflection fires "when the sum of
  the importance scores for the latest events perceived by the agents exceeds a threshold (**150** in our
  implementation)", about **two or three times a day**, and begins by asking "what are **3** most salient
  high-level questions we can answer about the subjects in the statements?". Ours fires on a fixed nightly
  schedule and asks for a routine table. **Verdict: variant.**
- **Think-in-Memory** (Liu et al.; arXiv 2311.08719; **59 cites**) stores induced *thoughts* rather than raw
  text and has explicit insert/forget/merge operations — closer to ours in that the store is derived, and it
  is the one member of this family with a forget operation. [U: I did not read its method section this pass.]
- Also in this family and already in SURVEY.md: MemGPT's recursive summary, Letta sleep-time compute.
- **2026 strong instance to cite instead of our own:** **SimpleMem** (Liu, Su, Xia, Han, Zheng, Xie, Ding,
  Yao; arXiv 2601.02553, Jan 2026, v3 Jan 29; cites n/a). Verified from the abstract page: three stages —
  *semantic structured compression* (condense unstructured interactions into indexed memory units),
  *online semantic synthesis* (integrate related context to reduce redundancy), *intent-aware retrieval
  planning* (decide retrieval scope from search intent). It is the paper other 2026 systems use as the
  strongest simple baseline. The abstract says nothing about contradictory or outdated memories.

**`retrieval` — variant. The periodic time-of-day key has no published counterpart I could find.**
The family (retrieve what is relevant to this query from an episodic store) is the most standard thing in
the field. The named method closest to our *specific* relevance function is **TempRALM** (Gade & Jetcheva,
"It's About Time: Incorporating Temporality in Retrieval Augmented Language Models"; arXiv 2401.13222;
cites n/a), which adds to the semantic score a **temporal relevance score inversely proportional to the gap
between the query timestamp and the document timestamp**, reranking documents temporally nearer the query;
reported up to **74% over ATLAS** and 32% over a commercial retrieval-augmented LLM, with no pre-training or
index replacement. [U: taken from the paper's summary, not its method section.] Ours is the **periodic**
analogue — distance modulo 24 hours instead of absolute distance — and I found no published method that
uses a periodic temporal key. LongMemEval's *time-aware query expansion* (already in SURVEY.md) is the
closest published relative in the memory literature.
**Verdict: variant, with the periodic key our own.** That is defensible and worth stating as a design choice,
because our sightings are structured `(time, receptacle)` tuples and embedding similarity over them is
degenerate. But see 1.3: a reviewer will still want a lexical or embedding retriever run, because that is
the baseline that actually wins in the published comparisons.

**`reflect` — variant of Reflexion; the faithful named counterpart is ExpeL, and ours is ExpeL with the
bookkeeping removed.**
- **Reflexion** (Shinn, Cassano, Gopinath, Narasimhan, Yao; **NeurIPS 2023**; arXiv 2303.11366;
  **5372 cites**). Reflects after a *failed trial* and retries the *same* task with the reflection in a short
  buffer. Ours accumulates a persistent cross-episode note and never retries. **Verdict: variant.**
- **ExpeL** (Zhao, Lin, Zhu, Ye, Chen, Zheng; **AAAI 2024**; arXiv 2308.10144; **936 cites**). Verified from
  the method section: an experience pool of successful and failed trajectories; insight extraction where the
  LLM applies four operations — **ADD, EDIT, UPVOTE, DOWNVOTE** — to a dynamic insight list; a new insight
  starts with **importance count 2**, UPVOTE/EDIT increments it, DOWNVOTE decrements it, and the insight is
  **removed at 0**; extraction runs both on success/failure *pairs* and on batches of L successful
  trajectories; at inference the agent gets the full insight list plus the top-k similar successful
  trajectories by embedding similarity (k=6 HotpotQA, k=2 ALFWorld/WebShop). Gains over ReAct: HotpotQA
  39 vs 28, ALFWorld 59 vs 40, WebShop 71 vs 67. **Verified: no ExpeL environment has a correct answer that
  changes over time.** Our `reflect` is this without the vote counters, without the pairing, and without
  retrieval of past trajectories. **Verdict: an impoverished variant of ExpeL.** The cheap upgrade is the
  vote counter, which is the one part of ExpeL that can make an insight die when the world changes.
- **Agent Workflow Memory** (Wang, Fried, Neubig; **ICML 2024**; arXiv 2409.07429; **285 cites**) induces
  reusable workflows from experience — the procedural cousin. [U: abstract only.]
- **Voyager** (arXiv 2305.16291; **TMLR**; **2326 cites**) is the skill-library ancestor and is what a
  reviewer will name if we call our notes "self-written". [U: abstract only.]
- **The 2026 named successor, and the most interesting thing I found for this arm:**
  **"Closing the Feedback Loop: From Experience Extraction to Insight Governance in Verbal Reinforcement
  Learning"** (Cui et al.; arXiv 2606.17591, June 2026; cites n/a). Three layers, verified from the HTML:
  *rules* (natural-language trigger→action statements, **deprecated rather than deleted**, so the history
  survives); *evidence* (a persistent log of every episode where the rule was evaluated, whether it helped
  or hurt, and under what conditions — the paper contrasts this explicitly with a scalar confidence score);
  *skills* (routing, conflict resolution and **abstention**). Three roles: a **Critic** that evaluates rules
  against outcomes, a **Proposer** that appends evaluations and proposes rules, a **Curator** that deprecates
  rules with consistently negative evidence. At inference "its parameters are frozen; only its context
  changes", and abstention fires when no rule has sufficient positive evidence. Case study: S&P 500
  five-day direction from 20-day candlesticks, 2013-2016 train / 2017 test, base agent Qwen3-VL-235B with
  Claude Sonnet 4.6 as critic/proposer/curator. **Without governance: −4.9pp directional accuracy and a
  negative Sharpe. With the full loop: +5.3pp, Sharpe about 2× baseline, 60% lower max drawdown.** The
  paper says rules can be deprecated and later reactivated when conditions recur, but I did **not** find an
  explicit false→true→false demonstration [U on the reactivation claim].
  This is the closest published thing to what we would build next for this arm, and it is one of the very
  few papers in this whole survey whose evaluation domain is genuinely non-stationary.

**`longcontext` — faithful instance of the standard control, and a strong one.**
Called "long-context agents" in MemoryAgentBench, "full-context" in LongMemEval, "long-context" in AutoMEM.
Citable as-is. The standard reference for why it fails is **Lost in the Middle** (Liu, Lin, Hewitt, Paranjape,
Bevilacqua, Petroni, Liang; **TACL 2024**; arXiv 2307.03172; **5111 cites**). Two verified data points that
this control is not a straw man: in MemoryAgentBench's FactConsolidation single-hop, GPT-4o long-context
scores **60.0** against Mem0 18.0 and MemGPT 28.0; in AutoMEM's LoCoMo evaluation, long-context scores
**61.5** against DCI-Lite 45.0, with AutoMEM itself at 67.3.

### 1.3 What a 2026 reviewer will consider the standard baseline set

Grounded in what the 2026 papers actually run, not in what I expect.

**MemoryAgentBench** (arXiv 2507.05257; ICLR 2026; 225 cites per SURVEY.md) evaluates, verified from its HTML:
- long-context agents: GPT-4o, GPT-4o-mini, GPT-4.1-mini, Gemini-2.0-Flash, Claude-3.7-Sonnet
- simple RAG: **BM25**
- embedding RAG: **Contriever, text-embedding-3-small, text-embedding-3-large, NV-Embed-v2**
- structure-augmented RAG: **RAPTOR, GraphRAG, HippoRAG-v2, Mem0, Cognee**
- agentic memory: **Self-RAG, MemGPT**
Its four competencies are accurate retrieval, test-time learning, long-range understanding and
**conflict resolution / selective forgetting**. Its FactConsolidation task is built from **MQUAKE
counterfactual edit pairs**: each pair is an original fact and a contradictory rewrite, concatenated with
the outdated version given a *lower* serial number and the newer one a higher number, at 32K/64K/262K
context. FactCon-SH: GPT-4o 60.0, GPT-4o-mini 45.0, GPT-4.1-mini 36.0, Gemini-2.0-Flash 30.0,
Claude-3.7-Sonnet 43.0, **BM25 56.0**, NV-Embed-v2 55.0, HippoRAG-v2 54.0, Mem0 18.0, MemGPT 28.0.
Multi-hop: nothing above 6. Conclusion quoted in the paper: "All methods fail on the multi-hop situation".
**The lesson for our baseline set: BM25 beats every dedicated memory system on the one task in that
benchmark about a fact that changed.** We do not have a BM25 arm. We should.

**AutoMEM / "Exploring Cross-Scenario Generality of Agentic Memory Systems"** (Chen, Gu, Yin, Long, Zeng,
Liu, Guo, Zhou, Tang; arXiv 2606.04315, 3 June 2026; cites n/a). Verified from the abstract and HTML. Eight
systems on five scenarios: **SimpleMem, LightMem, HippoRAG, PlugMem, AMA-Agent, Mem-T, MemRL, DCI-Lite**;
scenarios LoCoMo (multi-session chat), HotpotQA-scale corpus, AMABench agentic-trajectory QA,
MemoryAgentBench stress tests (AR / TTL / LRU / **CR = conflict resolution**), and ALFWorld + MemoryArena.
Headline, quoted: the harness that "self-manages flat text-file storage via tool calls" achieves the best
cross-task ranking, "suggesting that memory performance hinges on **giving the agent active control over
storage and retrieval rather than on a passive store behind a fixed pipeline**". AutoMEM is a
plan-execute-judge loop over `grep` / `read` / `dump` / graph queries, **3-4 LLM calls per question** against
1 for long-context. Backbones **Qwen3-32B**, Qwen3-Embedding-4B, Qwen2.5-7B-Instruct, Qwen3-4B-Instruct,
all open-weight on sglang/vLLM. Also verified: index methods failed on agentic trajectories partly because
"passive retrieval couldn't surface evidence the storage retained" — a storage/read split like ours, on the
retrieval side rather than the reasoning side. **This is the 2026 paper a reviewer is most likely to cite at
us, and it runs on a model our size.**

**"Harness the Memory: A Holistic Evaluation of Memory Substrates in Memory Agents"** (arXiv 2608.15008;
cites n/a). Seven substrate categories — dense and sparse indices, text records, structural stores,
hierarchical stores, refinement-based memories, parametric updates, activation-compatible context
mechanisms — over three backbones and four benchmark suites. Verified findings: **no single substrate wins
everywhere**; broad retrieval helps factual QA but **harms sequential decision-making** by diverting
attention from action-critical information; substrate *routing* is proposed instead. The abstract does not
say whether any suite has contradictory or updated facts [U].

**Survey: "Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers"**
(arXiv 2603.07670, covers 2022 to early 2026; cites n/a). Verified taxonomy: memory as a
**write–manage–read loop**, five mechanism families with these representatives — *context-resident
compression* (Self-Controlled Memory), *retrieval-augmented stores* (RAG, RETRO, ChatDB, RET-LLM),
*reflective self-improvement* (**Reflexion, Generative Agents, ExpeL, Think-in-Memory**), *hierarchical
virtual context* (**MemGPT, JARVIS-1**), *policy-learned management* (AgeMem). Its four headline benchmarks
are LoCoMo, MemBench, MemoryAgentBench, MemoryArena. Two quotes worth having: "in any long-running
deployment, the inability to discard outdated information gradually poisons retrieval precision" and
"**the primary bottleneck is no longer storage — it is retrieval quality**"; its recommended engineering
practice is "temporal versioning (prefer the newest record), source attribution (user statement >> agent
inference), contradiction detection, and periodic consolidation"; and it lists "learning to forget" and
"self-reinforcing error, where false reflections persist unchallenged" as open problems.

**So: the baseline set a 2026 reviewer will expect from us.** Seven arms, in the order they will look for them:
1. **Long-context / full-history control.** We have it (`longcontext`). Keep it and name it as the control.
2. **BM25 over the sighting log.** We do not have it. It is the cheapest arm in this list and it is the one
   that beats Mem0, MemGPT, GraphRAG and Cognee on the only changing-fact task in MemoryAgentBench.
   Its absence is the most quotable hole in our set.
3. **Embedding retrieval** (Contriever or a small Qwen3-Embedding). Our `retrieval` arm occupies this slot
   but with a hand-chosen key; say so, and ideally run one embedding arm so the comparison is not only
   against our own key choice.
4. **One compression/summary system with a name.** SimpleMem (2601.02553) or plain recursive summarisation
   (2308.15022). Our `routine7` is a faithful instance of the latter; cite it that way.
5. **One reflective system with a name.** Reflexion or ExpeL. Our `reflect` is an impoverished ExpeL; the
   vote counter is the missing part and it costs nothing.
6. **One commodity memory framework, ideally two with opposite revision policies.** We already have
   Mem0 (delete) and Zep (invalidate) plus STALE/CUPMem in the `facts_*` arms — this part of our set is
   ahead of the field and should be foregrounded.
7. **One tool-based / self-managed memory.** MemGPT/Letta is the canonical citation; AutoMEM (2606.04315)
   is the 2026 state of the art and, on its own evidence, the strongest general baseline there is. We have
   nothing in this slot. See section 4.
Plus, not a baseline but expected: **an oracle / upper bound per arm** (we have `truecard` and
`debate_oracle`, which is good), and a **no-memory control**.

---

## 2. Prompting before architecture

### 2.1 The answer

**No. Do not expect a prompt to fix a read-time override like ours.** Expect 0 to +10 points with a real
chance of a negative, and a tax on the ~70% of our questions where nothing has changed. Every paper that
measures *our* failure — the right answer visibly in the prompt, the model answering with the prior anyway —
reports that instructions, chain-of-thought and self-critique do not fix it, and several report that they make
it worse. Meanwhile the effects that do move this failure are 3–5× larger and all live at write time or in
deterministic code.

**But run four cheap prompt arms first**, because three are free, one has a large untested precedent on
exactly the quantity our card ablation measures, and the negative result is itself publishable. They are in
§2.6.

### 2.2 The single most targeted numbers against "just prompt it"

- **"Does RAG Know When Retrieval Is Wrong?"** (Chen et al.; arXiv 2605.14473, May 2026 rev. Jul 2026;
  21 cites). A **conflict-aware instruction** — verbatim *"use the context but override it when it conflicts
  with established facts"* — on Gemini-2.5-Flash: entity swap 58.4 → 79.3 (**+20.9**); logical contradiction
  56.0 → 75.4; **temporal shift 68.8 → 70.0 (+1.2)**; distractor evidence 68.8 → 69.2. **Ours is a temporal
  shift.**
- **"Diagnosing Retrieval Bias Under Multiple In-Context Knowledge Updates"** (Qiao et al.; arXiv 2603.12271,
  Feb 2026; 0 cites) — **the closest published replica of our prompt structure: one attribute updated
  repeatedly inside a single prompt.** Earliest-state accuracy stays high; latest-state accuracy degrades as
  updates accumulate (their Earliest-Latest Accuracy Gap), widening from T=32 to T=128; the effect survives
  being embedded in coherent narrative prose. Models include **Qwen-2.5 7B/14B/32B/72B**. They tested six
  cognitively-motivated prompts — rote rehearsal (`Rehearse each new cue:value pair three times when you read
  it. Do this internally`), semantic elaboration, memory integration as evolving chains `CUE: v(1) → v(2) →
  v(T)`, directed forgetting (`Overwrite every previous cue-value pair with the current cue-value pair`), CoT,
  and index-style structured prompts. Verbatim result: interventions *"yield only modest gains in latest-state
  retrieval and do not eliminate the bias"*. Best case LLaMA3.1-8B memory-integration **+9.15**;
  **Qwen2.5-7B +0.61.**
- **STALE / CUPMem** (already in SURVEY.md, but this is the number to put in the paper): **Qwen3.5-27B scores
  76.0% on Type-I state resolution and 4.0% on Type-I premise resistance.** Gemini-3.1-pro: 92.0% → 30.0%.
  Verbatim: *"models can identify outdated information under explicit probing, yet still comply when a query
  presupposes the outdated state."* Their attention analysis on Qwen3.5-9B/27B shows correct answers assign
  relatively more attention to the new session — **the evidence is read either way.** Their own limitation
  section says the fix is *"not query-time correction, but reliable write-time consolidation, stale-state
  retirement, and reconstruction of the current basis"*. CUPMem is **+36.7 over the plain 27B**, from
  restructuring the store. ~$0.37/instance.
  **Our written routine card is a presupposition of exactly this kind, and deleting it is the
  premise-resistance intervention. Our 19–29-point recovery is a larger, cleaner version of their 72-point
  SR→PR gap.**
- **"When Memory Updates but Behavior Does Not" / StateAuditor** (Sun & He; arXiv 2608.01619, Aug 2026;
  2–3 cites). On STALE: write-side prototype **91% on state resolution, 32% on implicit policy adaptation**,
  and **"the updated evidence is visible in 67.8% of failed IPA cases"** — our 807/890 is 90.7%, the same
  failure independently measured. Their prompt interventions: **self-critique consistency checks performed
  worse than baseline; few-shot + CoT reduced stale-premise recall from 0.38 to 0.13; timeline conditioning
  gave 0.373 → 0.517.** Verbatim: *"the bottleneck is extraction, not verification — prompting cannot
  overcome implicit dependency blindness."* Their deterministic fix (provenance-verified transition assembly,
  quotation matching ≥80% of tokens, timestamp ordering) buys **+5.0 macro [+2.9, +7.2] for 6 LLM calls and
  ~$0.34 per scenario**, and a **Qwen3-4B auditor did not match the frontier auditor while gpt-4o-mini as
  auditor wrecked conflict-free accuracy (LongMemEval 0.816 → 0.579)**. Judge–human agreement κ=0.126, so
  weight accordingly. Their safety variant is the design lesson: a **repair-only** auditor with no "verify"
  directive got +3.7 while rewriting only **3% of conflict-free examples instead of 80%**.

### 2.3 (a) Context-versus-parametric conflict: the effect is real, large, and unreliable on our model class

**The canonical pro-prompting result.** **"Context-faithful Prompting for LLMs"** (Zhou, Zhang, Poon, Chen;
arXiv 2303.11315; **EMNLP 2023 Findings; 112 cites**). Three templates, verbatim: *attributed*
`{c} Q: {q} based on the given text? Options:{o} A:`; *instruction* `Instruction: read the given information
and answer the corresponding question. {c} Q: {q}? Options: {o} A:`; **opinion-based**
`Bob said, "{c}" Q: {q} in Bob's opinion? Options: {o} A:`; plus **counterfactual demonstrations** whose
contexts assert false facts and whose correct behaviour is to follow the context anyway. Their metric is ours:
**memorisation ratio (MR)**, the rate at which the model answers from its prior instead of the context.
GPT-3.5, MRC knowledge-conflict, Table 1: base MR 35.2 / EM 6.2; attributed 16.6 / 29.6; instruction
17.7 / 27.1; opinion 11.0 / 24.9; **opinion+instruction 9.1 / 48.6**; few-shot original demos 53.3 / 35.1;
**few-shot counterfactual demos 7.0 / 80.2**; counterfactual + opinion + instruction **3.0 / 85.2**.
So the headline "35.2 → 3.0" is zero-shot base versus counterfactual few-shot — **the demonstrations, not the
instruction, carry most of it** (35.1 → 80.2 EM from swapping demo type alone).
**The caveat that matters for us.** Their Table 2, LLaMA-2-7B-chat, same setting: base 44.6 / 3.5; attributed
26.4 / 4.7; **instruction 20.2 / 27.0**; opinion 16.4 / 9.4; opinion+instruction 15.1 / 13.7. **The ordering
inverts on the small model** — the plain instruction gives the best EM and the opinion reframing 9.4 — and on
relation extraction the instruction *hurt* (F1 81.6 → 75.1). The paper states that larger LLMs update
memorised answers more readily both with and without the method. Not tested on facts that change.
**Zero extra LLM calls, READ-side.**

**The independent re-test, where prompting stops being reliable.** **Context-DPO** (Bi et al.;
arXiv 2412.15280; **ACL 2025; 60 cites**), ConFiQA context-faithfulness Pc:

| model | base | attributed | opinion+instr | Context-DPO (trained) |
|---|---|---|---|---|
| LLaMA2-7B-chat | 61.5 | 72.0 | 77.3 | 92.3 |
| **LLaMA3-8B-instruct** | 35.8 | **25.7** | **32.7** | 69.7 |
| Mistral-7B-instruct | 39.3 | 44.4 | 60.3 | 78.6 |
| Qwen2-7B-instruct | 24.0 | 38.3 | **58.0** | 74.3 |

**On Qwen2-7B the prompts are worth +34 points; on LLaMA3-8B both score below the plain baseline.** Same
prompts, same benchmark, opposite sign. **FaithfulRAG** (Zhang et al.; arXiv 2506.08938; **ACL 2025;
39 cites**) reproduces this: on Llama3.1-8B, Opin(Instr) **+4–5**, ATTR **~0**, while their multi-call
fact-level pipeline reaches **+16**. CAD/COIECD decoding baselines land at +0–3 on these models.

**The confirmation-bias result that explains our routine card.** **"Adaptive Chameleon or Stubborn Sloth"**
(Xie, Zhang, Chen, Lou, Su; arXiv 2305.13300; **ICLR 2024 Spotlight; 399 cites**). Models are highly
receptive to coherent counter-evidence when it is the *only* evidence (ChatGPT and GPT-4 both below 30% MR on
LLM-generated coherent counter-memory). But their Table 6, MR by the proportion of prior-aligned evidence in
the context:

| prior-aligned share | 0% | 33% | 50% |
|---|---|---|---|
| ChatGPT | 3.7 | 30.0 | 43.0 |
| GPT-4 | 8.9 | 50.3 | 65.4 |
| PaLM2 | 15.8 | 15.8 | 56.8 |

**Adding one piece of prior-aligned evidence to a context otherwise full of counter-evidence raises the
memorisation ratio from ~4–9% to 30–50%; removing it drops it back.** That is our 19–29-point card recovery,
measured independently in 2023, and it is the best single citation for that result. Their Table 5 also shows
MR swinging over 30 points on a 7B from evidence *ordering* alone, with the direction differing by model
(ChatGPT favours first, PaLM2 and Llama2-7B favour last; GPT-4 alone is order-insensitive).

**The benchmarks that establish "the answer is in the prompt and the model still fails".**
- **FaithEval** (Ming, Purushwalkam, Pandit, Ke, Nguyen, Xiong, Joty; arXiv 2410.03727; **ICLR 2025;
  104 cites**), which includes **Gemma-2-27B-it**. GPT-4o: closed-book **96.3%** on the underlying facts →
  **47.5%** with a counterfactual context, while humans score **95%** on a held-out subset of the same
  contexts. Larger is not more faithful (Phi-3-mini 3.8B outranks GPT-4o and Llama-3-70B on counterfactual
  context). **CoT helps** on unanswerable and inconsistent contexts (best 71.8%). And the cost we must note:
  **adding a conflict-detection instruction degrades performance on normal contexts consistently** — GPT-4o
  0.94→0.84, 0.90→0.85, 0.86→0.78; Claude 3.5 loses ~5% average. Their cleanest diagnosis of our failure:
  models handle the new context fine when presented alone (Command R 88% new vs 81% original) and collapse
  when **both** passages are present.
- **Sufficient Context** (Joren et al.; arXiv 2411.06037; **ICLR 2025; 90 cites**): hallucination rate *when
  the context is sufficient* — Claude 3.5 Sonnet 3.2%, GPT-4o 12.7%, Gemini 1.5 Pro 14.3%, **Gemma 27B
  25.4%.** Fine-tuning to teach abstention failed; their selective-generation method is worth 2–10%.
- **Entity-Based Knowledge Conflicts in QA** (Longpre et al.; arXiv 2109.05052; **EMNLP 2021; 451 cites**) —
  the origin of the memorisation-ratio framing.
- **"Knowledge Conflicts for LLMs: A Survey"** (Xu, Qi, Guo, Wang, Wang, Zhang, Xu; arXiv 2403.08319;
  **EMNLP 2024; 354 cites**). I verified the taxonomy myself: **context-memory / inter-context /
  intra-memory**, with **outdated information** named as a cause of inter-context conflict. **Our failure is
  inter-context** (routine card versus sighting list, both in the prompt) **layered on context-memory.** That
  matters because almost all the prompting evidence comes from the context-memory cell and ours is the
  under-studied one. As of EMNLP 2024 every solution the survey lists under "eliminating conflict" is a
  **trained** discriminator.
- **"Investigating Context-Faithfulness: Memory Strength and Evidence Style"** (arXiv 2409.10955; **ACL 2025;
  13 cites**): high **memory strength** (response divergence across paraphrases) predicts reliance on internal
  memory, and **paraphrased** evidence increases receptiveness versus simple repetition. **Our settled
  two-week routine is a maximal-memory-strength prior by construction and our sightings are near-identical
  repetitions** — the worst possible combination on both axes.

**2026: instructions do not override the prior.**
- **"Prior Beliefs Prejudice LLM-as-Judge"** (Zahraei, Wang, Bozdag, Tur, Hakkani-Tür; **ACL 2026 Findings**,
  pp. 42046–42062). 27,756 arguments; 17 models including **Gemma-2-9B-it, OLMo-3.1-32B, Qwen-2.5-7B,
  Qwen-3-4B, Llama-3.1-8B**. A 2×2 design crossing rating-only versus rating+reasoning with basic versus
  **belief-independent** instructions (`judge "regardless of whether you agree with it"`). Verbatim:
  *"Even explicit instructions to 'judge rhetoric regardless of agreement' fail to mitigate prior
  prejudice."* / *"awareness of logical flaws does not prevent biased evaluation."* / *"Explicit reasoning
  instructions sometimes amplify bias."* / *"Instruction-following is not a sufficient remedy when the bias
  operates at a level the model cannot override through its own reasoning."* The dominant failure —
  the model **states** the evidence is missing and scores it high anyway — is **81–97% of failures, 88%
  overall**, and persists across all four prompt variants. **[U: the "35–43% of conditions got worse" figure
  circulating on the project page is not in the paper text; do not cite it.]**
- **"Control Illusion: The Failure of Instruction Hierarchies in LLMs"** (Geng et al.; arXiv 2502.15851;
  **AAAI 2026 Main; 41 cites**). Primary-constraint compliance under conflict: **Qwen-7B 9.6%, Llama-8B
  10.1%, Llama-70B 16.4%, Claude 3.5 Sonnet 29.9%, GPT-4o 40.8%** — versus 80–91% when the instructions are
  given individually. Verbatim: *"societal hierarchy framings (e.g., authority, expertise, consensus) show
  stronger influence on model behavior than system/user roles, suggesting that pretraining-derived social
  structures function as latent behavioral priors."* **Social-consensus framing got Qwen-7B to 65.8% versus
  14.4% for system/user markers.** For us: the **authority framing** of the routine card is doing the work,
  not its placement, and reframing it is a cheap lever with a 4× precedent on a small open model.
- **Positive results, both small:** "When LLMs Lag Behind: Knowledge Conflicts from Evolving APIs"
  (Ashik et al.; arXiv 2604.09515; 2 cites) — 270 real API updates, documentation alone 42.55% → 66.36%
  executable, models still emit outdated patterns with the spec in front of them, **self-reflection prompting
  +11%**. And "Can LLMs Take Retrieved Information with a Grain of Salt?" (Shayegh et al.; arXiv 2605.06919;
  0 cites) — eight open models including **Gemma-3 27B/12B/4B/1B**; a prompting-only pipeline (prior reminder,
  certainty recalibration, context simplification) cut obedience error **Gemma-3-27B 0.48 → 0.28 (−42%)**,
  average −25%, ~3 forward passes with KV reuse. **Caution: their failure is over-trusting uncertain context;
  ours is under-trusting it.** The transferable ingredient is the **prior reminder** — elicit the model's
  no-context answer and put it in the prompt as a *separately labelled hypothesis* rather than an assertion.
- **A warning about decorating the prompt with metadata:** "Metadata, Structure, or Strategy? A Decomposition
  of RAG Context Enrichment" (Zerhoudi, Granitzer, Mitrovic; arXiv 2606.29645; **ECML-PKDD 2026**; 1 cite),
  24,000 responses, six benchmarks, four models, five enrichment levels. Verbatim: *"Most enrichment reduces
  accuracy. Models prompted to use confidence scores comply correctly yet produce worse answers, a gap
  between utilization and accuracy that no prior work has measured."*

### 2.4 (b) Self-verification: the negatives are stronger than the positives

**The positives, with their true cost.**

| method | citation | cites | mechanism | effect | extra calls |
|---|---|---|---|---|---|
| Self-Refine | 2303.17651, NeurIPS 2023 | **4,725** | generate → self-feedback → refine | ~+20% avg over 7 tasks | 2 per iteration |
| Reflexion | 2303.11366, NeurIPS 2023 | **5,372** | verbal reflection into an episodic buffer across trials | HumanEval 80→**91** pass@1 | ≥2 per trial, multi-trial |
| Chain-of-Verification | 2309.11495, ACL 2024 | **586** | draft → plan verification questions → **answer them in isolation** → revise | Wikidata precision 0.17→**0.36**; FactScore 55.9→**71.4** | 1 + 1 per question (≈4–10) |
| Self-Consistency | 2203.11171, ICLR 2023 | **7,719** | sample k CoT paths, majority vote | large on arithmetic | k (5–40) |
| Take a Step Back | 2310.06117, ICLR 2024 | **251** | derive a principle first, then reason | MMLU-Physics +7%, **TimeQA +27%** | 2 |
| RECITE | 2210.01296, ICLR 2023 | 89 | recite passages from parameters first | modest | 2 |
| **`Wait`** | Tsui, 2507.02778, **COLM 2026** | 16 | append the single token `Wait` | cuts the self-correction blind spot **89.3%** | **0** |

Three of those are load-bearing for us.
- **CoVe's own caveat, verbatim:** *"Models that attend to existing hallucinations in the context from their
  own generations tend to repeat the hallucinations."* That is why they built the **factored** variant, which
  excludes the draft answer from the verification context. **Any self-check we add must not see the previous
  answer, or it will ratify it.** Our own judge/writer split already hit a version of this.
- **`Wait`, and the variable it names.** Self-Correction Bench (Tsui, COLM 2026) injects the *identical*
  error as either user-attributed or model-attributed across **14 open-source non-reasoning models**.
  Verbatim: *"Testing 14 open-source non-reasoning models reveals a 64.5% Self-Correction Blind Spot: models
  correct external errors but fail on identical internal ones, proving the capability exists but is not
  activated."* 5,306 error-correction traces cut the blind spot 76.0%; **appending `Wait` cuts it 89.3% with
  no training**; and they identify a causal conversational-role direction in representation space that gates
  correction. **This is the most actionable finding in the survey for us, because our routine card is
  model-attributed content — it reads as the system's own standing belief — while our sightings are data.
  Re-attributing the recent sighting as an external correction, or the card as a stale external record, flips
  which side of the 64.5% blind spot we are on.** Zero extra calls, one prompt edit, and it is the same lever
  as the opinion reframing and the authority framing, arrived at from a third independent direction.
- **"Take a step back" gets +27% on TimeQA**, the only classic technique with a large gain on a temporal
  benchmark. Worth one arm; note TimeQA is closed-book temporal reasoning over a provided passage, not a
  prior-override task.

**The negatives.**
- **"LLMs Cannot Self-Correct Reasoning Yet"** (Huang, Chen, Mishra, Zheng, Yu, Song, Zhou; arXiv 2310.01798;
  **ICLR 2024; 1,208 cites**). Prompt verbatim: *"Assume that this answer could be either correct or
  incorrect. Review the answer carefully and report any serious problems you find."* Rounds 1 and 2:
  GPT-3.5 GSM8K 75.9 → 75.1 → 74.7; GPT-3.5 CommonSenseQA 75.8 → **38.1** → 41.8; GPT-4 GSM8K
  95.5 → 91.5 → **89.0**; GPT-4 HotpotQA 49.0 → 49.0 → 43.0. **Every cell flat or worse.** With **oracle
  labels** telling the model when it is wrong, everything improves (GPT-4 HotpotQA 49.0 → 59.0).
  **The binding constraint is knowing when to revise, not how.**
- **"When Can LLMs Actually Correct Their Own Mistakes?"** (Kamoi, Zhang, Zhang, Han, Zhang; **TACL 2024**
  vol. 12 pp. 1417–1440; **356 cites**): **no prior work successfully demonstrates self-correction with
  feedback from prompted LLMs**, except on tasks unusually suited to it; it works with reliable *external*
  feedback; large-scale fine-tuning enables it.
- **Stechly, Valmeekam, Kambhampati** (arXiv 2402.08115; **ICLR 2024; 161 cites**): self-critique **degrades**
  GPT-4 on Game of 24, graph colouring and STRIPS planning; a sound external verifier gives substantial gains
  and *"merely re-prompting with a sound verifier maintains most of the benefits."* **"GPT-4 Doesn't Know
  It's Wrong"** (arXiv 2310.12397; 129 cites): *"the correctness and content of the criticisms… seems largely
  irrelevant to the performance."*
- **Tyen et al.** (arXiv 2311.08516; **ACL 2024 Findings; 95 cites**): models fail at *locating* errors even
  in objective cases, correct them robustly given the location, and **a small trained classifier on
  out-of-domain data beats the LLMs at detection.** Detection is the bottleneck and is better served by a
  cheap classifier.
- **Self-Verification Dilemma** (Long et al.; arXiv 2602.03485, Feb 2026; 3 cites): in reasoning models
  *"the vast majority [of reflective steps] are confirmatory rather than corrective, rarely identifying
  errors"*; suppressing unnecessary rechecks saves 20.3% tokens at equal accuracy.
- **"Self-Correction as Feedback Control"** (Liu & Meng; arXiv 2604.22273, Apr 2026; 4 cites) — **the most
  useful 2026 framing for our decision.** A two-state Markov model with an **Error Introduction Rate** and
  **Error Correction Rate** gives an iterate-only-when rule: **ECR/EIR > Acc/(1−Acc)**, with a sharp
  **EIR < 0.5%** boundary separating beneficial from harmful self-correction. Across 7 models on
  GSM8K/MATH/StrategyQA only three were non-degrading; GPT-5 and four others lost accuracy. A **verify-first
  prompt** took GPT-4o-mini's EIR from 2% to 0% and converted **−6.2pp into +0.2pp** (p<10⁻⁴). Verbatim:
  *"Prompt-level EIR suppression prevents degradation, whereas ECR enhancement — plausibly training-level —
  is required for genuine gains."* **Translated: a prompt can make a self-check harmless. It cannot make it
  helpful.**

### 2.5 (c) and (d) Recency prompting, date stamps, and position

**Date-stamping is worth under a point where it has been properly ablated.**
- **FreshLLMs / FreshPrompt** (Vu et al., Google; arXiv 2310.03214; **ACL 2024; 433 cites**). Evidence
  rendered as `{source} / {publication_date} / {title} / {snippet} / {highlighted_words}`, oldest→newest so
  the freshest sit nearest the question, with 5 CoT demos. Headline GPT-4 28.6 → 75.6 STRICT — **but that is
  retrieval.** The ablations: **`SNIPPETS ONLY`** (strip source, date, title) scores **74.0–74.8 vs 75.6**,
  verbatim *"slightly reduces accuracy, with less than 1% in both settings."* Ordering: TIME 74.8 / SEARCH
  74.0 / RANDOM 72.4. What actually matters is **evidence count**: 1→5→10→15 gives +9.2 / +14.2 / +16.2.
  Residual **59.2% on fast-changing facts** with everything on. And their premise-check instruction
  (`Please check if the question contains a valid premise before answering`) gave **+23.4pp on false-premise
  but −20.8pp overall** on GPT-3.5.
- **evolveQA** (Nakshatri et al., AWS; arXiv 2510.19172; 2 cites), Table 10, date-only condition:
  **Gemma3-27B-instruct 39.05 → 40.24 (+1.2)**; Gemma3-4B +4.7; **GPT-5-mini −4.5; Llama-3.3-70B −4.1**;
  Claude-3.5-Sonnet-v2 +1.5. Verbatim: *"providing only the 'current date' in the prompt generally does not
  improve LLMs ability to recall authoritative information."* **A Gemma-family 27B — our model class — got
  +1.2 points, and the sign is negative on three of eight models.** Also: in **32–45%** of cases models picked
  the right multiple-choice option while generating the outdated open-ended answer.
- **TempLAMA / Time-Aware LMs** (Dhingra et al.; **TACL 2022; 414 cites**) is the origin of date-prefixing and
  it is a **training-time** intervention (`year: 2014 text: …` on T5), worth **+1.6 token-F1**.

**HoH — the paper that already runs our mitigation as its default, and still breaks.** (Ouyang, Pan, Cheng,
Yan, Luo, Lin, Liu, USTC; arXiv 2503.04800; **ACL 2025 Long**, pp. 6037–6055). **96,124 QA pairs, 219,463
documents**, five months of real fact evolution. Their **default RAG condition already includes a full
time-aware instruction**: `Cutting Knowledge Date: December 2023` / `Today Date: 01 November 2024` /
`## Title: {title} (Last Modified Time: {date})` / `- Your answer should be up-to-date as of today. Refer to
the most up-to-date and relevant information regarding this question.` **With all of that on**, adding one
outdated passage beside one relevant one costs: Llama-3.1-70B perfect **93.24 → 83.00** (composite
89.12 → 72.95); Llama-3.1-8B 90.34 → 68.13 (composite 85.70 → **50.93**); **Qwen-2.5-7B 79.82 → 55.61**
(composite 76.31 → **33.93**, harmful 3.51 → 21.68). Pure distractors barely matter (93.24 → 92.57) — it is
the *plausible stale* passage that does the damage. Timeliness awareness with the timestamps right there:
**Qwen-2.5-7B flags the outdated document only 41.3% of the time.** Verbatim: *"merely identifying information
as outdated does not guarantee the model will avoid using it harmfully"* — Llama-70B with outdated-awareness
only was **35.94% harmful**. And ordering is a coin flip whose sign depends on the family: newest-first vs
relevance-ordered, Llama-70B 83.00 → 90.05 (helps) but **Qwen-2.5-7B 55.61 → 42.06, composite 33.93 → 7.76
(catastrophic)**; newest-**last** (the FreshPrompt recipe), Qwen-2.5-7B composite 33.93 → **61.54 (+27.6)**
while Llama-70B 83.00 → 75.07 (hurts). **Qwen-7B's composite swings more than 50 points on ordering alone.**
With only outdated passages, models show "dangerous overconfidence" and Qwen-7B scored **−2.77%**, worse than
guessing, whereas with no relevant information at all they show appropriate uncertainty — **stale-but-plausible
context destroys calibration in a way absent context does not.** Retrieval is not the fix either: outdated
passages occupy about **50% of the top-5** even with temporal weighting, and temporal weighting costs **17%
of relevant-document recall**.
**Why this matters for our decision.** We already do HoH's mitigation: `header_lines` ends with an explicit
`Now: <day>, <hh:mm> (day N of the study…)` line and every sighting is rendered through `clock()` with its day
and time. **We have both awareness types HoH says are sufficient for a 70B, and we still lose 45–60 cold
points.** The cheap temporal-prompting fix is already spent. Two things still worth one experiment each:
removing the `Now:` line, to measure what it is already buying; and rewriting the reply instruction, which
currently asks for *"what the sightings, the time of day and the residents' routine suggest"* — **we have
measured that deleting the routine card is worth +19 to +29 in the disruption, and we have never tested
deleting the instruction that tells the model to consult a routine.** Given the card result, that is the
single highest-expected-value prompt experiment available to us.

**Telling the model to prefer newer evidence: 0 to +20, median ~+6, sometimes negative.**
**"When Facts Change: Temporal Knowledge Conflict Resolution in LLMs"** (Wallat, Nejdl, Sikdar, L3S Hannover;
**Findings of ACL 2026**, pp. 2156–2168) is the only paper that cleanly ablates date-grounding *and* an
explicit temporal instruction on in-context conflicts. WikiRecentChanges, **2,380 facts that actually changed
in 2025** plus a matched stable set; nine open models including **Gemma-3-4B, Qwen-3-8B, GPT-OSS-20B/120B,
Llama-3.3-70B**. Prompts verbatim: standard = *"…Your task is NOT simply to extract an answer from the
context, but to critically evaluate whether the context should be trusted."*; **+Dates** prepends
`Today is {date}. Your knowledge cutoff is {cutoff}.`; **+Prompted** adds *"Please put special emphasis on
whether a question's answer will change over time and use that information to select/reject the provided
context."* Their `updated / True context` condition **is our condition**:

| model | standard | +Dates | +Prompted |
|---|---|---|---|
| GPT-OSS-20B | 51.5 | 63.8 | **71.6 (+20.1)** |
| GPT-OSS-120B | 63.7 | 70.6 | 74.5 (+10.8) |
| Qwen-3-8B | 80.5 | 86.4 | 87.1 (+6.6) |
| Phi-4-mini | 68.0 | 72.7 | 72.9 (+4.9) |
| OLMO-3-7B | 78.5 | 81.8 | 78.5 (0.0) |
| DS-Llama-8B | 83.2 | 82.2 | **79.5 (−3.7)** |

Three further results matter more than the table. **Verbalised temporal reasoning rises far more than
accuracy** — traces mentioning mutability go GPT-OSS-120B 20.1% → 24.5% → **59.8%** — and verbatim:
*"reasoning traces appear to be unfaithful — temporal reasoning is verbalized but not causally linked to the
final prediction."* **The bottleneck splits by scale:** Qwen-3-8B detects the conflict in only 10–17% of
cases (detection-bound) while GPT-OSS-120B detects mutability 79–91% of the time but **uses** it 3.5–62.9%
(action-bound) — **a 27B sits in the trough between the two.** And **stamping the context with a date can
backfire**: `The retrieved context is from 2023` raised Qwen-3-8B mutability reasoning 20.5% → 27.0%, while
stating **2025**, newer than the cutoff — our case — **lowered it to 11.1%.**

**"Right Knowledge, Wrong Answer"** (Hossain et al.; arXiv 2606.20959v3, Aug 2026; 4 cites) — read this
carefully, because its abstract is misleading about the practical effect. Parametric temporal conflict,
**8,746 verified Wikidata position-holder transitions**, four **open-weight** models. *"The newer fact is
present and recoverable, but the default forward pass prefers the outdated one"*; activation patching flips
72–85%, localised to upper layers. The abstract's "a date-prefix prompt recovers the newer fact in 61–81% of
cases" is **candidate log-probability scoring** (Table 6: 0.614 / 0.782 / 0.794 / 0.805). The bare **recency
instruction** on the same metric is **0.416 / 0.278 / 0.154 / 0.193** — half to a quarter as effective, and
worsening with scale. **In free greedy generation (Table 19) the date-prefix new-entity rate is
0.06 / 0.15 / 0.15 / 0.01 versus standard 0.03 / 0.21 / 0.00 / 0.05 — the 0.61–0.81 "recovery" almost
entirely fails to appear in the text the model emits.** Ask of any large date-prompt number whether it was
measured on logits or on generations. **And we cannot gate it:** automatic conflict detection has held-out
AUROC 0.467–0.657 and AUPRC 0.028–0.097 at a 2–7% base rate; at the most permissive threshold the gate fires
on 0.5–10.9% of queries and catches 3–23% of true conflicts, collapsing end-to-end recovery to **0.03–0.08**
versus 0.32–0.54 oracle-gated. Verbatim: *"All recovery figures are measured on oracle-identified
instances."* **So any recency intervention must be always-on, and always-on means paying the FaithEval-style
normal-context tax on the ~70% of our questions where nothing has changed.**

**"Set the Clock"** (Zhao, Brumbaugh, Wang, Hajishirzi, Smith; arXiv 2402.16797; **ACL 2024 Findings;
34 cites**) is the paper usually cited for "time-aware prompting works": LLaMA2-70B F1 on F²⁰²² goes
unaligned 17.2 → **prompting 27.4 (+10.2)** ≈ finetuning 27.9 with `As of year {y}, the answer is:` plus 5
time-sensitive demos. **Their own ablation splits the credit — year mention alone +7.2, time-sensitive demos
alone +10.4 — so the demos carry it**, and Fmax drops 1.8–3.1 points. **It does not transfer to us: this is
closed-book elicitation, where `As of 2022` selects a time-slice already in the weights. Our correct answer is
already in the prompt in 807/890 cases.** Anyone citing "+10 from time-aware prompting" is citing this, in the
wrong setting.

**MenatQA** (Wei et al.; arXiv 2310.05157; **EMNLP 2023 Findings; 21 cites**) is the clean contrast between
temporal prompts and a deterministic tool: **scope prompt** LLaMA-7B +1.10 EM, LLaMA-13B +1.41,
**GPT-3.5 −6.42 EM**; **rerank prompt** "only a minor improvement" and the model degrades the context while
reordering it; **counterfactual/attribution prompt (borrowed from Zhou et al.) best of the three, +7.71 EM
avg**; **deterministic time-comparison tool via ReAct: LLaMA-13B +13.45 EM on scope, +23.14 EM overall**,
robust where the prompt was destructive. **Note that the best prompt is the attribution one, not the temporal
ones.** [U on verbatim prompt wording — typeset as figures.]

**Position: relative instructions do not work, and the kind that works presupposes the answer.**
- **Lost in the Middle** (**TACL 2024; 5,111 cites**): best-to-worst position gaps GPT-3.5-Turbo 14.4pp at 10
  docs, 22.0 at 20, 22.5 at 30. GPT-3.5 closed-book 56.1, oracle 88.3, **worst-position 50.9 — badly placed
  evidence is worse than no evidence.** Their own prompt fix, query-aware contextualization (repeat the
  question before *and* after the documents), is a near-total fix on synthetic key-value retrieval
  (45.6% → ~100%) and, verbatim, *"slightly improves performance when the relevant information is located at
  the very beginning… but slightly decreases performance in other settings"* on multi-document QA.
- **"Attention Instruction: Amplifying Attention in the Middle via Prompting"** (M. Zhang, Meng, Collier;
  arXiv 2406.17095) is the cleanest direct test of "just tell it where to look", on 20-document QA with
  Llama-2-chat, Tulu-2, Mistral-Instruct-v0.2, Llama-3: **relative/positional-language instructions ("pay
  more attention to the beginning / midsection / tail") have no effect** — verbatim, *"LLMs do not have
  relative position awareness therefore cannot follow relative attention instruction"* — while **absolute
  index instructions give +4–10pp when the pointed-at document is gold and −25pp when it is not.**
  **"Attend to the recent sightings" is a relative instruction.**
- **"Beyond Early-Token Bias"** (Menschikov et al.; arXiv 2505.16134; 5 cites): 450,000 QA pairs, 5 models ×
  5 languages × 3 positions. Inline relevance scores formatted `"[{score}] {document}"` — **the "No Scores"
  condition consistently won**, instructions *"consistently degrade accuracy across all languages"*, and
  mis-specified scores are catastrophic (Llama-3.1-8B 0.735 → 0.481, **−25.4pp**). **Position-bias direction
  is family-specific: Qwen2.5-7B, DeepSeek-7B and Mistral-7B show strong recency bias; Llama-3.1-8B and
  Gemma-7B favour early positions** (Gemma worst late-position of the set). **Gemma is the early-bias
  family** — relevant if our backbone behaves like its family.
- **"Positional Biases Shift as Inputs Approach Context Window Limits"** (Veseli, Chibane, Toneva, Koller;
  arXiv 2508.07479; **COLM 2025**), which includes **Gemma-2-27B**: the U-shape with a strong primacy arm is
  strongest at **relative occupancy ≤ 0.5**, and above 50% occupancy primacy collapses. **Our prompt is short
  relative to the window, which puts us in the regime where the front of the prompt is maximally
  privileged — exactly where the routine card sits.** [U on magnitudes; they report indices.]
- **"On the Emergence of Position Bias in Transformers"** (Wu, Wang, Jegelka, Jadbabaie; **ICML 2025;
  65 cites**) proves **causal masking intrinsically biases attention toward earlier positions**. "The start
  of the prompt is structurally over-weighted" has a proof.
- **Self-consistency is actively harmful here.** "Self-Consistency Falls Short!" (Byerly & Khashabi, JHU;
  arXiv 2411.01101; **TACL**): 651 experiments, 8 models, 9 long-context tasks — majority voting makes
  long-context performance **worse**, because position bias produces *correlated* errors that voting
  amplifies. Only **3 of 56** dataset-model pairs improved significantly; ROUGE declined significantly in
  **19 of 24 (79%)**; retrieval tasks lost 20–25% in larger models. **This kills "sample a few times and
  vote" for us, and kills it for a reason that applies to our prompt.** Note the tension with permutation
  self-consistency (Tang et al.; **NAACL 2024; 55 cites**; +34–52% Mistral on *ranking* tasks at ~20 calls):
  marginalising over **order** helps, resampling at **fixed** order hurts.
- **Deflationary and important:** "Do RAG Systems Suffer From Positional Bias?" (Cuconasu, Filice, Horowitz,
  Maarek, Silvestri; arXiv 2505.15561) — in controlled settings position moves accuracy ~5pp; in **realistic**
  retrieval, position-aware reordering is worth **~1–2pp and is statistically indistinguishable from random
  shuffling** (Qwen-2.5-7B k=5: MaxRelevance 71.73% vs Shuffle 71.00%), because strong retrievers also put
  highly distracting passages at top ranks. **Reordering is not where the points are; what else is in the
  prompt is** — consistent with our own card ablation.
- The ceiling that prompt fixes compete against: **"Found in the Middle: Calibrating Positional Attention
  Bias"** (Hsieh et al.; **ACL Findings 2024; 130 cites**) estimates and divides out each document's
  position-induced attention, training-free at inference, **recovering up to 15pp of RAG accuracy** — but it
  needs attention access and an extra forward pass.
- **The attention-level analogue of our 807/890:** "Attention Sorting" (Peysakhovich & Lerer;
  arXiv 2310.01427), verbatim: *"even when models fail to use the information from a relevant document in
  their response, they still pay preferential attention to that document compared to an irrelevant document
  at the same position."* [U on effect size.]
- **Negative 2026 mitigation results:** a systematic evaluation of positional bias in multi-video
  summarisation (arXiv 2606.04596) found explicit "allocate equal attention" prompts produce **no reliable
  mitigation**, and for one model the curve flattened by *lowering* edge coverage rather than raising the
  middle — *"the prompt can reshape the position-wise coverage curve but does not consistently improve
  summary quality or remove position bias."* [U on numbers.]
- **The one big prompt-only number, and what it really is:** Anthropic's Claude 2.1 needle-in-a-haystack blog
  (vendor, not peer-reviewed) reports that one assistant-turn prefix — `Here is the most relevant sentence in
  the context:` — moved 200K-token needle retrieval **27% → 98%**. Same family as the synthetic tasks where
  query-aware contextualization worked and then failed to transfer. **Treat as an existence proof for
  extract-before-answer, not as an expected effect size.** Mechanically it is the same move as the
  deterministic-extraction fixes: force the evidence span out before committing to an answer.

**On noticing that the situation has changed — BEAM's numbers, because they are brutal.** BEAM
(arXiv 2510.27246, **ICLR 2026, 52 cites**), knowledge update, vanilla full-context → RAG → their LIGHT: at
100K, Qwen2.5 0.437 → 0.275 → 0.362; at 1M, Qwen2.5 **0.064** → 0.378 → 0.357; Llama-Maverick
0.164 → 0.342 → 0.414; at 10M, 0.100 → 0.300 → 0.275. **Nothing exceeds ~0.45 on knowledge update at any
length. Contradiction resolution: 0.006–0.050 at 100K, collapsing to 0.000–0.025 at 10M across essentially
every method.** **If our robot needs to *notice* a contradiction rather than merely answer, no published
system does this.**

### 2.6 The four prompt arms to run anyway, and why

1. **Reframe the routine card; do not delete it.** `As of {date}, the household routine was recorded as: "…"`
   — attributed, dated and defeasible, so it reads as a stale *observation* rather than a standing rule. This
   is the intersection of four independent literatures: Zhou et al.'s opinion/attributed reframing
   (**MR 35.2 → 9.1 zero-shot**), MenatQA replicating the same template as its best prompt (**+7.71 EM**,
   beating both temporal prompts), Control Illusion (**authority framing beats role markers; social-consensus
   framing took Qwen-7B from 14.4% to 65.8%**), and Self-Correction Bench's **64.5% model-attributed blind
   spot**. **It has never been tested on intra-context conflict between a written prior and a
   recent-observation list — the inter-context cell of the Xu et al. taxonomy. That gap is
   contribution-shaped.** Zero extra calls.
2. **`Wait`, or an extract-before-answer prefix.** 89.3% blind-spot reduction across 14 open models at zero
   cost; the Claude-2.1 prefix is the same move. Zero extra calls.
3. **Ordering, and test both directions.** HoH swings Qwen-2.5-7B's composite by **over 50 points** on
   ordering alone with **opposite signs for Llama-70B and Qwen-7B**; Xie et al. measure >30-point swings on
   7B models. COLM 2025 on **Gemma-2-27B** says that below 50% window occupancy the *front* of the prompt is
   maximally privileged, which is where our card sits. So: newest sightings last, card not first, and
   measure — **do not assume the sign.** Zero cost.
4. **`Today is {date}.` plus Wallat et al.'s verbatim mutability sentence.** 0 to +20, median ~+6, negative on
   one of six. Cheap to test, not to bank on. **Do not stamp the context with a date newer than the cutoff
   without checking** — that lowered Qwen-3-8B's mutability reasoning from 20.5% to 11.1%.

**And one nearly-free non-prompt arm with the best cost/benefit in the literature:** one temperature-0
structured-JSON call that extracts **every** matching sighting verbatim **without ranking them**, then
`max(timestamp)` in Python. **+10.8pp average, +21pp at long context**, 2 calls, ~$0.0001/query
(Reddy & Challaram, arXiv 2606.01435, 4 cites — v1 was titled *"Don't Ask the LLM to Track Freshness"*). The
author names our mechanism: **"prior-override — LLMs ignore explicit freshness rules when facts conflict with
strong training-data priors"** and *"serial-comparison drift"*. Restricted to questions where the newer fact
was *provably retrieved*, the LLM baseline still falls 78% → 66%, i.e. *"post-retrieval judgment failure
rather than retrieval issues."* **Two caveats the authors themselves report, and we must carry:** most of the
gain comes from *separating evidence identification from policy execution*, not from the freshness operator
(swapping only the final executor is worth 2.0pp average and 0pp at 262K); and **on LongMemEval
knowledge-update it does not help — 26/45 vs 29/45, paired McNemar p = 0.45** — *"bounding the result to
current-value questions with explicit version metadata."* FactConsolidation hands the model serial numbers;
real conversations do not. **Our timestamps are the analogous crutch, and testing whether they suffice is
exactly the experiment to run.** Models were closed-weight only, so 27B behaviour is unknown.

### 2.7 How to frame this in the paper

**Do not present prompting as a candidate fix. Present it as a measured non-fix**, which is now a
well-supported claim with STALE, Sun & He, Wallat et al., HoH, evolveQA, Qiao et al., Prior Prejudice and
Right-Knowledge-Wrong-Answer behind it. Our card ablation is the more interesting result and it has a clean
home: it is a **premise-resistance failure** (STALE's PR, 4.0% on a Qwen 27B), it is quantitatively mirrored
by Xie et al.'s confirmation-bias table, and the literature says it is fixed by **attribution, not recency**.
The strongest empirical addition would be a five-arm read-time comparison — card as standing rule / card as
dated attributed observation / no card / card plus extract-then-`max()` — against one write-time arm that
retires superseded sightings. The literature predicts the ordering of those arms and nobody has run them on a
local model in an embodied memory setting.

---

## 3. Hypothesis reweighting and regime inference with LLMs

### 3.0 The answer to the critical sub-question, first

**Almost none of this literature has been evaluated where the right answer changes over time, and the
split is clean.** The LLM-Bayesian and hypothesis-reweighting work (BIRD, Bayesian Teaching, BayesBench,
BayesPE, HypoGeniC, Hypothesis Search, Hypothesis Refinement, BoxingGym, the SMC family, BeliefMem) is
uniformly evaluated on **stationary latent truth**: "sequential belief updating" in these papers means
evidence accumulating about a **fixed** fact, which is the opposite of our setting. Non-stationary ground
truth with feedback exists in two other places — the **cognitive-science-style reversal-learning**
literature, and the **memory-benchmark** literature — and neither overlaps with the hypothesis-reweighting
methods. No published work infers a regime from a per-question correctness signal and uses it to reweight
what is **read** from an already-sufficient prompt. That is the hole.

### 3.1 The single best citation we found in this whole survey

**"Comparative reversal learning reveals rigid adaptation in LLMs under non-stationary uncertainty"**
(Haomiaomiao Wang, Tomás E. Ward, Lili Zhang; arXiv 2604.04182, 5 April 2026; **IPMU 2026**, SS04
Explainable AI and Decision-Making Under Uncertainty; 0 cites, too new). I verified the whole of the
following in the paper's HTML myself:
- Two-armed probabilistic reversal task, **three latent states: s=0 [0.80,0.20], s=1 [0.50,0.50],
  s=2 [0.20,0.80]**. The fixed schedule is **s_{m+1} = (s_m + 1) mod 3**, i.e. **0→1→2→0→…** — it
  **returns to the original state**. There is also a stochastic schedule.
- **N = 200 runs per condition, T = 250 trials per run.**
- Each trial's prompt is a system instruction plus "the current trial index and a **running history of
  prior choices and outcomes**" — so the model has every piece of evidence it needs in its context, exactly
  as ours does.
- Models: DeepSeek-V3.2, Gemini-3, GPT-5.2, against human behavioural data.
- **Win-stay > 0.93 for every model. Lose-shift: DeepSeek-V3.2 0.035 (fixed) / 0.038 (random);
  Gemini-3 0.235 / 0.210; GPT-5.2 0.241 / 0.209; humans 0.495.** The asymmetry is the finding: positive
  evidence is used, negative evidence is not.
- **Perseveration length after a reversal (consecutive trials still choosing the previously-optimal
  action): DeepSeek-V3.2 19.63 fixed / 27.39 random; Gemini-3 7.24 / 10.05; GPT-5.2 7.34 / 10.90;
  humans 2.87.**
- Higher volatility *increased* perseveration without uniformly reducing total reward — the paper's phrase
  is that high aggregate payoff can coexist with rigid adaptation. That is a direct warning about
  aggregate-accuracy metrics hiding an adaptation failure, and it is the argument for our windowed reporting.
- Frontier models only; no 27B-class local model; no stated-confidence measurement.

**Why this matters to us.** This is our experiment stripped to a bandit, with an A→B→C→A schedule and the
full outcome history in the prompt, and it finds that frozen LLMs perseverate 2.5–10× longer than humans
and specifically under-use *negative* evidence. Our 807-of-890 number is the question-answering shape of
their attenuated lose-shift. It is prior art for the phenomenon and it leaves the memory-over-an-episodic-
stream version — ours — open. Cite it early and prominently.

Adjacent, weaker: **"Set-shifting Behavioral Test for Harnessed Agents"** (Ye Ziwei; arXiv 2607.13396,
July 2026; COLM 2026 Workshop on Agent Behavior; 0 cites) — libraries of redundant tools whose hidden
reliability shifts; some models "latch onto a fixed routine within a few turns". **No reversion to the
original rule.** [U on its metrics.] And **"Semantic Bandits: In-Context Exploration-Exploitation is Biased
by Semantic Priors"** (arXiv 2608.16707, 2026; 0 cites) — in-context bandit exploration by a frozen LLM is
biased by semantic priors over the arm *names*. Relevant because our arms are **room names**, which carry
exactly such priors ("keys go by the front door"); this is the closest thing to a published account of the
resident-card effect we measured. [U — not verified beyond search-level.]

### 3.2 (a) LLM-based Bayesian reasoning: the theory is contested and the systems need training

- **"An Explanation of In-context Learning as Implicit Bayesian Inference"** (Xie, Raghunathan, Liang, Ma;
  arXiv 2111.02080; **ICLR 2022**; **1167 cites**) is the licence everyone cites for "the model is already
  reweighting hypotheses".
- **"Is In-Context Learning in LLMs Bayesian? A Martingale Perspective"** (Falck, Wang, Holmes;
  arXiv 2406.00793; **ICML 2024**; **61 cites**) tests the martingale property — a *necessary* condition for
  Bayesian learning on exchangeable data — and **finds violations and deviations from Bayesian
  uncertainty-scaling across three experiments**, tying this to unreliable uncertainty for safety-critical
  use. **This is the citation for "do not assume our model's stated confidence behaves like a posterior",
  which is directly our third measurement.**
- **"LLMs are Bayesian, In Expectation, Not in Realization"** (Chlon, Sheaib, Khamis, Chlon;
  arXiv 2507.11768; 0 cites) is the rebuttal: violations are Θ(log n / n) and come from positional
  encodings breaking exchangeability; optimality holds in expectation over orderings. The practical reading
  for us is the opposite of reassuring: **behaviour is order-dependent, and order is exactly what differs
  between old-correct and new-correct evidence in our prompt.**
- **"Are LLM Belief Updates Consistent with Bayes' Theorem?"** (Imran, Kendiukhov, Broerman et al.;
  arXiv 2507.17951; ICML 2025 workshop; 9 cites) introduces a Bayesian Coherence Coefficient; larger models
  are more coherent. **No changing-truth condition.**
- **"LLMs are not (consistently) Bayesian"** (Chen, Jörke, Goliński, Fedzechkina, Sapiro, Williamson, Foti;
  arXiv 2605.06915, May 2026; 3 cites). The finding that should temper our ambitions: some
  evidence-incorporation methods give nearly-Bayesian updates and others a learned heuristic, and **the
  non-Bayesian heuristic updates frequently outperform exact Bayesian computation downstream**. Do not
  assume a more principled posterior beats a crude one here.
- **BayesBench** (Samanta et al.; arXiv 2606.30850, June 2026; 4 cites) — **seven LLMs from 3B to 70B**, the
  only one in this group whose scale covers ours. Finding: scaling improves latent inference and evidence
  accumulation, updates sometimes match the posterior, **but the gains do not carry over to downstream
  prediction**. That gap — inferred the latent state, did not use it — is our failure in someone else's
  benchmark. **No mid-sequence truth change.**
- **BIRD** (Feng, Zhou, Lin, Roth; arXiv 2404.12494; **ICLR 2025 Oral**; 23 cites). Abduction produces
  factors, then coarse verbal probabilities ("very unlikely"…"very likely") are mapped to numbers and the
  per-factor conditionals are **learned by constrained optimisation** (Bordley 1982 multi-factor
  approximation, MSE plus margin-ranking loss, **128 sampled complete-information instances per scenario**).
  READ-side, which is the right side for us — but **there is a fitted component per scenario, no online
  updating from feedback at all, and no changepoint notion. Not tested on changing facts.** Do not build it.
- **Bayesian Teaching** (Qiu, Sha, Allen, Kim, Linzen, van Steenkiste; arXiv 2503.17523;
  **Nature Communications**; 37 cites): LLMs "fall far short" of the Bayesian standard by default, and
  **supervised fine-tuning on traces from a normative Bayesian model** fixes it, with transfer. Requires
  weight updates, so out of scope — but cite it as the reason not to expect a frozen model to update well
  unprompted.
- **BayesPE / Bayesian Prompt Ensembles** (Tonolini, Aletras, Massiah, Kazai; **Findings of ACL 2024**;
  32 cites): output probabilities are a weighted ensemble over M semantically equivalent instructions, the
  weights being a prompt posterior fitted by approximate variational inference on a small labelled
  validation set. From the authors' repo: **9 instructions, weights fitted by one call on 100 labelled
  validation examples, 5 forward passes per test input** in the worked example. Black-box, no fine-tuning,
  changes how the answer is weighted at READ time. **Weights are fitted once; no incremental updating and
  no non-stationary evaluation** — which is precisely the hole our feedback signal fills for free.
- Peripheral: **LLAMBO** (arXiv 2402.03921, ICLR 2024, **200 cites**) — frozen LLM as BO surrogate/prior,
  stationary objective. **LLM Processes** (arXiv 2405.12856, NeurIPS 2024, 69 cites) — explicit numerical
  predictive distributions from a frozen LLM, regression, not multi-hypothesis, no non-stationary data.
  **Amortizing intractable inference** (arXiv 2310.04363, ICLR 2024, 109 cites) — GFlowNet fine-tuning,
  out of scope.

### 3.3 (b) Hypothesis generation and testing: HypoGeniC is the one usable method

**HypoGeniC — "Hypothesis Generation with Large Language Models"** (Zhou, Liu, Srivastava, Mei, Tan;
arXiv 2404.04326; NLP4Science @ EMNLP 2024; **109 cites**). I re-verified the mechanism in the HTML myself:
- A **hypothesis bank**, sizes **3 and 20** in the experiments.
- The update rule is **arithmetic, not a prompt asking for a score**:
  **r_i = ( Σ_{(x_j,y_j)∈S_i} 1[y_j = ŷ_j] ) / |S_i| + α·√( log t / |S_i| )**
  — empirical accuracy of hypothesis i on the examples S_i where it has been evaluated, plus a UCB
  exploration bonus, t the training timestep.
- New hypotheses are generated only when a **wrong-example pool reaches w_max = 10**; low-reward
  hypotheses are then replaced.
- Three inference strategies: best single hypothesis; **filter-then-weighted-vote with weights = training
  accuracy**; single-step adaptive selection by similarity of the test example to each hypothesis's
  training instances (plus a two-step variant).
- Gains over few-shot: **+31.7% (Shoe Sales), +13.9% (Deceptive Reviews), +3.3% (Headlines),
  +24.9% (Tweet Popularity)**; also beat supervised learning.
- **Changes what is READ at answer time.** Right side of our divide.
- **Not tested on changing ground truth.** But the reward's first term is a *running accuracy per
  hypothesis*, so making it non-stationary is a one-line change. See the recommendation.

- **"Phenomenal Yet Puzzling: Testing Inductive Reasoning with Hypothesis Refinement"** (Qiu et al.;
  arXiv 2310.08559; **ICLR 2024**; **130 cites**): propose → execute on examples → revise, with a symbolic
  interpreter supplying the feedback. The "puzzling" result is that models propose plausible rules yet
  **fail to apply them consistently**, and the gains come largely from the executor rather than the model's
  own revision. That dissociation — having the right hypothesis and not using it — belongs next to our
  807/890. [U on mechanism detail this pass.]
- **"Hypothesis Search"** (Wang, Zelikman, Poesia, Pu, Haber, Goodman; arXiv 2309.05660; **ICLR 2024**;
  **172 cites**): natural-language hypotheses implemented as Python programs, kept if consistent with the
  examples. The "weight" is a **hard consistency filter over a batch**, not a soft score; no online
  updating, stationary ARC-style tasks. [U on mechanism detail this pass.]
- **BoxingGym** (Gandhi et al.; arXiv 2501.01540; 12 cites): ten environments as generative models, agents
  design experiments, scored by **Expected Information Gain** and by communicating the discovered theory.
  Stationary generative models, no mid-episode regime change. Relevant to us only as the *evaluation idea*:
  EIG is the principled way to score "should I ask the human?", which is our answer-versus-ask decision.
- **DiscoveryBench** (arXiv 2407.01725; cites n/a), **"Toward Auditable AI Scientists: A Hypothesis
  Evolution Protocol for LLM Agents"** (arXiv 2607.09195, July 2026; 3 cites — an explicit
  hypothesis→test→evidence→belief cycle, materials science, fixed underlying reality), **"Hypothesis-Driven
  Skill Optimization for LLM Agents"** (arXiv 2606.22330; 4 cites). All stationary. [U on internals.]

### 3.4 (c) Persistent hypotheses and multiple world-states

**An important clarification to put in the paper: in the LLM+SMC literature the particles are token
prefixes, not world-states.** **SMC Steering** (Lew, Zhi-Xuan, Grand, Mansinghka; arXiv 2306.03081;
88 cites), **Twisted SMC** (Zhao et al.; arXiv 2404.17546; ICML 2024; 81 cites) and **"Syntactic and
Semantic Control of LLMs via SMC"** (Loula et al.; arXiv 2504.13139; **ICLR 2025**; 53 cites) all resample
partial generations against potentials during decoding. None carries a persistent world hypothesis across
questions or days. **This family is a smarter decoder, not a particle filter over "which regime is the
household in".** Cite it and say so explicitly, or a reviewer will ask why we did not use it. Cost is k×
decoding with a custom sampler that vLLM does not provide out of the box.

**BeliefMem / "Belief Memory: Agent Memory Under Partial Observability"** (Liao, Wang, Zhu, Du, Yan, Chen;
arXiv 2605.05583, May 2026; 6 cites) — already in SURVEY.md, but the reading there should be sharpened.
It retains **multiple candidate conclusions with probabilities** per observation, updated by **noisy-OR** as
observations arrive, and surfaces all candidates with their probabilities at retrieval — so it touches READ
as well as STORED. Its stated motivation is "self-reinforcing error", which is our failure mode named.
Evaluated on LoCoMo and ALFWorld; **non-stationarity not addressed**. **The decisive objection: noisy-OR is
monotone in evidence — support never decays — so across our disruption and return it would accumulate
support for both the old and the new location and never prefer one over the other.** Cite as prior art and
as a foil. [U: candidate count, whether the update is arithmetic or prompted, and calls per observation are
not in the abstract; worth one method-section fetch before citing mechanics.]

**Bayesian-Agent** (Wu et al.; arXiv 2606.08348, June 2026; 0 cites): reusable skills as Bayesian evidence
objects, a **feature-conditioned categorical posterior per skill**, mapped to inspectable actions (patch,
split, compress, retire, explore), explicitly contrasted with "heuristic reflection or raw success counts";
benchmarks RealFin-Bench, SOP-Bench, Lifelong AgentBench. **The posterior is over skills, not world-states**,
and non-stationarity is not claimed. Not our problem. [U on the update rule.]

**The two robotics papers that are mechanically closest to our task, and neither is in SURVEY.md:**
- **CoCo-TAMP — "LLM-Guided State Estimation for Partially Observable Task and Motion Planning"**
  (Kim, Arora, Martín-Martín, Stone, Abbatematteo, Sung; arXiv 2603.03704, March 2026; 3 cites). Two
  LLM-supplied priors — objects are more likely in certain locations, and similar objects co-locate —
  implemented as LLM multiple-choice QA over rooms/surfaces plus LLM sentence embeddings for a
  similarity-based co-location model, with a "co-location toggler" that disables co-location when semantics
  imply dispersion (light switches). **Beliefs are maintained in an explicit hierarchical Bayes filter over
  rooms → surfaces → poses**, with a visibility-aware observation model for misses. **62.7% reduction in
  planning+execution time in simulation, 72.6% real-world** against a no-commonsense baseline.
  **This is the division of labour worth copying: the LLM supplies the prior, arithmetic does the updating.**
  But the filter updates from *observations*, not from outcome feedback, and there is no regime change.
  [U: call counts, hypothesis count, and whether objects move mid-episode. Worth a full method read before
  we write related work.]
- **GLOBE — "Personalized and Robust Proactive Robot Assistance with Uncertainty-Guided LLM Reasoning"**
  (Gonzalez, Shovo, Ayub; arXiv 2606.08458, June 2026; **IEEE RO-MAN 2026**; 0 cites).
  **n-gram Markov models capture the temporal behavioural pattern and the LLM is invoked only when the
  Markov model's confidence is low.** Introduces **HOMER-Noise**, a noisy extension of HOMER+ simulating
  structured disturbances from humans, pets and toddlers. **This is the closest published system to our
  architecture and it is a direct precedent for "cheap statistical model in front, LLM on low confidence".**
  Whether the routine itself shifts during its evaluation is not stated [U]; the disturbances read as noise,
  not regime change. Worth checking whether we can run on HOMER-Noise.

**Tree-of-Thought / Graph-of-Thought:** multiple partial reasoning states scored by an LLM-as-judge prompt,
within one question, discarded afterwards; no cross-question persistence, no outcome feedback, no
non-stationary evaluation, O(breadth × depth) calls. Cite and dismiss. [U on mechanism this pass.]

### 3.5 (d) Change-point and regime detection with LLMs: the LLM is always the wrapper, never the detector

- **SigLLM — "Large language models can be zero-shot anomaly detectors for time series?"** (Alnegheimish,
  Nguyen, Berti-Equille, Veeramachaneni; arXiv 2405.14755; **IEEE DSAA 2024**; 53 cites): forecasting-guided
  detection beat direct prompting on all 11 datasets, but **classical deep-learning detectors beat the LLM
  pipelines by 30%** across 10 pipelines. **Read this as: do not ask our 27B to eyeball its own error stream
  for a change-point. Compute the statistic.**
- **"LLM-Augmented Changepoint Detection"** (Lukassen et al.; arXiv 2601.02957, Jan 2026; 0 cites): an
  ensemble of **ten classical changepoint algorithms** detects; the **LLM only writes the explanation**.
  Online/streaming not addressed. [U on which ten.]
- **EvoTS-Agent** (Jiang, Wei, Xi, Langham-Lopez, Bao, Khraishi, Ang, Tung, Szpruch, Ni; arXiv 2608.17933,
  Aug 2026; 0 cites): the agent **selects and configures classical detectors**; three evolution operators
  (Revision, Alternative Strategy, Recombination) driven by validation performance. Motivation stated: no
  single unsupervised CPD algorithm works across market regimes.
- **TIME-LLM** (arXiv 2310.01728; **ICLR 2024**; **1195 cites** — the most-cited item in this section):
  reprogramming for forecasting, **requires training an input projection**. Not change detection, not
  usable frozen.
- **"Exploring Zero-Shot Data Drift Detection with LLMs"** (Park, Nam, Cho, 2026, APMS/Springer) — paywalled,
  **[U]**, but it is the one paper that sounds like it asks our question directly.
- **Classical yardsticks:** **Bayesian Online Changepoint Detection** (Adams & MacKay; arXiv 0710.3742,
  2007; **923 cites**) — exact recursive filter over run-length with a hazard rate, O(t) per step, closed
  form for exponential-family likelihoods, **zero LLM calls**; **ADWIN** (Bifet & Gavaldà, SDM 2007) and
  **CUSUM** (Page 1954), a few arithmetic operations per observation.
- **We found no paper coupling BOCPD / ADWIN / CUSUM to an LLM agent's own outcome stream to control what
  the agent reads.** That is unoccupied ground and it is cheap ground.

### 3.6 (e) Test-time adaptation from outcome feedback with a frozen model

| Method | Citation | Mechanism | STORED / READ | Cost | Changing truth? |
|---|---|---|---|---|---|
| **Reflexion** | arXiv 2303.11366, NeurIPS 2023, **5372 cites** | after a failed episode an LLM writes a self-reflection string into an episodic buffer, prepended on retry; the "weight" is text, nothing is ever down-weighted or retired | both, but **monotonically** | 1 call per failure | **No** (HumanEval, ALFWorld, HotpotQA) |
| **ExpeL** | arXiv 2308.10144, AAAI 2024, **936 cites** | cross-task insight pool; LLM applies ADD / EDIT / UPVOTE / DOWNVOTE, importance starts at 2, removed at 0 | storage + retrieval mainly | offline extraction + retrieval | **No** (verified) |
| **Agent Workflow Memory** | arXiv 2409.07429, ICML, **285 cites** | induces reusable workflows, retrieves them into the prompt | **storage-only in our sense — unlikely to help us** | offline | **No** |
| **Algorithm Distillation** | arXiv 2210.14215, ICLR 2023, **219 cites** | trains a transformer on across-episode learning histories so in-context improvement emerges | n/a | **requires pretraining** | learns to adapt, but needs weights |
| **DPT** (Lee et al.) | arXiv 2306.14892 | same shape, pretraining required | n/a | n/a | n/a frozen |
| **Just-In-Time RL** | arXiv 2601.18510, Jan 2026, 13 cites | non-parametric memory of experiences; retrieves trajectories to **estimate action advantages on the fly** and uses them to **modulate the LLM's output logits** | **READ / decode — right side** | retrieval + a logit bias per decode; needs logit access, which vLLM gives us | motivated by non-stationarity; whether a regime change is *evaluated* unconfirmed [U] |
| **"In-Context RL under Non-Stationarity: A Survey"** | arXiv 2607.11906, July 2026, 0 cites | organises non-stationary ICRL by what changes, how it unfolds, how observable it is | — | — | **the framing citation.** Its abstract contains the sentence we want: "previously useful context can therefore become stale, misleading, **or useful again**" |
| **"Reward is Enough: LLMs are In-Context RL Learners"** | ICLR 2026, cites n/a | claims frozen LLMs self-improve in-context from **scalar rewards alone**, beating language-based self-reflection | READ | scalar reward in the prompt | unknown **[U, not primary-verified]** |

**Supersede — "Diagnosing and Training the Memory-Update Gap in LLM Agents"** (Vedant Patel;
arXiv 2606.27472, June 2026; 7 cites). The nearest published *diagnosis* of our problem, and its answer is
the opposite of ours:
- Built on the **LongMemEval knowledge-update subset**. Oracle split ~2 sessions/question, 78 questions;
  `_s` split ~48 sessions (~122k tokens), 25 questions. Bounded notes field, typically **300 characters**.
- **Full context versus bounded self-maintained memory: gpt-4.1-mini 82% → 63% (p=0.0035); gpt-4.1
  91% → 64%; gpt-5.4 92% → 77% (p=0.0033).**
- Scale study: oracle 68% → `_s` 28%; **giving 24× more notes budget (300 → 7,150 characters) recovered
  nothing — still 28%**. The failure scales with conversation length, not compression ratio.
- Their fix is **GRPO fine-tuning** of Qwen2.5-3B on 2,000 generated episodes: 9.0% → 16.7%.
- **Their errors are "dominated by the relevant fact being compressed away or not overwritten", and the
  model typically claims no information exists rather than giving the stale fact. They do not report a
  "correct answer present but stale answer given" breakdown.**
- **No fact ever reverts.** Forward-only updates.

**This is good news for the paper.** The field's flagship diagnosis of the memory-update gap attributes it
to *compression*, and shows that more storage budget buys nothing. Our 807/890 is the complement: present
and unused. We can say, with citations, that when compression is removed as an explanation the gap persists,
and that no benchmark, Supersede included, tests a return to a previously-correct value.

Other non-stationary evaluations to name: LongMemEval's knowledge-update type; **BEAM** (ICLR 2026,
updating information and contradiction resolution); Memora/FAMA; TemporalWiki. All storage/retrieval-focused
and all forward-only. [U — metadata from search, not individually primary-verified.]

---

## 4. Memory as a tool, and multi-agent memory

### 4.1 Three things this section establishes, all unfavourable to the premise

1. **Giving the agent explicit write/edit/delete tools is the 2025–26 consensus design and it is essentially
   never evaluated on facts that change.**
2. **Where tool-based memory *has* been re-evaluated on a conflict-resolution axis, it barely beats the plain
   buffer.**
3. **The field's own diagnostic now names our failure and locates it at the point of use.** A-TMA calls it
   **"ghost memory"** — *"old, current, and transition facts coexist in the memory bank, remain mixed during
   retrieval, and mislead the answer model"* — and demands *"decoupled evaluation of bank, retrieval, and
   answer level failures, since final QA accuracy can hide where ghost memory occurs."*

The read-time interventions with real numbers on changing facts are: **constrained or labelled readout**
(A-TMA, CUPMem's step 3), **separating evidence extraction from policy execution** (§2.6), **an adversarial
critic role** (DoT-Prompting), and — unique to a robot — **probing the environment to re-check a belief**.

### 4.2 (a) Memory as a callable tool

**The reference implementation, with no changing-facts evaluation anywhere.** Anthropic's memory tool
(`memory_20250818`, public beta 2025-08-18) plus context editing (`clear_tool_uses_20250919`). No paper. Six
client-side commands the model *requests* and your handler executes: `view`, `create` (creates **or
overwrites**), `str_replace` (**omitting `new_str` deletes `old_str`**; refuses on multiple occurrences),
`insert`, `delete` (recursive), `rename`. The API silently prepends to the system prompt
`IMPORTANT: ALWAYS VIEW YOUR MEMORY DIRECTORY BEFORE DOING ANYTHING ELSE` plus an "ASSUME INTERRUPTION"
protocol, and the docs' only invalidation guidance is the suggested reinforcement *"when editing your memory
folder, always try to keep its content up-to-date, coherent and organized. You can rename or delete files that
are no longer relevant."* Context editing is server-side and separate: `trigger` (default 100k input tokens),
`keep` (default 3 tool uses), `clear_at_least`, `exclude_tools`, applied after cache lookup and before token
counting.
**STORED and READ both** — `str_replace`/`delete` change what is stored, `view` changes what is read — **but
nothing in the design adjudicates between two surviving entries: a stale note and a fresh note can coexist in
the same file and both get read.** Cost on a frozen 27B is trivial (a tool schema plus a file handler, no
training). **Changing facts: no published evaluation, by Anthropic or anyone.** The only numbers are
Anthropic's own internal agentic-search eval (+39% memory+context-editing, +29% context-editing alone, 84%
token reduction on a 100-turn web-search eval) on an unnamed internal set. **The catch:** the behaviour
Anthropic gets comes from an API-injected system prompt plus a frontier model's willingness to maintain a
directory, and the Memory Trust Gap result (§4.4) says a 27B-class model is precisely where that willingness
fails.

**The closest thing to an audit of that pattern.** "Filesystem-based memory" (Sizhe Zhou et al.;
arXiv 2607.26637, Jul 2026; 0 cites) formalises deployed markdown-directory practice as three roles — a
management agent, a search agent retrieving with citations, an execution agent — on LoCoMo, PersonaMem,
REALTALK and ALFWorld. **The finding that matters: in the conversational setting agents predominantly *edit*
existing files rather than delete them; "early memories survive."** The paper acknowledges that stores contain
"duplicates, contradictions, stale facts" and **does not systematically evaluate outdated-fact handling**.
**So the pattern's own audit shows the stale entry stays in the file.**

**AutoMEM / DCI-Lite — tool-based memory on a frozen ~30B, and the conflict number is missing.**
(Chen, Gu, Yin, Long, Zeng, Liu, Guo, Zhou, Tang; arXiv 2606.04315, 3 Jun 2026; 1 cite.) Action set = `rg`
(regex over raw records), `read` (fetch by id), `dump` (send a short corpus to the answer LLM), `index_query`
(typed query, by default Cypher over a graph built from LightMem's write-time summary index). Loop: a
**planner** LLM emits one action → executor runs it → evidence appends to a trace → a **judge** LLM assesses
sufficiency and returns a hint if insufficient → an **answerer** composes. **3–4 LLM calls minimum per
question**, one backbone for all roles. Backbones **Qwen3-32B**, Qwen2.5-7B-Instruct on ALFWorld,
Qwen3-Embedding-4B. **No fine-tuning of AutoMEM or of any baseline.** Headline, verbatim: the harness that
"self-manages flat text-file storage via tool calls" achieves the best cross-task ranking, and "memory
performance hinges on **giving the agent active control** over storage and retrieval rather than on a passive
store behind a fixed pipeline."
**The load-bearing detail.** Table 3, **Conflict Resolution** column: **long context 12.0 · SimpleMem 20.0 ·
LightMem 16.0 · HippoRAG 14.0 · PlugMem 24.0 · AMA-Agent 12.0 · DCI-Lite 14.0 · DCI-Lite+Sum 16.0 ·
Mem-T 10.0 · MemRL 6.0.** **AutoMEM itself appears only in a separate table on LoCoMo/HotpotQA/AMABench — it
has no reported CR score.** **So the paper that concludes "give the agent tools" never measures its own method
on the axis where facts change.** That is the single most citable fact in this section. Also verified: index
methods failed on agentic trajectories partly because "passive retrieval couldn't surface evidence the storage
retained" — a storage/read split like ours, on the retrieval side.

**PlugMem — the best conflict-resolution score in the field, and it is 24 out of 100.** (Yang, Chen, He,
Jiang, Galley, C. Wang, Gao, Han, Zhai; arXiv 2603.03296; **ICML 2026**; 27 cites.) A task-agnostic plugin over
a knowledge-centric memory graph whose units of access are *knowledge*, not entities or chunks, with
**create / retrieve / update ("revising existing memory entries when new evidence becomes available") /
delete ("removing obsolete or low-utility memory")**. **Its own paper does not evaluate conflicting or
obsolete facts**; CR = 24.0 comes from AutoMEM's independent re-run. Worth trying because it is the only
system with an explicit delete-obsolete operation that leads a conflict column — **but 24/100 is not a
solution.** Training status not stated; presumed prompted [U].

**AgentRunbook-C — files plus a coding agent, big win, wrong axis.** (Wu, Ji, Kawatkar, Kwan, Gu, Peng,
Chang; arXiv 2605.12493, May 2026; 13 cites.) LongMemEval-V2: 451 curated questions, histories to 500
trajectories / 115M tokens, five abilities including **dynamic state tracking**. Storing trajectories as files
and invoking a coding agent to gather evidence in a sandbox gives **72.5% versus 48.5% for the strongest RAG
baseline and 69.3% for an off-the-shelf coding agent** — **the strongest published evidence that agentic,
tool-mediated *reading* of a file store beats fixed retrieval.** Caveats: high latency, and the axis is
environment experience rather than fact supersession; dynamic state tracking is not broken out as a
replace-a-fact test.

**Claude Agent Skills are the wrong tool for this, by their own measurement.** "Demystifying Agent Skills:
Why They Work—Until They Don't" (Jiang et al.; arXiv 2608.14036, Aug 2026; 1 cite): 8,135 normalised trial
records, 238 labels. **"Procedural anchoring accounts for 65.7% of skill cases, versus 4.5% for explicit
knowledge injection, showing that skills stabilize action rather than inject missing facts."** Skills beat
Workflow Memory by 6.06 points in matched comparisons, but **as skill pools grow 5 → 100, actual-use precision
falls 29.6% → 3.3%.** Nothing about stale instructions.

**Storage-only tool-memory papers — unlikely to help us, and here is why for each.**
- **MemTool** (Lumer et al.; arXiv 2507.21428; 17 cites): three modes for adding and removing **tools and MCP
  server contexts** from short-term memory; reasoning models hit 90–94% tool-removal efficiency, **mid-size
  models 0–60%**. **What is removed is tool definitions, not facts.** Its one transferable datum is that
  mid-size models are bad at deciding what to evict.
- **ByteRover** (arXiv 2604.01599; 2 cites): hierarchical Context Tree with provenance and an "Adaptive
  Knowledge Lifecycle" (importance, maturity tiers, **recency decay**), 5-tier retrieval resolving most
  queries sub-100ms without LLM calls, SOTA on LoCoMo. **No supersession evaluation, and recency *decay* is
  not recency *adjudication*** — decay would fade our old routine during the ten sick days and then have
  nothing to revive.
- **LeanMem** (arXiv 2608.03463; 0 cites): routes content into profile / event / record memory by
  compressibility and **volatility**, updating only "dynamically evolving event memories"; LoCoMo +
  LongMemEval-S on GPT-4.1-mini and **Qwen3-8B**, up to +15.1. **No superseded-fact evaluation.** The
  volatility split is the free idea; the paper gives no evidence it survives a reversal.
- **DeMem / "Remember the Decision, Not the Description"** (arXiv 2605.10870; 4 cites): decision-centric
  rate-distortion with an exact forgetting boundary, refining its partition "only when data certify that a
  shared state would induce decision conflict". The most principled forgetting criterion here — but it is an
  **online learner**, and no supersession evaluation.
- **MemTools** (arXiv 2607.21404; 0 cites): interoperability infrastructure only. **The abstract does not
  even state whether its standardised operations include invalidate or delete.** No scientific content for us.
- **LangMem** (LangChain, no paper): "hot path" tools `create_manage_memory_tool` / `create_search_memory_tool`
  the agent calls inline, plus a background manager that consolidates outside the request path; consolidation
  is advertised as "resolving contradictions". **No published evaluation** [U].
- **OpenAI:** **there is no technical report on memory mechanics.** The ChatGPT Agent system card (Jul 2025)
  states memory is *disabled*. The only circulating number is OpenAI's own self-reported time-sensitive
  evaluation of updating outdated context, **75.1% up from 9.4% in 2024**, cited second-hand [U].
- **Requires training, therefore out:** **VerMem** (arXiv 2608.03137) — seven atomic operations including
  add / revise / **soft-delete**, but SFT-initialised plus a three-stage RL curriculum, and *"the verifiers
  are used only during training"*; **MEMO** (arXiv 2609.07471) — a trained query-conditioned memory manager
  supervised by an offline reader's utility.

**Parametric, test-time-learned and editable memory: a clean sweep of disqualifications.**

| method | citation | cites | mechanism | frozen 27B? | changing facts? |
|---|---|---|---|---|---|
| MemAgent | 2507.02259 | 214 | 1024 natural-language memory tokens, **overwritten** per chunk | **No** — the mechanism *is* Multi-Conv DAPO RL | accumulate only |
| MemoryLLM | 2402.04624, ICML 2024 | 84 | 7,680 latent memory tokens/layer × 32 ≈ **+1.066B params**; update = forward pass, drop K oldest | **No** — co-pretrained with Llama2-7B, 8×A100 × 3 days | forgetting is **positional, not contradiction-aware** |
| M+ | 2502.00592, ICML 2025 | 46 | evicted tokens → CPU store; **co-trained retriever** pulls back 2,560 long-term + 10,240 short-term | **No** — 3-stage curriculum | trained for relevance, **no recency or supersession notion** |
| Titans | 2501.00663, NeurIPS | 338 | MLP memory whose **weights update at test time** by online GD on a surprise loss | **No** — *"models are trained from scratch"*, 170M–760M | no contradictory-information condition |
| ATLAS / Miras / HOPE | 2505.23735 / 2504.13173 / 2512.24695 | 60 / 60 / 89 | Omega-rule; 4-axis framework with a **retention gate**; nested optimisation + **Continuum Memory System** = banks updated at **different frequencies** | **No** — architectures | no change-of-fact eval [U]. **CMS's multi-frequency split is the one architecturally right idea** — and it is free as a *prompting* ablation: a fast bank for the 10-day window, a slow bank for the routine |
| Larimar | 2403.11901, ICML 2024 | 54 | fixed K×C memory matrix; writing = **one-shot pseudo-inverse solve, no gradient steps at inference** (1.1–1.7s vs ROME 4.8–13.9s); **selective forgetting by overwriting a slot** | **No** — encoder, read-weight distribution and decoder-side projection trained on 7.6M WikiText chunks; needs hidden-state access | **best-evaluated on change in this scope**: forgotten-fact recall **0.0** while the other 511 stay at **0.997**; 1,000 sequential ZsRE edits, retention 0.97 vs GRACE 0.93. Still permanent replacement, never a revert |
| ROME / MEMIT / GRACE / WISE / AlphaEdit | 2202.05262 / 2210.07229 / 2211.11031 / 2405.14768 / 2410.02355 | **3,273 / 1,229 / 335 / 113 / 278** | weight or hidden-state edits | **No** | yes but **permanent**, and applied *before* the question — useless when the answer is already in the prompt |

**The degradation evidence is why not to go near weight editing at all.** Gupta, Rao, Anumanchipalli
(arXiv 2401.07453, **Findings ACL 2024, 118 cites**): sequential editing forgets in *"an initial gradual but
progressive forgetting phase followed by [an] abrupt or catastrophic forgetting phase."* Yang et al.
(arXiv 2402.09656, Findings ACL 2024, 71): **a single edit can trigger collapse.** **WikiBigEdit** (Thede
et al.; arXiv 2503.05683; **ICML 2025; 30 cites**): 500K+ real QA pairs from Wikidata diffs over eight 2024
timesteps — ROME/R-ROME/MEMIT *"rapidly degrade within the first few hundred updates, leading to model
collapse"*, WISE decays within 10K updates back to pre-update accuracy, and **plain RAG vastly outperforms
every specialised editor.** LightEdit's Table 5 is the cleanest single citation: after 1,000 sequential edits,
base MMLU 0.681 → ROME 0.269 / MEMIT 0.235 / AlphaEdit 0.366, TriviaQA 0.518 → ≈0.00, while LightEdit sits at
0.6108 against base 0.6092.
**And the serving blocker, before accuracy is even discussed:** RW-TTT (arXiv 2605.28053; 0 cites) states it
in one line — *"Test-time training adapts an LLM during generation by reading and updating request-owned
state. This breaks batched LLM serving, which assumes shared static weights."* Their best result is 274.61
aggregate tok/s across eight fast-weight streams on one GPU. **Every fast-weight method is incompatible with
our vLLM deployment.**

**The one portable idea from that whole family: LightEdit's in-context decoding.** (Jung, Lee, Lim;
arXiv 2604.19089; **ACL 2026**; 1 cite.) **No parameter modification at all.** Two parts: an **edit-aware
selector** (an XLM-RoBERTa-large cross-encoder over `[CLS] q [SEP] (s,r,o*) [SEP]`, thresholded at 0.5, BCE on
1,000 instances / 1 epoch / one A100), and **in-context decoding on the first token only**:
`log p′(x₁) = log p(x₁ | C, q) − α · mean_edits log p(x_o | s, r)` with **α = 0.2**, where the subtracted term
is the log-probability of the first token of the **stale** object. ZsRE AVG **0.9664** vs RECIPE 0.9380,
AlphaEdit 0.6220, BASE 0.5182, ROME 0.0363; CounterFact 0.9296, RIPE 0.9818; inference 0.2024s vs MEMIT
11.94s. **Ablations we must respect: plain RAG 0.7615; selector-only 0.9312; and ICD *without* the selector
collapses locality to 0.4612** — unconditional suppression wrecks unrelated questions, so **the gate is
mandatory.** First-token-only (0.9664) beats all-tokens (0.9174). Generic ancestor to cite: **context-aware
decoding** (Shi et al., **NAACL 2024, 421 cites**) — LLaMA-30B NQ-Swap 9.6% → 37.7%, MemoTrap 25.8% → 50.6%,
two forward passes, no extra call — **but note that instruction-tuned FLAN-T5 gains only 71.4 → 73.3, and
FaithfulRAG's 2025 re-test puts CAD at +0–3 on instruction-tuned 7–8B models, so a modern instruction-tuned
27B may behave like FLAN-T5.**

### 4.3 (b) One agent curating memory for another

**The best fit for a robot, and the only curator paper with a large verified gain: environment-probing
curation.** "Grounding Agent Memory: Environment-Probing Curation for Enterprise Agents" (Suresh, Mak,
Bhatnagar, Methani, Gutierrez Munoz; arXiv 2609.11060, Sep 2026; 1 cite). A **post-task, asynchronous curator
agent** — a separate LLM session, not a continuation of the task agent, which cannot see future tasks — is the
only agent allowed to mutate the store, via `memory_read` / `memory_create` / `memory_update` /
`memory_delete`. The contribution is giving that curator **least-privilege, read-only world tools to "check,
scope, and refresh" candidate memories** before they are written: it **queries the live environment** rather
than reasoning only over the completed trajectory. Verbatim: *"It requires no model retraining and leaves the
task agent, retriever, memory representation, and production write authority unchanged."*
**Numbers:** on **CLBench** database exploration, probing raises pass rate **39% → 73%** and pass-discounted
reward **8.60 → 22.60**, while *reducing* queries 8.8 → 4.7 per question and task-agent cost $3.38 → $1.68.
Across **six APEX worlds** (90 adapted consulting tasks) all 18 memory-versus-baseline mean-reward comparisons
are positive, tool calls fall 16–75%, and probing gives the best reward gain per dollar in five of six.
**Storage-side — but with the crucial property that a *verified* store stops putting stale evidence in the
prompt at all, which is the one storage intervention that does address a read-time failure.** Cost: a few
curator calls per task plus world queries; no training. [U beyond the abstract on the exact stale/changed
evaluation categories.]
**Why this is our best structural match: a home robot can look again.** No conversational-memory paper has
that affordance; we do.

**A-TMA — "ghost memory", a three-level decomposition, and answer-time state labels.** (Shi, Tang, Tung;
arXiv 2607.01935, Jul 2026; 2 cites.) A **state-aware overlay for existing memory systems**. It deliberately
**keeps** superseded and transition records in the bank; builds **"evidence packets for the query's requested
state view"**; and **exposes `current` / `historical` / `transition` labels to the QA step**. Three
optimisation levels — bank maintenance, retrieval, **answer-time resolution** — and an explicit call for
**decoupled evaluation of bank / retrieval / answer-level failures "since final QA accuracy can hide where
ghost memory occurs."** New conflict-heavy benchmark **LTP (LoCoMo Temporal Plus)**. **Graphiti+ATMA improves
conflict accuracy by 0.240 absolute over Graphiti; LoCoMo temporal F1 0.0295 → 0.1705.** Gains are host
dependent. **It is an overlay, it is read-time, it needs no training, and its labelling scheme is exactly the
"pre-resolve the conflict before the answerer sees it" intervention that §4.4 says is the only thing that
works for small models.** We already have a Zep/Graphiti-style arm for it to bolt onto.

**Reflective Memory Management — the read-path half is the interesting half.** (Tan, Yan, Hsu, Han, Z. Wang,
Le, Song, Chen, Palangi, Lee, Iyer, T. Chen, Liu, Lee, Pfister, Google; arXiv 2503.08026; **ACL 2025;
123 cites**.) **Prospective Reflection** summarises at utterance/turn/session granularity into a bank
(storage). **Retrospective Reflection** iteratively refines *retrieval* online, using the LLM's own **cited
evidence** as the signal for which memories actually got used. **>10% accuracy over no memory management on
LongMemEval.** A genuine self-curating reader/writer split with no separately trained model, and
citation-based credit assignment is cheap to implement. **Changing facts: not isolated** — LongMemEval's
knowledge-update subset is present in aggregate with no per-category number.

**Teacher-student memory — training-free, but needs a teacher we do not have.** "Agent Memory Distillation"
(Kim, Kim, Hwang; arXiv 2608.07169, Aug 2026; 2 cites). A large teacher (GPT-5-mini) writes three memory types
from its *successful* trajectories: **Workflow** and **Subtask** injected proactively at task start,
**Function** memory retrieved reactively on tool-call errors. Four students at **4B–8B**: **+27.2pp AppWorld,
+11.2pp BFCL V3, +3.4pp ToolSandbox**, with **4B students benefiting most**. **Changing facts: none** — all
static. A precedent that a stronger curator lifts a small answerer substantially, and irrelevant as a
fact-currency method because **we have no stronger local teacher.**

**Multi-agent shared memory — storage and governance only; unlikely to help us.**
- **G-Memory** (G. Zhang, Fu, Wan, Yu, K. Wang, Yan; arXiv 2506.07398; **NeurIPS 2025; 95 cites**): a
  three-tier insight/query/interaction graph hierarchy, up to **+20.89%** embodied action and **+10.12%**
  knowledge QA across five benchmarks and three multi-agent frameworks. **No changing-facts evaluation. This
  is cross-trial experience accumulation — the opposite of invalidation.**
- **Collaborative Memory** (Rezazadeh, Li, Lou, Zhao, Wei, Bao; arXiv 2505.18279; 56 cites): private/shared
  tiers, immutable provenance, read policies projecting filtered per-permission views, write policies
  governing retention and redaction, provable policy adherence. **Access control, not currency.**
- **SSGM** (arXiv 2603.11768; 19 cites): **position paper, no experiments.** Citable for framing only.
- **TOKI** (Ziming Wang, single author, HKUST; arXiv 2606.06240; 4 cites): a **bitemporal** (valid time ×
  system time) operator algebra with Allen interval relations, typing four write-time heuristics —
  **last-writer-wins, evidence-weighted merge, await-confirmation, per-rule policy** — over a dual-row schema,
  each with an isolation precondition and a provenance **audit row** preserving the losing fact. One
  citation-worthy finding: *"every baseline that keeps a language-model judge on the write path admits at
  least one of three write-time anomalies."* But **write-time only**, no invalidate/retract operator distinct
  from the audit row, and the authors are candid: *"the audit-row defence moves LoCoMo by 0.86"* and *"the
  cross-system comparison stays underpowered and claims no superiority."* **The bitemporal schema could
  express valid → invalid → valid again; nothing in the paper exercises it (0 occurrences of "revert").**

**Where the surveys stand, which is the gap claim.** The 2026 surveys all decompose memory into
**write / manage / read** and all decline to name a benchmark for *currency*:
- **2603.07670** (62 cites) says only *"Long-lived memory stores accumulate stale records, and without
  explicit mechanisms the agent has no way to distinguish the 2024 address from the 2022 one"*, recommending
  temporal versioning and contradiction detection **as engineering practice, not evaluated capability**, and
  **does not frame read-time versus write-time failure as an open problem.** Its usable quotes are
  *"the primary bottleneck is no longer storage — it is retrieval quality"* and its open problems "learning
  to forget" and "self-reinforcing error, where false reflections persist unchallenged".
- **"Are We Ready For An Agent-Native Memory System?"** (W. Zhou, X. Zhou, Han, Xu, Li, Z. Li, Xiong, Wu;
  arXiv 2606.24775, Jun 2026; 12 cites): 12 systems × 5 workloads × 11 datasets, decomposed into
  representation/storage, extraction, retrieval/routing and **maintenance** — *"no single architecture
  dominates… effectiveness depends heavily on how well the memory structure aligns with the workload
  bottleneck"*, and **localized updates are more economical than system-wide reorganization.**
- **"Harness the Memory"** (Huang et al.; arXiv 2608.15008, Aug 2026; 0 cites): 26 metrics, 3 backbones,
  4 suites over seven substrate categories. The key line for us: *"broad retrieval benefits long-context
  factual QA, while **excessive retrieval can harm sequential decision-making by shifting attention away from
  action-critical context**"* — **more evidence in the prompt is actively harmful when the memory must drive
  behaviour.** Motivates **substrate routing**.

### 4.4 (c) Critics and debate applied to belief revision

**The Memory Trust Gap — frozen Qwen3 size series, and the sentence to design around.** (Hu & Ramachandran;
arXiv 2609.01852, Sep 2026; 0 cites.) A frozen, closed-set, action-scored benchmark with a **Benefit** suite
(unsolvable without the stored fact) and a **Safety** suite (an authoritative tool always holds the correct
value), on **Qwen3 0.6/1.7/4/8B**, replicated on Llama-Instruct and on **RGB** and **MisBench**. Verbatim:
*"A stale stored fact can override current authoritative evidence without warning."* In the Benefit suite
models answer with the **stale value 0.92–1.00 of the time at every scale** — "over-trust rather than
confusion". In a 2×2×2×2 factorial: **removing a label amplifies over-trust at every size; a recency feature
(stale dated newer) fools the larger models harder; source authority is weak and scale-flat; position flips
from positive to negative across the series.** And the sentence:
> ***"Mitigation is likewise capability-dependent: exposing metadata improves accuracy for the capable models,
> but only pre-resolving the conflict restores accuracy for the 2 smaller checkpoints."***
Framing control: at the three smaller scales models trust a stale **document** more than a stale **memory**.
**Implication: annotating our buffer with timestamps and hoping the 27B arbitrates is the documented failure
path. The conflict must be resolved before the answer prompt.**

**When Memory Lies — the nearest published setting to ours, and a sobering ceiling.** (Sun & Zhang;
arXiv 2608.04574, Aug 2026; 0 cites.) A dynamic FrozenLake testbed pairing **staleness detection** with
**downstream navigation**; three closed models and three open-weight VLMs; **1,800 detection runs, 12,000
text-mode navigation episodes** over four navigators at 50 seeds. Three findings:
1. *"Text solvability does not imply visual grounding"* — models that flag stale entries reliably from text
   span **vision F1 0.887 → 0.067** on identical grids.
2. *"Consuming stale memory without an audit is a safety liability: in our primary GPT-4o setting, an agent
   that trusts raw memory **dies more than twice as often as the same agent given no memory at all**."*
3. *"Auditing helps but does not close the gap: a **transparent read-time filter** removes much of the safety
   cost in text mode, yet **even oracle stale labels bring no further significant gain**."*
**Read the third point carefully: with perfect staleness labels there was no further gain. Detection is not
the bottleneck; answer selection under memory–observation conflict is.** This converges with STALE's SR-vs-IPA
split and with DERELAB's finding that *"several models correctly identified a weakening update yet failed to
revise their conclusion."*

**Provenance links are useless if nobody follows them, and the cheap remedy is content-shaped, not
freshness-shaped.** "When Stale Constraints Go Unchecked: Budgeted Verification Failures in Inherited Agent
Memory" (Nakayashiki; arXiv 2608.25553, Aug 2026; 2 cites; single-author, unvenued — low authority, concrete
numbers). Six memories, a **budget of two record inspections**, and a consolidated memory stating a constraint
whose source record has since been **superseded by a record that withdraws it**. **Sixteen LLMs inspected the
critical provenance path in about one episode in five and produced stale-consistent decisions 77.3% / 74.7% /
74.7%** of the time. Forcing one of the same two slots onto the critical path recovered **+74.0 / +72.7 /
+61.3** points, positive in every model. **And the remedy: a one-sentence, target-blind rule ("prefer memories
that state a limit on a candidate direction") moved the agent's own allocation onto the constraint's path and
recovered the oracle contrast (+89.3 points), while a content-free freshness cue did not materially redirect
allocation.** **Translation: "prefer the freshest sighting" is a content-free cue and is predicted to fail; a
content-shaped attention rule may not.**

**DoT-Prompting — an adversarial critic against the evidence, on our model family.** "Debate-of-Thoughts:
Resolving Knowledge Conflicts in LLMs Through Internal Deliberation" (Li, Hu, P. Wang, G. Zhang, Wu, Xu;
**ACL 2026 Long**, pp. 35674–35696). **Not answer-selection debate** — one model role-playing a critic
**against evidence**, which is the opposite of the MADAM-RAG/SR-DCR family already in SURVEY.md.
(1) **Multi-hypothesis generation**: one call yields M distinct *grounded* hypotheses, each attributed to a
document or to parametric memory, under a "Latent Coverage Assumption" that the answer lies in C ∪ K_θ —
**true by construction in our 807/890.** (2) **Adversarial internal debate** per hypothesis: a **Proponent**
mines support; a **Critic**, *forbidden from using the Proponent's premises*, finds fallacies, **assesses
evidence reliability, "e.g. outdated or non-authoritative sources"**, and supplies counter-evidence — stated
purpose *"suppressing Confirmation Bias and preventing the model from exhibiting a bias towards initial
hypotheses."* (3) **Evidential adjudication**: scores first, prose second, on `S_evid` (grounding, rewarding
verbatim quotation), `S_logic`, and **`S_source` — "prioritizing recent over outdated information"** —
`argmax` of the sum, with a **τ = 0.6 fallback to "Uncertain"**, which is a free abstention arm.
**Cost: 1 + 2M + 1 ≈ 8 calls at M=3**; output tokens 294 versus CoT's 311 for +12.8% on MuSiQue. Training-free
(DoT-**Tuning** needs LoRA SFT and is out). Base models **Qwen3-8B / Qwen3-14B** and Llama-3.1-8B — our
family. Qwen3-14B, prompting versus full-context: FaithEval-Counterfactual **71.9 → 78.2**, MuSiQue
**80.5 → 89.2**, SQuAD 85.8 → 91.3. **The ablation to remember: removing the Critic costs −13.0 average;
removing the judge only −3.7. If we can afford one extra role, build the adversary, not another judge.**
**Changing facts: no** — FaithEval plus KRE-adapted MuSiQue/SQuAD are synthetic entity swaps, and the recency
criterion in `S_source` is **asserted, never measured.**

**TEPA — deterministic revocation with a validity posterior, and the only published schedule that matches
ours.** (Y. Zhou, Ouyang, Zheng, Xiang; arXiv 2608.07429v2, Aug 2026; 0–5 cites.) Names the failure
**"memory pollution"**. A precedent `p = (k, v, s, f, σ, τ)` with lifecycle **σ ∈ {Hypothesis, Active,
Revoked}** and a **Beta-Bernoulli posterior mean of current validity** (α=β=1);
`conflict(xᵢ,xⱼ) = 𝟙[κ(xᵢ)=κ(xⱼ) ∧ ν(xᵢ)≠ν(xⱼ)]`; on a same-key conflict the stale precedent moves to a
**revoked archive excluded from retrieval but available for later re-promotion**. **Zero extra LLM calls** —
I verified in the HTML that the extractors κ,ν are hand-written and deterministic (controlled drift: "κ(x) is
the tuple of task type, domain, and input type, while ν(x) is the successful tool pattern") and that all
experiments use deterministic benchmark executors; the authors concede open-domain LLM-parsed keys are future
work. **I also verified the phase function verbatim: "A phase function ϕ(t)∈Φ maps each episode to a phase,
where Φ={stable,light,reversal,return}."** Reversal-phase success: **TEPA 0.950 vs append-only 0.210 vs
last-write-wins 0.210 vs no-memory 0.309** (controlled; 0.950 vs 0.203 / 0.203 / 0.298 file-backed
executable). On clean MemoryAgentBench SH-6k, **TEPA merely matches last-write-wins (0.890 vs 0.890, against
append-only 0.583)**, *"confirming that current-key replacement is the decisive operation for single-hop fact
consolidation."* They also define a **Memory Pollution Index** `MPI = (S_NoMem − S_mem)/S_NoMem`; **positive
MPI means the memory is a net harm**. [U: the per-phase numbers for the *return* phase are presented in a
heatmap figure and I could not extract them reliably; do not quote a return-phase number.]
**Our rolling buffer is the append-only arm, and 0.21 → 0.95 in the reversal phase is the largest effect
anywhere in this literature — obtained by changing what is stored, not by instructing the reader.**

**Self-contradiction detection — the honest numbers.**
- **ChatProtect** (Mündler, He, Jenko, Vechev; arXiv 2305.15852; **ICLR 2024; 189 cites**): extract a triple
  with CompactIE (**a trained IE model — the one non-frozen part**), regenerate an alternative sentence
  **conditioned on the same prefix**, have an analyzer LM judge the pair with CoT, then revise or **delete**.
  ~3 calls per sentence; detection ≈80% F1 with ChatGPT; 17.7% of ChatGPT sentences self-contradictory.
  **But it detects a model contradicting itself within its own output — there is no stored belief and nothing
  is revised in a memory.** The transferable piece is only the *trigger pattern*: same-prefix alternative plus
  a forced pairwise judgement, applied to (stale sighting, fresh sighting).
- **"Contradiction Detection in RAG Systems"** (Gokul, Tenneti, Nakkiran; arXiv 2504.00180): 1,867 synthetic
  samples over HotpotQA; validating the **whole context in one call** gives **precision 0.90–0.99 but recall
  0.04–0.57** — the failure mode is uniformly "no contradiction here". Best per-type accuracy **0.893 on
  pairwise, 0.006 on within-document self-contradiction**; CoT helps detection for Claude but *degrades* type
  classification. **Design consequence: if we build a detector, give it the pairwise framing with timestamps,
  never "read the whole log and find the conflict".**

**Belief-revision formalisms: nobody has done it.**
- **No paper implements AGM belief revision with an LLM.** Belief-R cites Alchourrón–Gärdenfors–Makinson
  (1985) as motivation only.
- **"Truth Maintenance Systems with LLMs" is a false friend.** In current usage (AutoEval,
  arXiv 2410.08437, **ICLR 2025**) "truth maintenance" means *truth-preserving autoformalization* checked by
  an equivalence checker. Not a JTMS/ATMS, and nothing to do with retracting a stale belief.
- **The symbolic-solver lineage solves the wrong problem.** **BeliefBank** (Kassner, Tafjord, Schütze, Clark;
  EMNLP 2021) uses a **weighted MaxSAT solver** over a hand-authored constraint graph plus a feedback
  mechanism that queries the LM *using already-believed facts as context* — that second half is a read-time
  intervention and is CUPMem's step 3, twenty years cheaper. **REFLEX** (EMNLP 2023) backward-chains a belief
  graph and minimises contradictions with a formal reasoner: **+8–11% absolute consistency**, at tens of calls
  per query. **ConCoRD** (Mitchell et al.; EMNLP 2022) gets pairwise relations from an **off-the-shelf NLI
  model** and solves MaxSAT. All three are **synchronic consistency, not diachronic revision — no fact ever
  becomes false.** **The genuinely useful residue: a small off-the-shelf NLI model (DeBERTa-MNLI) can supply
  the contradiction signal for zero LLM calls**, which sidesteps the dismal LLM contradiction recall above.
- **Belief-R / ΔR** (Wilie, Cahyawijaya, Ishii, He, Fung; arXiv 2406.19764; **EMNLP 2024; 25 cites**) is the
  Byrne suppression task at scale: premises licensing a modus ponens, then a third premise that either
  **defeats** the inference or does not; ~2K entries, categories Basic@t / Belief Update / **Belief Maintain**
  / All-w-3-premises, metric BREU, ~30 LMs. **No fact is replaced — this is logical defeasance.** Its value to
  us is the **Belief-Maintain control set**: without questions whose answer did *not* change during the
  disruption, any "revise more aggressively" method wins for the wrong reason. **We should add that control.**
- **DERELAB** (arXiv 2608.30413, Aug 2026): generative multi-turn belief-updating conversations from
  parameterised graphs with **per-turn formally verified ground truth**, nine LLMs. Two findings straight into
  our discussion: *"nearly all"* models *"exhibit a systematic tendency to accept congruent evidence while
  resisting incongruent updates"*, and *"several models correctly identified a weakening update yet failed to
  revise their conclusion."*
- **DeltaLogic** (Dhanda; arXiv 2604.02733, Apr 2026): a reusable protocol — apply a minimal premise edit and
  ask whether the prior conclusion should change. **Qwen3-0.6B/1.7B/4B and Phi-4-mini: inertia = 0.600** on
  should-revise episodes; *"stronger initial accuracy still does not imply stronger revision behavior."*
  Low authority, but **"inertia" is a better-named metric than anything we currently report.**

**Mechanistic explanations for why the stale entry wins.**
- **Memory-Induced Tool-Drift** (Dabas, Jeong, Jin, Jia; arXiv 2605.24941, May 2026; 3 cites): MEMDRIFT, 105
  scenarios, seven frontier models, deflection up to **+3.6 on a 1–5 scale**; 608 of 6,062 real MCP tools
  flagged susceptible. Two mechanisms, verbatim: biased memories *"act as implicit steering vectors, pushing
  activations along the same latent directions as explicit behavioral instructions"* and
  ***"redistribute attention from task-relevant context toward memory entries with surface-level keyword
  overlap to the target parameter."*** And: *"Standard defenses — prompt-based relevance instructions and
  memory filters — reduce drift but do not eliminate it."* **The lexical-overlap mechanism is a concrete story
  for why two weeks of near-identical stale sightings out-compete one fresh one.**
- **"Right Knowledge, Wrong Answer"** (arXiv 2606.20959; 4 cites) — see §2.5. Same *shape* as ours one level
  down: *"the newer fact is present and recoverable, but the default forward pass prefers the outdated one."*
- **Astute RAG as a foil, not a baseline** (F. Wang et al.; arXiv 2410.07176; **ACL 2025**): training-free,
  ~2–3 calls, consolidating internal and external passages by **knowledge source, cross-source confirmation,
  frequency and thoroughness**. **In our regime frequency and corroboration certify the stale location** — two
  weeks of sightings against a handful of fresh ones — **so its scoring function would reproduce our bug.**
  That is a genuinely useful thing to say in the paper.

**Already in our set, restated where it answers the change-versus-accumulate question.** STALE/CUPMem names
the **"current-state adjudication gap"** — *"updated evidence can be stored and retrieved, but it does not
reliably become the basis that governs subsequent answers"* — and its §4.4 diagnostic is the closest published
twin of our 807/890: **new evidence is in the retrieval results for 77.5% of failures**; at write time the
top-3 recall of a new observation contains the corresponding *old* entry **60.5%** of the time yet **only
3.3%** are judged as needing update; and reducing stale-premise retrieval bias is *insufficient* — top-1-old
falls to 25.5% while implicit-policy-adaptation failure stays at **78.6%**. Its **Type II propagated
invalidation** (a relocation invalidating a structurally related slot) is exactly what a resident's ten-day
absence generates, and it is where every system collapses worst. **StateAuditor** (arXiv 2608.01619) is the
read-side counterpart on the same benchmark: **VTA 0.736 vs 0.686, +5.0 [+2.9, +7.2]**, no fine-tuning,
storage untouched. **Note the uncomfortable comparison: write-side adjudication (+12.8) beats read-side repair
(+5.0) on the same data.**

### 4.5 Change versus accumulate: the summary table

**CHANGE** = a specific fact's value becomes false and is superseded, both observable. **ACCUM** = new facts
added to a growing store.

| item | cites | STORED / READ | frozen 27B? | evaluated on CHANGE? |
|---|---|---|---|---|
| Anthropic memory tool + context editing | — | both | yes, trivially | **NO** — internal agentic-search eval only |
| Claude Agent Skills pattern | 1 | read (injected) | yes | **NO** — skills anchor procedure (65.7%) not facts (4.5%) |
| MemTool | 17 | storage of *tools* | yes | **NO** |
| LangMem | — | both | yes | **NO published eval** [U] |
| AutoMEM / DCI-Lite | 1 | read (tool-planned) | **yes, Qwen3-32B, no FT** | **partly, and damningly** — a CR column exists (long-ctx 12.0, DCI-Lite 14.0, PlugMem 24.0) but **AutoMEM has no CR score** |
| PlugMem | 27 | both | presumed yes [U] | **not in its own paper**; best CR (24.0) in AutoMEM's re-run |
| AgentRunbook-C | 13 | read (files + coding agent) | [U] | **adjacent only** — 72.5% vs 48.5% RAG, no replace-a-fact split |
| Filesystem memory audit | 0 | storage | yes | **NO** — *agents edit, rarely delete* |
| ByteRover / LeanMem / DeMem / MemTools | 2/0/4/0 | storage | mostly yes | **NO** |
| ChronoMem | 1 | storage + versioning | yes | **yes in protocol, but rollback is USER-initiated** → oracle |
| VerMem / MEMO | 0/0 | both / read | **no** (SFT+RL / trained) | **NO** |
| Env-probing curation | 1 | storage, **verified against the world** | **yes, no retraining** | **framed on stale knowledge**; CLBench 39→73% [U on categories] |
| **A-TMA** | 2 | **read (labelled state view)** + bank | yes | **YES** — own LTP benchmark, +0.240 conflict accuracy |
| RMM | 123 | both (retrospective refines retrieval) | mostly [U] | **not isolated** |
| Agent Memory Distillation | 2 | storage (teacher→student) | needs a stronger teacher | **NO** |
| G-Memory / Collaborative Memory / SSGM / TOKI | 95/56/19/0 | storage, governance, write-time | yes | **NO** |
| **Post-retrieval assembly** | 4 | **read** | closed models only [U] | **YES** on FactConsolidation; **NO on LongMemEval-KU (p=0.45)** |
| **Memory Trust Gap** | 0 | diagnostic (read) | **yes — frozen Qwen3 0.6–8B** | **YES** |
| **When Memory Lies** | 0 | **read-time filter** | open-weight VLMs included | **YES** — oracle stale labels give no further gain |
| Budgeted verification | 2 | read (provenance) | yes, 16 models | **YES** — 77.3% stale-consistent decisions |
| **DoT-Prompting** | ~0 | **read** | **yes, Qwen3-8B/14B** | **NO** — entity-swap benchmarks |
| **TEPA** | 0–5 | storage σ, effect on the prompt | **yes, ZERO LLM calls** | **YES, with reversal *and* return** |
| STALE/CUPMem | 24 | write adjudication + **constrained readout** | yes, no training | **YES, entirely** |
| StateAuditor | ~0 | **read (post-hoc repair)** | yes, no FT | **YES** — +5.0 |
| ChatProtect / RAG-contradiction / Astute RAG | 189/0/23 | generation / read / read | mixed | **NO** — and Astute RAG's heuristics would **pick our stale answer** |
| Belief-R / BeliefBank / REFLEX / ConCoRD | 25/—/8/21 | reasoning, read | needs MaxSAT + NLI | **NO** — synchronic consistency |
| ROME/MEMIT/GRACE/WISE/AlphaEdit/Larimar | 3273/1229/335/113/278/54 | weights | **NO** | **YES but permanent**, and never a revert |
| MemAgent / MemoryLLM / M+ / Titans / ATLAS / Miras / HOPE | 214/84/46/338/60/60/89 | storage (fast weights) | **NO** | **ACCUM only** |
| **LightEdit** (ICD half) | 1 | **read (decoding)** | **yes for the ICD half** | **YES** — 1,000 sequential edits |

---

## 5. Non-stationarity and transfer: how empty the gap is

Verified against primary sources, one row per candidate, by a dedicated research agent whose highest-value
rows I spot-checked myself. **REV** = a fact becomes false and later true again. **REC** = the same *kind*
of change happens more than once. **XFER** = a pattern learned about one entity is applied to a different
entity. Citation counts are Semantic Scholar; OpenAlex badly undercounts arXiv preprints and was not used.

### 5.1 The precise statement

Of **23** fact-change / agent-memory benchmarks and studies read to primary source — LongMemEval,
TemporalWiki, EvolvingQA, TAQA/Set-the-Clock, FreshQA, StreamingQA, RealTimeQA, DyKnow, RippleEdits,
MQuAKE (via MemoryAgentBench), MemoryAgentBench-FactConsolidation, STALE, Memora, EvoArena/PersonaMem-Evo,
HaluMem, MemTrace, StreamMemBench, Ground Truth First, Supersede, LifeFuse-Mem, ChronoMem, TOKI,
RAG-or-Learning:

> **23 contain a knowledge update. 0 construct a reversion as an evaluated condition. 0 measure recovery
> after a return. 0 contain a recurring change of the same kind that a system could learn within an episode.
> 0 contain cross-entity transfer. 0 report calibration across a change in the facts.**

Of **24** embodied benchmarks and robot memory systems: **9** contain any temporal change to the world,
**3** a recurring change of the same kind, **1** cross-entity transfer, **0** a reversion.
Of about **30** works bearing on transfer of a learned regularity to a new entity: **0**.

**The A→B→A structure is not a new idea. It is a solved measurement problem in stream mining and a modelled
phenomenon in long-term robot mapping, and it has never been built into a benchmark that asks a language
model to answer from memory — let alone one that also asks whether its stated confidence is usable at the
moment the world changes back.** There is no baseline to beat here, only adjacent work to position against.
That is the honest sentence for the paper, and it is stronger than claiming novelty for the structure itself.

### 5.1b TWO CORRECTIONS TO THAT CLAIM, which I made myself against the primary sources

The sweep above was done by one agent working through the benchmark literature. Two papers surfaced from a
different direction (the memory-as-a-tool and prompting sweeps) **do** contain a reversion, and I verified both
myself rather than take either agent's word. **Do not publish the "zero reversions" sentence without these
two.**

**1. TEPA (arXiv 2608.07429v2, Y. Zhou, Ouyang, Zheng, Xiang, Aug 2026, 0–5 cites) has an explicit `return`
phase.** I read the HTML and the phase function is stated verbatim:
> *"A phase function ϕ(t)∈Φ maps each episode to a phase, where Φ={stable,light,reversal,return}."*
This is a method paper with its own drift suite, not a community benchmark; the keys and values are extracted
by **hand-written deterministic functions** (controlled drift: "κ(x) is the tuple of task type, domain, and
input type, while ν(x) is the successful tool pattern"), there are **no LLM calls** at write or read time, and
the domain is tool-pattern success rather than an observation log a language model reads. Reversal-phase
success is **TEPA 0.950 vs append-only 0.210 vs last-write-wins 0.210 vs no-memory 0.309**. **[U on the
return-phase numbers: they are in a heatmap figure and I could not extract them reliably. Do not quote a
return-phase number.]**
**So the correct statement is: exactly one paper in this literature evaluates a settled → shift → return
schedule, it is an unrefereed August 2026 preprint, its memory is a deterministic keyed table with no language
model in the loop, and our rolling buffer is its append-only arm.** That makes TEPA our **must-beat baseline**
and our closest methodological relative, not a reason to abandon the gap claim.

**2. TANGLE (arXiv 2608.13921, Lu Yang, Shusheng Xu, Zhuoran Li, Tongkai Yang, Longbo Huang, Aug 2026,
0 cites) has an oscillation conflict type, and it scores confidence calibration.** 541 instances, 40 personas,
three conflict types: Context-Partitioned, **Behavior-Oscillation (BOC)**, and Source-Contradiction, over two
tracks (oracle curated memory versus an end-to-end extraction pipeline). I read the HTML; the BOC definition
is verbatim:
> *"Memories in ℳ report the user's value on life aspect a at different times… but the trajectory is
> non-convergent — exhibiting repeated reversals, partial retention, or amplitude drift rather than settling to
> a stable state."*
The worked example is an exercise routine adopted, abandoned, then retried. **Five scored dimensions:**
D1 conflict perception, D2 causal reasoning, **D3 confidence calibration** (rewarding "conditional
recommendations over overcommitment", 0–4 scale with conflict-type-specific anchors), D4 clarification
seeking, D5 memory faithfulness. Models: Claude Sonnet 5, Gemini 3.1 Pro, DeepSeek-V3.2, GLM-4.7, GPT-4o,
judged by GPT-5.4 and Claude Opus 4.7. **BOC is the lowest-scoring type: 10.81/20 (GPT-5.4 judge) and
10.14/20 (Opus judge), against CPC 14.79/14.96 and SCC 11.92/11.58.** Findings: with curated memory *"models
recognize conflicts more reliably than they calibrate actions or seek targeted clarification"*; with pipeline
memory *"extraction fails to preserve conflict-bearing relations needed for downstream reasoning"*.
**Important difference from us, and it is the difference that keeps our contribution:** TANGLE's oscillation is
designed to leave the current state **genuinely underdetermined** — the correct behaviour is to hedge or ask,
and that is what D3 rewards. **Ours is not underdetermined: the routine returns and there is a single correct
answer at every moment.** TANGLE also scores rubric dimensions with LLM judges rather than accuracy, runs
frontier models only, and is unrefereed. **[Note for the write-up: an earlier PDF read attributed to TANGLE a
claim that "models systematically prefer stale evidence over fresh". The abstract does not support it and the
claim was discarded. Do not cite it.]**

**The corrected gap statement, which is what should go in the paper:**
> Of 23 fact-change / agent-memory benchmarks verified against primary sources, **23 contain a knowledge
> update and none constructs a reversion.** Two unrefereed August 2026 preprints do: **TEPA**, a method paper
> whose drift suite has an explicit `{stable, light, reversal, return}` schedule but whose memory is a
> deterministic keyed table with no language model in the loop; and **TANGLE**, whose Behavior-Oscillation
> conflict type has "repeated reversals" and which scores confidence calibration — but whose oscillations are
> deliberately underdetermined, so there is no recovery to measure. **No benchmark asks a language model to
> answer from an observation log across a change that reverts to a previously-correct value, and none measures
> whether stated confidence is usable at the moment the world changes back.** Recurrence of the same kind of
> change: zero in the LLM literature, fully developed in stream mining. Cross-entity transfer: zero of ~30
> candidate works.

### 5.2 (a) Reversion — the verified rows that matter

| benchmark / study | citation | what non-stationarity | REV | how verified |
|---|---|---|---|---|
| **LongMemEval** | 2410.10813, **ICLR 2025, 652 cites** | knowledge-update category | **NO** | the agent downloaded the released `longmemeval_oracle` split and counted: **all 78/78 knowledge-update instances have exactly 2 evidence sessions** (old value, new value) — structurally incapable of a reversion. **0 occurrences of "revert"/"revers"** in the paper. Independently corroborated by Supersede's "~2 sessions/question". |
| **TAQA / "Set the Clock"** (Zhao, Brumbaugh, Wang, Hajishirzi, Smith) | 2402.16797, **ACL Findings 2024, 34 cites** | 20K time-sensitive questions with a gold answer **for every year 2000-2023** | **YES in the data, NO in the evaluation** | the agent downloaded `dev.jsonl` (1,000 questions) and computed it: of 535 single-valued questions, **390 (72.9%) have a value that recurs after being replaced and 288 (53.8%) have an immediate A-B-A** (e.g. Minnesota Mr. Hockey school: Eden Prairie 2009 → Blaine 2010 → Eden Prairie 2011). But the protocol only asks "what was the answer in year Y" — no memory, no adaptation, no recovery metric. |
| **STALE** | 2605.06527, **24 cites** | implicit one-shot invalidation, 400 scenarios, 1,200 queries, 150K-token haystacks | **NO — in its own limitations** | full HTML: "focused on **one-shot** implicit state transitions… real-world interactions may involve **repeated updates**, coupled propagation, or gradual state drift". Binary accuracy only. |
| **Memora** | 2604.20006, **ACL 2026, 24 cites** | 10 personas, up to ~1,991 sessions, FAMA penalises use of invalidated memory | **NO** | full HTML. The only near-hit is "users may reinforce existing preferences, weaken them, or **reverse earlier statements**" — a reversal of a statement (A→¬A), not a return to a previously-held value. 0 hits for revert / back to the original / oscillat. "Recurring activities" means repeated step-count logging, not a recurring *change*. |
| **EvoArena / PersonaMem-Evo** | 2606.13681, **3 cites** | three evolution regimes; 89 workflow chains, mean 4.96 versions | **NO — explicitly designed out** | full HTML, verbatim: "The goal is **not to create arbitrary binary reversals**, but to model natural preference evolution". Rollback appears only as motivation. **Trap:** its "single-pattern transfer" question type is transfer to a new *domain for the same persona*, not to a new person. |
| **MemoryAgentBench FactConsolidation** | 2507.05257, **226 cites** | selective forgetting; numbered facts, newest wins | **NO** | Appendix A.4.2: "counterfactual **edit pairs** from MQuAKE… the outdated sentence is given a smaller number, the more recent a larger number". Pairs ⇒ exactly one update. |
| **EvolvingQA** | 2311.08106, **NAACL 2024, 24 cites** | six consecutive Wikipedia snapshots; Unchanged / New / Edited | **NO** | full HTML, **0 hits for revert/revers**. |
| **TemporalWiki** | 2204.14211, **EMNLP 2022, 150 cites** | TWiki-Diffsets between snapshots | **NO by construction** | 0 hits revert/revers/recurr; the "periodic" hits are about evaluating the *model* periodically. [U: Wikipedia edit-wars could put an incidental A-B-A in the diffsets; not identified or measured.] |
| **FreshQA / FreshLLMs** | 2310.03214, **ACL 2024, 433 cites** | four categories by *rate* of change | **NO** | 0 hits for revert / change back / answer history. Each release is scored against the current answer only; **no per-question value history is kept**, so a fast-changing answer that genuinely returns is never recorded as a return. |
| **StreamingQA** | 2205.11388, **ICML 2022, 153 cites** | 2007-2020 news stream; separates *adaptation* from *forgetting* | **NO** | full HTML, 0 reversion hits. Closest pre-LLM framing to our degradation/recovery pair, but no old answer ever comes back. |
| **RealTime QA** | 2207.13332, **NeurIPS 2022, 314 cites** | weekly ~30 new questions | **NO** | questions are retired, never re-asked. |
| **DyKnow** | 2404.08700, **EMNLP Findings 2024, 35 cites** | outdated facts vs current Wikidata | **NO** | [U: arXiv HTML returns 406; abstract + framing only.] |
| **RippleEdits** | 2307.12976, **TACL 2023, 320 cites** | one edit plus six ripple families | **NO** | the edit is formally one object swap; no re-edit back. |
| **HaluMem** | 2511.03506, cites [U] | extraction / updating / QA, ~15k memory points | **NO on every axis** | full HTML: **0 hits each for revert, revers, back to the original, recurr, cyclic, seasonal, abstain, calibrat, confidence, cross-entity.** A confident, fully-swept NO. |
| **MemTrace** | 2606.17328, **2 cites** | per-fact probing (see §0) | **NO** | full HTML, 0 hits revert/recurr/cyclic/seasonal. Every fact changes at most once. |
| **Supersede** | 2606.27472, **7 cites** | the memory-update gap on LongMemEval's 78 KU questions | **NO** | full HTML; single- and two-update episodes only. |
| **Ground Truth First** | 2607.21962, **0 cites**, single author | per-fact **validity intervals** and **volatility classes** (permanent → durable → slow-changing → transient → ephemeral); 383 questions, 15 types, 6 users, 9-week horizon | **NO** | full HTML: 0 hits for revert / recurr / seasonal / periodic / recover. Facts are soft-invalidated with supersession pointers, never restored. **Its real value to us is calibration — see §5.5.** |
| **LifeFuse-Mem** | 2609.12436, **0 cites**, BAAI et al. | "**Against Temporary Overwriting**": Phase A writes permanent facts, Phase B writes conflicting temporary ones; permanent queries must still return the Phase-A value | **NO — and it is an oracle** | full HTML. **This is the only paper that names our failure mode**, and it says itself: write episodes "**specify** whether incoming evidence should be treated as durable or temporary, and phase-aware readout uses **known phase boundaries and query lifecycles** at evaluation time… it **does not claim autonomous lifecycle discovery from unlabeled interaction histories**". Stable rows are restored from a Phase-A checkpoint. There is no time at which the temporary phase *ends* and the old value becomes correct again for the same query; the query is *labelled* instead. Trains LoRA rank-8 adapters on Qwen3-4B / SmolLM3-3B on 3,243 samples — **not a frozen-model evaluation**. |
| **ChronoMem** | 2607.27773, **1 cite** | whole-memory snapshot per write; natural-language undo; post-exposure counterfactual protocol on LoCoMo + MemoryAgentBench | **NO in the world; YES as an operator** | full HTML. Rollback is **externally requested**: "supports natural-language rollback **requests** by mapping 'undo' intents to concrete historical versions". The earlier value is restored **because a user asked** — the oracle version of what we want a system to do by itself. |
| **TOKI** | 2606.06240, **4 cites**, single author | **bitemporal** (valid time × system time) operator algebra for contradiction resolution, Allen interval relations; LoCoMo, LongMemEval-S, MultiTQ | **representable, never evaluated** | full HTML: 0 hits for revert / A-B-A. The schema could express valid → invalid → valid again; no dataset or metric exercises it. The contribution is soundness theorems about write-time isolation. |
| **RAG or Learning?** | 2604.05096, **ACL 2026, 3 cites** | real-world knowledge drift; RAG vs editing vs continual learning | **NO** | forward-only accumulation. [U on a full keyword sweep.] |

**Knowledge editing, settled separately.** Nothing in the sequential-edit literature re-edits a fact back to
its original value as a *world* event. The nearest works are security-motivated undo methods: **"How to Make
LLMs Forget: On Reversing In-Context Knowledge Edits"** (2410.12586, **NAACL 2025, 10 cites**) — reversal
tokens recover >80% of original unedited outputs; **"Tracing and Reversing Edits in LLMs"** (2505.20819,
**7 cites**) — reverses up to 94% of edits; **"Selective Knowledge Edit Reversal via Gated Singular Vector
Shrinkage"** (2609.02091). All three restore the *model* as a defence against malicious edits: A→B→A at the
parameter level, with no world, no time and no recovery curve. [U on an exhaustive sweep of UNIEDIT, LyapLock,
PRUNE/RECT/AlphaEdit for a re-edit to the original value.]

### 5.3 (b) Recurrence of the same kind of change

**The concept is fully developed — outside LLM work — and has not been imported.**

| work | citation | what it gives us |
|---|---|---|
| Gama, Žliobaitė, Bifet, Pechenizkiy, Bouchachia, "A survey on concept drift adaptation" | **ACM Computing Surveys 2014, 4,035 cites** | the canonical taxonomy; names **recurring drift** as a first-class type |
| Lu, Liu, Dong, Gu, Gama, Zhang, "Learning under Concept Drift: A Review" | **IEEE TKDE 2019, 1,987 cites** | the review to cite for "the same shift can happen again" |
| Katakis, Tsoumakas, Vlahavas, "Tracking recurring contexts using ensemble classifiers" | **KAIS 2010, 230 cites** | the founding method: concepts "disappear and re-appear" |
| **RCD: A recurring concept drift framework** (Gonçalves & Barros) | **Pattern Recognition Letters 2013, 112 cites** | **stores and re-activates a previously-built model when a past state returns** — mechanically our "does it recover?" question |
| Cetrulo, Quintana, Cervantes, survey on ML for recurring concept drifting streams | **ESWA 2022, 165 cites** | "the system must store the old behaviour and reuse the learned knowledge once it reappears" |
| **Shaker & Hüllermeier, "Recovery analysis for adaptive learning from non-stationary data streams"** | **Neurocomputing 2014/15, 42 cites** | **defines the recovery-after-shift measurement protocol we are running**, a decade before LLMs |
| Zhao et al., "Handling concept drift via model reuse" | **Machine Learning 2019, 59 cites** | model-reuse-on-recurrence |
| **Continual Learning in the Presence of Repetition** (CLVision @ CVPR 2023 challenge report) | **Neural Networks 2024, 10 cites** | quotable: "although re-occurrence of previously seen objects or tasks is common in real-world problems, the concept of repetition in the data stream is **not often considered** in standard benchmarks for CL". Vision, not language. |
| **Yang et al., "Reawakening knowledge: Anticipatory recovery from catastrophic interference via structured training"** | 2403.09613, **NeurIPS 2024, 5 cites** | the one LLM result showing **recurrence is learnable**: with documents presented "cyclically in a fixed, repeated sequence", LLMs "exhibit anticipatory behavior, **recovering from the forgetting on documents before encountering them again**", strengthening with scale. Fine-tuning dynamics, not memory — but it is the strongest prior evidence that our recurrence condition could pay off. |
| Wild-Time | 2211.14238, **NeurIPS 2022 D&B, 138 cites** | temporal distribution shift with timestamps so models "can potentially learn from trends in past distribution shifts". Input shift, not facts; no reversion. |
| **LLM-agent adoption of any of this** | — | **none found.** EvoArena's "recurring evolution dimensions" and Memora's "recurring activities" are the only near-misses and neither gives a learnable within-episode pattern. |

**And the one LLM paper with a returning regime** is the reversal-learning study already given in §3.1
(arXiv 2604.04182, IPMU 2026): **REV YES, REC YES**, cycling s→(s+1) mod 3, with perseveration length and
post-reversal regret as metrics — but a two-armed bandit with **0 hits for "memory", "recovery",
"confidence", "abstain"**. No facts, no entities, no memory system.

### 5.4 (c) Cross-entity transfer, and (d) embodied

**(c) Zero of about 30 works, and the axis never co-occurs with non-stationary facts.**
- The **analogy** thread is the wrong shape: Webb, Holyoak & Lu (2212.09196, **Nature Human Behaviour 2023,
  522 cites**) and its whole critique literature — Lewis & Mitchell (2402.08955, CogSci 2024, 50),
  "Evaluating the Robustness of Analogical Reasoning in LLMs" (2411.14215, **TMLR 2025, 37**), Hodel & West
  (2308.16118, 21), Webb et al.'s rebuttal (2404.13070, PNAS Nexus 2024, 16), Musker et al. (2406.13803,
  *Journal of Memory and Language* 2025, 22), Mitchell (*Current Directions in Psychological Science* 2026,
  1) — **hand the source and target to the model in the prompt; nothing is learned from accumulated
  observation.**
- **Induction** benchmarks have no persistent entities to transfer between: MIRAGE (2410.09542, ICLR 2025,
  25), Cheng et al. "Inductive or Deductive?" (2408.00114, 32), Hypothesis Search (**172**), "Language Models
  as Inductive Reasoners" (2212.10923, EACL 2024, 59), ARC-AGI-2 (2505.11831, **178**), ACRE (CVPR 2021, 59),
  COGS (**365**), FalsifyBench (2606.04751, 1). The held-out axis is always another *instance of the same
  rule*; "entity" is a symbol slot.
- **Agent experience transfer** moves across tasks, websites and domains, never entities: ExpeL (**936**) —
  right mechanism, wrong axis, stationary environment; Agent Workflow Memory (**285**) whose own three axes
  are verbatim "cross-task, cross-website, cross-domain"; Reflexion (**5372**), Voyager (**2326**),
  AutoGuide (70), Memp (ACL 2026, 67), Memento/AgentFly (2508.16153, 100).
- **Trap to pre-empt:** the one 2026 paper with "cross-entity" in the title, **ProGraph** (2607.19359,
  1 cite), means multi-hop *retrieval* across co-occurring entity names, treats dates and quantities as
  static, and does not test transfer to an unseen entity. If we cite it we must say so, or a reviewer will
  think it scoops us.
- **The right formal ancestor is inductive relational learning:** **GraIL** (1911.06962, **ICML 2020,
  547 cites**) and **NBFNet** (**NeurIPS 2021, 534 cites**) generalise entity-independent relational rules to
  graphs of entirely unseen entities — structurally exactly "A's things move to the living room ⇒ B's things
  move to the living room". Missing: a static snapshot, no regime shift, GNN link prediction rather than a
  frozen LLM reading an observation log. [U on 2026 inductive *temporal* KGC, where both axes might co-occur.]
- **Best contrast citation: TidyBot** (2305.05658, **IROS 2023, 466 cites**) — a household robot that
  summarises a handful of one person's example placements into "a generalized set of rules (personalized to
  that user)" and applies them **to new objects for the same user, never to a new user.** Exactly one axis
  short of the capability we want, from a well-cited robotics venue.

**(d) Embodied: 0 of 24 contain a reversion.** Empty on all three axes, each read to the benchmark-design
section: **Habitat 2.0/HAB** (NeurIPS 2021, **805**) — GeometricGoal *tells* the agent the change and
"object positions are randomized between episodes"; **Habitat 3.0** (ICLR 2024, **328**); **TIDEE** (ECCV
2022, 54); **Housekeep** (ECCV 2022, **93**) — correctness is a fixed annotator-consensus prior,
"revert"/"routine"/"over time" appear 0 times; **BEHAVIOR-1K** (**180**); **ALFRED** (**1201**) / **ALFWorld**
(**1246**); **TEACh** (AAAI 2022, **298**) — state changes within a session only.
**OpenEQA** (Majumdar et al., **CVPR 2024, 385 cites**) is a fully-read NO on all three: its seven categories
are verbatim "object recognition, attribute recognition, object state recognition, object localization,
spatial understanding, functional reasoning, world knowledge" — **there is no temporal category at all**, and
the history is a single tour of a static scan. Likewise Explore-until-Confident (RSS 2024, **113**),
EXPRESS-Bench (ICCV 2025, 35), **ReMEmbR/NaVQA** (ICRA 2025, **103**) — whose own limitation, "NaVQA ensures
a unique answer for each question", structurally excludes a moved-then-moved-back object — 3D-Mem (CVPR 2025,
**100**), Embodied-RAG (61) [U], and **FARM** (2606.15476, He et al., July 2026), which I checked myself:
object-centric 3D Gaussians with captions and three retrieval embeddings, evaluated on **static** ScanNet-30
(35.9 Acc@1), HM3D-30 (7.9 Acc@1) and FARM-Scenes, and the paper "does not address scenarios where
previously-correct object locations become invalid".

The 2025-26 wave gets closest without arriving:
- **FindingDory** (2506.15635, **ICLR 2026, 12 cites**) — a real two-phase design where oracle agents "pick
  up and place objects onto designated receptacles… introducing meaningful state changes", tasks phrased
  "yesterday". **One irreversible A→B boundary, never a return.**
- **HUMEMBR / PersonEQA** (2606.30404, IROS 2026, 0 cites) — the cleanest **recurrence** case: 20 real days,
  31 hours, 13,000 images, questions like "When does Nemo *usually* arrive at work?" requiring aggregation of
  a repeated pattern. But it is an office, asks about people not object locations, and **never intervenes**.
- **MEMENTO** (2505.16348, 14 cites) — tests "recalling sequences of object-location pairs from consistent
  user behavioral patterns, such as daily routines" and finds agents "struggle to apply sequential user
  patterns to planning". The pattern is stated once and never broken and restored.
- **PersONAL** (2509.19843, 4 cites) writes our gap sentence and does not fill it: preferences must be
  maintained "in complex household settings **where ownership is stable but scenes continually evolve**" —
  evaluated on non-evolving scenes.
- **The only embodied work with both REC and XFER: CHORES/CORA** (2110.10067, **CoLLAs 2021, 51 cites**) —
  "Mem-VaryRoom changes the room scene, Mem-VaryTask changes the task type, **Mem-VaryObject changes the
  object**", with **Zero-Shot Forward Transfer** as a headline metric. Training never returns to an earlier
  regime; 64×64 RGB RL, not memory QA.

**Where the reversion actually lives: long-term robot mapping.**
- **FreMEn** (Krajník et al., **IEEE T-RO 2017, 159 cites**) models "the probability of each environment
  state as a function of time… by a combination of harmonic components" — a state that goes A→B→A on a daily
  or weekly cycle is precisely the modelling target. **REV YES, REC YES.**
- **Perpetua** (2507.18808, **IROS 2025, 3 cites**) — chained "persistence" and "emergence" filters model
  "the probability that features will **disappear or reappear**… in the present as well as at arbitrary
  future times". **REV YES, REC YES, and predictive.**
- **Khronos** (2402.13817, **RSS 2024, 84 cites**) draws exactly our distinction — "short-term dynamics…
  disconnected from long-term change detection, where the scene undergoes substantial changes (e.g. furniture
  being rearranged) while the robot is not directly observing it" — and its demo contains an incidental A-B-A
  ("correctly detects that the cooler has disappeared again"). Reporting, not anticipation, and no QA.
All three are occupancy/geometric: no language, no questions, no foundation model. **This is the literature
whose framing we should borrow, and it is the strongest "why has nobody done this" answer: the people who
model returning states do not use language models, and the people who use language models do not model
returning states.**

**Motivational citation worth having:** "Designing Robots for Families: In-Situ Prototyping for Contextual
Reminders on Family Routines" (2602.22628, **HRI 2026, 4 cites**) — a four-day in-home deployment with ten
families in which routines broke exactly the way ours does (**a daughter became sick and altered her morning
and bedtime routines**; a family moved dinner to the patio), used to argue robots must cope with
"ever-changing contexts and rhythms". Real evidence that our scenario occurs, from a top HRI venue, with no
benchmark attached. **Cite this in the introduction.**

### 5.5 (e) Confidence and abstention across a change in the facts

**Verified negative on the canonical survey.** Wen et al., **"Know Your Limits: A Survey of Abstention in
LLMs"** (2407.18418, **TACL 2025, 148 cites**): a full-HTML sweep found **0 hits for "distribution shift",
0 for "drift", 0 for "outdated", 0 for "stale", 0 for "time-sensitive"**, one "temporal" hit (post-cutoff
election questions), and 34 "calibrat" hits all method-side. **The field's reference survey on abstention has
effectively no sentence about abstaining when the facts have changed.**
- Calibration-under-shift in the classic sense means *input* shift: Ovadia et al. (1906.02530,
  **NeurIPS 2019, 2,464 cites**). Kadavath et al. (2207.05221, **2,049**) and Xiong et al. (2306.13063,
  **ICLR 2024, 1,197**) elicit confidence over stationary facts.
- **Closest to what we need, and it is an uncited preprint.** *Ground Truth First* (2607.21962, 0 cites) is
  the only work found that measures abstention *quality* over a longitudinal corpus whose facts change:
  "our most accurate system almost never abstains when wrong — **93.9% of its judged errors classify as
  wrong-specific rather than abstention, vs. 62.7% for the least accurate**… **accuracy does not confer
  calibrated abstention**", robust across two judge families (85.4% vs 62.5%). Question types include
  abstention, abstention-false-premise, expired-state and conflict-resolution. It has no reversion and no
  calibration curve across the shift. It also reports the **tenure crossover**: at a 3-week horizon a
  budgeted curated-map memory wins; at 9 weeks it degrades **96% → 72% recall** while a provenance-typed
  graph rises to **90%**, across all six users, p=0.031. **Credibility caveat: uncited single-author
  preprint; treat as a design-space source, not a result to lean on.**
- **MemTrace** probes each knowledge point under evidence-missing (should abstain) and false-premise (should
  reject) conditions with a Fresh / Saturated / ΔForget profile — per-fact selective behaviour under
  staleness, no reversion, no proper scoring rule.
- **"Manufactured Confidence"** (2606.29279, 1 cite) is the mechanism story for why confidence is wrong after
  a change: memory writers "rewrite conversation into stored facts" so that "a casual, hedged remark becomes
  a confident, dated assertion the agent then obeys like a verified fact… A passive 'unverified' tag is
  ignored, and an active 'do not trust this' instruction escalates even correct memory." No shift
  measurement. **Directly relevant to our nightly-write arms and to our confidence channels.**
- **LongMemEval** is the only *established* benchmark with an abstention category (30 false-premise items)
  and it reports **no calibration metric at all**.

**So our third measurement — is stated confidence usable for answer-versus-ask at the moment the world
changes — is not merely under-studied. The reference survey of the sub-field does not mention the condition.**

### 5.6 The closest existing work, in four pieces

There is no single closest work; the four legs of our setting sit in four disjoint literatures.
1. **Closest in intent (LLM memory): LifeFuse-Mem** (2609.12436) — the only paper that names temporary
   overwriting of a durable fact, and it solves it by **being told** which writes are temporary, saying so
   itself. Ours is the unlabelled version, with a phase that actually ends.
2. **Closest in structure: the reversal-learning study** (2604.04182) — the latent state cycles back, and
   perseveration is the metric; but a bandit, no memory, no confidence.
3. **Closest in measurement: Shaker & Hüllermeier's recovery analysis** (Neurocomputing 2014/15) plus the
   recurring-concept line (Katakis 2010, RCD 2013, Cetrulo 2022) — the protocol we are running is standard
   stream-mining practice from a decade ago that the LLM-agent field has not imported.
4. **Closest in setting: WorldLines** (2606.18847, **EMNLP 2026, 1 cite**) for multi-day household traces
   with carry-forward state and an overwritten-state query family ("where was the laptop before Bob moved
   it?") whose worked example is a genuine A→B→A device-timer correction; **FindingDory** for real objects
   moved across a day boundary; **HUMEMBR/PersonEQA** for 20 real days of repeating routines; **TidyBot** for
   inducing a placement rule from one person's behaviour.

### 5.7 An opportunity this section turns up

**TAQA already contains the reversions.** 288 of its 535 single-valued dev questions have an immediate
A-B-A across consecutive years, and nobody evaluates them that way. A text-only companion experiment —
replay TAQA year by year, feed back the true answer after each year, and measure adaptation at the change
and recovery at the return — would give the paper a **second, non-embodied, publicly-available domain** with
the same A→B→A structure, at negligible GPU cost, and would answer the reviewer who suspects the effect is
an artefact of our simulator. This is the cheapest external-validity win available to us.

### Caveats this section must carry

- **2026 arXiv contains a large cluster of single-author, zero-citation agent-memory preprints** (Ground
  Truth First, Supersede, TOKI, Manufactured Confidence, and others) that cite each other densely. Several
  are substantive and were read in full, but none is refereed, and none should be cited as an established
  result — only as evidence that a design feature does or does not exist in the published record.
- **[U] flags in this section:** TemporalWiki's incidental Wikipedia reverts; DyKnow full text (arXiv HTML
  returns 406); HaluMem's citation count; an exhaustive sweep of sequential-edit benchmarks for a
  re-edit-to-original; RAG-or-Learning's full keyword sweep; 2026 inductive temporal KGC; Embodied-RAG,
  GraphPad and OASIS-Map at abstract level only.

---

## 6. Recommendation

### 6.1 The three most worth implementing next

**1. Pre-resolve the conflict deterministically before the answerer sees the prompt — a single-value current
view plus a labelled historical archive. Zero to one extra LLM calls.**
Four independent 2026 papers converge on this mechanism, and it is the **only** intervention with evidence
that it works on models our size or smaller.
- Mechanically: per key (object, or object × time-slot — see the warning below), build the **current value**
  deterministically from the latest sighting; move superseded sightings to a **revoked archive that is excluded
  from the answer prompt but available for re-promotion** (TEPA's `σ ∈ {Hypothesis, Active, Revoked}` with a
  Beta-Bernoulli validity posterior, **zero LLM calls**); pass the answerer **evidence packets carrying
  explicit `current` / `historical` / `transition` labels** rather than a raw sighting list (A-TMA, +0.240
  conflict accuracy over Graphiti, LoCoMo temporal F1 0.0295 → 0.1705); and where a real judgement is needed,
  use the **extract-then-decide split** — one temperature-0 structured-JSON call listing *every* matching
  sighting verbatim **without ranking them**, then `max(timestamp)` in Python (+10.8pp average, +21pp at long
  context, 2 calls, ~$0.0001/query).
- STORED **and** READ. It changes what is stored, and the *point* is that it changes what reaches the prompt.
  So it is not a storage-only method and the 807/890 objection does not apply to it.
- Implementation cost on a frozen 27B: **trivial.** The keyed table is a dictionary. The extract-then-decide
  arm is one extra structured call. No training, no fine-tuning, no logit access.
- Tested on changing facts: **yes, more than any other family here.** TEPA reversal phase **0.210 → 0.950**
  against append-only, which is our rolling buffer; CUPMem **8.7% → 68.0%**, **+36.7 over the plain 27B**;
  StateAuditor +5.0 on the read side of the same benchmark; post-retrieval assembly +10.8 to +21pp.
- Why it and not a prompt: the Memory Trust Gap's sentence on frozen Qwen3 0.6–8B —
  ***"exposing metadata improves accuracy for the capable models, but only pre-resolving the conflict restores
  accuracy for the 2 smaller checkpoints."*** We have already annotated the buffer with timestamps and a `Now:`
  line, which is HoH's successful mitigation, and we still lose 45–60 cold points.
- **Three caveats to design in.** (i) Post-retrieval assembly's gain **vanished on LongMemEval knowledge-update
  (26/45 vs 29/45, McNemar p = 0.45)** once explicit version numbers were absent; **our timestamps are the
  analogous crutch and testing whether they suffice is the experiment**. (ii) Keying matters and we already
  know it: if location depends on time of day, keys on (object, location) will flip back and forth, so key on
  **(object, time-slot)**. (iii) Add STALE's **Type II propagated invalidation** — a resident's ten-day absence
  must invalidate *structurally related* slots, not only the one directly touched — because that is where every
  system collapses worst, and our state schema (`object → location`) is trivial, so the hand-built-schema
  limitation STALE concedes costs us nothing.

**2. Environment-probing re-verification by a separate curator. The one thing we can do that the
conversational-memory literature cannot.**
A **post-task, asynchronous curator** — a separate LLM session that cannot see future questions — is the only
agent allowed to mutate the store, through `memory_read` / `memory_create` / `memory_update` /
`memory_delete`, **plus read-only world tools that let it re-observe before writing or retiring a belief**
(arXiv 2609.11060). Verified numbers: **CLBench pass rate 39% → 73%**, pass-discounted reward 8.60 → 22.60,
**while reducing queries 8.8 → 4.7 and task-agent cost $3.38 → $1.68**, positive in all 18 APEX comparisons,
**no retraining, task agent and retriever unchanged.**
- STORED, but this is the one storage intervention that attacks a read-time failure, because a *verified* store
  stops putting the stale evidence in the prompt at all rather than asking the 27B to out-argue it.
- Cost: a few curator calls per day plus patrol observations we already take. No training.
- Tested on changing facts: framed explicitly on stale knowledge; exact categories [U].
- **Why this is our best structural match: a home robot can go and look.** We already have a free-look
  affordance (`look_on`) and a patrol stream. This is the paper that says to spend it on *re-checking a belief*
  rather than on answering the current question, and it reports a large effect for doing so. It also gives us
  a story a reviewer will like: the embodied setting is not a decoration, it is the reason the method is
  available.

**3. An adversarial critic at read time — budgeted, and only if 1 and 2 leave a gap.**
DoT-Prompting's **Critic** role: forbidden from using the proponent's premises, tasked with assessing
*"outdated or non-authoritative"* evidence and supplying counter-evidence. Training-free on **Qwen3-8B/14B** in
the original paper — our family — at ~**8 calls at M=3** for 294 output tokens against CoT's 311. Qwen3-14B,
prompting versus full-context: FaithEval-Counterfactual **71.9 → 78.2**, MuSiQue **80.5 → 89.2**. The ablation
is unambiguous: **removing the Critic costs −13.0 average; removing the judge only −3.7.**
**If we can afford one extra role, build the adversary, not another judge.** That is a direct verdict on our
own `debate` arm, whose sides argued to fixed positions and whose judge did the deciding. Its **τ = 0.6
"Uncertain" fallback** also gives us a free abstention arm for the third measurement.
- READ-side. No training. Not tested on changing facts (entity-swap benchmarks; its `S_source` recency
  criterion is asserted, never measured) — so this is the one of the three where we would be extending rather
  than replicating.
- **Three guardrails from elsewhere.** (i) A single-call "is anything here contradicted?" detector will be
  **high-precision, low-recall** on a 27B (0.90–0.99 precision, 0.04–0.57 recall), so give the critic the
  **pairwise (stale, fresh) framing** where 0.893 accuracy is achievable, never "find the conflict in the log"
  (0.006). (ii) Detection alone is not enough: **When Memory Lies found that even oracle staleness labels
  brought no further significant gain**, and DERELAB found models that *"correctly identified a weakening
  update yet failed to revise their conclusion."* **So the critic must feed the pre-resolution step in
  recommendation 1, not the answerer directly.** (iii) CoVe's caveat: the critic must not see the previous
  answer, or it will ratify it.

**Near-free additions, one afternoon each, in descending order of expected value:**
- **Delete the routine clause from the reply instruction.** It currently asks for *"what the sightings, the
  time of day and the residents' routine suggest"*. We measured that deleting the routine *card* is worth +19
  to +29 in the disruption; we have never tested deleting the instruction that licenses a routine. One line.
- **Reframe the card instead of deleting it:** `As of {date}, the household routine was recorded as: "…"` —
  attributed, dated, defeasible. Four independent literatures predict this works (§2.6) and **nobody has tested
  attribution reframing on intra-context conflict between a written prior and an observation list.**
- **TEPA's Memory Pollution Index**, `MPI = (S_NoMem − S_mem)/S_NoMem`, computed for our buffer arm in the
  disruption window. One line of arithmetic, and it may well come out **positive** — our memory being a net
  harm during the disruption is a headline, and "When Memory Lies" reports the same thing (an agent trusting
  raw memory dies more than twice as often as one with no memory).
- **A Belief-Maintain control set** (Belief-R): questions whose answer did *not* change during the disruption.
  Without it, any "revise more aggressively" method wins for the wrong reason. We partly have this in the
  moved/unmoved strata; make it explicit.
- **An off-the-shelf NLI model (DeBERTa-MNLI) over (stale, fresh) sighting pairs** as the contradiction signal:
  **zero LLM calls**, and it sidesteps the LLM recall problem.
- **`Wait`, or an extract-before-answer prefix.** 89.3% blind-spot reduction across 14 open models at zero
  cost.
- **A BM25 arm over the sighting log.** The cheapest missing baseline, and the one that beats Mem0, MemGPT,
  Cognee and GraphRAG on the only changing-fact task in MemoryAgentBench (BM25 56.0 vs Mem0 18.0).
- **HypoGeniC's UCB hypothesis bank with a discounted accuracy term** (§3.3): a bank of ~5 natural-language
  routine hypotheses, `r_i = windowed-accuracy_i + α√(log t / |S_i|)` with γ ≈ 0.95, regeneration when 10
  errors accumulate, top-1 or top-2 in the prompt. **One answer call per question as now, plus one generation
  call per ~10 errors.** It makes the regime hypothesis explicit and inspectable, which is worth a figure, and
  the discounted-accuracy term is exactly the one-line change the paper leaves open.
- **BOCPD over our binary correctness stream** (Adams & MacKay, 923 cites) with a Bernoulli-Beta likelihood and
  a constant hazard: O(t) arithmetic, **zero LLM calls**, giving both a retrieval gate and a confidence
  deflator. Nobody has coupled a classical change-point detector to an LLM agent's own outcome stream, and
  SigLLM shows that asking the model to eyeball the sequence loses to specialised detectors by 30%.
- **Replay TAQA year by year as a text-only companion domain.** 288 of its 535 single-valued dev questions have
  an immediate A-B-A across consecutive years and nobody evaluates them that way. Negligible GPU cost, and it
  answers the reviewer who suspects our effect is a simulator artefact.

### 6.2 The two most likely to be a waste of GPU time

**1. Anything in weight space or fast-weight space: model editing, test-time-trained memory, and parametric
memory pools.** ROME, MEMIT, GRACE, WISE, AlphaEdit, Larimar, Titans, ATLAS, Miras, HOPE, MemoryLLM, M+,
MemAgent. Three independent reasons, any one of which is sufficient:
- **We cannot run them.** Every one needs weight access, hidden-state access with gradients, or pretraining a
  memory interface. We serve a frozen 27B on vLLM. RW-TTT states the deployment blocker in one line:
  *"Test-time training adapts an LLM during generation by reading and updating request-owned state. This breaks
  batched LLM serving, which assumes shared static weights."*
- **They collapse under exactly our workload.** WikiBigEdit, on 500K real Wikidata updates across eight
  timesteps: ROME/R-ROME/MEMIT *"rapidly degrade within the first few hundred updates, leading to model
  collapse"*, WISE decays within 10K updates, and **plain RAG vastly outperforms every specialised editor.**
  LightEdit's Table 5: after 1,000 sequential edits, MMLU 0.681 → 0.235–0.366 and TriviaQA 0.518 → ≈0.00.
  A *single* edit can trigger collapse (arXiv 2402.09656). Our study is 34 days of continuous updates.
- **They are the wrong mechanism for our failure.** Every one of them is applied *before* the question and
  changes what the model knows. **In 807 of 890 cases the correct answer was already in the prompt.** Making
  the model's parameters hold the right answer does not address a failure to use an answer it is already
  looking at.
- **The one thing to take and leave the rest:** HOPE's **Continuum Memory System** — banks updated at different
  frequencies — as a *prompting* ablation, i.e. a fast block for the last ten days beside a slow block for the
  settled routine. That costs nothing and needs no architecture. And **LightEdit's in-context decoding** at the
  first answer token only, `log p′(x₁) = log p(x₁|C,q) − 0.2·log p(x₁|stale)`, **gated** by a relevance
  check — ungated it collapses locality from 0.997 to 0.4612. That is a real read-time method we could run on
  vLLM logits, but it is a second-tier bet, not a headline.

**2. More debate, more voting, more self-critique, and more write-side consolidation machinery.**
Four separate bodies of evidence, and they point the same way:
- **Debate and voting.** SURVEY.md already establishes that majority voting explains most of debate's gain and
  that debate is a martingale (Choi et al., NeurIPS 2025 spotlight). Add to that: **self-consistency is
  actively harmful on long context** — 651 experiments, 8 models, 9 tasks, only **3 of 56** dataset-model pairs
  improved significantly, **ROUGE declined significantly in 19 of 24 (79%)**, because position bias produces
  *correlated* errors that voting amplifies (Byerly & Khashabi, TACL). Our prompt is long context. **And our
  own prediction was right for the right reason: these methods are built to resist the context, and we need the
  opposite.** If we spend calls on an extra role, spend them on the **Critic** (−13.0 when removed) and not on
  another judge (−3.7).
- **Self-critique.** Huang et al. (1,208 cites): intrinsic self-correction is flat or degrading on every task,
  and works only with oracle labels. Kamoi et al. (TACL, 356 cites): **no prior work demonstrates
  self-correction from prompted-LLM feedback.** "Self-Correction as Feedback Control" (2026): *"prompt-level
  EIR suppression prevents degradation, whereas ECR enhancement — plausibly training-level — is required for
  genuine gains."* On our exact failure, Sun & He found **self-critique consistency checks performed worse than
  baseline** and **few-shot + CoT reduced stale-premise recall from 0.38 to 0.13**, and a **Qwen3-4B auditor
  did not match the frontier auditor while gpt-4o-mini as auditor dropped conflict-free LongMemEval accuracy
  0.816 → 0.579.** A small-model auditor makes things worse.
- **More consolidation.** "Useful Memories Become Faulty When Continuously Updated by LLMs" (arXiv 2605.12978):
  **memory utility rises, then degrades, and can fall below the no-memory baseline**; GPT-5.4 fails on **54%**
  of ARC-AGI problems it had previously solved without memory, *even when consolidating from ground-truth
  solutions*; and their recommendation is to *"treat raw episodes as first-class evidence and gate
  consolidation explicitly rather than firing it after every interaction."* Our `routine7`, `reflect` and
  `facts_*` arms all consolidate nightly with no gate, and we have already watched our fact store corrupt
  itself four ways before a question was answered. **Supersede independently shows that more storage budget
  buys nothing: 24× more notes budget left accuracy at 28% → 28%.** And AutoMEM's filesystem audit shows that
  in practice *"early memories survive"* because agents edit rather than delete.
- **Storage-only frameworks generally.** G-Memory, Collaborative Memory, SSGM, TOKI, ByteRover, LeanMem,
  MemTools, Agent Workflow Memory, BeliefMem's noisy-OR (monotone in evidence, so it can never prefer the
  returning old routine), and MemoryBank-style recency decay (which would fade the old routine during the ten
  sick days and then have nothing to revive). **None is evaluated on facts that change; several are evaluated
  on facts that accumulate, which is the opposite regime; and our 807/890 says the binding constraint is not
  there.** Say this plainly in the paper rather than listing them neutrally.
- Two specific traps worth naming so a reviewer does not think they scoop us: **"Devil's Advocate"**
  (arXiv 2405.16334, Findings EMNLP 2024) is plan-level anticipatory reflection on WebArena with **no stored
  belief and no memory** — the name is a trap. And **ProGraph** (arXiv 2607.19359) means multi-hop *retrieval*
  across co-occurring entity names, not cross-entity transfer.

### 6.3 What the survey changed about how the paper should be framed

Three things, in order of how much they matter.

1. **The read-time diagnosis is no longer novel, and we should stop treating it as our headline.** MemTrace
   (June 2026) measured it on 835 knowledge points across 13 systems: **"Of the 300 probes, 21 are reach
   misses (7.0%), 220 are retriever-reached but unsolved (73.3%)"** — about 10× more often reachable-and-unused
   than missing. Our 807/890 is 90.7%, about 9.7×. STALE reports 77.5%. Sun & He report 67.8%. MERIT reports
   that agents act on correctly retrieved updated facts **only 55% of the time**. **Cite these up front and
   state that our number replicates a known diagnosis in an embodied setting on a local model.** What remains
   ours is the **A→B→A structure** and the **confidence / answer-versus-ask measurement**, neither of which any
   of them has.
2. **Prompting is a measured non-fix, and that is a publishable claim with eight papers behind it.** Frame it
   that way rather than as a candidate we tried. The routine-card ablation is the more interesting result and it
   has a clean published home: it is a **premise-resistance failure** (STALE's PR: Qwen3.5-**27B** scores 76.0%
   when asked directly whether the old belief holds and **4.0%** when the question presupposes it), and it is
   quantitatively mirrored by Xie et al.'s confirmation-bias table (**one prior-aligned evidence piece raises
   the memorisation ratio from 4–9% to 30–50%**). The literature says the fix is **attribution, not recency**.
3. **Our baseline set has three named holes and one unexpected strength.** Holes: no BM25 or embedding
   retriever; no tool-based / self-managed memory arm (MemGPT or an AutoMEM-style file+tool harness, which is
   the 2026 strongest general baseline and runs on Qwen3-32B); no named compression system (SimpleMem or plain
   recursive summarisation). Strength: **our `facts_mem0` / `facts_zep` / `facts_stale` trio — one shared
   nightly fact store under three published revision policies, delete versus invalidate versus label — is
   ahead of the field and should be foregrounded.** No paper in this survey runs a controlled comparison of
   revision policies on a single store, and TEPA's result (append-only 0.210 versus keyed replacement 0.950 in
   the reversal phase) says that is exactly the comparison that matters.

### 6.4 Credibility hygiene, which this survey needs stated explicitly

**2026 arXiv contains a thick layer of single-author or two-author, zero-citation agent-memory preprints that
cite each other densely**: Ground Truth First (2607.21962), Supersede (2606.27472), TOKI (2606.06240),
Manufactured Confidence (2606.29279), Tenure/Structured Belief State (2605.11325), MemStrata (2606.26511,
whose header reads "Draft v2"), ChurnBench (2609.11515), Memory Trust Gap (2609.01852), When Memory Lies
(2608.04574), Budgeted Verification (2608.25553), TEPA (2608.07429), TANGLE (2608.13921), StateAuditor
(2608.01619), DeltaLogic (2604.02733), DERELAB (2608.30413). **Several were read in full and several are
substantive. None is refereed.** They should be cited as evidence that a design feature does or does not exist
in the published record, and for their mechanisms, **not for their headline spreads**. What carries weight is
the **convergence of their architectural conclusions** with the refereed work — STALE, CUPMem, MemoryAgentBench
(ICLR 2026, 226 cites), BEAM (ICLR 2026, 52 cites), PlugMem (ICML 2026, 27 cites), RMM (ACL 2025, 123 cites),
DoT-Prompting (ACL 2026), Wallat et al. (ACL 2026 Findings), Prior Prejudice (ACL 2026 Findings), Control
Illusion (AAAI 2026), Memora (ACL 2026, 24 cites).

**Refereed and safe to lean on** for benchmarks: MemoryAgentBench (ICLR 2026, 226), BEAM (ICLR 2026, 52),
LongMemEval (ICLR 2025, 652), MemBench (ACL 2025 Findings, 89), Mem2ActBench (ACL 2026, 29), Memora (ACL 2026,
24), RealMem (ACL 2026, 17), EverMemBench (KDD 2026, 14), FaithEval (ICLR 2025, 104), Sufficient Context
(ICLR 2025, 90), ClashEval (NeurIPS 2024, 138), HorizonBench (arXiv 2604.17283, 12).

**Two more construction facts worth knowing, both verified by the section-5 agent against primary sources, and
both of which say the field is actively removing our condition from its benchmarks:** **Mem2ActBench**
(ACL 2026) resolves "contradictions that manifest as cycles in the graph" **by removing a node**, and
**STALE** computes exactly when a temporary state expires and then **only ever queries inside the validity
window** — a benchmark that works out when the new state stops being true and never asks a question after that
moment. **MemoryAgentBench** states the gold rule outright: *"Treat the facts as a chronological update
stream… you must ALWAYS overwrite the earlier fact with the one having the larger serial number."* **That rule
is wrong in our world, and saying so is a clean contribution.**

### 6.5 Loose ends worth one fetch each before submission

- **BeliefMem's method section** (2605.05583) for the exact noisy-OR rule, the candidate count and the calls
  per observation, before we cite its mechanics.
- **CoCo-TAMP's method section** (2603.03704) for what the LLM is called for and how often, and whether objects
  move mid-episode. It is the strongest existing argument for "LLM supplies the prior, arithmetic does the
  updating".
- **The taxonomy section of "In-Context RL under Non-Stationarity: A Survey"** (2607.11906), which is the
  natural place to position the contribution and whose abstract already contains the sentence we want:
  *"previously useful context can therefore become stale, misleading, or useful again."*
- **GLOBE / HOMER-Noise** (2606.08458, IEEE RO-MAN 2026): whether we can run on their dataset. An n-gram Markov
  model gated by an LLM-on-low-confidence, in a noisy household object-location setting, is both a baseline and
  a precedent for the architecture we should build.
- **TEPA's return-phase numbers** (2608.07429), which are in a heatmap we could not read reliably. If the
  authors report them in text or a table elsewhere, they are the numbers our reversal-and-return figure should
  sit beside.
- **BEAM's per-category table** for knowledge update and contradiction resolution. **No per-category table is
  public**, which is a gap we could fill with a small amount of work on a public benchmark, using
  **Qwen2.5-32B-AWQ**, which BEAM already evaluated and which is close to our backbone.
