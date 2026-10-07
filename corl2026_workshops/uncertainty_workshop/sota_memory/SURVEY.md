# Survey: published LLM memory designs and multi-agent debate, as they bear on a temporary routine change

Written by a survey agent for dynamic-home-eqa-34, 2026-09-23 ~02:20. [U] marks claims it did not verify in the primary source.
Spot-checked against the primary sources by -34: STALE (arXiv 2605.06527) Table 3: 77.5% retrieval vs 3.3% judged stale, CUPMem 8.7 -> 68.0, Mem0 8.3 / Zep 6.0 / A-Mem 5.1 / LightMem 17.8. Choi et al. 2508.17536 abstract: majority voting explains most of debate's gains; debate is a martingale.

## Survey: LLM agent memory under change, plus a debate/committee addendum

Sources are arXiv HTML/PDF texts I read directly. Citation counts come from Semantic Scholar and star counts from the GitHub API, both taken 2026-09-23. **[U]** = not verified in the primary source.

### Ranked top 3 for our regime

**1. Zep / Graphiti: a knowledge graph whose facts carry validity dates** (Rasmussen et al., arXiv 2501.13956, 2025; 365 cites; graphiti 31k stars)
- **Mechanism:** Facts are graph edges with four timestamps: valid-from and valid-to (when the fact held), and created and expired (when the system wrote and retired it). When a new edge arrives, an LLM compares it with semantically related edges. If they contradict, the old edge's valid-to is set to the new edge's valid-from. **Old edges are kept, not deleted.** Retrieval combines cosine search, BM25 and graph search, then reranks. The answering model sees each fact as "FACT (Date range: from – to)". Of everything surveyed, this has the most explicit notion of how long a stored fact stays true.
- **Evaluated under change?** Yes, with mixed results:
  - LongMemEval knowledge-update, full-context → Zep: 76.9→74.4 with gpt-4o-mini (slightly worse), 78.2→83.3 with gpt-4o.
  - MemoryAgentBench FactConsolidation (FC) single-hop: **7%, the worst of all methods**; multi-hop 3%.
  - HaluMem memory-updating: 47% correct (medium) and 37% (long).
  - "Are We Ready…" (2606.24775): best on knowledge-update (44.4 substring exact match). That paper has co-authors from MemTensor (the company behind the competing system MemOS).
- **Cost:** Open source. Supports local OpenAI-compatible servers via `OpenAIGenericClient`; the docs warn that small local models break the JSON extraction. Several LLM calls per ingested episode (entity extraction, resolution, fact extraction, invalidation, dates); exact count not stated.
- **Prediction:**
  - Helps at the shift: the desk edge gets closed and the dated display fights the "model overrides the recent sighting" failure.
  - The return is fine only if a fresh "desk" edge is written. Whether Graphiti revives or duplicates a previously invalidated identical edge is **[U]**.
  - Main risk: if location depends on time of day, facts keyed on (object, location) will flip back and forth. Key them on (object, time-slot) instead.

**2. CUPMem, from the STALE benchmark: decide what is current at write time, then restrict what the reader may trust** (Chao et al., arXiv 2605.06527, 2026; 24 cites)
- **Mechanism:**
  - On each new session, an LLM judge labels every affected old entry KEEP, STALE, REPLACE or UNKNOWN.
  - Updates are propagated to dependent entries.
  - At question time the prompt is constrained: active items are the grounding, stale items are marked as history, and unresolved slots cannot be used as defaults.
- **Evaluated under change?** Yes; this is the benchmark's whole purpose (implicit invalidation). Its diagnosis is our failure exactly: **new evidence was in the retrieved set in 77.5% of cases, but only 3.3% of the old entries were judged to need updating.** GPT-4o-mini rose from 8.7% to 68.0%. Existing frameworks scored 5–18% (Mem0 8.3, Zep 6.0, A-Mem 5.1, LightMem 17.8). The best frontier model reached 55.2%.
- **Cost:** About one judge call per affected entry per write; easy to re-implement as prompts. Code release **[U]**.
- **Prediction:** The most direct attack on read-time override. The risk is the return: a STALE label on the old routine must stay retrievable (as it is here, marked "historical"), not be deleted.

**3. Hindsight** (Latimer et al., arXiv 2512.12818, Dec 2025; 31 cites; **25k stars**)
- **Mechanism:**
  - Facts are narrative text with a start and end time for when the fact held, plus a mention time.
  - Four stores: world facts, experiences, entity summaries, and opinions.
  - Opinions carry a confidence that moves in steps: reinforcement adds to it, contradiction subtracts 2α. Opinions are never overwritten wholesale.
  - Background profiles are merged by an LLM, with new information winning conflicts.
