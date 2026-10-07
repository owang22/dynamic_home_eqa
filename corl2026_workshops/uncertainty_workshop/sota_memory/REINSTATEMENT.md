# REINSTATEMENT: what brings a suspended item back, and on what signal?

Written 2026-09-23/24 by a research agent, as a fourth layer on `SURVEY.md`, `SURVEY2.md` and `EXPIRY.md`.
Those three cover **how an item leaves**. This one covers **how an item comes back**, because `EXPIRY.md` §4.3
concluded that language-model memory can archive but "cannot re-promote", and that conclusion is partly wrong.

**Scope.** Systems where a small in-context working set sits in front of a larger store; ACT-R-style activation
in agents; forgetting curves with reactivation; summarisation hierarchies where detail survives the summary;
and retrieval conditioned on an inferred situation rather than on the text of the query. No experiments were
run and no other directory was touched.

## Conventions

- **[U]** = not verified in a primary source this pass. Everything else was read today in the arXiv HTML
  (`arxiv.org/html/…`), the publisher HTML, or the vendor's own live documentation.
- **Citation counts.** Semantic Scholar returned HTTP 429 to every request (including the batch endpoint) for
  most of the session, then cleared; a slow retry loop eventually got **every load-bearing count**, all
  verified by me on 2026-09-23/24 and listed in §12. OpenAlex was tried and discarded: it reports MemGPT at 56
  against Semantic Scholar's 1362, i.e. it undercounts arXiv preprints by ~20×. Counts marked *(S2 via
  SURVEY.md, same date)* are the sibling survey's pull of 2026-09-23, reused rather than re-fetched.
  **[cites U]** marks the few I never got and which must not be quoted.
- **Venue caution.** Semantic Scholar assigns a venue to some 2026 arXiv preprints that the preprint itself
  does not claim (it lists SYNAPSE and HeLa-Mem under "Annual Meeting of the ACL"). Where the paper's own
  arXiv comment says "Preprint" or gives no venue, I treat it as unrefereed regardless of the S2 venue field
  and say so.
- **WebSearch was unavailable** (session budget 200/200 exhausted before I started). All discovery was done
  through the arXiv API (`export.arxiv.org/api/query`, which searches title/abstract/author/comment fields,
  **not** full text) plus targeted fetches. Where I report "zero hits", that means zero in arXiv *metadata*,
  which is a weaker statement than zero in the literature. Both such claims below are flagged.
- **Preprint hygiene.** Author counts are given for every 2026 preprint. **1a = single author.** No headline
  number from an unrefereed preprint is stated as established fact. Three of the load-bearing finds in this
  document (RaMem, TEPA, QUMem) are unrefereed 2026 preprints and are labelled as such every time they appear.

---

## 0. The verdict in six sentences

1. **The archival half of the EXPIRY claim is wrong as stated.** Letta's own documentation says all state —
   memories, user messages, reasoning, tool calls — "are all persisted in a database, so they are **never
   lost, even once evicted**", and archival memory is "**Agent-immutable** — agents cannot easily modify or
   delete archival memories". In the MemGPT/Letta line nothing about the past is destroyed, so there is no
   representational barrier to an item returning.
2. **The re-promotion half is right about almost everything and wrong about one paper.** Across tiered memory,
   activation decay, forgetting curves and summary hierarchies, every return path is triggered by the current
   query, by the agent choosing to issue a search, by a cue, by predicted usefulness, or by a human asking —
   never by evidence that the world went back.
3. **The exception is TEPA** (arXiv 2608.07429, 4 authors, Aug 2026, unrefereed): precedents carry lifecycle
   states {Hypothesis, Active, Revoked}, retrieval is conditioned on `σ = Active` rather than on similarity,
   revocation fires when a precedent's **recent success rate falls below θ_rec = 0.34**, and promotion fires
   when accumulated same-key evidence clears θ_pro = 0.6 or passes trial-by-execution. That is re-promotion on
   an outcome statistic — a world signal — and its drift suite has an explicit `return` phase.
4. **The narrower claim under test is nearly right but needs one correction.** 2026 systems do carry a
   "situation" variable now, but it is derived from the query: the one system in the literature actually named
   for our mechanism, **RaMem — "Contextual Reinstatement for Long-term Agentic Memory"** (2606.22844, 8
   authors), induces a "recall frame" *from the query*, uses it only "when the relevant cues can be grounded
   reliably", and **explicitly falls back to plain content retrieval otherwise**. For "where is the mug?",
   asked identically on every day, there is nothing to ground, so RaMem degrades to similarity by design.
5. **What is genuinely missing is not reversibility but a trigger**: no language-model memory system computes,
   from the observation stream, a belief about *which period's evidence is currently in force*, and uses that
   belief to select what to read. The nearest things are TEPA's per-key success rate (outcome feedback
   required), Oblivion's uncertainty gate (decides *whether* to retrieve, not *which era* to trust), and
   EM-LLM's contiguity buffer (pulls in temporal neighbours of whatever similarity already found).
6. **One caveat cuts against our own premise**: retrieval memory is only reversible if the store is unbounded.
   A restore-counterfactual audit of eviction (2609.08279, **1 author**, Sep 2026, **0 cites**, unrefereed) reports that at
   an 80k-token budget **0.60–0.73** of corrected errors were *irreversible* (the evidence was gone, not
   merely unretrieved) and at 8k tokens **1.00** for all four eviction policies tested. Under a budget, things
   really are destroyed.

---

## 1. The two claims, restated so they can be scored

**(C1) EXPIRY's claim.** *LLM memory systems can archive an item but cannot re-promote it because the world
reverted.*

**(C2) The narrower claim.** *These systems re-promote a stored item when the current query resembles it, not
when evidence indicates the world has returned to an earlier state.*

For our setting the query is a constant — "where is the mug?" — before, during and after the disruption. So a
system satisfies C2's escape clause only if **something other than the query text** can change what it reads
between day 9 and day 11. Three candidate non-query signals exist in principle:

- **(a) the clock / a timestamp** — a temporal filter or recency term;
- **(b) the agent's own internal state** — uncertainty, insufficiency, surprise;
- **(c) an outcome or observation statistic per stored item** — support/conflict counts, success rate, presence.

(a) is everywhere and is the wrong shape: a monotone recency term fades the pre-shift routine during the
suspension and cannot distinguish "suspended" from "superseded". (b) exists and gates *whether* to retrieve.
(c) exists in exactly one language-agent memory system, TEPA, and (outside language) in the robotics filters
already covered in `EXPIRY.md` §2.8.

---

## 2. Tiered and paged memory: what decides eviction, what decides recall

### 2.1 MemGPT — verified against the paper, and the mechanism is a token-pressure FIFO plus a tool call

(Packer, Fang, Patil, Lin, Wooders, Gonzalez; arXiv 2310.08560; **1362 cites** (verified today); 25k stars.)

Verbatim on eviction: main context is split into system instructions, conversational context and working
context, and "conversational context is read-only with a **special eviction policy (if the queue reaches a
certain size, a portion of the front is truncated or compressed via recursive summarization)**". So **what
moves an item out of context is its position in a FIFO plus a token count.** Nothing semantic, nothing about
truth. The paper also warns that "recursive summarization is inherently lossy and eventually leads to large
holes in the memory of the system".

