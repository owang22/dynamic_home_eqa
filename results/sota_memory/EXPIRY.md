# EXPIRY: when does a stored item stop being useful for a question about NOW?

Written 2026-09-23 by a research agent, as a third layer on `SURVEY.md` and `SURVEY2.md`. Read those first.
This document does **not** re-describe the memory systems they cover (Zep/Graphiti, Mem0, MemGPT, A-MEM,
MemoryBank, MemOS, MemStrata, CUPMem/STALE, Hindsight, BeliefMem, TEPA, TANGLE, ChronoMem, TOKI, A-TMA,
LifeFuse-Mem, MemTrace, Supersede, HypoGeniC, ExpeL, Reflexion, the debate literature, the drift-detector
yardsticks in §3.5, or the reversion sweep in §5). It goes after one question those two only touched:
**by what mechanism does any system decide that a stored item no longer describes the world — and can that
decision ever be undone?**

## Conventions

- **[U]** = not verified in the primary source this pass. Everything else was read in the primary source
  (arXiv abstract page, arXiv HTML/ar5iv, publisher HTML, or the PDF) today.
- **Citation counts are patchy on this pass**: the Semantic Scholar API returned HTTP 429 for most requests
  all session (a sibling survey agent appears to have exhausted the shared quota) and the WebSearch budget
  (200/200) was spent before I started, so counts were scraped by a slow retry loop that got through only part
  of the list. **Verified myself today:** Zhang & Choi 26; CyGNet 390; Persistence Filter 89; BOCPD 923
  (confirming SURVEY2's figure); Song et al. latent-cause 7; Oblivion 3; Nous 2; FSFM 2; MemCon 1. Counts
  marked *(S2 via SURVEY2)* come from the sibling survey of the same date. Counts marked **[cites U]** are
  unknown and **must not be quoted** — §7 lists them as one-lookup-each loose ends.
- **Preprint hygiene.** 2026 arXiv has a thick layer of single-author, zero-citation agent-memory preprints
  that cite each other. Every one below carries its author count. **1a = single author.** Nothing marked 1a
  or 0-cite is an established result; several are substantive as design-space evidence and are used only that
  way. No headline number from an unrefereed preprint is quoted here as fact without that flag attached.
- **A / B** split is kept throughout, as asked:
  - **(A) STALE EVIDENCE** — an individual observation or retrieved item. *"The mug was on the desk at 9am
    on the 12th."*
  - **(B) STALE BELIEF** — a generalisation, rule, summary, profile or explanation the system itself wrote
    and now acts on. *"Yuki keeps her things at the desk during the day."*

---

## 0. The answer in five sentences

1. Every deployed mechanism for deciding an item is stale reads one of six signals: **elapsed time, an
   explicit validity interval, a contradiction with a newer item, a prediction error, a usage/utility
   statistic, or the source it came from.** A seventh — **going and looking again** — exists only in robotics
   and in one 2026 agent-memory preprint.
2. **Nearly all of it is applied to (A) and almost none to (B).** For a self-written generalisation the only
   signals in use are usage/reward counters (ExpeL, HypoGeniC, MemCon) and a fresh LLM re-adjudication
   (CUPMem, EvoGraph-Mem, TARL, ReTree — three of those four are 2026 preprints). Nothing derives the
   staleness of a belief from the staleness of the evidence that produced it, except by propagation rules
   introduced in 2026 and by a 1979 formalism nobody has implemented with an LLM (JTMS).
3. **Forward expiry prediction is a real and separate NLP literature** (fact-duration prediction, temporal
   validity duration, content expiry dates) which is done by small finetuned encoders and threshold rules,
   is never wired into a memory loop, and **states in its own limitations that it cannot represent a fact
   that becomes true again** (Chronocept, verbatim, below).
4. **The distinction between "this belief is wrong" and "this belief is suspended and may return" exists in
   exactly four places**, none of them LLM memory: bitemporal databases (valid time vs transaction time),
   Katsuno–Mendelzon *update* vs AGM *revision*, truth-maintenance IN/OUT labels, and latent-cause inference
   in cognitive science. Zep's four timestamps are the one LLM-memory schema that can express it; no
   evaluation exercises it.
5. **Restoration after a revert has been measured, once, per literature**: in stream mining (recurring-concept
   model pools, and Shaker & Hüllermeier's recovery protocol), in long-term robot mapping (persistence +
   **emergence** filters — Perpetua, 2025), and in exactly one LLM-adjacent method paper with no LLM in the
   loop (TEPA). For everything that reads or writes natural-language beliefs, the answer to "tested under a
   change that reverts?" is **no**.

---

## 1. Why (B) is emptier than (A), mechanically

A stale observation has an external referent: another observation can contradict it, and a key
`(object, location)` makes the contradiction a string comparison. A stale *belief* has three properties that
break every mechanism in §2:

- **It has no timestamp that means anything.** A routine card written last night is *fresh as a write* and
  *stale as a claim*. Recency-weighted retrieval scores it highest exactly when it is most wrong. This is
  the mechanism behind "Manufactured Confidence" (2606.29279, *SURVEY2* §5.5): the write step converts a
  hedged observation into a confident dated assertion.
- **It is not contradicted by any single observation.** "Yuki keeps her things at the desk" survives one
  sighting of the bag on the couch; it is only contradicted by a *statistic over* sightings. None of the
  contradiction detectors in §2.3 takes a set of observations as one side of the pair.
- **Its usage statistics rise as it gets more wrong.** A belief that the model keeps consulting and keeps
  being confident about accumulates access counts, reinforcement and "importance" — the eviction signals in
  §2.5 all point the wrong way. The empirical version of this warning is *"Useful Memories Become Faulty When
  Continuously Updated by LLMs"* (2605.12978, *SURVEY2* §0): memory utility rises then falls below the
  no-memory baseline.

The one mechanism family that addresses (B) *in principle* is **dependency tracking**: mark which
observations justify a belief, and withdraw the belief when its justifications are withdrawn. That is a
justification-based truth maintenance system (Doyle 1979). Its 2026 descendants are three preprints that
propagate an invalidation into derived text (CUPMem's dependent entries, ReTree's regenerated summaries,
EvoGraph-Mem's archived insights). None of them keeps the justification set, so none of them can bring the
belief back when the justifications return.

---

## 2. The mechanism families

### 2.1 Time-based decay and recency weighting

**Signal:** elapsed wall-clock (or simulated) time since the item was written or last retrieved.
**Decision:** arithmetic, in every case; no model call.
**Effect:** downweight at retrieval. Deletion only where a decayed score crosses an eviction threshold.

- **Where the functional form comes from.** ACT-R's base-level activation, whose empirical justification is
  Anderson & Schooler, *"Reflections of the environment in memory"* (Psychological Science 1991): the power
  law of forgetting mirrors the environmental statistics of an item being **needed again**. The decay
  constant is, in the original theory, an estimate of recurrence in the environment. **[U — foundational,
  not primary-verified this pass; cites U.]** In every LLM memory system below it is a constant.
- **Generative Agents** (Park et al. 2023): `score = α_rec·recency + α_imp·importance + α_rel·relevance`,
  all α = 1, recency = exponential with factor **0.995** per sandbox hour since last retrieval (verified in
  *SURVEY2* §1.1 against the paper).
- **MemoryBank** (2305.10250, AAAI 2024, 688 cites *(S2 via SURVEY2)*): explicit Ebbinghaus curve; recall
  strengthens the item. Time-based only — no evidence enters the decision.
- **Oblivion — "Self-Adaptive Agentic Memory Control via Decay-Driven Activation"** (2604.00131, 5 authors:
  Rana, Hung, Sun, Kunkel, Lawrence; Mar 2026, rev. Sep 2026; **3 cites**). Verbatim abstract: *"Human
  memory adapts through selective forgetting: experiences become less accessible over time but can be
  reactivated by reinforcement or contextual cues… We introduce Oblivion, a memory control framework that
  casts forgetting as decay-driven reductions in accessibility — not explicit deletion."* It also gates
  *whether to consult memory at all* on agent uncertainty and buffer utility (a model-side decision).
  Reported: **73% token-cost reduction at 120K-interaction spans**; evaluated on "static and dynamic
  long-horizon interaction benchmarks". **This is the only decay mechanism I found that advertises
  reactivation — but reactivation restores *accessibility* on a cue, not *truth*: nothing in it decides that
  the old value is correct again.** No reverting fact in the evaluation.
- **Chronofy — "Temporal-Logical Decay"** (2607.20560, 4 authors, Jul 2026; **[cites U]**, unrefereed).
  Exponential decay inside graph retrieval, Signal-Temporal-Logic robustness, and a "possibilistic
  weakest-link" bound that caps output confidence at the most decayed evidence in the chain. Its decay
  coefficient β_j is claimed to be *"grounded in Bayesian decision theory as an approximation of twice the
  latent process mean-reversion rate"* — the one place I found where a decay constant is tied to a property
  of the underlying process rather than picked. **[U on whether β is fitted from data or derived
  analytically.]** Note the irony: mean reversion is a model of a quantity that *comes back*, and the paper
  neither models nor evaluates a return.
- **Learned decay, outside LLM memory:** LSTM forget gates (Gers et al. 2000) **[U]**; volatility-tracking
  Bayesian learners that infer how fast the world changes and set the learning rate from it (Behrens et al.,
  *Nature Neuroscience* 2007) **[U — nature.com paywalled this pass]**; the hazard rate in Bayesian online
  changepoint detection (Adams & MacKay 2007, **923 cites**, confirmed today).

**Can an item come back?** Only by being re-written or re-retrieved (Oblivion's cue-driven reactivation,
MemoryBank's recall reinforcement). **Never because the world reverted.**
**Tested under a revert?** **No**, for every item in this family.
**Frozen local 27B?** Yes — pure arithmetic; zero calls.
**Verdict for us:** structurally wrong for a 10-day suspension. Decay is a function of elapsed time alone, so
during the suspension it monotonically fades the belief that will be correct again on day 11, and after the
return that belief must re-earn support from zero. This is already the reasoning in *SURVEY.md* on MemoryBank;
the addition here is that **no decay variant published since fixes it, including the ones that advertise
reactivation.**

### 2.2 Explicit validity intervals, temporal scoping, bitemporal stores

**Signal:** a stored `valid_from` / `valid_to`, compared against the question's time.
**Decision:** the *comparison* is a rule; **who sets `valid_to` is the whole question.**

- **The database answer, and the most useful distinction in this review.** Verified in Kulkarni & Michels,
  *"Temporal features in SQL:2011"* (SIGMOD Record 2012; IBM) — read in the PDF today. SQL:2011 separates
  **valid time**, verbatim *"the time period during which a row is regarded as correctly reflecting reality
  by the user"* (application-time period tables), from **transaction time**, *"the time period during which a
  row is known to the database"* (system-versioned tables), and notes that *"for any given row, its
  transaction time may arbitrarily differ from its valid time."* An UPDATE on a system-versioned table
  **closes the current row's system period at the transaction timestamp and inserts a new current row** —
  history rows are retained and may be modified *only by the system*. Meanwhile users *"update the validity
  periods of the rows as errors are discovered or new information is made available."*
  **So: a world change writes a new valid-time interval; an error correction writes a new transaction-time
  version of the same valid-time fact. That is exactly "suspended" versus "wrong", it is in the SQL standard,
  and nothing is deleted — a value that becomes true again is a new interval carrying an old value.**
  (Snodgrass/TSQL2 as the lineage: **[U]**.)
- **The knowledge-base practice.** Wikidata: statements carry **start time / end time** qualifiers and a
  rank (preferred / normal / **deprecated**). Verified in `Help:Ranking`: deprecated is for statements
  *"containing known errors"*, and explicitly *"does not apply to correct historical information, such as
  previous values of a statement… Such statements should instead be annotated with the appropriate start
  time/end time qualifiers."* Demotion is reversible — the ranks are annotations, not deletions. This is the
  cleanest archive-and-restore convention in production anywhere, and it is editorial, not algorithmic.
- **Who predicts the interval, pre-LLM:** the temporal-scoping line. **CoTS, "Coupled Temporal Scoping of
  Relational Facts"** (Talukdar, Wijaya, Mitchell; WSDM 2012) infers intervals by *coupling* facts through
  containment, alignment, succession and mutual-exclusion constraints; **CTPs** (Wijaya et al., EMNLP 2014)
  detect state changes in contextual temporal profiles; **TISCO** (WWW 2019) and **MemTimes** (2020) continue
  it. All corpus-statistics plus constraint propagation, no language model. **[cites U]**. Their constraint
  vocabulary is the diachronic analogue of NLI labels and is cheap to compute over keyed facts — a point the
  agent-memory literature has not picked up.
- **In LLM memory** (systems already in *SURVEY.md*, listed here only for the mechanism): **Zep/Graphiti**
  is the one schema with four timestamps — `valid_from`, `valid_to` (when the fact held in the world) and
  `created_at`, `expired_at` (when the store wrote and retired the edge) — **i.e. it is bitemporal, so it can
  separate "stopped being true" from "stopped being believed"**, and it keeps old edges; the invalidation
  decision is an **LLM call** on semantically related edges. Whether Graphiti *revives or duplicates* a
  previously invalidated identical edge is still **[U]** (flagged in *SURVEY.md* and not resolved here). **MemStrata** (1a) does
  deterministic supersession on `(subject, relation)` plus a validity ledger and puts *"facts reverting to
  earlier values"* in future work. **TOKI** (1a) gives a bitemporal operator algebra with Allen relations —
  representable, never evaluated. **MemOS** has lifecycle states ending in *archived* and *expired*, plus TTL.
- **Engram — "Less Context, More Accuracy: a Bi-Temporal Memory Engine"** (2606.09900, **1 author**,
  Liuyin Wang, Jun 2026; **[cites U]**, almost certainly 0). Verbatim on the mechanism: facts are
  *"invalidating, never deleting, so every fact keeps provenance and a supersession chain"*, with valid time
  and transaction time and point-in-time queries. **LongMemEval_S: 83.6% vs 73.2% full-context (+10.4,
  McNemar p < 10⁻⁶) at ~9.6k vs 79k tokens.** Single-author preprint — quoted as evidence that the
  bitemporal design has been tried in this setting, not as a result. **Re-promotion of an invalidated fact is
  not addressed; no fact reverts.**
- **MedCache** (2608.29528, 7 authors, Aug 2026; **[cites U]**) is worth one sentence because of its
  *finding* rather than its mechanism: across four memory design choices on multi-visit clinical records,
  *"temporal validity is more important than simply retaining more history"*. **[U on the mechanism — the
  abstract does not say who assigns the validity window or what happens at expiry.]**

**Can an item come back?** In every interval-based store the old value is *retained*, so yes in principle —
but only by writing a **new** interval after a **new** observation. **No system re-opens a closed interval,
and none predicts that a closed interval will re-open.**
**Tested under a revert?** **No** — confirmed for Zep, MemStrata (own future work), TOKI, Engram, MemOS;
the sweep in *SURVEY2* §5.2 is the authority for the benchmark side.
**Frozen local 27B?** Yes for the rule half. Zep's LLM invalidation step is known to break on small local
models (*SURVEY.md*).

### 2.2b Predicting how long a fact stays true — the first thing you asked me to chase

This is a genuine, self-contained literature that neither prior survey covers, and its punchline is bad for us.

| work | what it predicts | how | verified numbers |
|---|---|---|---|
| **MCTACO**, *"'Going on a vacation' takes longer than 'going for a walk'"* (Zhou, Khashabi, Ning, Roth; EMNLP 2019) | five temporal-commonsense dimensions including **duration** and **stationarity** (does a state hold indefinitely) | 13k QA pairs, binary plausibility | the original source of "is this the sort of statement that persists?" **[cites U]** |
| **Takemura & Tajima** (CIKM 2012) | tweet **lifetime duration** classes | supervised classification | **[U — known only as prior work cited by Wenzel & Jatowt]** |
| **Almquist & Jatowt**, *"Towards content expiry date determination"* (ECIR 2019) | a document's **expiry date** | supervised, feature-based | **[U, same]** |
| **Lynden et al., CoTAK** (CIKM 2023) | temporal validity duration of statements | dataset + models | **[U, same]** |
| **Zhang & Choi**, *"Mitigating Temporal Misalignment by Discarding Outdated Facts"* (EMNLP 2023, **26 cites, verified today**) | **fact duration**: how long a given fact will remain true | **finetuned BERT-base**, cloze `", lasting [MASK][MASK]"`, 13-way duration class + log-seconds regression; distant supervision from TimeQA (11,708) and TimePre (24,089); evaluated on SituatedQA (322 examples, 157 changed / 165 unchanged, 2018→2021) | **65%** of temporally dependent facts from real search queries dated to within 3 years vs **11%** for an average-duration baseline; **expected calibration error cut 50–60%** vs system confidence alone. Discarding is a **threshold rule** on predicted duration |
| **Wenzel & Jatowt**, *"Temporal Validity Change Prediction"* (Findings of ACL 2024) | whether a **follow-up statement** shortens or lengthens a target statement's validity — ternary DEC / UNC / INC | 5,055 crowdsourced samples from 1,685 Twitter target statements | best **SelfExplain+multitask 88.5% acc / 69.8% exact match**; TF-BERT 84.8/61.2; **ChatGPT 66.3/29.3**. Verified in the HTML: **no mention of a statement becoming valid again** |
| **Chronocept** (2505.07637, 5 authors, May 2025; **[cites U]**, preprint) | temporal validity as a **skew-normal density over log time** (ξ location, ω scale, α skew) | 1,254 single-sentence + 524 multi-sentence samples, GPT-o1-generated, ICC 0.843 / 0.893; eight annotation axes including *Static* and *Recurrent* | best **FFNN MSE 0.876 / 0.872**; BERT underperforms. **Verbatim limitation: it *"cannot represent events with multiple distinct periods of relevance, such as seasonal or recurring phenomena"*** |

**Who does it, and how well:** small finetuned encoders, not LLMs, and the one LLM tested (ChatGPT on TVCP)
is 22 points of accuracy and 40 points of exact match behind a finetuned SelfExplain model. The best result
in the family — dating a fact's duration to within 3 years for 65% of queries — is a *coarse volatility
class*, not an expiry date.

**Three structural facts that matter more than the numbers:**
1. **None of it is wired into a memory system.** Every paper evaluates duration prediction, or calibration on
   a QA set, in isolation. Nobody feeds a predicted duration into a retrieval store as a TTL and measures the
   downstream effect.
2. **Recurrence is excluded by construction, twice, in writing.** Zhang & Choi list *"modeling whether a fact
   changes after a regular, periodic time interval"* as future work; Chronocept says its unimodal density
   cannot represent recurring relevance. Chronocept even has a *Recurrent* annotation axis and still cannot
   model recurrence in its output representation.
3. **Nobody predicts when a fact will become true again.** Across this whole literature the prediction target
   is one-sided: how long until it stops.

### 2.3 Contradiction and conflict detection

**Signal:** a newer item that cannot co-hold with the stored one.
**Decision:** three sub-families — a **key rule**, an **LLM judgement**, or an **NLI model**.

- **Keyed supersession (rule).** Last-write-wins on `(subject, relation)` or `(object, attribute)`: MemStrata,
  MemoryAgentBench's FactConsolidation construction, **TEPA**'s deterministic keyed table. TEPA is the only
  paper anywhere with an explicit `{stable, light, reversal, return}` phase schedule, and its reversal-phase
  numbers — **0.950 vs 0.210 append-only / 0.210 last-write-wins / 0.309 no-memory** — are the largest effect
  in this literature, achieved with **zero LLM calls** (*SURVEY2* §4.4; 0–5 cites, unrefereed). On clean
  single-hop consolidation TEPA merely matches last-write-wins (0.890), which tells you the keys are doing
  the work.
- **LLM adjudication.** Zep's edge invalidation; Mem0's ADD/UPDATE/**DELETE**/NOOP (delete is permanent);
  **CUPMem**'s KEEP / STALE / REPLACE / UNKNOWN labels **with propagation to dependent entries** and a
  constrained readout (STALE's 8.7 → 68.0 with GPT-4o-mini); **TARL** (2608.03699, 5 authors, Aug 2026;
  **[cites U]**) which replaces the binary Write/Hold decision with five actions — verbatim, whether new
  information should be *"added, ignored, used to revise an outdated belief, rejected as unreliable, or
  deferred for verification"* — and keeps **accepted / pending / rejected ledgers**, so a rejected item is
  retained; but the policy is **trained** by comparing memory states under alternative operations, so it is
  not a frozen-model drop-in. **[U on its numbers and backbones; restoration from the rejected ledger is
  implied by the design, not demonstrated.]**
- **NLI (a model, but a small one).** ConCoRD's off-the-shelf NLI + MaxSAT, BeliefBank, REFLEX — all
  **synchronic** consistency, no fact ever becomes false (*SURVEY2* §4.4). The transferable residue, already
  argued there and worth repeating because it is the cheapest option on our hardware: **a DeBERTa-MNLI-class
  model can supply a contradiction signal for zero LLM calls**, and the published LLM detection numbers are
  poor in exactly the framing we would naively use (whole-context recall 0.04–0.57; pairwise accuracy 0.893).
- **What happens to the superseded item:** delete (Mem0 DELETE, AriGraph), close-and-keep (Zep, Engram,
  MemStrata, A-TMA's retained transition records), or label at read time (A-TMA's `current` / `historical` /
  `transition`, CUPMem's "history" section).
- **Propagation into derived beliefs — the only (B) mechanisms in existence.** CUPMem propagates an update to
  *dependent entries*. **ReTree** (2608.10676, 6 authors, Aug 2026; **[cites U]**) is the sharpest statement
  of the problem: existing compression methods *"often replace erroneous facts without repairing downstream
  reasoning derived from them"*, so on a contradiction it **traces back to the node where the claim was
  introduced, replaces the outdated evidence, regenerates the summaries, prunes affected branches and resumes**
  (up to **+25.6 points** over full-trajectory ReAct, context 1.27–1.51× smaller). **EvoGraph-Mem**
  (2608.11248, 2 authors, Aug 2026; **[cites U]**) stores **insight nodes with positive evidence, negative
  evidence and activation states** and *"archiv[es] invalid ones, revis[es] outdated ones"*. **[U on both
  mechanisms' internals: neither abstract says whether detection is an LLM call or a rule, and neither says
  whether an archived insight can be re-promoted.]**

**Can an item come back?** In the keyed and interval variants, yes and *automatically*, but only through
**re-observation**: the return is superseded onto the shift value the same way the shift was superseded onto
the original. In the delete variants, never. In the propagation variants, unknown.
**Tested under a revert?** **TEPA yes** (the only one, no LLM in the loop). Everything else: **no** — Zep,
Mem0, CUPMem/STALE (its own limitations name *"one-shot"* transitions), A-TMA, ReTree, EvoGraph-Mem, TARL.
**Frozen local 27B?** Keys yes; NLI yes (a 400M encoder); LLM adjudication yes but with the known small-model
JSON and recall problems; TARL no (needs training).

### 2.4 Surprise, prediction error, change detection

**Signal:** the system's *own* errors, or the surprisal of a new observation under its current belief.
**Decision:** arithmetic in the classical work; a prompt in the LLM work.

- **Classical detectors:** DDM (Gama et al. 2004), ADWIN (Bifet & Gavaldà, SDM 2007), Page-Hinkley/CUSUM
  (Page 1954), **Bayesian online changepoint detection** (Adams & MacKay 2007, **923 cites**, confirmed today)
  — an exact recursive filter over run-length with a hazard rate, O(t) per step, closed form for
  exponential-family likelihoods, zero model calls. **Recurring-concept handling is a solved sub-problem**:
  Katakis et al. (KAIS 2010, 230 cites), **RCD** (Pattern Recognition Letters 2013, 112 cites) which *stores
  a retired model and re-activates it when a past state returns*, Cetrulo et al. (ESWA 2022), and
  **Shaker & Hüllermeier's recovery analysis** (Neurocomputing 2014/15) which is the recovery-after-shift
  protocol we are running (all counts *(S2 via SURVEY2)* §5.3).
- **Coupling to LLMs: still nobody.** *SURVEY2* §3.5 found the LLM is always the wrapper (SigLLM, LLM-augmented
  CPD, EvoTS-Agent) and no paper couples a detector to an agent's own outcome stream. **I re-swept arXiv
  independently today** (`ADWIN` / `Page-Hinkley` / `drift detector`, 2025–2026, plus `concept drift` ∧
  `agent memory`): the only LLM hits are **persona-drift monitoring** (2605.09863, cosine similarity to
  behavioural anchors), **prompt-injection semantic-drift auditing** (2606.19660), **layer-wise activation
  drift** (2602.00750), and an ADWIN application to software aging (2511.03103). **The gap is confirmed by a
  second, independent sweep: drift detection is applied to an LLM's style and security, never to its task
  outcomes, and never to decide what it reads.**
- **Surprise inside agent memory, write-side.** **Nous** — *"When Does Belief-Based Agent Memory Help?"*
  (2606.22030, **1 author**, Pranav Singh, Jun→Jul 2026; **2 cites**). Verbatim: it *"represents each
  entity-attribute pair as a categorical probability distribution updated through closed-form Bayesian
  inference, with information-theoretic surprise driving belief revision and entropy-based forgetting"*, plus
  **provenance-capped** trust bounds (reliability read off epistemic language, then capped by source, as a
  defence against memory poisoning). Evaluated on LoCoMo, a controlled contradiction benchmark and
  memory-poisoning; reports a **27.5-point gap between token-F1 and LLM-as-judge** scoring. Single-author
  preprint. **Restoration not addressed; no reverting fact.** This is nonetheless the closest published thing
  to "a numeric belief per attribute, revised by surprise, on a frozen model" — the design we would build.
- **In robotics the prediction error is a missed detection** — see §2.8, where it is used properly.

**Can an item come back?** In the recurring-concept pools, **yes, by design** — the retired model is stored
and re-activated. In the LLM work, not applicable (no detector).
**Tested under a revert?** **Yes in stream mining** (that is what RCD and recovery analysis are for);
**no anywhere near an LLM.**
**Frozen local 27B?** Yes, trivially — the detectors are arithmetic over a binary correctness stream, which we
already produce.

### 2.5 Usage statistics, utility, eviction, "importance"

**Signal:** access frequency, recency of use, an LLM-assigned importance score, or reward/task success
attributed to the item.
**Decision:** arithmetic thresholds, except where an LLM writes the importance score.

- **Established:** Generative Agents' importance score (0–10 by LLM, threshold 150 for reflection);
  MemoryBank's strength-on-recall; **MemoryOS**'s heat score with promotion and eviction; MemGPT paging;
  **ExpeL**'s insight counters (start at 2, UPVOTE/EDIT up, DOWNVOTE down, removed at 0); HypoGeniC's
  per-hypothesis running accuracy + UCB bonus (the one *belief-level* utility statistic in the literature,
  *SURVEY2* §3.3).
- **2026, all preprints, counts [cites U]:** **MemCon**, *"Memory as a Controlled Process"* (2607.13591,
  14 authors, Jul 2026, **1 cite**) casts memory operations as an **MDP** and learns *"when to consolidate or forget"*
  with a **tabular contextual bandit with UCB**, verbatim *"learns from task-by-task binary feedback with no
  pretraining and no additional LLM calls"*, converging *"within tens of tasks"*; up to **+15.2 points** task
  success and 5–20% fewer tokens across 6 benchmarks × 3 frameworks × 3 backbones. **This is the strongest
  "learned when to forget" result that is compatible with a frozen local model** — the learning is in a
  bandit, not in the LLM. **FSFM** (2604.20300, 10 authors, **2 cites**) gives the taxonomy: **passive decay / active
  deletion / safety-triggered / adaptive reinforcement**, reporting +8.49% access efficiency and +29.2% SNR.
  Also **SF-AMS** (utility survival from usage redundancy), **CAMeR** (keyword-gated decay with reinforcement
  above threshold), *"Learning What to Remember"* (2606.12945, multi-factor value over encoding depth, forget
  risk and retrieval rank), **ZenBrain** (decay 0.25/day), **LANTERN** (2606.05182, **1a**, *"proactively
  archives every conversation turn and restores relevant details after compaction via hybrid retrieval"*),
  **CausalCache** (2608.22577, 4a, *"swaps in an older event only when its predicted utility exceeds that of
  a recent event"*).
- **The defect is structural and it is ours.** Utility is not truth. Our failure mode is a belief that is
  being used constantly and looks successful; every signal in this family promotes it. LANTERN and
  CausalCache do archive-and-restore, but restoration is triggered by **predicted usefulness to the current
  query**, never by evidence that the archived claim is true again.

**Can an item come back?** Yes in the tiered/archival systems — on demand, never on truth.
**Tested under a revert?** **No**, for every item in this family.
**Frozen local 27B?** Yes for counters and bandits; the LLM-written importance score costs a call per item.

### 2.6 Provenance and source reliability

**Signal:** *where the item came from* and *how it was obtained*, not when.

- **Truth discovery** is the origin: iterative source-trust ↔ fact-confidence estimation (Yin, Han & Yu,
  TKDE 2008 **[U, cites U]**), scaled up as **Knowledge-Based Trust** (Dong, Gabrilovich, Murphy et al.,
  arXiv 1502.03519, VLDB 2015): score a source by *"the correctness of factual information provided by the
  source"* with a **multi-layer probabilistic model** that separates extraction error from source error, over
  **2.8B facts / 119M pages**. A learned model, not a rule. **[cites U]**
- **In agent memory, 2026, all preprints:** Nous's provenance-capped trust (§2.4); *"Stored Is Not Supported:
  Typed Provenance"* (2609.02127, 2 authors, Sep 2026), whose framing sentence is the best one-liner in this
  review — *"Persistence changes availability, not epistemic standing: stored or retrieved material is not
  thereby supported"* — and which **labels** rather than deletes items failing accepted-evidence,
  temporal-validity or disclosure policies (24 conformance cases; *"passed none of 19 unsafe opportunities
  unqualified"* versus 18–19/19 released by flat/source-tag baselines — a governance evaluation, not an
  accuracy one; restoration not addressed). **Budgeted verification** / *"When Stale Constraints Go
  Unchecked"* (2608.25553, **1a**, 2 cites *(via SURVEY2)*): models skip the critical provenance path in about
  one episode in five and make stale-consistent decisions **77.3% / 74.7%** of the time across 16 models.
- **Why it matters to us more than it looks.** Provenance is the only signal that discriminates *a fresh
  patrol sighting* from *a nightly-written routine card* **without any temporal model at all** — "this came
  from the sensor at 14:02" versus "this was inferred by me from sightings up to the 12th". It is also the
  one distinction our prompt currently does not make load-bearing. The caution from the same literature is
  that provenance annotations are ignored unless the read step is forced to use them.

**Can an item come back?** Provenance does not expire, so nothing is set aside by it permanently — it
**re-ranks** rather than retires. That is a point in its favour for a reverting world.
**Tested under a revert?** **No.**
**Frozen local 27B?** Yes — it is a field on a record plus a prompt policy.

### 2.7 Belief revision, truth maintenance, and the cognitive-science layer

This is where the "suspended vs wrong" distinction actually lives.

- **AGM** (Alchourrón, Gärdenfors & Makinson 1985) gives expansion / revision / contraction, and the
  **Recovery postulate** `K ⊆ (K ÷ p) + p` — the only formal statement in any literature that a retraction
  must be *reversible*. Verified against the Stanford Encyclopedia entry: Recovery holds in AGM, is
  contested (it fails in belief-base models), and **AGM "has no explicit representation of time" and no
  notion of a belief being temporarily suspended and later restored.**
- **Katsuno & Mendelzon's *update* versus AGM *revision*** — verified in the same source and the single most
  useful conceptual import available: **revision** is new information about a *static* world (we were wrong);
  **update** is a world that has *changed*. KM's solution is to index sentences with time, so a belief set
  holds ⟨p, t⟩ pairs and updating preserves past facts instead of overwriting them. **That is our A→B→A
  setting, formalised in 1991, and it is the same distinction as a bitemporal database's valid vs transaction
  time.** *SURVEY2* §4.4 established that no LLM system implements AGM; this adds that the AGM half is the
  *wrong* half — we want KM update, not AGM revision.
- **Truth maintenance (Doyle 1979; de Kleer's ATMS 1986).** A belief is **IN** or **OUT** depending on whether
  its **justifications** currently hold; an OUT belief is **kept, with its justification, and becomes IN again
  the instant its support returns**; dependency-directed backtracking retracts everything derived from a
  withdrawn premise. **This is exactly the archive-plus-restore-plus-propagate machinery that (B) needs, and
  it predates all of it.** *SURVEY2* §4.4 already established that "truth maintenance with LLMs" in current
  usage means truth-preserving autoformalization and has nothing to do with retracting a stale belief. **[U —
  Doyle/de Kleer not primary-verified this pass; textbook content; cites U.]**
- **Latent-cause inference — the one computational theory whose central phenomenon is literally called
  A-B-A.** Gershman, Blei & Niv, *"Context, Learning, and Extinction"* (**Psychological Review** 2010,
  117(1):197–209; **[cites U]**) — read in the PDF today. Observations are **partitioned into clusters
  corresponding to latent causes**, with a **Chinese restaurant process** prior over partitions (unbounded
  number of causes) and a **particle filter** for inference. Verbatim on the phenomenon, which they name
  **ABA renewal**: *"it would appear, at first glance, that the animal has 'unlearned' its response to the
  cue. However, if the animal is returned to the original context (A) in a test phase and presented with the
  cue, **the response is restored**, strongly suggesting otherwise."* And on the mechanism: *"our model
  predicts ABA renewal as a consequence of the animal's inference that different latent causes are active
  during conditioning and extinction. **When the animal is returned to the conditioning context in the test
  phase, it infers (because of the presence of contextual cues) that the first latent cause is once again
  active.**"* Restated in our terms: *a belief is suspended by inferring a second regime, not by being
  downweighted, and it returns when the first regime is inferred to be active again — and the cue that brings
  it back is the similarity of today's observations to the observations of the original regime.* The follow-up
  modelling paper is Song, Jones, Monfils & Niv (arXiv 2205.04670; published in *Neurons, Behavior,
  Data analysis and Theory* 2021; **7 cites**). Adjacent: Bouton on renewal/reinstatement,
  Gershman et al. on memory modification — **[U]** both.
- **Win-stay/lose-shift and perseveration** in frozen LLMs (2604.04182, IPMU 2026, *SURVEY2* §3.1): win-stay
  > 0.93, lose-shift ≈ 0.035, perseveration after a reversal **2.5–10× longer than humans**. The behavioural
  prior for us: our model will not drop a belief on one disconfirmation, so the mechanism must not rely on it.
- **Recency versus relevance** (Anderson & Schooler 1991, **[U]**): the decay curve is supposed to *be* an
  estimate of the odds that an item is needed again. Every system in §2.1 uses a constant instead, which is
  the formal reason decay cannot represent a scheduled return.

**Can an item come back?** JTMS: **yes, natively, and for the right reason** (support returned).
AGM: yes, by an axiom, with no time. Latent cause: **yes, and it predicts *when***.
**Tested under a revert?** In cognitive science, the revert *is* the experiment (renewal, spontaneous recovery).
In any LLM implementation: **there is no implementation.**
**Frozen local 27B?** A JTMS is bookkeeping — cheap, no calls, and it needs only that each written belief
records which observation ids justified it. A latent-cause/regime posterior is arithmetic over a small
hypothesis set.

### 2.8 Verification against the world — the mechanism only a robot has

**Signal:** a new observation deliberately collected to test a stored item.

- **In agent memory, once.** Environment-probing curation (2609.11060, 1 cite *(via SURVEY2)*): an
  asynchronous curator with **read-only world tools** that *"check, scope and refresh"* candidate memories
  before writing or retiring them; **CLBench pass rate 39% → 73%**, pass-discounted reward 8.60 → 22.60,
  queries 8.8 → 4.7, cost $3.38 → $1.68, **no retraining**, task agent and retriever unchanged.
- **In robotics, properly, and with restoration.** These three are the most directly relevant works in this
  entire review and neither prior survey cites them.
  - **The Persistence Filter** (Rosen, Mason & Leonard, *"Towards lifelong feature-based mapping in
    semi-static environments"*, ICRA 2016; **89 cites**). Read in the PDF today. The model is
    `X_t | T = 1 for t ≤ T, 0 for t > T` with a **prior `p_T(·)` over the survival time T**, and a detector
    model over two Booleans with exactly two free parameters — **missed detection `P_M = p(Y=0|X=1)`** and
    **false alarm `P_F = p(Y=1|X=0)`**. Verbatim: *"Since P_M and P_F are innate characteristics of the
    feature detector, the only freedom in the design of the model is in the selection of the survival time
    prior p_T(·)"*, which is designed through its **hazard function**; §V gives three routes, including
    **class-conditional learning of hazard rates from a training corpus** and a "general-purpose" prior with
    bounded rate. The filter computes `p(X_t = 1 | Y_1:N)` in **closed form with exact, constant-time online
    inference**, for `t` in the present *and the future*. Evaluated on 100 observation sequences from its own
    generative model under varying `(P_M, P_F)` and revisitation rate, by mean L1 error and by feature-removal
    precision/recall, against an empirical (frequency-count) estimator, which both filter variants
    *"significantly outperform… in precision and recall for feature removal decisions"*.
    **The important limitation, which I had to correct against the PDF: the model is one-way.** Absence is
    evidence rather than a verdict, so a positive detection after a run of negatives does raise the posterior —
    but `X_t` is monotone in `T`, so a feature that has genuinely gone and come back is **outside the model**.
    That is precisely the hole Perpetua fills.
  - **Perpetua** (Saavedra-Ruiz, Nashed, Gauthier & Paull, arXiv 2507.18808, Jul 2025; **[cites U]**). The
    decisive paper for our question. Verbatim: *"we chain together mixtures of 'persistence' and 'emergence'
    filters to model the probability that features will disappear **or reappear** in a formal Bayesian
    framework"*, giving predictions *"both in the present as well as at arbitrary future times"*. An emergence
    filter is the mirror of a persistence filter (`X_t = 0` for `t ≤ T^E`, `1` after), and a state machine
    switches between them at thresholds δ_low = 0.05 / δ_high = 0.95, refreshing mixture weights on re-entry
    with ε = 0.1 to avoid mode collapse. Parameters by **offline EM**; **online updates are closed-form and
    constant-time** (0.058 s/iteration to *train* a mixture on 12,500 points). Simulated room, where landmarks
    have **up to three appearance/disappearance times**: MAE **0.010 ± 0.001** vs 0.110 for the best
    persistence-filter baseline, balanced accuracy **0.738** vs 0.614, F1 **0.983** vs 0.806; parking-lot
    UFPR04 over 30+ days: MAE 0.201 vs 0.208, balanced accuracy 0.823 vs 0.813. Baselines include **FreMEn**
    and ARMA. **This is the only mechanism in this review that is (i) explicitly about a thing that goes away
    and comes back, (ii) evaluated on data where that happens repeatedly, and (iii) cheap enough to run per
    fact per day.** Its objects are binary presence, not facts, and there is no language model anywhere in it.
  - **FreMEn** (Krajník et al., *Frequency Map Enhancement*, IEEE T-RO 2017; **165 cites**). Binary
    presence/absence time series per feature → **frequency spectrum**; the dominant periodicity of the
    residual becomes a new component; the spectral model transforms back to the time domain to **predict the
    state of any feature at any future time**, at compression up to 1:100000. Reported: occupancy-grid
    prediction error **−60%** versus a static map, search time **−25%**. (Verified via Vintr et al.,
    *Frontiers in Robotics and AI* 2022, which also benchmarks the family for pedestrian flows; **[U] on the
    T-RO text itself.**) **FreMEn is the only mechanism anywhere that predicts the *time at which a state
    returns*** — which is what a ten-day sick leave with a known weekly rhythm would need.

**Can an item come back?** **Yes — in all three, and for the right reason.**
**Tested under a revert?** **Yes: Perpetua and FreMEn, in robotics, on presence data, with no LLM.** The
env-probing curator: **no.**
**Frozen local 27B?** Entirely — these are filters, not models. The LLM's only job would be supplying the
prior class per fact (the CoCo-TAMP division of labour: *the LLM supplies the prior, arithmetic does the
updating*).

---

## 3. The table

Columns: **Signal** (mechanically) · **Who decides** (rule = arithmetic, model = LLM/learned) · **Effect**
(delete / downweight / archive / label) · **Come back?** · **Tested where a fact becomes false then true
again?** · **Works on a frozen local model?** · **A / B** = which staleness it addresses.

| # | mechanism (exemplars) | signal | rule or model | effect | can it come back? | tested under a revert? | frozen 27B? | A/B |
|---|---|---|---|---|---|---|---|---|
| 1 | **Time decay / recency** (ACT-R & Anderson–Schooler [U]; Generative Agents 0.995; MemoryBank Ebbinghaus; ByteRover; ZenBrain 0.25/day) | elapsed time since write or last retrieval | rule | downweight; delete at threshold | only by re-write or re-retrieval | **NO** | yes, 0 calls | A (misapplied to B) |
| 1b | **Decay with advertised reactivation** (Oblivion, 5a 2026) | same + reinforcement/context cues | rule + a model call to gate memory use | downweight, *explicitly not deletion* | **yes — but on a cue, not on truth** | **NO** | yes | A |
| 1c | **Decay constant tied to the process** (Chronofy, 4a 2026, unrefereed) | exponential decay with β ≈ 2× mean-reversion rate [U if fitted] | rule | downweight + confidence cap | no | **NO** | yes | A |
| 2 | **Validity intervals / bitemporal** (Zep 4 timestamps; MemStrata; TOKI; Engram 1a; MemOS TTL; Wikidata ranks + start/end; SQL:2011 [U]) | stored `valid_to` vs question time | comparison is a rule; **setting `valid_to` is an LLM call** (Zep) or a key rule (MemStrata) | close interval, **keep the row**; MemOS archives/expires | **representable — a new interval with the old value**; nothing re-opens a closed one | **NO** (MemStrata says so in its own future work) | yes for the rules; Zep's LLM step breaks on small models | A |
| 2b | **Forward expiry prediction** (Zhang & Choi EMNLP 2023 **26 cites**; Wenzel & Jatowt ACL-F 2024; Chronocept 5a; MCTACO; Takemura 2012 [U]; Almquist & Jatowt 2019 [U]) | text of the fact → predicted duration / skew-normal validity density | **finetuned encoder** (BERT, SelfExplain, FFNN); discard by **threshold rule** | label volatile / discard from the prompt | no | **NO — and recurrence is named as out of scope twice, verbatim** | the predictor is a small encoder we can host; not a 27B prompt | A |
| 3 | **Keyed supersession** (TEPA 0 LLM calls; MemStrata; last-write-wins) | a newer item with the same key | rule | replace current value, ledger the old | **yes, automatically, on re-observation** | **YES — TEPA only** (`{stable, light, reversal, return}`; reversal 0.950 vs 0.210) | yes, 0 calls | A |
| 3b | **LLM contradiction adjudication** (Zep; Mem0 ADD/UPDATE/DELETE; CUPMem KEEP/STALE/REPLACE; TARL 5 actions + 3 ledgers) | LLM judgement on a candidate pair | model | delete (Mem0), close-and-keep (Zep), label (CUPMem), ledger (TARL) | Mem0 no; the others yes in principle | **NO** (STALE names "one-shot" transitions in its limitations) | yes, with poor small-model recall; **TARL needs training** | A |
| 3c | **NLI / entailment** (ConCoRD; BeliefBank; REFLEX; DeBERTa-MNLI as a cheap detector) | entailment/contradiction label between two statements | small trained model | feeds a solver; nothing retired | n/a | **NO — synchronic consistency only** | yes, ~400M encoder, 0 LLM calls | A |
| 3d | **Propagation into derived text** (CUPMem dependents; ReTree 6a; EvoGraph-Mem 2a) | an invalidated fact that a summary was built from | model | regenerate the summary; archive the insight | **[U] — neither says whether an archived insight returns** | **NO** | likely yes [U] | **B** |
| 4 | **Drift detectors on an outcome stream** (ADWIN; DDM; Page-Hinkley; BOCPD 923 cites; RCD; Shaker & Hüllermeier recovery) | the system's own error rate / run-length posterior | rule (arithmetic) | signals a regime change; **RCD stores and re-activates the retired model** | **yes — RCD by design** | **YES in stream mining; never coupled to an LLM** (confirmed by a second independent sweep today) | yes, 0 calls | A + **B** |
| 4b | **Surprise inside agent memory** (Nous 1a: categorical posteriors + info-theoretic surprise + entropy forgetting + provenance caps) | KL/surprise of an observation under the current posterior | rule (closed-form Bayes) | downweight / forget by entropy | not addressed | **NO** | yes | A (+B in principle) |
| 5 | **Usage / utility / eviction** (Generative Agents importance; MemoryOS heat; ExpeL counters; HypoGeniC accuracy+UCB; SF-AMS; CAMeR; FSFM taxonomy; LANTERN 1a; CausalCache) | access count, recency of use, reward, LLM importance score | rule, with an LLM-written score in some | evict, downweight, archive-and-restore-on-demand | **yes — but restoration is triggered by predicted usefulness, never by truth** | **NO** | yes; the importance score costs 1 call/item | A + **B** (ExpeL/HypoGeniC are the only belief-level ones) |
| 5b | **Learned forget policy** (MemCon 14a: MDP + tabular UCB bandit, binary task feedback, *no extra LLM calls*) | task success/failure | **learned policy, no LLM call** | consolidate / forget | not addressed | **NO** | **yes — learning lives in the bandit, not the LLM** | A + B |
| 6 | **Provenance / source reliability** (truth discovery [U]; Knowledge-Based Trust VLDB 2015; typed provenance 2a; Nous caps; budgeted verification 1a) | who said it, how it was obtained, how often that source is right | learned model (KBT) or rule (typed policy) | **label / re-rank**, not delete | **nothing is retired, so nothing needs restoring** | **NO** | yes | A + **B** |
| 7 | **Belief revision formalisms** (AGM 1985 + Recovery; **Katsuno–Mendelzon update**; **JTMS IN/OUT** [U]; latent-cause inference) | logical support: does a justification still hold / which latent cause is active | rule (bookkeeping or a small posterior) | **JTMS: label OUT, keep the justification** | **YES — natively, when support returns; latent cause even predicts when** | **YES in cognitive science (renewal, spontaneous recovery); no LLM implementation exists at all** | yes — bookkeeping, 0 calls | **B** |
| 8 | **Go and look** (env-probing curator 2609.11060; **Persistence Filter** ICRA 2016 (89 cites); **Perpetua** 2025; **FreMEn** T-RO 2017, 165 cites) | a new observation collected on purpose; missed detections as evidence (`P_M`) | rule (closed-form Bayes / spectral fit); curator version is a model | refresh, retire, or predict presence at a future time | **YES — Perpetua's emergence filters model reappearance and FreMEn predicts *when*; the plain Persistence Filter is one-way (absence is evidence, but a genuine return is outside its model)** | **YES — Perpetua (≤3 appear/disappear cycles per landmark; 30-day parking lot) and FreMEn; robotics only, no LLM. Curator: NO** | **yes — the filters are arithmetic; the LLM only supplies the prior** | A (B by extension, untried) |

---

## 4. The three things you asked me to chase

### 4.1 Predicting how long a fact stays true

**It exists, it is small-model NLP, and it forbids our case in writing.** §2.2b has the table. The
state of the art: **Zhang & Choi (EMNLP 2023, 26 cites)** predict a fact's duration with a finetuned BERT and
cut expected calibration error by 50–60%; **Wenzel & Jatowt (Findings of ACL 2024)** predict whether a
follow-up statement *changes* a duration (88.5% with a finetuned model, **66.3% for ChatGPT**);
**Chronocept (5-author preprint, 2025)** models validity as a skew-normal density over log time. Two of the
three say, in their own limitations, that periodic or recurring validity is out of scope, and the third has a
*Recurrent* annotation axis it cannot express in its output. **Nobody predicts the time at which a fact
becomes true again, and nobody has put a predicted duration into an agent's memory and measured what happens.**
For us the practical reading is: a volatility class per fact type ("location of a bag" = hours; "which desk is
Yuki's" = months) is cheap and buys calibration, and it is the *only* thing this literature can give us.

### 4.2 Does anything distinguish "this belief is wrong" from "this belief is suspended and may return"?

**Yes — in four places, none of them LLM memory, and the distinction is sharp in all four.**

1. **Bitemporal databases.** A world change is a new **valid-time** interval; an error is a new
   **transaction-time** version of the same valid-time fact. Same schema, different operation. Thirty years
   old. **[U on primary refs.]**
2. **Katsuno–Mendelzon *update* vs AGM *revision*** (verified via SEP): "the world changed" vs "we were
   wrong", with time-indexed sentences for the former. Our setting is *update*; every LLM paper that reaches
   for a belief-revision citation reaches for AGM *revision*.
3. **Truth maintenance IN/OUT** (Doyle 1979 **[U]**): a belief goes **OUT** when its justification lapses,
   **keeps its justification**, and comes back **IN** unchanged when support returns. A belief that is *wrong*
   instead has its justification deleted. Two different operations, two different futures.
4. **Latent-cause inference** (Gershman/Niv): suspension = inferring a **second latent cause**, not
   downweighting the first; the first is intact and is restored when the posterior returns to it. This is the
   only theory in which "and later it comes back" is the phenomenon being explained rather than an unhandled
   case.

**In LLM memory the distinction exists only as unused schema capacity.** Zep's `valid_to` (stopped being
true) versus `expired_at` (we retract the assertion) is the one place the two are separately representable;
TOKI's bitemporal algebra is another; neither has an evaluation that uses it. Everything else has a single
binary: current, or not.

### 4.3 Does any agent memory system archive rather than delete, and re-promote when the world reverts?

**Archive: several. Re-promote on reversion: none.** Sorted by how close they get:

| system | archives? | can an item come back? | on what trigger |
|---|---|---|---|
| **Zep / Graphiti** | yes — closes `valid_to`, keeps the edge | only as a *new* edge | a fresh contradicting observation, LLM-adjudicated |
| **MemOS** | yes — `archived` and `expired` lifecycle states + version chain | **[U]** — no re-promotion reported | — |
| **Engram** (1a) | yes — *"invalidating, never deleting… provenance and a supersession chain"* | not addressed | — |
| **A-TMA** | yes — deliberately keeps superseded and transition records | it is *labelled* `historical` at read time, not restored | — |
| **ChronoMem** | yes — whole-memory snapshots, semantic rollback | **yes, but the rollback is *requested by a user*** — the oracle version of what we want | a natural-language "undo" |
| **TARL** (5a) | yes — accepted / pending / rejected ledgers | design implies it; **[U]**, and the policy is trained | — |
| **EvoGraph-Mem** (2a) | yes — archives invalid insights, with positive/negative evidence and activation states | **[U]** | — |
| **LANTERN** (1a) / **CausalCache** (4a) | yes — archive every turn / every event | **yes**, and this is real restoration machinery | **predicted usefulness to the current query**, never truth |
| **Oblivion** (5a) | not archival — accessibility decay | **yes, by reinforcement or a contextual cue** | a cue, not evidence |
| **RCD / recurring-concept pools** (stream mining) | yes — stores the retired *model* | **yes, re-activated when the old state returns** | a drift detector recognising a known concept |
| **Persistence Filter** (robotics) | n/a — maintains a posterior | belief rises again on a positive detection, but the survival model is **one-way**: a genuine return is outside it | a later positive detection |
| **Perpetua** (robotics) | n/a — mixture of persistence **and emergence** filters | **yes — reappearance is modelled explicitly and predicted at arbitrary future times** | posterior crossing δ_high; the state machine switches back to a persistence model |

The two rows that actually do what we want are in **stream mining** and **robotics**. The LLM rows either
restore on demand (LANTERN, CausalCache), on a cue (Oblivion), or on a human request (ChronoMem).

---

## 5. What is missing

1. **Nothing decides that a self-written generalisation has expired using the evidence that produced it.**
   Beliefs in agent memory are retired by usage statistics (which rise when a belief is wrong-but-used), by a
   fresh LLM opinion, or not at all. The evidence-tracking answer is a JTMS and it is 47 years old and
   unimplemented here.
2. **No expiry mechanism has a two-sided model.** Every mechanism predicts "when does this stop being true".
   Only **emergence filters** (Perpetua) and **spectral models** (FreMEn) predict "when does this start being
   true again", and both live outside language entirely.
3. **No drift detector has ever been attached to an LLM agent's own outcome stream.** Confirmed today by a
   second independent sweep: the only LLM-side drift work is persona drift and prompt-injection monitoring.
   The stream-mining literature has the detector, the recurring-concept pool *and* the recovery-measurement
   protocol; the LLM literature has imported none of the three.
4. **Expiry prediction is never in a loop.** Fact-duration and temporal-validity models are evaluated as
   standalone classifiers. No paper predicts a TTL, writes it into a store, and measures downstream QA.
5. **Restoration is never evaluated because no benchmark reverts** — the corrected gap statement in
   *SURVEY2* §5.1b stands, and this pass adds five more negatives to it (Oblivion, Engram, Chronofy,
   MedCache, MemCon), plus two literatures where restoration *is* measured and no language model is present
   (Perpetua/FreMEn; RCD/recovery analysis).
6. **"Suspended" has no representation in any LLM memory schema that is exercised.** Zep and TOKI can express
   it; nothing tests it; nothing predicts a suspension's end.

---

## 6. What to implement, for a robot that can go and look

**(i) A per-fact persistence/emergence filter over the patrol stream, with the LLM only supplying the prior.**
Rosen et al.'s persistence filter plus **Perpetua's emergence half, which is the part that matters for us —
the plain persistence filter's survival model is one-way**: each `(object, location)` claim carries a
Bayesian posterior that it currently holds, updated in closed form from every patrol observation *including
non-observations* (via P_M), and the prompt shows only claims above a threshold, with the posterior printed.
Cost: arithmetic; the 27B is asked once per fact *type* for a volatility class (§4.1's one usable output) to
set the survival prior. **Restoration is native**: the day Yuki's bag reappears on the desk, the emergence
filter's posterior crosses δ_high and the claim returns without anything having to remember it was once true.
**Tested under a revert? Yes — in robotics, on binary presence, with no language model. Never on facts, never
in a prompt.**

**(ii) Keyed supersession with the old value kept, dated, and labelled at read time.** TEPA's keys
(the largest reversal-phase effect in the literature, with zero LLM calls) plus A-TMA's
`current` / `historical` / `transition` labels and CUPMem's constrained readout. Key on
`(object, time-slot)`, not `(object, location)`, for the reason already given in *SURVEY.md*.
**Tested under a revert? Yes — TEPA, and only TEPA, and with no LLM in the loop; the read-time labelling half
has never been tested under a revert at all.**

**(iii) Justification sets on every written belief — a JTMS in one file.** Each routine card records the
observation ids that justified it. When those observations are superseded, the card goes **OUT**: kept,
dated, not shown, with its justification list intact. When new observations re-satisfy the justification
pattern, it comes back **IN** unchanged. This is the only mechanism in this review that gives (B) what §2
gives (A), it costs nothing at runtime, and **it has never been built with a language model, anywhere, let
alone tested under a change that reverts.**

**A fourth, cheap and adjacent:** put a **drift detector (ADWIN or BOCPD) on our own correctness stream** and
use it to gate whether the routine card is shown at all. It is arithmetic over a signal we already log, the
recovery-measurement protocol for it has existed since 2014, and *nobody has ever coupled one to an LLM
agent's outcomes*. That is the cheapest unoccupied ground in this review.

**Plainly, on the revert question:**
- **Never tested under a revert:** time decay in all its forms (including Oblivion's reactivation and
  Chronofy's mean-reversion decay), all validity-interval stores (Zep, MemStrata, TOKI, Engram, MemOS),
  forward expiry prediction (which excludes recurrence by construction), LLM contradiction adjudication
  (Mem0, CUPMem, TARL), NLI consistency, propagation into derived summaries (ReTree, EvoGraph-Mem), every
  usage/utility/eviction scheme, learned forget policies (MemCon), provenance labelling, and the
  environment-probing curator.
- **Tested under a revert, outside language:** persistence + **emergence** filters (Perpetua), spectral
  periodicity models (FreMEn), recurring-concept model pools (RCD, Katakis) with Shaker & Hüllermeier's
  recovery protocol, and — in cognitive science, as the phenomenon itself — latent-cause inference.
- **Tested under a revert, inside the LLM-memory literature:** **TEPA, one unrefereed preprint, whose memory
  is a deterministic keyed table with no language model in it.**

---

## 7. Loose ends worth one fetch each before this is cited in a paper

- Semantic Scholar was rate-limited all session: **every citation count marked [cites U] needs one lookup**,
  and the counts attributed *(S2 via SURVEY2)* should be re-confirmed if they carry weight in the write-up.
- **Persistence Filter** experimental numbers and per-update cost (PDF tables did not extract).
- **Chronofy** β_j: derived analytically or fitted from data.
- **EvoGraph-Mem** and **ReTree**: whether detection is an LLM call or a rule, and whether an archived insight
  can be re-promoted. These are the only two (B)-side propagation mechanisms and both are abstract-level here.
- **MedCache**: how the validity window is assigned and what happens at expiry.
- **TARL**: numbers, backbones, and whether the rejected ledger is ever read back.
- **MemOS**: whether an `archived` unit can return to `activated`.
- **Doyle 1979 / de Kleer 1986**: primary text for the IN/OUT restoration claim, which recommendation (iii)
  leans on hardest. (The valid-vs-transaction-time claim is now verified in Kulkarni & Michels 2012, and the
  latent-cause claim in Gershman, Blei & Niv 2010; both were [U] earlier in the day.)
- **Behrens et al. 2007** and **Anderson & Schooler 1991**: the two "the constant can be learned" citations,
  both paywalled this pass.
- **CyGNet** (AAAI 2021, **390 cites**) and **Gastinger et al.** (IJCAI 2024): the temporal-KG-forecasting line explicitly
  exploits *recurring* facts — CyGNet's copy mechanism predicts *"facts with repetition"*, and the IJCAI 2024
  recurrency baseline *"ranks first or third in three of five datasets"* against 11 methods. Both verified at
  abstract level today; **neither reports the fraction of facts that recur**, which is the number we would
  want. If a reviewer asks whether anyone models returning facts, this is the literature to cite — it is
  entity-relation link prediction, not memory, and no language model is involved.