- **Evaluated under change?** Yes, on LongMemEval knowledge-update: **84.6 with GPT-OSS-20B versus 60.3 for the same model reading the full history.** Temporal-reasoning went 31.6→79.7.
- **Cost:** Open source, and evaluated end to end on open-weight models. This is the most local-friendly strong system.
- **Prediction:** The stepped confidence gives lag at both the shift and the return; with only 10 sick days, a large α is needed. The start/end times help the model date sightings.

### Other candidates (brief)

- **Mem0 / Mem0g** (Chhikara et al., 2504.19413, ECAI 2025; 652 cites; 66k stars)
  - Mechanism: 2 LLM calls per write (extract, then pick ADD/UPDATE/DELETE/NOOP against the 10 most similar memories). **DELETE is permanent.** The graph variant marks edges invalid instead of deleting them.
  - Under change: LoCoMo only (temporal J-score 55.5 / 58.1). FC 18/2. HaluMem update 25.5% (medium) and **1.45% (long)**.
  - Cost: supports vLLM.
  - Prediction: this is the yardstick. DELETE loses the old routine; it is recovered only by re-observation.
- **MemGPT/Letta** (2310.08560; 1360 cites; 25k stars)
  - Mechanism: the LLM edits its own memory blocks through tool calls. No validity notion. Sleep-time compute (2504.13171) rewrites memory offline between queries.
  - Under change: FC 28/3. "Are We Ready" temporal exact match: 0.0.
- **A-MEM** (2502.12110, NeurIPS 2025; 1028 cites)
  - Mechanism: notes with tags and links. "Memory evolution" rewrites the context text and tags of neighbouring notes. Nothing is ever invalidated.
  - Under change: LoCoMo only; 5.1% on STALE.
  - Cost: several calls per write; tested with Qwen 2.5 and Llama 3.2 via Ollama.
- **Memory-R1** (2508.19828, ACL venue per Semantic Scholar; 195 cites)
  - Mechanism: RL-trained (PPO/GRPO) ADD/UPDATE/DELETE/NOOP manager plus an answer agent that filters retrieved memories. Only 152 training QA pairs. Base models: Qwen-2.5 3B–14B and Llama-3.1-8B.
  - Under change: LoCoMo; LongMemEval zero-shot, with no knowledge-update breakdown seen. Code **[U]**.
  - The answer-agent filter is relevant to read-time override, but it needs fine-tuning, and we serve a 27B model.
- **MemoryOS** (2506.06326, EMNLP 2025; 119 cites)
  - Mechanism: short-, mid- and long-term tiers, with promotion and eviction by a "heat" score. No validity notion. 4.9 calls per response.
  - Under change: its big LoCoMo "temporal" gain (+118.8% F1) is **not** update evidence. LoCoMo's temporal questions ask *when* events happened, and LoCoMo has no knowledge-update category.
- **MIRIX** (2507.07957; 158 cites): six memory types with per-type managers. FC 14/2.
- **HippoRAG 2** (2502.14802, ICML 2025; 233 cites)
  - Mechanism: open information extraction (OpenIE) turns passages into (subject, relation, object) facts, plus Personalized PageRank retrieval. Treats knowledge as static.
  - Under change: best retrieval system on FC single-hop (54).
  - Cost: 1 call per passage and 1 per query; run with Llama-3.3-70B on vLLM.
- **AriGraph** (2407.04363, IJCAI 2025; 115 cites)
  - Mechanism: facts extracted from observations, linked to the episodes they came from. **Conflicting facts are deleted.**
  - Evaluated in TextWorld "Cleaning" (relocating misplaced objects): 0.79 vs 0.05 for full history. The closest task to ours.
  - Prediction: deletion is survivable here because patrols re-observe.
- **MemoryBank** (2305.10250, AAAI 2024; 688 cites): Ebbinghaus-curve decay and reinforcement on recall. No update evaluation. Decay is time-based, not evidence-based, so it would fade the old routine during the 10 sick days.
- **BeliefMem** (2605.05583, 2026; 5 cites): stores several candidate conclusions, each with a probability (Noisy-OR updates plus decay), and shows all candidates at read time. Tested on LoCoMo and ALFWorld with Qwen3-Next-80B; no change evaluation. It fits a temporary shift conceptually: keep "desk 0.3 / couch 0.7" visible rather than overwriting.
- **MemStrata** (2606.26511, 2026): deterministic supersession on (subject, relation) plus a ledger of when each fact was valid. Evolving-knowledge accuracy 0.95–1.00 vs 0.20–0.47 for RAG, using a 7B model. **Facts reverting to earlier values are explicitly listed as future work.**
- **MemOS** (2507.03724; 118 cites): lifecycle states (generated → activated → merged → archived → expired), version chain, and TTL. Best on HaluMem update (62–65%), but HaluMem shares authors with MemOS (Z. Li, F. Xiong).
- **Mem-α** (2509.25911): RL-trained memory construction. **Conflict resolution was excluded** from training for lack of a realistic benchmark.
- **SeCom** (ICLR 2025): no update evaluation.