Verbatim on recall: "**Memory edits and retrieval are entirely self-directed**: MemGPT autonomously updates
and searches through its own memory based on the current context." External context is split into **recall
storage** ("the entire history of events processed by the LLM processor, in essence the full uncompressed
queue") and **archival storage**; the paper provides three query modes — "**timestamp-based search,
text-based search, and embedding-based search**". Retrieval happens only when the model emits a function call,
and the paper notes the failure mode: "MemGPT will often stop paging through retriever results before
exhausting the retriever database."

Two details matter for C2. First, **the retrieval key need not be semantic**: timestamp-based search means an
agent that decided to look at days 1–10 could retrieve them, so the *mechanism* admits a non-similarity key.
Second, **nothing decides to use it.** The only non-user events that can wake the processor are "system
messages (e.g. main context capacity warnings)" and "timed events that are run on a regular schedule (allowing
MemGPT to run 'unprompted')". A clock can wake it; nothing tells it the world changed. Figure 4 shows the
destructive edit: `working_context.replace('I watch horror movies.','I like romantic comedies.')` — an
overwrite in context, while the raw event stays in recall storage.

### 2.2 Letta, the product — the documentation and the paper disagree, in our favour

Read live at `docs.letta.com` today.

- **"In Letta, all state, includes memories, user messages, reasoning, tool calls, are all persisted in a
  database, so they are never lost, even once evicted."** This is the strongest statement anywhere that the
  archive is complete.
- **Archival memory:** "a semantically searchable database… **cannot be pinned to the context window, and must
  be queried on-demand via tools**"; key characteristics include "**Agent-immutable** — Agents cannot easily
  modify or delete archival memories (though developers can via SDK)", "Unlimited storage", "**Semantic search
  — Find information by meaning, not exact keywords**", and tag-based organisation. Agent tools are
  `archival_memory_insert` and `archival_memory_search(query, tags, page)`.
- **Memory blocks (core memory):** "always visible — no retrieval needed", edited with `memory_rethink`,
  `memory_replace`, `memory_insert`. Size limits per the context-hierarchy page: blocks ~<50k chars and <20 per
  agent, archival passages **300 tokens**, unlimited count.
- **Disagreement with the paper.** MemGPT §2.2 describes archival storage as "a general **read-write**
  datastore that the agent can utilize as overflow for the in-context read-write core memory". The shipping
  documentation says the opposite: archival is agent-immutable and cannot be pinned into context. **So in the
  product the destructive operation exists only on core memory, and the archive is append-only.** That is good
  news for reversibility and bad news for re-promotion: there is no operation that moves an archival passage
  back into a memory block. The agent must search, read the result in a transient tool response, and then
  choose to write it into a block itself.

### 2.3 Background consolidation: triggered by step count and token pressure, never by the world

- **Letta "dreaming"** (live docs): "Dreaming uses background subagents to review recent conversations,
  consolidate useful lessons, and update memory without interrupting your active work… Choose when it runs:
  **after a set number of completed agent steps or when the context window is compacted.**" The two available
  triggers are a step counter and a compaction event. There is also `/doctor` to "audit placement,
  duplication, and system-prompt token usage" and an agent-invoked reorganisation that "backs up the current
  repository before splitting large files, merging duplicates, or restructuring the hierarchy" — i.e. memory is
  git-backed (MemFS), so old versions survive, and rollback is a human or agent action.
- **Sleep-time compute** (Lin, Snell, Yu Wang, Packer, Wooders, Stoica, Gonzalez; arXiv 2504.13171, 7 authors; **42 cites**). This is the paper usually cited for "Letta thinks between turns", and
  it is **not a memory-tiering paper at all**: it prompts the model to rewrite a context `c` into `c′` offline,
  `S(c) → c′`, and then answers with a smaller test-time budget. Datasets are Stateful GSM-Symbolic and
  Stateful AIME plus a software-engineering case study. Results: ~5× less test-time compute for equal accuracy,
  +13%/+18% by scaling sleep-time compute, 2.5× cheaper per query when amortised across queries about the same
  context. **The finding that bears on us is its own analysis: "sleep-time compute is more effective in
  settings where the query is more easily predictable from the context."** The offline work is *query
  anticipation*. Nothing in it reasons about a stored claim ceasing or resuming to be true, and no fact changes
  anywhere in the evaluation.

### 2.4 MemoryOS — a three-tier store whose movement is strictly one-way

(Kang et al.; arXiv 2506.06326; EMNLP 2025; **119 cites** *(S2 via SURVEY.md)*.) Verified in the HTML:
STM→MTM is "dialogue-chain-based FIFO"; MTM→LPM is heat-based with
`Heat = α·N_visit + β·L_interaction + γ·R_recency`, where `N_visit` is **the number of times the segment has
been retrieved**, `L_interaction` the number of dialogue pages, and `R_recency = exp(−Δt/μ)` with μ = 1e7 s.
"Segments with heat exceeding a threshold τ (i.e. 5) are transferred to LPM"; and "when the length of segments
exceeds the maximum capacity, **segments with the lowest heat are evicted**". Retrieval within MTM is two-tier
semantic: segment first, then pages. **So: up on retrieval count, out on low retrieval count, and no path
back.** An item that is right, unused for ten days, and right again is exactly the item this design discards.

### 2.5 Oblivion — the only agent memory that advertises reactivation, verified at the equation

(Rana, Hung, Sun, Kunkel, Lawrence; arXiv 2604.00131, 5 authors, Mar 2026 rev. Sep 2026; **3 cites** *(via
EXPIRY.md, verified there)*.) `EXPIRY.md` §2.1 read the abstract; I read the method.

- Working memory = recent-turn window + a buffer holding L1 cluster nodes permanently while "dynamically
  loading and evicting L2/L3 items retrieved from 𝒟".
- **Read path is gated by the agent's own uncertainty, not by similarity**: a Decayer estimates
  `u_t(c) ∈ [0,1]` per cluster from an **LLM-as-a-judge** verdict on whether the cluster provides sufficient
  evidence for `q_t`, plus a second signal; "Activation is always triggered when B_t contains no L2/L3 items.
  Otherwise… in the first round, either signal alone suffices (OR); in subsequent rounds, both must agree
  (AND)." **This is a genuine non-query trigger for *whether* to retrieve** — and it says nothing about which
  era of evidence to trust.
- Retention: `R_t(c)` is an interaction-based forgetting curve over `n_t(c)` = **turns since last access**, a
  utility proxy and an access-frequency proxy, with a decay temperature `T`.
- The reactivation sentence, verbatim: neglected clusters become "less prominent in retrieval ranking and more
  likely to be evicted during curation — **yet never deleted from 𝒟, preserving reactivatability when future
  interactions reinforce them**." So **reactivation means future access, not returned truth.**
- Oblivion also names our problem and forecloses it: footnote 2 defines "**world drift**" as "temporal
  inconsistency in stored facts as the world or user state changes over time", and its remedy is that
  "timestamps allow the system to resolve temporal conflicts by **prioritizing currently valid facts over
  outdated ones** during curation" — forward-only. Evaluated on LongMemEval and GoodAI LTM; no fact reverts.

### 2.6 Others in this family, one line each

- **Organize then Retrieve** (Hsu, Kuang, Liu et al.; arXiv 2606.11680, 5 authors, Jun 2026; **2 cites**):
  hierarchical navigation for working memory; retrieval is query-driven navigation.
- **CausalCache** (2608.22577, 4 authors) and **LANTERN** (1a): archive everything, restore on **predicted
  usefulness to the current query** — already the right row in `EXPIRY.md` §4.3, and I add nothing.
- **AutoMEM / DCI-Lite** (2606.04315) has a judge that assesses sufficiency and re-queries — a second instance
  of the Oblivion-style internal-state trigger for *whether* to look again. See `SURVEY2.md` §4.2 for its
  numbers, including that it never reports its own conflict-resolution score.

---

## 3. Working memory versus long-term memory, and where ACT-R activation actually lives

### 3.1 The canonical framework says modification and deletion are understudied

**CoALA — "Cognitive Architectures for Language Agents"** (Sumers, Yao, Narasimhan, Griffiths; arXiv
2309.02427; **TMLR** (per the v3 arXiv comment and S2); **524 cites**). Read today. It separates short-term working memory
from episodic, semantic and procedural long-term memory, defines *retrieval* as "a retrieval procedure reads
information from long-term memories into working memory", and lists implementations: Voyager's dense skill
retrieval, Generative Agents' recency+importance+relevance, DocPrompting's document lookup.

Two sentences in it are load-bearing for this review:

- Verbatim: "while our discussion has mostly focused on **adding** to memory, **modifying and deleting** (a
  case of 'unlearning') **are understudied** in recent language agents."
