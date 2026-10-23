# Embodied / spatial robot memory: survey for the Go2 lab agent (2026-10-22)

Scope: robot and egocentric memory, not LLM chat memory. Mem0, Zep, MemGPT, A-MEM, HippoRAG and similar are
already covered in `prior_work/corl2026_workshops/uncertainty_workshop/sota_memory/SURVEY*.md`. SURVEY2 section 5.4
mentions OpenEQA, ReMEmbR, 3D-Mem, FindingDory, HUMEMBR, Perpetua, Khronos and FreMEn only to ask whether they
contain a reversion; nothing here repeats that.

How the sources were checked: three sub-agents read arXiv abstracts or full text, and I re-read the abstracts of
the 2026 papers the recommendations lean on (H2-EMV, RAVEN, PreSIST, Surprise-gated, Industrial ReMEmbR, ECROM,
LA-EQA, When Memory Lies, HUMEMBR, DAAAM, MeMoREval). **[U]** = not verified in the primary source.
**(body)** = the number comes from the paper body, as reported by a sub-agent; I did not re-check it. Many entries
are 2026 preprints without peer review, so treat their numbers as provisional.

---

## 0. What our memory is today (measured from `go2/data/lab_agent/index.jsonl`, 2026-10-22)

- **Size:** 1,145 records over 3 recording days: Mon 616, Tue 185, Thu 344. There are 921 trail frames, 62 photos
  and 20 look_around pictures. The pictures take 32 MB.
- **Undescribed pictures:** **205 records (18%) have `seen: null`, all from Thu 10-22**: 142 trail frames, 47 photos
  and 16 look_around. Search skips them, so today's pictures are partly invisible. The likely cause is VLM failures
  or a backlog; `retry_failed` exists.
- **Duplicate ids:** 38 ids occur twice.
- **Objects per picture:** about 8.0, with 153 distinct names. Synonyms are split: chair 1,495 vs office chair 217,
  box 1,628 vs cardboard box 212, bin vs trash can. "backpack" appears in **179 pictures**, but the lab probably
  holds a handful of physical backpacks. That ratio is how much compression instance tracks would give.