### Benchmarks that test memory under change

- **LongMemEval** (ICLR 2025, 651 cites)
  - Has a knowledge-update category.
  - Reading strategy (Chain-of-Note plus JSON-formatted memories) is worth up to 10 points even with perfect recall, which supports the view that the read step is the bottleneck.
  - Time-aware query expansion adds 6.8–11.3% on temporal questions.
- **MemoryAgentBench** (ICLR 2026, 225 cites)
  - Key quote: "forgetting out-of-date memory poses a significant challenge… **all methods fail on the multi-hop situation**" (≤7% except GPT-5-mini at 28%).
  - On single-hop, long-context GPT-4o (60), HippoRAG-v2 (54) and BM25 (48) beat every dedicated memory system.
- **LoCoMo** (ACL 2024, 859 cites): no update category. "Temporal" means dates of events.
- **STALE** (2026): see CUPMem above. The adjudication gap is its headline finding.
- **HaluMem** (2511.03506): omission is the dominant update error, with rates above 50% for most systems.
- **Memora** ("From Recall to Forgetting", 2604.20006, ACL 2026): preferences that reverse. Scores fall with timeline length; 64% of recommendation failures are "outdated memory not being forgotten".
- **Anatomy of Agentic Memory** (2602.19320): graph and episodic memories are the most fragile under weaker backbones (Nemori had 30% format errors on Qwen2.5-3B).
- **No benchmark tests a temporary change that reverts to the prior routine.** This is a real gap in the literature.

---

### Addendum: multi-agent debate and committees

None of the works below was evaluated with facts that change over time.

- **Du et al. 2023** (ICML 2024, 2270 cites): 3 agents × 2 rounds = 6 calls. It beats majority vote (e.g. GSM8K 85 vs 81), but the vote used fewer calls, so this is **not an equal-compute comparison**. Tasks are static (arithmetic, GSM8K, biographies, MMLU, chess).
- **Liang et al. MAD** (EMNLP 2024, 1392): affirmative and negative debaters plus a judge, aimed at "degeneration of thought"; counter-intuitive arithmetic and commonsense translation. **ChatEval** (989) is a debating panel of LLM judges **[U: details]**. **ReConcile** (ACL 2024, 386): heterogeneous models with confidence-weighted voting; the gains come from model diversity.
- **Self-consistency** (ICLR 2023, 7710) and **Universal Self-Consistency** (211, in which an LLM picks the most consistent of N samples): these are the equal-compute yardsticks.
- **The critiques:**
  - Smit et al. (ICML 2024, 131): debate does not reliably beat other prompting strategies and is sensitive to hyperparameters.
  - Zhang et al. 2025 "Stop Overvaluing MAD" (40): 5 debate methods, 9 benchmarks, 4 models. Debate often fails to beat chain-of-thought and self-consistency "even when consuming significantly more inference-time computation".
  - **Choi et al. "Debate or Vote"** (NeurIPS 2025 spotlight, 75): majority voting explains most of debate's gain. They prove debate is a martingale: it does not raise expected correctness. On Qwen2.5-7B, a vote of 5 single calls scored 0.769 versus 0.711–0.738 for debate at 5×T calls.
  - Wu et al. 2025 (26): "majority pressure suppresses independent correction".
- **Knowledge conflict (most relevant):**
  - **MADAM-RAG** (Wang, Prasad, Stengel-Eskin, Bansal; COLM 2025; 87): one agent per document plus an aggregator. +15.8 absolute on the FaithEval inconsistent subset with Llama-3.3-70B. About 4× the input tokens of plain RAG. No vote or equal-compute baseline.
  - **SR-DCR** (2506.06020, 3 cites): a defender argues from the context, a critic *without* the context challenges it, and a judge decides; about 13 passes. On ClashEval it keeps 95.7% on trustworthy context while resisting perturbed context. It notes that longer classical debates *increase* reliance on the context.
- **Prediction for our failure:** These methods are built to *resist* the context. Our need is the opposite: trust the recent sighting over the routine prior. An agent without the context, or a majority that defaults to the routine, would argue for the stale answer and outvote the one agent citing the sighting. The expected result is at best parity with self-consistency at equal calls.