- And the one place it gestures at our mechanism, as future work: "learning better retrieval procedures could
  enable agents to better connect memorized information to new scenarios… (e.g., reason about '**in what
  situations would this knowledge be useful?**', and append the reasoning results to the knowledge to help
  later connect the knowledge to new situations)."

That is situation-conditioned retrieval, named as unexplored in the framework paper, and — see §6 — still
unexplored except in query-conditioned form.

### 3.2 ACT-R base-level activation has not reached LLM agent memory. It reached recommender systems.

This was the specific thing I was asked to chase, and the answer is clean.

- **arXiv metadata contains zero papers with the phrase "base-level activation"** (`all:"base-level
  activation"` → `totalResults 0`), and zero with **"ACT-R" AND "agent memory"** (→ 0). *Caveat: the arXiv API
  searches title/abstract/author/comment, not full text, so this bounds the claim rather than proving it.*
- **The only ACT-R×LLM integration on arXiv is LLM-ACTR** (Siyu Wu, Oltramari, Francis, Giles, Ritter; arXiv
  2408.09176, 5 authors, Aug 2024; [cites U]): it "extracts and embeds knowledge of ACT-R's internal
  decision-making process as latent neural representations, injects this information into **trainable LLM
  adapter layers**, and fine-tunes the LLMs". It is about manufacturing-decision grounding, requires
  fine-tuning, and contains no memory-activation retrieval.
- **Where the base-level learning (BLL) equation is actually deployed to predict that an item will be needed
  again: psychology-informed recommender systems, 2014–2021.** "Predicting Music Relistening Behavior Using the
  ACT-R Framework" (Reiter-Haas, Parada-Cabaleiro, Schedl; arXiv 2108.02138, 6 authors, 2021; [cites U]) uses **five** declarative-memory components — "base-level, spreading, partial matching, valuation,
  and noise" — on 1.7M Last.fm listening events, and finds "recency and frequency of prior exposure to tracks
  is an effective predictor of relistening behavior". The earlier line is Kowald/Lex on hashtag reuse (arXiv
  1701.01276, 1908.00977) and Lacic et al. on social tagging (1406.7727), all explicitly using "the Base-Level
  Learning (BLL) equation from the cognitive architecture ACT-R… to model how a person **reuses** hashtags".
  **This is the literature that treats "will this come back?" as the prediction target — and its predictor is
  the item's own access history, with no term for the state of the world.** Nobody has carried it into LLM
  agent memory.
- **Two 2026 preprints import the neighbouring ACT-R machinery into agent memory, both retrieval-seeded by the
  query:**
  - **SYNAPSE** (arXiv 2601.02744, **11 authors**, Jan 2026 v3; **10 cites**; no venue claimed in the paper, treat as unrefereed). Episodic-semantic
    graph; activation is injected into **anchor nodes found by BM25 (lexical) plus dense retrieval
    (semantic)**, then spreads with an ACT-R **fan effect** (`S = 0.8`, divided by out-degree), temporal edge
    weights `w_ji = e^{−ρ|τ_i − τ_j|}` with ρ = 0.01, lateral inhibition, and node garbage collection
    ("activation consistently below a dormancy threshold ε = 0.01 for W = 10 windows are **archived to disk**"
    — with no described route back). Its own ablation is the most useful sentence for us: "**Node Decay is the
    sole driver of timeline awareness. Setting δ = 0 destroys Temporal reasoning capabilities (50.1 → 14.2),
    as the model loses the ability to distinguish between current truths and obsolete facts based on activation
    energy.**" In other words the only thing separating current from obsolete is time decay — exactly the
    mechanism that cannot represent a ten-day suspension. Evaluated on LoCoMo only, which has no knowledge
    update at all (`SURVEY2.md` §5.2).
  - **HeLa-Mem** (arXiv 2604.16839, 5 authors, Apr 2026; **5 cites**; no venue claimed in the paper, treat as unrefereed): Hebbian edges strengthened by
    **co-activation**, `Δw_ij = η·x_i·x_j`, plus "Hebbian Distillation" of dense hubs into semantic memory, plus
    dual-path retrieval using spreading activation. Strengthening is a function of co-retrieval. LoCoMo only.

**Answer to the brief's question:** the activation never responds to the world changing. In every
implementation it responds to access — and in the one literature that *does* aim the equation at "needed
again", the prediction is made from access statistics too.

---

## 4. Forgetting curves with reactivation: does strengthening ever depend on being *correct*?

### 4.1 MemoryBank — verified at the equation; strengthening is on recall alone

(Zhong, Guo, Gao, Wei Ye, Zhang; arXiv 2305.10250; **AAAI 2024**; **692 cites**, verified today.)
Verbatim: `R = e^{−t/S}`, "`S` is the memory strength… To simply memory updating process, we model `S` as a
discrete value and initialize it with 1 upon its first mention in a conversation. **When a memory item is
recalled during conversations, it will persist longer in memory. We increase `S` by 1 and reset `t` to 0**,
hence forget it with a lower probability." Retrieval is dual-tower dense (DPR-style, FAISS): "the **current
context of conversation** `c` is encoded… which serves as the query to search `M` for the most relevant
memory". The authors' own hedge, verbatim: "**It is important to note that this is an exploratory and highly
simplified memory updating model.**"

So: **reinforcement is conditioned on retrieval, retrieval is conditioned on similarity to the current
context, and correctness never enters.** This is C2's mechanism in its purest published form. During a ten-day
suspension the correct-on-day-11 item is not recalled, so `S` stagnates and `t` grows.