- **People:** 179 pictures contain people. The people notes already carry re-ID cues ("light blue t-shirt, dark
  pants", "black t-shirt and a cap", "blue shoes"), but nothing links them across pictures.
- **Redundancy:** only 35 of 921 consecutive trail frames are near-duplicates (under 0.3 m and under 20 deg apart).
  The trail is already sparse, so keyframe dropping saves little. The gain is in **merging repeated sightings of
  the same object**, not in dropping frames.

---

## 1. Long-horizon robot memory systems (what is stored, at what depth, how retrieved)

| System | Stored unit | Compression / hierarchy | Retrieval | Change handling | Key result |
|---|---|---|---|---|---|
| **ReMEmbR** (NVIDIA; 2409.13682; ICRA'25 [U]) | VILA caption of each short video chunk, plus text embedding, position and time | none (the authors list this as a limitation) | LLM loops over text, position and time tools; answers as JSON {text, xyz, time} | none | correctness stays flat as history grows, while full-context baselines degrade. **Closest to ours.** |
| **Embodied-RAG** (2409.18313) | topological node: pose, time, image, GPT-4o caption | **semantic forest**: nodes clustered on spatial plus caption similarity, LLM summary per cluster, up to a root | top-down LLM traversal, then rerank | none | Find P(Q\|A) 0.55-0.62 vs <0.15 for Naive-RAG, GraphRAG and LightRAG |
| **KARMA** (2409.14908) | long-term: static 3D scene graph as text. Short-term: fixed-capacity object units (coordinates, state, image) | **W-TinyLFU eviction** in the short-term store | embedding top-K | short-term state | removing short-term memory drops ALFRED-L complex-task success 21% to 5% |
| **3D-Mem / SnapMem** (2411.17735; CVPR'25 [U]) | **a few real images ("memory snapshots")**, each object assigned to one snapshot by co-visibility clustering, plus frontier snapshots | about 39.8 observations become 10.9 snapshots; about 3.3 per query after prefiltering | VLM ranks object classes and keeps snapshots containing the top-K | assumes a static scene | A-EQA 52.6 vs 46.9 for Explore-EQA; EM-EQA 57.2 with 3.1 frames vs 48.1 for multi-frame |
| **MemoryEQA** (2505.13948) | per-view entries: image, pose, text, embedding | entry replaced when pose is close, SSIM/embedding similar and view unobstructed | entropy-adaptive threshold, separately per module | replace-on-revisit | MT-HM3D 33.2 to 43.1; HM-EQA 47.4 to 61.4 (v2) |
| **Mem2Ego** (2502.14254) | landmark memory: global coordinate plus VLM description; frontier and visitation maps | none | LLM top-k, drawn as markers on a panorama | none | HSSD success 0.869 vs 0.784 |
| **Embodied VideoAgent** (2501.00358; ICCV'25) | **object memory**: 3D box, category, state, on/in relations, CLIP feature. Plus action and visible-object logs | re-ID by overlap and visual similarity; moving-average merge | SQL plus feature search, temporal_loc, spatial_loc, vqa tools | VLM updates an object's state when an action touches it | OpenEQA subset 47.0 vs 36.3 |
| **ConceptGraphs** (2309.16650) | object node: point cloud, averaged CLIP feature, LLM-condensed caption from up to 10 views | multi-view captions condensed into one caption per object | graph serialised as JSON to the LLM | static | node precision 0.71 |
| **HOV-SG** (2403.17846; RSS'24) | floor, room and object layers with CLIP features | hierarchy | language to floor to room to object | static | 75% smaller than a dense open-vocabulary map |
| **Hydra** (2201.13360; RSS'22) | layered 3D scene graph: mesh, objects, places, rooms, building | rooms found by community detection | - | loop-closure optimisation | real-time |
| **Clio** (2404.13696; RA-L'24) | object segments and places | **Agglomerative Information Bottleneck against a task list**: merge primitives until task-relevant information would be lost, so the task sets the granularity | - | static | Office: 99 objects vs 339 for ConceptGraphs; Cubicle: 49 vs 751; higher F1 |
| **STaR** (2602.09255) | task-agnostic store | **Information Bottleneck at query time**, not at write time | IB retrieval | - | NaVQA and warehouse VQA (no numbers in the abstract) |
| **DovSG** (2410.11989; RA-L'25) | voxel objects with CLIP and text features; on/belong/inside edges | - | - | **local update**: re-project stored voxels into a new view, delete those that disagree, recompute relations of affected objects | long-term task success 35% vs 5% for OK-Robot; update takes 1 min vs 27 min for a rebuild |
| **Khronos** (2402.13817; RSS'24) | object "fragments" with first and last observation | 4D map | - | **absence inferred from free-space rays; change time = midpoint between last seen present and first seen absent** | change-detection F1 66.2 vs 60.4 |
| **LA-EQA "Mind Palace"** (2507.12846; CoRL'25) | **one hierarchical scene graph per episode** (viewpoint nodes with pose, image, caption and objects, grouped into areas), indexed by time | episode, then area, then viewpoint | LLM picks which past episodes to search, then a cost-aware planner trades recall against going to look | episodic snapshots, compared across time | (body) 65.0% vs 46.1% for ReMEmbR; 61.8% with value-of-information stop using 15.7 images vs 22.9 |
| **DAAAM** (2512.00565) | hierarchical **4D scene graph of object descriptions**; a tool-calling agent queries it | object-level | tools | 4D | **OC-NaVQA +53.6% accuracy**, position error -21.9%, time error -21.6% vs the best baseline |
| **RAVEN** (2606.25206) | **image embeddings + pose + time; no captions** | - | spatially grounded vector search | - | beats caption memories; matches frontier VLMs at about 10x lower retrieval cost; **runs on a Unitree Go1** |
| **Industrial ReMEmbR** (2610.28624) | embeddings, vision tokens and reconstruction latents on the robot; no raw frames | **captions generated later, on demand, from cached tokens** | content, position and time | - | **people patches zeroed out for GDPR** |
| **HUMEMBR / PersonEQA** (2606.30404; IROS'26) | frames at 2 Hz, redundant frames dropped by ResNet similarity; caption embedding, waypoint, time | **people clustered by face and body re-ID; an LLM writes a daily summary per person** | 5 retrieval tools | people move | (body) 75.4% vs 67.3% for full-context Gemini, using about 17% of the tokens |
| **Surprise-gated memory** (2606.03787) | stores an episode only if its Bayesian surprise in V-JEPA-2 latent space passes a threshold; sits on a 4D scene graph | write gating | - | - | at least 12% better than prior robot memories on temporal, spatial and yes/no QA |
| **H2-EMV "Learning to Forget"** (2604.11306) | hierarchical episodic memory | **an LLM scores relevance against natural-language forgetting rules; user feedback edits the rules** | - | - | 20.5 h of ARMAR-7 logs: memory 45% smaller, query compute 35% lower, same QA accuracy; +70% on second-round queries |
| **MeMoREval "What should embodied agents remember?"** (2610.12561) | compares memory formats: frames, descriptions, scene graphs | - | - | - | **frames beat generated descriptions, with lower write cost; frames plus scene graph had the best success for every model** |
| **LT-Mem** (2608.19059; IROS'26) | Live, Delta and Meta stores | **per object, by volatility: overwrite, hold, or keep several hypotheses** | - | volatility-aware | about 10x fewer tokens |

Also seen: WorldLines (2606.18847; visibility-aware state trails, ObsMem), EmbodiedMemory-Bench (2609.28236),
MemoryVLA (2508.19236; manipulation), RoboMemory (2508.01415), SG-Nav (2410.08189), GraphEQA (2412.14480), and
"Spatial Memory by Agents, for Agents" (2610.22736; an LLM writes the memory code; 44.2 vs 29.3 for ReMEmbR).
**Mem4Nav (2506.19433) is withdrawn pending a misconduct investigation: do not cite it.** No paper named "STMR"
was found; the closest are LA-EQA and STaR.

**What this means for us.** Most systems store either caption or embedding snapshots keyed by pose and time
(ReMEmbR, RAVEN, HUMEMBR), or object-centric scene graphs (ConceptGraphs, Clio, DAAAM, Embodied VideoAgent).
Three 2026 results point the same way: object-level 4D graphs beat frame captions on real logs (DAAAM +53.6%),
embeddings beat captions (RAVEN), and frames beat descriptions (MeMoREval). **A text-only index that is written
once and searched by word matching is the weakest point in our current design.** Few systems handle change
explicitly: DovSG, Khronos, Embodied VideoAgent, LA-EQA, LT-Mem.

**OpenEQA** (Majumdar et al., CVPR'24; no arXiv): blind GPT-4 scores 33.5 on EM-EQA. GPT-4 with LLaVA frame captions
scores 43.6, **but with ConceptGraphs captions it scores only 36.5**. GPT-4V scores 55.3; humans 86.8. Models are no
better than blind on spatial questions. **Any lab eval must report a blind-LLM baseline:** "where is the fire
extinguisher" can often be answered from priors.

---

## 2. Compression, hierarchy, forgetting, object permanence, people

### 2.1 Hierarchy and compression
- **Frame, then place, then day.** Three precedents:
  - Embodied-RAG builds a semantic forest from clustered nodes.
  - LA-EQA keeps one graph per episode, with areas inside it.
  - EgoLife/EgoRAG (2503.03803) summarises by clip, then hour, then day [U on exact levels].
  - HippoMM (2504.10739) segments at change points, searches the summaries first and widens to raw segments
    only when needed; about 5x faster than RAG.
- **Compression that keeps what recurs:** Imprint (2607.00696) groups records into recurring patterns and decides
  what to keep from recurrence, recency and distinctiveness. On EgoLifeQA it reaches 35.8% vs 31.0%, with 2.3x
  less memory and 11.8x lower latency than EgoRAG. MemLife (Meta, 2609.40195) trains the memory writer with RL
  (+2.7-5.0%).
- **Task-driven compression:**
  - Clio applies the Information Bottleneck at write time, given a known task list.
  - STaR applies it at query time.
  - Our task distribution is open-ended ("where is X", "who was here", "is the door open"), so the
    STaR-style query-time version fits better. Clio-style merging is worth it only for object instances.
- **What to store (gating):**
  - Surprise gating (2606.03787).
  - H2-EMV's forgetting rules, written in language and edited from user feedback, suit an LLM agent well.
  - KARMA's W-TinyLFU eviction keeps items by recency and frequency.
  - Social-robot memories store moments of high salience or novelty (2604.12081).
  - MemoryBank (2305.10250) uses an Ebbinghaus forgetting curve [U]. It is text memory, so mention it only briefly.
- **Store the raw signal, describe it later:**
  - Industrial ReMEmbR keeps vision tokens and latents, and writes captions on demand.
  - RAVEN keeps embeddings only.
  - MeMoREval finds frames beat descriptions.
  - So: **keep the pictures, and treat the description as a re-generable index rather than the memory itself.**

### 2.2 Object permanence and change (semi-static mapping)
- **Persistence filter** (Rosen, Mason, Leonard; ICRA 2016; MIT DSpace hdl 1721.1/107620): a Bayesian estimate of
  P(feature still exists | time since last seen, noisy detections and misses). It is the base model for this line.
- **Perpetua** (2507.18808; IROS'25): chains mixtures of persistence and emergence filters, so it models
  disappearance *and* reappearance and predicts future states. **Predictive Spatio-Temporal Scene Graphs**
  (2605.00121; RA-L'26) put these filters on scene-graph object edges and test over 3 weeks with changes every 2 h.
- **PreSIST** (2607.04057; Biswas lab): **a VLM gives the persistence prior** (a parked car vs a car at a light);
  a filter refines it with observations; a vision-only model is distilled from it. **This fits our setup best:**
  ask Qwen once per object class "how long does a <backpack on a desk> usually stay?", then run a persistence
  filter per instance.
- **ECROM** (2610.00330; Soh lab): each detection *or non-detection* updates the belief **in proportion to how
  well the robot could actually observe that spot**. This gives a long-term prevalence prior for search: +4.5 AP
  and +4.2 SPL. **This is the correct way to use "the dog looked there and did not see it".**
- **"Where Did I Leave My Glasses?"** (2509.19851; RA-L'26): per-instance stationarity plus revisiting stale areas,
  with an LLM choosing where to search. Detects 95% of changes; search more than 29% more efficient than patrol.
- **Classics:** FreMEn (Krajník, T-RO 2017; periodic state models); Toris and Chernova, ICRA 2017 (exponential
  decay of P(object still where last seen)) [U].
- **Change detection:** POCD (2205.01202; RSS'22); Panoptic Multi-TSDFs (2109.10165); FOCUS (2610.05639;
  persisted, replaced or removed; replacement F1 0.20 to 0.84); Object Permanence Filter (2403.08231; ICRA'24).
- **Time-propagated belief:** EvolvingNav (2609.39166): an object stays or relocates, with some probability left
  for "somewhere unseen"; negative evidence counts only if the object would have been visible.

### 2.3 People and identity
- **HUMEMBR** is the template: face and body re-ID clustering, then a per-person daily summary from an LLM, then
  questions such as "when does X usually arrive?".
- **Clothes-based re-ID only works within a day.** The standard clothes-changing re-ID baseline is CAL
  (2204.06890; CVPR'22; CCVID dataset; also LTCC 2005.12633). For a robot that follows a person and keeps learning
  their appearance: 2309.11727 (RA-L'24).
- **The practical rule for us:** clothing (teal shirt) is a **session-level** identity key, valid for one day. A
  stable identity across days needs face or gait, or a person telling the agent who they are, and that has privacy
  costs.
- **Privacy:** Industrial ReMEmbR zeroes out people patches (GDPR). FiFA (2512.12856) gives forgetting policies
  with sensitivity labels, for software agents. 2509.19041 argues for dynamic privacy controls in HRI. **No robot
  system was found that combines perception, anonymisation and deletion on request. That is a gap and could be a
  small contribution.**

---

## 3. When to consult memory and when to go look

- **LA-EQA (Mind Palace)** states our problem directly:
  - Recall costs a constant; looking costs path length.
  - An LLM chooses past only, present only, or past then present.
  - Recall stops on a value-of-information test: stop when the candidate set narrows to one area, or when more
    recall would not change where to look next.
  - (body) Retrieves 77% fewer images and saves 3-10 room searches on a legged robot in a 1,000 m^2 office over
    6 months.
- **Conformal stopping:**
  - Explore-until-Confident (2403.15941; RSS'24) intersects answer prediction sets over time and stops when one
    answer remains. An entropy stopping rule stopped too early.
  - KnowNo (2307.01928; CoRL'23) asks a human when the set has more than one option.
- **Other stopping rules:** EfficientEQA (2410.20263; IROS'25) stops on relevance outliers. MemoryEQA uses
  entropy-adaptive retrieval.
- **Staleness is a safety issue:** "When Memory Lies" (2608.04574):
  - An agent that trusts raw stale memory dies more than twice as often as one with no memory; (body) 74.4% vs
    28.0% for GPT-4o.
  - A read-time audit that checks memory against the current observation removes much of that cost.
  - Visual staleness detection is unreliable for some VLMs: F1 ranges from 0.887 down to 0.067.
- **Uncertainty at write time:** UQ-DAAAM (2606.08277) flags objects whose multi-view captions disagree and takes
  about 2 extra views of them. OC-NaVQA descriptive accuracy rises from 0.711 to 0.761.
- **Belief with time decay:** PreSIST, ECROM, EvolvingNav and the persistence filter (2.2).

**A policy for us** (cheap to implement as tool output plus a prompt rule):
- Compute **p_still = persistence(class, surface, time since last seen, misses since)** for every candidate.
- Weigh the cost of a wrong answer against the cost of going: **answer from memory if p_still > tau(question)**,
  otherwise offer to go and look.
- The cost of looking is route length from the console's route preview, which `locate` already calls.
- The cost of being wrong is high for "go to X" (wasted walk) and low for "did you see X on Monday" (a past fact
  never goes stale).
- **Questions about the past never need a look. Questions about now always need p_still.**

---

## 4. Benchmarks we can use or copy

| Benchmark | History | Scene changes? | Real? | Use for us |
|---|---|---|---|---|
| **OpenEQA** EM/A-EQA (CVPR'24) | short single tour (about 30 s per ReMEmbR) | no | real scans | blind-LLM baseline methodology; LLM-Match scoring |
| **NaVQA** (ReMEmbR) | 3-25 min CODa campus robot | barely | real | **format to copy**: 210 questions, 7 sequences, short/medium/long windows, 5 experts writing questions; binary 32 / time 14 / duration 4 / position 34 / text 16%; correct within 15 m and 2 min |
| **OC-NaVQA** (DAAAM) | up to 35.8 min, 1.6 km | barely | real | **fixes NaVQA's flaw**: its ground truth was the robot's viewpoint, not the object's position. We have the same flaw in "near <place>" |
| **PersonEQA** (HUMEMBR) | 20 days, about 31 h, 13k images, Spot in an office | people move | real | **closest to our lab**; within 5 m and 5 min; person-ID questions |
| **LA-EQA** | 3-10 episodes over days in sim; 10 episodes over 6 months in a real office | yes, hand-placed | sim + real | past, present, multi-past and past-present questions; 7 human authors; LLM-generated questions judged poor |
| **FindingDory** (2506.15635) | 400-3,500 frames, 2-11 pick-and-place events | yes | sim | procedural questions from logged ground truth; GPT-4o 27.3% |
| **HM-EQA** | single scene | no | sim | VLM drafts the questions, humans filter: a cheap middle ground |
| **MeMoREval** (2610.12561) | event sequence, then questions | - | sim | protocol for comparing memory formats |
| **EgoLifeQA**, Ego4D NLQ, EgoSchema | week / clips | - | real egocentric | analogs only |
| Sequential EQA (2607.21571), EmbodiedMemory-Bench (2609.28236), WorldLines (2606.18847) | | yes | | check before claiming novelty |

**Building a lab eval from our logs (the NaVQA / PersonEQA recipe, adapted):**
1. **Pick windows.** Use our 3 days, plus new days. Sample windows of under 10 min, under 2 h, same day, and
   across days.
2. **Write questions by hand.** Oliver, plus one labmate, writes about 150 questions from the pictures. Generate
   candidates from the index (objects seen at least 2 times, people pictures) and have a human edit them.
3. **Use typed answers:**
   - position: **object** position, labelled by clicking it on the map, within 1 m (the lab is small, so not
     NaVQA's 15 m);
   - time: within 10 min;
   - count;
   - yes/no;
   - free text, scored by an LLM judge.
4. **Change categories** (what our current memory cannot do):
   - "where is X now" when X **moved after its last sighting**;
   - "is X still there" when the latest picture shows it gone;
   - "who was at desk_kang on Monday and was it the same person on Tuesday";
   - "how many distinct people today".
5. **Ground truth for change:** stage 10-20 deliberate moves (backpack, bottle, tripod, chair) at logged times, in
   the FindingDory style. Then "moved since" labels are exact.
6. **Report:** blind-LLM baseline (OpenEQA lesson), current memory, each new layer, and an oracle given all
   pictures. Also report **tokens per answer**, **pictures opened**, **metres walked**, and **wrong-confident
   rate** (answered from stale memory when the object had moved).

---

## 5. Concrete recommendations for our system

### 5.1 Layered design (keep L0; add L1-L3 as derived, rebuildable views)

| Layer | Unit | Contents | Built how | Kept how long |
|---|---|---|---|---|
| **L0 raw** | picture | JPEG, t, pose, look_deg; the current VLM JSON as a **re-generable index**; **add an image embedding** (SigLIP/CLIP; RAVEN, MeMoREval) | today, plus embeddings | keep all (32 MB per 1k pictures is nothing). Blur faces in stored copies if privacy matters |
| **L1 sightings** | (picture, object) | canonical class (merge synonyms: "office chair" to chair), colour, surface, bearing line, crop embedding | parse the existing JSON; crop by `across` or with an open-vocabulary detector | all |
| **L2 instances** | object instance / person-session | map position (triangulated across sightings, as in `locate`), class, colour, **first_seen, last_seen, n_seen, n_missed_when_visible**, p_still, mobility class, representative pictures (3D-Mem-style: the 1-3 pictures that best cover it) | associate sightings by class + colour + position within about 0.75 m + crop-embedding similarity; **misses** come from pictures whose pose and field of view cover the instance's position without detecting it (Khronos / ECROM negative evidence) | live. Retire with a "gone since" date, never delete (SURVEY.md lesson) |
| **L2p people** | person-session (per day) | clothing descriptor, positions over time, desk association, pictures | cluster `people_notes` + crop embeddings **within one day only** | per day; cross-day linking only if a person names themself, or opt-in |
| **L3 place/day** | (place, day) or (place, hour block) | text summary: which instances were present, which changed, people counts, coverage (how many pictures, which hours) | LLM summary of L2 deltas (Embodied-RAG / EgoRAG style) | keep; this is what the agent reads first |
| **L4 static map** | furniture, places | desks, cabinets, doors: objects with p_still near 1 over all days | promoted from L2 when stable | permanent; becomes part of the system prompt |

**What to store at what depth:**
- **Store at L2 with tracks:** objects people ask about (bags, bottles, laptops, jackets, tools, robots).
- **Promote to L4:** furniture.
- **Never instantiate:** boxes, cables and lights, unless asked about. They are noise; box alone has 1,628 rows.
- **People:** a session-level count and clothing only. No identity across days by default.

### 5.2 Retrieval policy (tool-level, so it does not depend on prompt obedience)
- **`search_memory` returns L2 instances first.** Each comes with last_seen, p_still, n_missed and the 1-3 best
  pictures, then falls back to L0 pictures. **Add embedding search** next to word matching.
- **New tool `where_is(thing)`:**
  - returns the belief: candidate instances with p_still;
  - says whether anything newer covered that spot ("covered 3x since, not seen": negative evidence);
  - gives the recommended action: answer / answer with a caveat / go look, plus the route length.
- **Persistence prior per (class, surface):**
  - ask Qwen once (PreSIST-Lang style), e.g. backpack on floor: about hours; fire extinguisher: weeks;
  - then **fit the hazard rates from our own L2 tracks** as days accumulate.
- **Past-tense questions never trigger a look. Questions about now use the threshold from section 3.**
- **Keep the existing rule that the agent opens pictures before answering.** With L2 it opens 1-3
  representative pictures instead of searching 12.

### 5.3 Experiments to run first (cheapest first)
1. **Fix ingestion.** Retry the 205 undescribed pictures and remove the 38 duplicate ids. Rerun stats. (An hour.
   It changes every number below.)
2. **Instance compression study:**
   - build L1 and L2 offline from the existing 940 described pictures;
   - report sightings per instance per class (for example, 179 backpack pictures to N backpacks);
   - hand-check about 50 associations for purity.
   - This is the "compression ratio vs QA accuracy" axis.
3. **Write a 100-question lab eval** (section 4) over Mon/Tue/Thu, including about 20 "moved since" questions
   from staged moves.
4. **Compare memory formats on that eval, holding the agent (Opus) fixed:**
   - (a) blind;
   - (b) current word search over VLM JSON;
   - (c) + image-embedding search;
   - (d) L2 instances;
   - (e) L3 summaries only;
   - (f) L3, then L2, then L0 drill-down.
   - Metrics: accuracy, tokens, pictures opened.
   - This is the "what depth to store" result, a lab version of MeMoREval / DAAAM.
5. **Memory or look:**
   - stage moves, then ask "where is X now";
   - compare always-memory, always-look and the p_still policy;
   - metrics: accuracy, metres walked, wrong-confident rate.
   - This is the "when to check memory" result, a lab version of LA-EQA.
6. **Forgetting / compression sweep:**
   - drop L0 descriptions older than k days, keeping L2/L3;
   - or apply H2-EMV-style forgetting rules written in language;
   - plot accuracy against storage and against tokens per answer.
7. **People:**
   - within-day person clustering from `people_notes` + crops, scored against a hand-labelled day;
   - "how many distinct people Tuesday" error, compared with the current per-picture count.

### 5.4 Framing note
The gap that still looks open:
- Within this list, only HUMEMBR and LA-EQA work on a real robot, over multiple days, with an LLM agent.
- Persistence modelling (Rosen, Perpetua, PreSIST) has not been joined with LLM-agent memory, except
  PreSIST-Lang's prior.
- Nobody reports the **memory-or-look trade-off in metres walked vs accuracy on a real legged robot across days**,
  except LA-EQA (6-month office). LA-EQA is the paper to position against.
- People memory with privacy controls (deletion, anonymisation) is unaddressed in robot memory.
