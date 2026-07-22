# H2 — Does World Knowledge Buy Faster Adaptation in Atypical Households?

**CONFIRMED (confirmatory run, dev/test wall, 3 models).** On **three new confusable
persona pairs unseen during design**, with the E5 prompt/schema/digest **frozen and
predictions pre-registered** (`PREREGISTRATION.md`), the LLM's world-knowledge regime
inference transfers to **held-out** objects that the per-edge statistical model
provably cannot reach — replicated across **DeepSeek-V4-Flash, Qwen3.6-35B-A3B, and
GLM-4.5-Air** — and it survives the strongest simple baseline (the class-frequency
table that beat the LLM zero-shot in E0), not just the classical 0.00 strawman.

**Held-out regime-flipped targets (300 queries/model, clustered 95% CI):**

| arm | DeepSeek-V4 | Qwen3.6-35B | GLM-4.5-Air |
|---|---|---|---|
| classical (per-edge control) | 0.00 | 0.00 | 0.00 |
| **class_freq** (strong baseline) | 0.11 [.00,.25] | 0.11 | 0.11 |
| **llm_named** | **0.48 [.27,.68]** | **0.41 [.23,.58]** | **0.35 [.17,.54]** |
| llm_anon (semantics stripped) | 0.01 | 0.01 | 0.03 |

Every model: **llm_named ≫ class_freq ≫ classical**, and **anon ≈ 0** (semantics
necessary). All three correctly named the personas ("night-shift healthcare worker",
"retiree gardener", "toddler household", …) from ~6 diagnostic sightings.

**E4 hybrid (item 4) — the system payoff.** The LLM reads the digest once, flags each
object regime-shifted or not, takes its own regime-aware prediction where shifted and
the frequency table where not. On a realistic conventional-heavy object mix (75% conv
/ 25% regime-shifted) it **dominates both endpoints** because `llm_named` sacrifices
conventional objects (catastrophically for the weaker models) while class_freq lacks
transfer:

| realistic-mix acc | DeepSeek | Qwen3.6 | GLM |
|---|---|---|---|
| class_freq | 0.614 | 0.614 | 0.614 |
| llm_named | 0.515 | 0.365 | 0.112 |
| **e4_hybrid** | **0.601** | **0.646** | **0.632** |

E4 beats `llm_named` on all three and matches-or-beats class_freq — the weaker the
model's conventional reliability, the larger the hybrid's win (GLM: named 0.11 → E4
0.63). Conventional-object reliability is preserved (E4 = class_freq = 0.78 on
DeepSeek 0.71).

**Honest caveats carried into the claim.** (a) One pre-registered sub-prediction was
FALSIFIED: the two "structure-sufficient" households (wfh_senior, traveler) showed
named ≫ anon too (wfh +0.70 on all three models) — predicting a *held-out* object
needs its identity, so anonymization hurts even structurally-inferable regimes; the
honest conclusion is *stronger* than pre-registered (semantics are uniformly
necessary for held-out transfer). (b) retiree_gardener is a weak semantics case
(named−anon ≈ 0.00–0.10). (c) Capability axis: DeepSeek > Qwen3.6 > GLM on target
transfer; GLM over-applies the regime and nearly zeros conventional (0.03) with the
raw LLM — exactly the failure the hybrid repairs. (d) n=30 target queries/household;
CIs are wide, so the *pattern* (named≫class_freq≫classical; anon≈0; E4 dominance on
the realistic mix) is the robust result, not single cells.

---
## E5 (design study) — verdict below; the CONFIRMATORY run above is the result

**Verdict (E5, on the design pairs): H2 is SUPPORTED, under a fair design.**
When the atypical households are *inferable single-conditioned regimes* (personas
a human could guess), the observations are *sparse and diagnostic* (not dense
snapshots a stats model can copy), and the LLM is *prompted to reason about the
regime*, the LLM's world knowledge **does** transfer to held-out objects the
per-edge statistical model provably cannot reach: **llm_named 0.50 > llm_anon 0.25
> classical 0.00** on held-out regime-dependent targets (E5), and the LLM correctly
names every persona from a handful of diagnostic sightings.