### 4.2 CAMeR — the same design stated as a virtue, by a single author

**CAMeR: "Keyword-Gated Hybrid Activation for Adaptive Memory Retention in LLM Agents"** (Haowen Lai; arXiv
2607.20458, **1 author**, 2026; **0 cites**, verified; unrefereed). Mechanism: a hybrid score per
memory-query pair, embedding cosine (α = 0.6) plus keyword Jaccard (0.4); "**memories exceeding a threshold
receive reinforcement while all memories undergo controlled decay**". It diagnoses the field correctly —
prior methods "rely predominantly on sub-symbolic (embedding-based) similarity signals for activation
decisions" — and then fixes the *precision* of the similarity gate rather than replacing it. Its own
benchmark, CAMeR-Bench, is 76 memories × 100 rounds with a graded *activation-frequency* gradient: the
independent variable is how often a memory is queried, which is the wrong axis for us. Reported (**do not
quote as established**): a 1.6× larger retention gap than embedding-only gating (0.039 vs 0.024), and
"time-driven baselines (Oblivion, SuperLocalMemory) collapse to near-zero weights over 100 rounds".

### 4.3 Where correctness *does* gate strengthening — and whether demotion reverses

Three systems condition the weight on an outcome rather than on retrieval:

- **ExpeL** (arXiv 2308.10144, AAAI 2024, **936 cites** *(S2 via SURVEY2.md)*): LLM applies ADD/EDIT/**UPVOTE**
  /**DOWNVOTE**; importance starts at 2 and the insight is removed at 0. Reversible while alive, dead at 0,
  no changing facts.
- **RIZZ** (Goel, Vaidhyanathan, Schorling et al.; arXiv 2606.20638, 5 authors, Jun 2026; **0 cites**,
  unrefereed): procedural rules carry **helpful and harmful counters that affect retrieval score**, and "only
  verified interactions can update memory, promote reusable rules, demote harmful rules, or create
  anti-patterns", with a deterministic verifier as the gate and "rules are promoted only after repeated
  verified usefulness". **A rule demoted during a disruption can regain score after the return** — genuine
  outcome-driven, reversible weighting. Two limits: the *routing* that decides which memory branch is even
  consulted is query-driven (§6.4), and the benchmarks (StreamBench, TRACE, LongMemEval-S, τ-bench) are
  forward-only.
- **MemCon** (14 authors; see `EXPIRY.md` §2.5 row 5b): a tabular UCB bandit over binary task feedback with no
  extra LLM calls. Restoration is not addressed.
- **Spaced repetition proper is absent.** arXiv metadata search for `"spaced repetition" AND "language model"
  AND memory` returns only **LECTOR** (1a, 2508.03275), which is an LLM-enhanced spaced-repetition scheduler
  for *human* learners. **Nobody schedules an agent's own memory refresh.**

**Answer to the brief's question:** strengthening depends on correctness in exactly the systems that have an
outcome signal to condition on (ExpeL, RIZZ, MemCon, TEPA), and on retrieval alone in every
forgetting-curve system (MemoryBank, Oblivion, CAMeR, MemoryOS heat, SYNAPSE, HeLa-Mem). No forgetting-curve
system has ever been given a correctness signal.

---

## 5. Summarisation hierarchies: the detail survives; nobody rebuilds the summary because the world moved

### 5.1 RAPTOR and MemWalker — leaves are retained, and both are built once over a static corpus

- **RAPTOR** (Sarthi, Abdullah, Tuli, Khanna, Goldie, Manning; arXiv 2401.18059, 6 authors; **ICLR 2024**, verified in S2; **726 cites**). Verified: chunks of 100 tokens → SBERT embeddings → GMM clustering → LLM summaries → recurse. Both
  querying strategies score nodes by **cosine similarity to the query vector**; the chosen one is the
  **collapsed tree** ("collapses the tree into a single layer and retrieves nodes until a threshold number of
  tokens is reached"), at 2000 tokens ≈ top-20 nodes, because "by searching through all the nodes
  simultaneously, it retrieves information that is at the correct level of granularity for a given question".
  **The leaves are always in the index, so detail is reachable — by query similarity.** The paper contains no
  insertion, invalidation or re-summarisation mechanism: the tree is built once over a retrieval corpus.
- **MemWalker** ("Walking Down the Memory Maze"; Chen, Wong, Chen, Tian; arXiv 2310.05029, 4 authors; arXiv-only per S2; **155 cites**). Verified: tree of LLM summaries built query-independently ("this construction does not
  depend on the query, and can hence be computed in advance"); navigation from the root by
  `LLM(reasoning, action | summ, query)`; at each node the model picks a child **or the `revert` action to
  return to the parent** "if it chose the wrong path or the segment at hand is irrelevant". **The `revert`
  action is backtracking within one question, triggered by judged insufficiency relative to that query** — it
  is not re-promotion of a suspended item, and I flag it because the word invites confusion.

So for area 4 the answer to "can the underlying detail be reached and the summary rebuilt?" is: **reached,
yes, in both; rebuilt because the world changed, in neither — neither paper has a write path at all.**

### 5.2 The one paper that does rebuild derived text, and the one that proves nobody else does

**"Forgetting Without Restarting: Execution-State Unlearning for Stateful LLM Agents"** (Yao, Wei, Huang et
al.; arXiv 2609.04875, **8 authors**, Sep 2026; **1 cite**; unrefereed). This is the most useful paper I found
for area 4 and neither prior survey cites it.

- The negative result, stated precisely: on 280 episodes converted from LongMemEval, ToolSandbox and
  AgentDojo, "**B1 equals B0 in every cell**: deleting the persistent record changes nothing — the target
  survives in answer, summary, plan, and cache (p = 1.0 vs B0)". Source redaction still leaks through derived
  artifacts (0.84/0.94 any-leak) because "the model's own summary re-encodes the target in paraphrase". Their
  framing sentence: "**The industry has equated forgetting with un-indexing.**"
- The theory sentence that generalises to our problem: "once read, `z`'s influence propagates along the
  reachability closure into summaries, plans, and pending tool calls; local edits can remove nodes of `I(z)`
  but cannot reverse computation that has already happened — **computation cannot be edited, only replayed**."
- The mechanism: an **artifact-level provenance graph** (`memory/tool field → prompt block → model turn →
  reply/plan → tool call → observation → summary write-back`, each artifact carrying `id, type, parents,
  source_ids, token_span, turn, committed`), checkpoints, and **Provenance-Guided Selective Replay** that
  crops the KV cache to the clean prefix and regenerates the tainted suffix. Reported: indistinguishable from
  a full reset at up to 9.3× fewer recomputed tokens (133 vs 1235).
- **Why it is not our mechanism.** This is the justification-tracking machinery `EXPIRY.md` §2.7 said was
  missing (a JTMS in all but name — a provenance graph plus dependency-directed regeneration), now
  implemented. But its semantics are **AGM revision, not Katsuno–Mendelzon update**: the target is something
  that *should never have been observed* (revoked consent, a pasted secret, an indirect prompt injection), the
  trigger is "a revocation event `(z,s)`… raised by the user, the platform, or an injection detector", and the
  operation *removes* influence. There is no inverse operation that *restores* a suspended item's influence
  when its support returns, and no fact in it ever becomes true again.

---

## 6. Context-dependent retrieval — the crux

### 6.1 RaMem: the literature's own "contextual reinstatement", and its context comes from the query

**RaMem: "Contextual Reinstatement for Long-term Agentic Memory"** (Wei Yang, Bryce Kan, Shixuan Li et al.;
arXiv 2606.22844, **8 authors**, Jun 2026; **3 cites**; unrefereed; code released). This is the single most
relevant paper to our question and it is in neither prior survey.

- It names our failure mode precisely — "**context collapse**: memories lose the surrounding context needed to
  judge whether they provide valid evidence for the current query" — and separates the two notions we care
  about: "**a memory can be related to the query while still being invalid evidence for it**", calling the
  failure "evidence misidentification, where the agent retrieves information that is related to the query but
  belongs to the wrong context".
- Four stages: (i) **episodic anchoring** — each memory carries event time, mention time, session span,
  participants; (ii) **recall condition induction** — "we map each query `q` into an information need `r_q`
  and a contextual recall frame `c_q`", where "explicit anchors include named entities or dates, while implicit
  anchors arise from temporal cues, referenced events, or evolving user state"; (iii) **validity-aware
  retrieval** — temporal compatibility is **session-overlap** between a grounded query range and a memory's
  session span, with a **±5-day buffer**, ordered by content relevance and temporal proximity; (iv)
  **context-preserved synthesis** — the generator sees each memory with its episodic coordinates.
- **The decisive sentence for C2**, verbatim: "**RaMem therefore uses selective contextual reinstatement: it
  activates validity-aware retrieval only when the recall frame contains grounded evidence conditions;
  otherwise, it falls back to content-based retrieval.**" And: "If an inferred condition is wrong, enforcing
  it may exclude the correct memory and turn contextual verification into a false constraint."
- Diagnostics worth having: on the context-confusable subset, the baseline SimpleMem "ranks a context
  distractor first in **43.66%, 45.88%, and 54.14%** of examples on GPT-4.1-mini, Qwen3-8B and Qwen2.5-3B";
  RaMem lowers that D@1 to 0.3495/0.3846/0.4796. LoCoMo average F1 rises 39.06 → 51.66 (GPT-4o), 43.24 →
  54.23 (GPT-4.1-mini), 33.45 → 44.55 (Qwen3-8B), 17.98 → 24.65 (Qwen2.5-3B).
- **The result that matters most, and it is unfavourable to the reinstatement idea as a cure for staleness.**
  On LongMemEval-S (judge-based, per the SimpleMem protocol) RaMem raises the average 76.87 → 80.15, but the
  **Knowledge-Update** column reads full-context 41.03 · Mem0 69.23 · **LightMem 92.30** · SimpleMem 79.48 ·
  **RaMem 83.33** — the paper itself says RaMem is merely "competitive in Single-Session-User and
  Knowledge-Update categories **where LightMem is especially strong**", and locates its gains in
  Multi-Session, Single-Session-Assistant and Single-Session-Preference, i.e. in *identifying which episode*.
  **Contextual reinstatement buys episode identification, not supersession handling.**
- Hygiene note the paper discloses itself: for LongMemEval-S it uses "a benchmark-specific adapter… exact-match
  fallback over generated memory entries and raw-haystack fallback over salient prior messages; these
  adapter-specific fallbacks are used only for LongMemEval-S evaluation and are **separate from the core RaMem
  method**." Quote the LoCoMo numbers in preference to the LongMemEval ones.
- **In our setting**: the query "where is the mug?" carries no entity-plus-date anchor and no referenced
  event, the recall frame cannot be grounded, and RaMem reduces to content retrieval by its own control flow.
  Unless we put the date into the question — at which point the anchor is ours, not the system's inference.

### 6.2 QUMem: a user-state variable, inferred per query, by design

**QUMem: "Personalized Memory for Query-Conditioned User-State Inference in LLM Agents"** (Heng Wang, Yifei
Li, Lingling Zhang et al.; arXiv 2608.16168, **7 authors**, Aug 2026; **0 cites**; unrefereed). Its framing is
almost ours: "the current task is not always an effective similarity query, particularly when user preferences
evolve. Independent top-`k` retrieval may return fragments that are individually relevant but do not
collectively cover the user's current state, the reasons for state transitions, or the temporal validity of the
evidence"; and it defines the goal as inferring "a task-relevant user state that is **temporally and
contextually valid**". Three sequential agents do information-need identification, retrieval planning over
typed stores (factual / preference / transferable-insight), then state inference.

But the title is the finding: the state is **query-conditioned**. Verbatim: "the system must perform user-state
inference by retrieving and jointly interpreting evidence distributed throughout the interaction history **in
light of the current query**." The state is recomputed from scratch per query out of evidence the query
selected; it is not a persistent latent variable carried across days, and it cannot be updated by an
observation that arrives while no question is being asked. Benchmarks: PersonaMem and KnowU-Bench — and
`SURVEY2.md` §5.2 established that the PersonaMem-Evo line **explicitly designs reversals out** ("the goal is
not to create arbitrary binary reversals").

### 6.3 Retrieval signals that genuinely are not query similarity

- **EM-LLM** (Fountas et al.; arXiv 2407.09450, 7 authors; **ICLR** — the arXiv journal-ref says 2025, S2 says 2024; **69 cites**). Two-stage retrieval: a **similarity buffer** from k-NN over event representations **plus a
  contiguity buffer "populated by neighboring events"**, reproducing human temporal contiguity and asymmetry
  (Howard & Kahana 2002) via the effect Ji-An et al. 2024 found in attention heads. **Write-side segmentation
  is driven by Bayesian surprise** with an adaptive threshold `T = μ_{t−τ:t} + γσ_{t−τ:t}`, refined by graph
  modularity/conductance over attention-key similarity. Two things to take from it: (a) **temporal adjacency is
  a real, published non-similarity retrieval signal**, but it is seeded by similarity and so inherits its
  choice of era; (b) **prediction error is used to decide where events begin, never to decide which era's
  events to trust at read time.** It is a KV-cache mechanism inside one context; no fact changes.
- **"Temporal Context Reinstatement Drives Episodic-Like Order Memory in Long-Context Language Models"**
  (Pink, Vo, Wu et al.; arXiv 2607.22575, **10 authors**, 2026; **0 cites**). The cognitive-science mechanism we
  want *does* exist inside the models: on a full novel (*The Murder of Roger Ackroyd*) with new human data,
  Llama-3.1-8B/70B show the human distance effect, performance survives sentence-block shuffling (all
  p ≥ 0.307 / p ≥ 0.104), and the mechanism is "a one-dimensional temporal code that is **reinstated during
  retrieval by a single time-reinstatement attention head**", causally validated by ablation and shown not to
  depend on RoPE. **This is temporal-context reinstatement in an LLM — used to answer "which came first", not
  to decide which period's evidence is currently in force.** It is the best citation available for "the
  representational ingredient exists".
- **Uncertainty/insufficiency gates** (Oblivion §2.5; AutoMEM's judge): decide *whether* to retrieve.
- **Latent-cause inference** (Gershman, Blei & Niv 2010; the ABA-renewal theory quoted at length in
  `EXPIRY.md` §2.7) remains **unimplemented in any LLM agent**: arXiv metadata has **zero** papers with
  `"latent cause"` and `"language model"` together.

### 6.4 Mixture-of-experts-style gating over memory

- **RIZZ** (§4.3) is the clearest instance and says so: "This resembles **mixture-of-experts specialization at
  the memory level: branches act as non-parametric experts, and the router learns which expert should
  condition each input**." The routing features are an LLM-judge hierarchical label (abstracted function +
  application domain), output-shape guards, embedding snapping at `τ_snap = 0.92`, Jaccard overlap at
  `τ_J = 0.40`, and reward history. **All of them are properties of the query or of the task family.** A
  regime change in the world that leaves the query unchanged would route to the same branch.
- **"Learning What to Retain: Gated-Memory Routing"** (Rajib, Zheng, Lou; arXiv 2609.00237, 3 authors, Aug
  2026; [cites U], unrefereed) makes the right complaint — "**routing from the query alone cannot adapt to
  intermediate progress**" — and fixes it by encoding the state as `s_t = (q, S_{t−1})`, query plus prior
  execution state, with a learned router (training required). The state is the agent's own execution
  progress, not the world's regime.
- **ElasticMem** (2605.30690, 8 authors) treats latent memory as a learnable resource; **BIO-MEMART**
  (2609.08566) gates KV blocks on biometric identity — a non-semantic gate, for access control.

**Answer to the brief's crux question:** nothing conditions retrieval on an inferred *world* regime. 2026 work
has moved from "retrieve what resembles the query" to "infer a validity context and filter by it", which is
real progress — and in both systems that do it (RaMem, QUMem) the context is induced from the query, with
RaMem falling back to similarity whenever it cannot be grounded.

---

## 7. The counterexample: TEPA re-promotes on an outcome statistic

**TEPA: "Revoking Stale Memories for Conflict-Robust Language Agents"** (Yan Zhou, Yue Ouyang, Kaiyang Zheng,
Xiang; arXiv 2608.07429 v2, **4 authors**, Aug 2026; "Preprint" per its own arXiv comment; **2 cites**,
verified today; **unrefereed**). `SURVEY2.md` §5.1b established it as our must-beat baseline for
having a `return` phase. I read the mechanism, and it also breaks C1 and C2.

Verified in the primary source:

- Each observation becomes a **keyed precedent** `(k, v, s, f, σ, τ)`: conflict key, asserted value, **support
  count, conflict count**, lifecycle state, creation time. `κ` and `ν` "are **deterministic** in the reported
  benchmarks".
- Lifecycle states are **{Hypothesis, Active, Revoked}** and — the sentence that matters — "**Retrieval is
  conditioned on the active state, σ = Active.**" Semantic retrieval is one of the *baselines* TEPA is
  compared against, not its mechanism.
- **Revocation trigger, on outcomes:** "A precedent leaves the active set when either its posterior mean falls
  below `θ_rev` after `n_min = 5` total observations or, once at least `n_rec = 3` same-key outcomes are
  available, **its recent success rate falls below `θ_rec = 0.34`**." Defaults `θ_prop = 3`, `θ_rev = 0.3`,
  `θ_pro = 0.6`.
- **Promotion trigger, on outcomes:** "**Fresh evidence can later promote a new precedent under the same
  key**", when `q(p′) ≥ θ_pro` or the candidate passes trial validation. TEPA-Full adds trial-by-execution on
  a held-out task set with a budget of 3 (one support, one counterfactual, one contamination check), promoting
  after ≥60% positive trials and ≥1 support success.
- **The archive is audit-only:** "Revoked memory remains in the archive for audit while leaving the active
  retrieval set."
- Its own framing sentence, verbatim: "these results establish lifecycle revocation as a core memory operation
  for agents that must falsify, audit, **and later re-promote evolving knowledge**."
- Setting and numbers: a hidden regime `z_t` is evaluator-side; "a phase function `ϕ(t) ∈ Φ` maps each episode
  to a phase, where `Φ = {stable, light, reversal, return}`". Controlled drift over 50 seeds: append-only
  0.210, last-write-wins 0.210, no-memory 0.309, **TEPA 0.950**; real file-backed execution: append-only
  0.203, no-memory 0.298, TEPA 0.950. MemoryAgentBench SH-6k: TEPA matches last-write-wins. Its own
  memory-pollution index `MPI > 0` marks a method as **worse than no memory**, which append-only memory is
  during reversal.

**What this does and does not concede.**

- It **refutes C1's "cannot re-promote"** in the only sense that matters operationally: the old value comes
  back into the retrieval set without anyone asking a similar question, driven by a statistic over outcomes.
- It **refutes C2** for one system: the trigger is not query similarity.
- But note the fine print. The returned item is a **new precedent** carrying the old value; the archived one
  stays Revoked. For a fact keyed `(object, location)` that is a distinction without a difference; for a
  self-written belief with provenance it matters, and it means TEPA does **not** implement JTMS-style
  "support returned, so the same belief goes back IN".
- And the **prerequisite is the thing our setting lacks**: TEPA needs a per-episode binary outcome
  `y_t ∈ {0,1}` under the same key. Its benchmarks use "deterministic benchmark executors so that the
  experiments isolate memory behavior from language-model sampling variance"; the only LLM in the loop is the
  answer backend on MemoryAgentBench. **A household-QA agent is not told whether yesterday's answer was
  right.** To use TEPA's trigger we would have to manufacture the outcome stream — e.g. score each stored
  claim against the next patrol's observation of the same `(object, time-slot)` key — which is the same
  arithmetic as the persistence/emergence filter `EXPIRY.md` §6 recommends, differently packaged.

For completeness, the two other places re-promotion on a world signal exists are both outside language and
both already in `EXPIRY.md` §2.8 / §4.3: **RCD** re-activating a stored classifier when a drift detector
recognises a known concept (stream mining), and **Perpetua**'s emergence filters modelling reappearance with
prediction at arbitrary future times (robotics). Nothing changes about those rows.

---

## 8. The table

Columns: **out** = what removes the item from what the model reads · **back** = what returns it ·
**trigger** = query-similarity, or something else, named · **A-B-A tested?** = evaluated where a fact becomes
false and then true again.

| system (citation) | what moves it out | what moves it back | trigger: similarity or other | A-B-A tested? |
|---|---|---|---|---|
| **MemGPT** (2310.08560; **1362 cites**) | FIFO position + token-count eviction of conversational context; recursive summarisation | agent emits `search` (text, **timestamp**, or embedding); nothing is deleted from recall/archival storage | **agent decision from current context** — key may be a timestamp, but no signal prompts it; only clock ticks and capacity warnings wake it unprompted | **NO** |
| **Letta (product docs)** | `memory_replace`/`memory_rethink` overwrite core blocks; context compaction | `archival_memory_search` (semantic + tag filter); "never lost, even once evicted"; archive is **agent-immutable** | **query similarity** + tags; there is **no operation that promotes a passage into a block** — the agent must rewrite it | **NO** (no published evaluation on changing facts, per `SURVEY2.md` §4.2) |
| **Letta dreaming / sleep-time compute** (2504.13171; **42 cites**, verified today) | n/a — rewrites context `S(c)→c′` | background subagents consolidate | **step count or context compaction** (docs); paper's own finding: benefit tracks **query predictability** | **NO** (Stateful GSM-Symbolic / AIME) |
| **MemoryOS** (2506.06326, EMNLP 2025; 119 cites *S2 via SURVEY.md*) | lowest `Heat = α·N_visit + β·L_interaction + γ·e^{−Δt/μ}` **evicted** | nothing — MTM→LPM at heat > τ = 5 is the only move, and it is one-way up | retrieval count + recency (out), semantic two-tier (read) | **NO** |
| **Oblivion** (2604.00131, 5a; 3 cites) | `R_t(c)` decay on **turns since last access** + utility/frequency proxies; evicted from buffer, **never deleted from 𝒟** | "**reactivatability when future interactions reinforce them**" | **access/reinforcement**; retrieval *whether* is gated by **agent uncertainty** (LLM-judge sufficiency) — a real non-query trigger for looking, not for which era to trust | **NO**; names "world drift" and answers it with timestamps, forward-only |
| **MemoryBank** (2305.10250, AAAI 2024; 692 cites) | `R = e^{−t/S}` probabilistic forgetting | recall sets `S += 1`, `t = 0` | **similarity of the current conversation context** (DPR/FAISS); correctness never enters | **NO** |
| **CAMeR** (2607.20458, **1a**; 0 cites) | decay for all memories each round | reinforcement above a hybrid threshold | **explicitly query similarity**: 0.6·cosine + 0.4·keyword Jaccard | **NO** (its own bench varies query frequency) |
| **SYNAPSE** (2601.02744, **11a**; 10 cites) | activation < ε = 0.01 for 10 windows → **archived to disk**; lateral inhibition; node decay | not described | **BM25 + dense anchors**, then spread along temporal/semantic edges with fan effect | **NO** (LoCoMo only); own ablation: decay is the *sole* current-vs-obsolete signal (50.1→14.2 without it) |
| **HeLa-Mem** (2604.16839, 5a; 5 cites) | graph pruning / distillation of hubs | Hebbian edge strengthening on **co-activation** | similarity + learned associations | **NO** (LoCoMo) |
| **RAPTOR** (2401.18059, **ICLR 2024**; 726 cites) | nothing — leaves retained in a collapsed-tree index | n/a | **cosine to the query** across all layers | **NO**; no write path at all |
| **MemWalker** (2310.05029; 155 cites) | nothing — tree over the whole text | `revert` to parent **within one question** | judged insufficiency **relative to the query** | **NO** |
| **Execution-state unlearning** (2609.04875, **8a**; 1 cite) | provenance-closure taint + KV crop; deletion of a record is a **no-op** (B1 = B0, p = 1.0) | **sanitized replay regenerates** derived summaries/plans | **a revocation event** from user, platform, or injection detector — "computation cannot be edited, only replayed" | **NO**; semantics are "never should have been seen", not "true again" |
| **RaMem** (2606.22844, **8a**; 3 cites) | nothing evicted; context-invalid memories **de-prioritised** at read time | promoted back when the recall frame matches their episodic coordinates | **an inferred situation — induced from the query**; falls back to content retrieval when it cannot be grounded | **NO** (LoCoMo + LongMemEval-S); Knowledge-Update 83.33 vs LightMem 92.30 |
| **QUMem** (2608.16168, **7a**; 0 cites) | typed stores, nothing deleted | multi-query retrieval plan + LLM state inference | **query-conditioned** user-state inference (per the title) | **NO** (PersonaMem, KnowU-Bench) |
| **RIZZ** (2606.20638, 5a; 0 cites) | verifier-gated writes; **demotion via harmful counters**; branch prune/merge | **helpful counters raise retrieval score again** | **outcome/verifier for the weight** (reversible); **query + task-family label for the routing** (MoE-style branches) | **NO** (StreamBench, TRACE, LongMemEval-S, τ-bench) |
| **EM-LLM** (2407.09450, **ICLR**; 69 cites) | KV events outside the buffers | contiguity buffer pulls **temporal neighbours** of retrieved events | **similarity seed + temporal contiguity**; surprise is used for write-side segmentation only | **NO** (LongBench) |
| **Time-reinstatement head** (2607.22575, **10a**; 0 cites) | n/a — in-context | a **single attention head reinstates a 1-D temporal code** | internal temporal code, causally validated | **NO** — the task is temporal order, not validity |
| **TEPA** (2608.07429, 4a; 2 cites; unrefereed) | **recent success rate < θ_rec = 0.34** (or posterior < θ_rev after 5 obs) → **Revoked archive**; retrieval reads only `σ = Active` | **fresh same-key evidence promotes a precedent at `q ≥ θ_pro = 0.6`**, or trial-by-execution | **an outcome statistic per key — not similarity** | **YES** — `Φ = {stable, light, reversal, return}`; reversal 0.950 vs 0.210 append-only / 0.309 no-memory |
| *(non-LLM, for contrast: RCD; Perpetua; FreMEn — see `EXPIRY.md` §2.8)* | drift detection; persistence posterior | **re-activation of a stored model / emergence filter crossing δ_high** | **recognised concept / observation statistic** | **YES**, both, without any language model |

---

## 9. Verdict on the claim under test

**C1 — "can archive but cannot re-promote" — is wrong in two different ways, and the second one is the useful
one.**

1. *Archival is stronger than the claim allows, and it is a documented product guarantee, not an accident.*
   Letta persists everything "so they are never lost, even once evicted" and makes archival memory
   agent-immutable. MemGPT's recall storage holds "the entire history of events". TEPA keeps a revoked archive
   for audit. Oblivion never deletes from 𝒟. Our user is right that in this family nothing is destroyed, so
   nothing stands in the way of an item's return.
2. *Re-promotion on a world signal exists — once.* TEPA revokes on a falling per-key success rate and promotes
   on accumulated same-key evidence, retrieves on lifecycle state rather than similarity, and is evaluated
   across a `reversal → return` schedule. The blunt version: **the sentence "no language memory system
   re-promotes when the world reverts" was already false at the time `EXPIRY.md` was written, by a paper
   `SURVEY2.md` had already flagged for a different reason.** `EXPIRY.md` §4.3's table should gain a TEPA row,
   and its §0 item 5 ("for everything that reads or writes natural-language beliefs, the answer is no") needs
   the qualifier that TEPA's keys and values are extracted deterministically, so it is only half a language
   system — which is a reason to be careful, not a reason to leave it out.

**C2 — "re-promotion is triggered by query resemblance" — survives as the description of the field, but not as
a universal, and it needs one substantive amendment.**

The amendment: it is no longer true that these systems have no situation variable. RaMem has a *recall frame*,
QUMem an inferred *user state*, RIZZ a routed *branch*, Oblivion an *uncertainty* gate, EM-LLM a *contiguity*
buffer. What is true is narrower and sharper.

**The narrower form, stated precisely — this is what I would defend in a paper:**

> In every published language-model memory system except TEPA, the decision to read a stored item is a
> function of the current query (its text, entities, dates and inferred intent), of the item's own access
> history, or of the agent's internal uncertainty — and of nothing else. Where a system does condition
> retrieval on an inferred situation rather than on surface similarity (RaMem's recall frame, QUMem's user
> state), that situation is **induced from the query**, is recomputed per query rather than carried across
> time, and degrades to content similarity when the query contains no groundable anchor. Consequently, for a
> query that is verbatim identical before, during and after a disruption, **no such system can change which
> period's evidence it reads.** The missing component is not an archive and not a re-promotion operation: it
> is a persistent, observation-driven estimate of which regime is currently in force, maintained between
> questions and consulted at read time. The only agent-memory system that has anything of the kind is TEPA,
> whose estimate is a per-key recent-success rate — which requires an outcome signal that a question-answering
> agent is not given.

**One correction to our own premise, and it is the reason to keep it narrow.** "Retrieval-based memory is
inherently reversible" is true of an *unbounded* store and false of a *budgeted* one. Beyond the destructive
operations already catalogued (Mem0's permanent DELETE, AriGraph deleting conflicting facts, MemoryOS evicting
lowest-heat segments, Letta's `memory_replace`), the eviction audit (**"What Eviction Destroys", arXiv
2609.08279, 1 author, Sep 2026, **0 cites**, unrefereed — do not quote its numbers as established**) reports that among
errors that restoring the gold evidence would fix, the **irreversible** share is **0.67–0.73** for FIFO,
random and redundancy-aware eviction and **0.60** for LLM-importance at an 80k-token budget, rising to
**1.00** for all four at 8k. Its methodological point is worth adopting regardless of the numbers: report the
retrieval regime, because "recoverable errors occur under top-`k` retrieval at 80k tokens but are absent under
forced-gold injection by construction, so budget–accuracy results are not directly comparable". For our
experiments this argues for stating explicitly that our store is unbounded, so that "present and unused"
(`SURVEY2.md`'s 807/890) is a read-time claim and not a storage artefact.

---

## 10. What is still missing after this pass

1. **A persistent regime variable.** Nothing maintains, between questions, a belief about which period's
   evidence is in force. RaMem recomputes a frame per query; QUMem recomputes a state per query; TEPA keeps
   per-key counters but no notion of a global regime that could transfer across keys.
2. **Prediction error at read time.** EM-LLM uses surprise to decide where events *begin*; SigLLM and the
   change-point line (see `SURVEY2.md` §3.5) compute change points but never feed them into what an agent
   reads. Nobody uses surprise to decide *which era* to read.
3. **Correctness-conditioned forgetting curves.** Every Ebbinghaus-style system strengthens on retrieval. The
   one-line change — strengthen on *verified* retrieval — has never been tried, though ExpeL, RIZZ, MemCon and
   TEPA show the outcome-gated weight works when a verifier exists.
4. **Summary rebuild triggered by a world change.** The provenance-plus-replay machinery now exists
   (2609.04875) and is pointed at privacy revocation. Nobody has pointed it at "the observations this summary
   was built from have been superseded — regenerate it", and nobody at all at "…and have now been reinstated".
5. **Spaced repetition for an agent's own store.** Absent. The BLL equation is used to predict *human* item
   reuse in recommender systems and in spaced-repetition tutors, never to schedule an agent's memory refresh.
6. **A benchmark.** Unchanged from `SURVEY2.md` §5.1b: TEPA's drift suite is the only `return` schedule, it is
   a method paper's own suite, and its keys are extracted by deterministic functions.

---

## 11. Loose ends worth one fetch each before this is cited

- **The four citation counts I never got** (Semantic Scholar 429 to the end): **Oblivion** 2604.00131
  (`EXPIRY.md` verified **3** on the same date, reused), **LLM-ACTR** 2408.09176, the **ACT-R recommender
  line** 2108.02138 / 1701.01276 / 1406.7727, and **gated-memory routing** 2609.00237. Everything else cited
  here is verified — see §12.
- **MemWalker's venue.** S2 lists it as arXiv-only (2023); it is often cited as ICLR 2024. Unresolved.
- **EM-LLM's year.** The arXiv journal-ref says ICLR **2025**; S2 says ICLR **2024**. One of them is wrong.
- **TEPA's `return`-phase numbers.** `SURVEY2.md` flagged that they live in a heatmap and could not be
  extracted; I did not extract them either. The reversal-phase numbers (0.950 / 0.210 / 0.309) are safe to
  quote; **the return-phase numbers are not.**
- **Whether TEPA's revoked precedents are ever re-activated in the implementation**, as opposed to a new
  precedent being created under the same key. The text says the latter; the released code would settle it.
- **Whether Graphiti revives or duplicates a previously invalidated identical edge** — still open from
  `SURVEY.md` and `EXPIRY.md`; a code read, not a paper read.
- **Full-text search for "base-level activation" and "latent cause" in LLM-agent papers.** My zero-hit results
  are arXiv *metadata* searches; a Google Scholar or full-text sweep could still turn up a §3.2 or §6.3
  counterexample.
- **GoodAI LTM** (Castillo-Bolado et al.), Oblivion's "dynamic" benchmark: does anything in it revert? Not
  checked.
- **LightMem**, which beats RaMem on LongMemEval knowledge-update (92.30): its mechanism is not described in
  this document and is only partially covered in `SURVEY2.md` §4.2.

---

## 12. Citation counts verified for this document

Semantic Scholar, fetched by me 2026-09-23/24 after the rate limit cleared. Venue is S2's field; where the
paper's own arXiv comment claims no venue I treat it as unrefereed regardless (see Conventions).

| arXiv | short name | cites | S2 venue / year |
|---|---|---|---|
| 2310.08560 | MemGPT | **1362** | arXiv 2023 |
| 2401.18059 | RAPTOR | **726** | ICLR 2024 |
| 2305.10250 | MemoryBank | **692** | AAAI 2023 |
| 2309.02427 | CoALA | **524** | TMLR 2023 |
| 2310.05029 | MemWalker | **155** | arXiv 2023 |
| 2407.09450 | EM-LLM | **69** | ICLR 2024 *(journal-ref says 2025)* |
| 2504.13171 | Sleep-time compute | **42** | arXiv 2025 |
| 2601.02744 | SYNAPSE | **10** | S2 says ACL 2026; paper claims no venue |
| 2604.16839 | HeLa-Mem | **5** | S2 says ACL 2026; paper claims no venue |
| 2606.22844 | RaMem | **3** | arXiv 2026 |
| 2608.07429 | TEPA | **2** | arXiv 2026, "Preprint" |
| 2606.11680 | Organize then Retrieve | **2** | arXiv 2026 |
| 2609.04875 | Execution-state unlearning | **1** | arXiv 2026 |
| 2608.16168 | QUMem | **0** | arXiv 2026 |
| 2606.20638 | RIZZ | **0** | arXiv 2026 |
| 2607.20458 | CAMeR (1 author) | **0** | arXiv 2026 |
| 2607.22575 | Time-reinstatement head | **0** | arXiv 2026 |
| 2609.08279 | What Eviction Destroys (1 author) | **0** | arXiv 2026 |