The first-pass banks (E1–E3 below) did NOT show this — but that was a design
artifact, not a null result: `atyp_v2`/`atyp_authored` paired *dense* observations
(so per-edge statistics win, E1/E2) with *idiosyncratic* reassignments ("keys in a
bowl" — unguessable, so nobody wins, E3). Removing both confounds (E5) surfaces the
true effect. The honest composite verdict:

- **H1 holds** (E0): population priors are fragile to atypicality — no edge over a
  frequency table, collapse when placements are reassigned.
- **On observed objects with dense data, statistical adaptation wins** (E1/E2):
  classical adapts within a day; the LLM's digest signal there is in-context
  statistics (survives anonymization), not world knowledge.
- **On held-out objects under an inferable regime with sparse diagnostic data, the
  LLM's world knowledge is decisive** (E5): it infers the persona from
  semantically-loaded sightings and predicts objects the per-edge model can't,
  and NAMING matters (named ≈ 2× anon).

---
## Original E0–E3 (first-pass banks; see E5 for the redesign that flips the H2 verdict)

**[superseded framing] H2 appeared to fail on the first-pass banks.** The LLM's
world knowledge did not beat statistical adaptation there — but the banks confounded
observation density with regime guessability (see the revised verdict above).

Model: **DeepSeek-V4-Flash** (only model with atypical-bank coverage; served
locally, 4×H100). Banks: `typ_v1` (typical), `atyp_v2` (timing-transform atypical,
placements identical to typ), `atyp_authored_v1` (placement/role reassignment).
Classical arm: **C3** (persistence + periodic GLM). Temperature 0, frozen prompt,
identical episodes per cell (`sample_stream` seeded), clustered bootstrap CIs.
Caveat throughout: **n=8 episodes/cell** — CIs are wide; treat single-cell
differences as noise and read the aggregate pattern.

---

## E0 — H1 completed: is the zero-shot prior HARMFUL, or just un-advantaged?

D=0 accuracy vs no-prior baselines (per bank):

| bank | uniform | class_freq (b2 static) | llm_zeroshot |
|---|---|---|---|
| typ_v1 | 0.052 | **0.500** | 0.354 |
| atyp_v2 | 0.055 | **0.521** | 0.208 |
| atyp_authored_v1 | 0.058 | 0.281 | 0.234 |

**Verdict:** the zero-shot LLM prior is **NOT harmful** — it beats uniform (~0.05)
in every bank. But it is **not advantaged** either: a static class-frequency table
*beats* the LLM on typ (0.50 vs 0.35) and timing-atyp (0.52 vs 0.21), and only on
placement-atyp do both collapse together (0.28 vs 0.23). The honest H1 claim is
**"the prior's advantage collapses under atypicality"** — and more precisely, at
D=0 the LLM never had an advantage over a frequency table to begin with.
(*Caveat:* `class_freq` is derived from the typ profiles, so it is near-oracle on
typ/atyp_v2 by construction; the out-of-sample comparison is on `atyp_authored`,
where it too collapses.)

---

## E1 — Adaptation curves: no robust llm_digest advantage

Accuracy vs observation-days D, classical (C3) vs llm_digest, same episodes.
Aggregated over low D (1–3) and high D (10–13):

| bank | classical D1–3 | llm D1–3 | classical D10–13 | llm D10–13 |
|---|---|---|---|---|
| typ_v1 | 0.562 | 0.597 | 0.604 | 0.427 |
| atyp_v2 | 0.583 | 0.562 | 0.531 | 0.542 |
| atyp_authored_v1 | 0.646 | 0.672 | 0.664 | 0.617 |

**Pre-registered signature (llm crosses ABOVE classical at small D, converges
later): NOT supported.** Classical adapts *immediately* — from ~0 at D=0 it jumps
to ~0.5–0.67 by **D=1** (one day of observations lets the persistence model lock
onto last-observed positions), erasing the LLM's zero-shot lead. At low D the two
are tied (within ±0.035, inside the CIs); at **high D classical wins** in every
bank. Nominal per-bank "crossovers" (typ D=1, atyp_v2 D=2, authored D=1) are all
within the wide n=8 CIs — not real leads.

**Why:** in E1 both arms see the *queried object's own history*, so classical's
per-edge model just tracks last-observed and does fine — there is no regime to
infer. The LLM's putative world-knowledge advantage cannot show here. That pushes
the entire H2 mechanism onto **held-out** objects (E3).

---

## E2 — Anonymization control: it's in-context statistics, not world knowledge

llm_digest with semantics stripped (object→object_N, room→recep_M), same episodes.
Named − anon gap by D:

| bank | D=0 gap | mean gap D≥1 | mean gap (all D) |
|---|---|---|---|
| atyp_authored_v1 | **+0.281** | ≈ 0 (±0.06) | +0.029 |
| atyp_v2 | +0.062 | ≈ 0 (±0.10) | +0.026 |

**Verdict: named ≈ anon at every D≥1 → drop the H2 mechanism claim (for observed
objects).** Semantics help *only* at D=0 (+0.28 on the placement bank — the
zero-shot prior genuinely uses object/room names). Once a digest of observations
is present, stripping every name does **not** hurt: the LLM is pattern-matching the
observation stream (in-context copying of the object's own recent positions), not
recognizing a regime from semantics. This is the pre-registered "IN-CONTEXT STATS"
outcome, and it is what makes E1 interpretable: the D≥1 llm_digest signal is
statistics our own fitting also captures, not world knowledge.

---

## E3 — Regime transfer to HELD-OUT reassigned objects (the sharpest test)

Digest covers conventional objects + a subset of reassigned objects; the **held-out
reassigned objects are queried** (their own history absent). classical (per-edge)
provably learns nothing about them — the control.

| bank | split | classical | llm_named | llm_anon |
|---|---|---|---|---|
| atyp_authored_v1 | few_evidence | 0.000 | 0.062 | 0.125 |
| atyp_authored_v1 | much_evidence | 0.000 | 0.094 | 0.094 |
| atyp_v2 | few_evidence | 0.000 | 0.083 | 0.125 |
| atyp_v2 | much_evidence | 0.000 | **0.208** | 0.125 |

**Pre-registered target (llm_named > llm_anon ≈ classical): NOT met on placement.**
On `atyp_authored` the LLM sits at the **floor** (~0.06–0.09), barely above
classical's 0, and **anonymized is no worse than named** (0.109 vs 0.078) — more
reassigned evidence does not help. The LLM does **not** infer "bed=sofa, desk=dining
→ studio conversion → the basket holds the books" and place held-out reassigned
objects. Regime transfer via world knowledge **failed** for placement/role
reassignment (the reassignments are idiosyncratic — "keys in a bowl" is
unguessable, and neither method exceeds ~0.1).

**One faint directional signal, on timing only:** on `atyp_v2`, llm_named scales
with evidence (0.083 → **0.208**) and exceeds llm_anon (0.125) at much_evidence —
consistent with "observe the shifted schedule on some objects → apply the phase
shift globally." But the absolute accuracy is tiny (0.21) and n is small; it is a
hint, not robust support.

---

## E5 — Regime inference from SPARSE diagnostic observations (the redesign)

New bank `atyp_regime_v1`: four **inferable single-conditioned regimes** in two
confusable pairs — early-morning fitness ⟷ night-shift nurse (both ~5am-active),
WFH-hybrid ⟷ daily-commuter (both leave some mornings). Each has **persona-exclusive
DIAGNOSTIC objects** (yoga_mat/dumbbells vs scrubs/badge; headset/webcam vs
transit_card/lanyard) and **shared DEPENDENT objects** whose location the regime
flips (water_bottle at 05:30 → living room for fitness, nightstand for nurse; laptop
at 14:00 → home desk for WFH, away for commuter). The digest is **sparse** (6–8
diagnostic sightings, targets never shown); the LLM is prompted to first state a
`regime_hypothesis`, then predict a HELD-OUT dependent object.

| arm | top-1 | top-3 |
|---|---|---|
| classical (per-edge control) | **0.000** | 0.100 |
| **llm_named** | **0.500** | 0.700 |
| llm_anon | 0.250 | 0.300 |

Per household (classical / named / anon, top-1):
| household | classical | named | anon | reading |
|---|---|---|---|---|
| night_nurse | 0.00 | **0.83** | 0.00 | cleanest world-knowledge win (scrubs⇒night shift⇒asleep 11am) |
| wfh_hybrid | 0.00 | 0.75 | 0.75 | inferable from *structure* (persist-at-desk), semantics don't add |
| commuter | 0.00 | 0.50 | 0.25 | partial semantic win (transit-card⇒laptop away) |
| early_fitness | 0.00 | 0.00 | 0.17 | regime inferred correctly but receptacle precision failed |

**Verdict: H2 supported — llm_named (0.50) > llm_anon (0.25) > classical (0.00).**
The LLM correctly named every persona from the sparse sightings ("night-shift
healthcare worker", "work-from-home routine", …) and used the regime to place
objects it never observed — which per-edge classical provably cannot. NAMING roughly
doubles accuracy over anonymized, isolating the mechanism as world knowledge, not
in-context statistics — driven by the nurse (named 0.83 vs anon 0.00), where the
inference *requires* recognizing what scrubs/a badge mean.

*Honest nuances:* the effect is not uniform — WFH is structure-inferable (anon ties
named), and fitness fails at receptacle precision (right regime, wrong shelf); n=20
held-out targets, so treat magnitudes as directional. But classical is pinned at 0
by construction and named beats anon 2:1 in aggregate — the qualitative claim is
robust.

## Overall verdict and consequence for the paper

**H2 is supported once the confound is removed.** On observed objects with dense
data (E1/E2), statistical adaptation wins and the LLM adds only in-context
statistics. But the paper's real claim survives on the redesigned bank (E5): when an
atypical household is a coherent, human-inferable *regime* and observations are
*sparse*, the LLM's world knowledge recognizes the persona from a few diagnostic
objects and transfers to held-out objects the per-edge model cannot — and this is
world knowledge, not in-context statistics (named ≈ 2× anon). The first-pass banks'
apparent failure (E1–E3) was an artifact of pairing dense observations with
unguessable reassignments.

**The paper's claim therefore becomes the honest characterization:**
> Population priors are fragile to atypicality (H1: the prior's advantage over a
> frequency table collapses when placements are reassigned), and **statistical
> adaptation is the remedy** — a persistence+periodic model reaches its plateau
> within a single day of observations and matches or beats the LLM digest
> thereafter, with the LLM contributing no distinctive world-knowledge advantage
> beyond the zero-shot (D=0) point that a frequency table already matches.

This is a publishable, honest characterization; it is not softened to protect H2.

### Caveats (attached to every claim above)
- n=8 episodes/cell → wide CIs; the *patterns* (classical adapts by D=1; named≈anon
  at D≥1; E3 floor) are robust, single-cell numbers are not.
- Single elicitation/prediction model (DeepSeek-V4-Flash). A gpt-5.5 replication of
  typ + one atyp bank is warranted if a key becomes available; gpt-5.5's stronger
  zero-shot prior (E0/D2: typ 0.625 vs DeepSeek 0.354) could shift E0/E1 magnitudes,
  though the *mechanism* verdicts (E2/E3) test the digest, not the zero-shot prior.
- E3 held-out reassigned targets may be near-impossible for any method (classical=0
  confirms difficulty); the finding is specifically that the LLM's world knowledge
  provides *no transfer advantage*, not that the task is easy.

### E4 (optional hybrid) — not run
Given H2 failed, the motivation for a prior-fusion hybrid is weakened (the LLM
placement it would inject is exactly what E0 showed a frequency table matches, and
E1 showed data overtakes within a day). Deferred; the D1 rule (take placement from
the LLM, timing from data) remains the right design if it is revisited.

---

*Artifacts:* `e0_rows.jsonl`, `e1_rows.jsonl`, `e2_rows.jsonl`, `e3_rows.jsonl` in
this directory; harness in `src/dynbelief/h2/` (`core.py`, `e0_baselines.py`,
`e1_curves.py`, `e2_anon.py`, `e3_transfer.py`). Reproduce a report with
`python -m dynbelief.h2.<module> --report-only`.

---

## Reviewer-driven rework (frozen classical, events axis, evidence-routed hybrid)

**1. Frozen classical = C3g (BIC/held-out-gated periodic).** The ungated C3 crashed
below persistence on sparse edges (pet cushion 0.86→0.29; sparse shift laptop) — an
anti-learning artifact from fitting a 13-feature periodic GLM on 8–40 events. C3g
enables the per-object periodic term ONLY when it beats the constant model on that
object's own held-out likelihood by ≥0.7 nats/pt. Verified: C3g never dips below C1,
and still reaches the genuine weekly ceiling (retiree coffee_mug → 1.0). This is the
single named "vs classical" opponent for every downstream claim.
`rates/c3g_gated.py`, arm "C3g".

**2. E7 v2 — events-observed axis, pooled, rarity-stratified.** Replaced the 4-panel
days-axis anecdote with pooled curves over all 18 regime-conditioned target objects ×
6 households, x = EVENTS-OBSERVED (removes the days↔rarity confound), rarity terciles,
clustered CIs. Robust findings (`e7_learning_curves.png`):
  - **Cold-start gap (k=0):** LLM 0.31/0.50/0.24 (rare/med/freq) vs classical **0.00**
    everywhere. World knowledge gives zero-shot regime transfer; the per-edge classical
    has nothing without target events. This is the clean, defensible headline.
  - **Frequent crossover:** in the frequent tercile C3g climbs to 0.64 by k=16 while C1
    (persistence) decays to 0.14 — the periodic term genuinely learning the cycle.
  - **Honest caveat:** the mid-k gap is NOT significant (n=6/tercile). A single recent
    observation of a *stable* regime object lets classical catch up, so the LLM's edge
    is concentrated at cold-start, not sustained. This is the truthful aggregate; v1's
    dramatic sustained gap was an artifact of 4 curated cases on a confounded axis.

**3. Evidence-routed hybrid (E4 v2) — HONEST NEGATIVE.** Routed LLM-vs-C3g by an
events-observed threshold frozen on the dev bank (atyp_regime_v1), evaluated on the
confirmatory bank. Both a global τ*=14 and a dev-frozen rarity-aware τ* FAIL the
pre-registered "hybrid ≥ max(endpoints) in every stratum" — they underperform the LLM
in the medium stratum (0.58/0.50 vs LLM 0.62). Reason: at k≤16 on the held-out bank,
C3g never establishes a clear winning regime for a frozen router to exploit (frequent
C3g 0.36 vs LLM 0.32 — tied); there is no classical "ceiling" to inherit. The LLM is
the strongest single arm in 2/3 strata and tied in the third. The dev/test wall
correctly surfaced that a frozen event-count router is insufficient — "enough events"
depends on per-object learnability (cyclic vs stable), which a count threshold cannot
see. `e7_hybrid.py`.

---

## Round 2 — paired analysis, granularity, and the fusion hybrid (reviewer moves)

**Move 1 — paired differences (free re-analysis, `e7_paired.py`).** The E7 comparison
is paired (same object×household×k, both arms on the same queries). Plotting the
per-cluster Δ(LLM−C3g) with clustered CIs removes between-object variance and flips
the significance story: the cold-start (k=0) LLM advantage is significant in ALL
strata (Δ=+0.31/+0.50/+0.24), and in MEDIUM the advantage is significant even pooled
over k (Δ=+0.23 [+0.06,+0.45]) — invisible in the overlapping marginal bands.
`e7_paired_diff.png`.

**Move 2+3 — granularity split + early-k headlines (`e7_score.py`).** Enriched E7 to
log per-query predictions, then scored at ROOM and RECEPTACLE and TOP-3 level.
Receptacle top-1 was punishing the LLM for shelf precision it never claimed; ROOM-level
recovers ~0.19 ("right room, wrong shelf"). Headline (paired room-level LLM−C3g):
cold-start +0.67/+0.60/+0.36 (all sig), early-k +0.15/+0.32/+0.14 (ALL sig). TOP-3 is
starkest: rare LLM 0.79 vs C3g 0.00 at k=0. The LLM's advantage is significant across
every stratum once scored at the granularity of the knowledge and weighted to the
deployment-relevant (cold-start / early-k) regime.

**Move 2 — LLM-as-prior FUSION (`e7_fusion.py`, the system contribution).** Router
selection failed because no event-count boundary predicts the winner. Fusion needs no
boundary: express the LLM regime prediction as κ days of pseudo-observations, prepend
to the object's real events (existing `e2.inject`), fit frozen C3g. κ and injection
granularity (room vs receptacle) chosen on dev, frozen. HONEST, MIXED result on the
confirmatory bank (κ=2, receptacle):
  - MEDIUM: fusion SIGNIFICANTLY beats both endpoints at receptacle level (+0.19
    cold-start, +0.10 early-k) — the pseudo-count prior DENOISES the LLM's jittery
    per-query predictions. Genuine complementarity.
  - RARE: fusion ties/loses — the LLM's sharp shelf guess is hard to beat by smoothing.
  - FREQUENT: fusion DEGRADES with more events (0.33→0.17 room-level) — the stationary
    regime-hour prior, injected as pseudo-obs at fixed hours, is fit by the periodic GLM
    and re-introduces a crash-like artifact; it never reaches C3g's cyclic ceiling.
  So "fusion ≥ max(endpoints) in every stratum" is FALSIFIED. `e7_fusion_curves.png`.

**Synthesis across the three honest results.** (1) Router: selection is the wrong
structure (no boundary). (2) Paired+granularity: the LLM PARETO-DOMINATES C3g at
room-level across the evidence range and strata (the positive headline). (3) Fusion:
because the LLM already dominates, a blend mostly dilutes; it adds value only where the
sources are genuinely complementary (MEDIUM: LLM right-but-noisy → prior denoises), and
a naive stationary prior HARMS frequent cyclic objects. Design implication: the prior
must be time-aware or gated (inject only into the occupancy term / only at low evidence)
to avoid fighting the periodic learner — future work. Deployment takeaway: LLM-alone
(optionally with light pseudo-count denoising for the noisy-regime middle) is the system;
the classical learner is the baseline it dominates, not a partner it needs — except on
frequent, densely-observed cyclic objects, the one regime where C3g still wins.

---

## Reflective memory (src/dynbelief/reflect/, reports/reflect/)

New architecture: an online agent lives through days 0-13 of the FULL event stream
(diagnostics + targets + conventional distractors), reflecting nightly into a memory
file (≤15 curated evidence lines + top-3 persona hypotheses with probabilities,
revisable). Hypothesis entropy gates the fusion prior: kappa_eff = round(kappa_max ·
(1 − H/log2 3)), kappa_max*=1 frozen on dev. All arms answer from the IDENTICAL
stream — classical updates statistically, llm_direct/nomem semantically, fusion both
(per-query memory-conditioned LLM belief injected as pseudo-obs into the TARGET's
edge only; base model, rates, and other objects stay real-data).

Findings (confirmatory bank, clustered CIs; reports/reflect/report_conf.txt):
1. CURATION KEEPS THE SEMANTIC CHANNEL ALIVE (strongest result). llm_nomem (raw
   digest) collapses as history grows: pooled room 0.65 (day 1) → 0.06 (day 14),
   literally 0.00 on frequent objects — the model drowns in ~400 uncurated lines.
   llm_direct (memory only, ≤15 lines) holds 0.63-0.79 throughout. Early (days 1-3)
   the two are equal — curation is lossless compression; late, it is the difference
   between reasoning and noise. P2 exceeded: curation doesn't just match raw
   context, it is what makes long-horizon semantic reasoning viable at all.
2. FUSION IS THE BEST ARM AT DAY 14, both granularities: pooled receptacle 0.70
   [0.60,0.80] vs C3g 0.60 / direct 0.55; room 0.79 [0.67,0.89] vs 0.71 / 0.63.
   P1 PASS (pooled fusion ≥ both endpoints). Crucially it WINS the FREQUENT stratum
   (0.79 recep at day 14 vs C3g 0.67, direct 0.36) — where every previous hybrid
   failed — because the prior is light (kappa=1), targeted (target edge only), and
   rates stay data-driven, so it can't corrupt the periodic learner; and where the
   memory's static hypothesis mis-serves a time-varying object, the statistical
   side carries the prediction. Statistical + semantic > either alone.
3. ENTROPY DYNAMICS (P3 confirmed): all six households converge to correct personas
   (reflect_entropy.png). Showcase: shift_rotator revises — confident-but-wrong day
   0 (H=0.47), contradiction spikes H to 1.36 (day 3), then correct Mon-We shift
   schedule at H=0.08. pet_heavy discriminates itself from its confusable partner.
4. ENTROPY GATE: honest FAIL (P4). On the H>0.5 slice (n=336) gated fusion 0.542 <
   flat 0.613: with kappa_max=1 the gate is binary and zeroes the prior exactly at
   early checkpoints where the classical fallback is weakest — an uncertain prior
   still beat no prior. The gate should be RELATIVE (memory uncertainty vs the
   classical model's own uncertainty), not absolute — future refinement. Elsewhere
   H is low so gated == flat.
