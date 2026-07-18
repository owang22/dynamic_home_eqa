# Active Displacement Probe — SUMMARY (Stage 2)

Budget-constrained active perception (value-of-information over a predictive belief),
replay-only, single-object single-(t_seen,t_query) episodes. Per-look cost; no navigation.

**Scope of this run.** One scene (`ep049w`: 11 rooms, 45 objects, 13 days, chance 0.083,
`max_looks=6`), all four belief tiers, the load-bearing policy cells, 840 episodes/cell over a
28-object stratified mix (8 static / 8 occasional / 12 dynamic). The cross-scene conventions
(C1–C5) are coded and ready; multi-scene is the next pass (see Limitations). Single-scene
already answers the crux questions decisively.

Every number is object-clustered bootstrap 95% CI (n_obj=28). Gaps are paired per-object.

---

## Headline, stated straight

The naive hoped-for headline — *voi beats the checklist on accuracy* — **does not hold**, and
it would have been the wrong result to claim. What holds instead is stronger and more honest:

1. **The predictive belief is load-bearing** (Q3, the anti-hollowing check): `voi` on b3
   beats `voi` on b2 by **+0.064 [+0.018,+0.123]** overall and **+0.08** on dynamic objects.
   VoI does *not* win on any belief — it needs the routine model. b2's decay belief is
   *confidently wrong* on movers, so VoI-under-b2 stops early and answers wrong (0.46 looks,
   0.839 acc on dynamic) while VoI-under-b3 senses the right rooms (0.94 looks, 0.919 acc).
2. **voi's win over the checklist is EFFICIENCY, and it is decisive on the abstention axis.**
   Same accuracy class, a fraction of the looks: voi reaches a correct ELSEWHERE answer in
   **1.1 looks** vs the checklist's forced **6.0**, at 0.94 precision — because its
   routine-conditioned elsewhere-mass lets it abstain *predictively*, which elimination
   structurally cannot. On stable objects voi spends **0.087** looks vs the checklist's 2.8.
3. **The checklist wins raw accuracy** (1.000) by sensing until it physically finds the
   object. voi trades accuracy for looks by design (VoI early-stopping). This is a Pareto
   trade, not a defeat — see the frontier below.

---

## The eight questions

**1. Re-prediction vs elimination (`voi_b3f` vs `sense_until_confident_b3f`).** MIXED, reported
honestly. Overall accuracy gap **−0.069 [−0.121,−0.027]** — the checklist is *more accurate*,
at 2.93 looks vs voi's 0.68. The gap survives budget tightening (−0.166 at max_looks=6 down to
−0.099 at max_looks=2 on the transition bin), so it is a genuine design trade, not only
budget-trivialization: the checklist senses until found; voi stops when VoI says stop. **The
isolable re-prediction win is on ELSEWHERE**: voi reaches a correct abstention in 1.1 looks
where the checklist needs all 6 — the routine model lets voi conclude "gone" without
exhaustive sensing, which pure elimination cannot. Net: voi is **not** more accurate, but it is
far more **look-efficient**, and re-prediction's value is real and concentrated exactly where
the brief predicted (the abstention axis).

**2. Value of acting (`voi_b3f` vs `answer_now_b3f`).** YES, clean. **+0.107 [+0.059,+0.163]**
overall for 0.68 looks. Sharpest in the transition-inside bin: answer_now **0.210** →
voi **0.688** — acting more than triples accuracy where the object moved, at 1.34 looks.

**3. Does the predictive belief matter, or just the policy? (`voi_b3f` vs `voi_b2`).** YES —
the predictive belief matters. **+0.064 [+0.018,+0.123]** overall, **+0.08** on dynamic. VoI on
the decay belief is materially worse *and spends fewer looks doing it* (confidently-wrong →
stops early). The advantage is the dynamics model, not the policy alone. This is the result
most able to hollow the paper, and it stands.

**4. Cross-consistency (does the voi-b3 advantage concentrate on the transition-inside bin?).**
YES, emphatically. 0-transition episodes: every policy ≈1.000 (answer_now 0.998) — nothing to
gain. All of the action is in the ≥1-transition bin (answer_now 0.210 → voi 0.688), the *same
axis where passive Stage-1 b3 wins*. The active advantage lives exactly where the dynamics are.

**5. Discrimination / stable-object control (looks ∝ volatility?).** YES for voi, NO for the
checklist. voi looks by stratum (**b3-fremen**): **static 0.10 / occasional 0.85 / dynamic
0.94** (overall 0.68); b3-schedule_prior spends more everywhere (0.09 / 1.42 / 1.25, overall
0.97) — both near-zero on stable objects. The checklist (b3-fremen): **static 2.8 / occasional
3.9 / dynamic 2.4** — it
over-senses stable objects *as hard as movers* (the wasted-looks-on-stable failure, the dual of
under-sensing). answer_now on a stable object is 0.96–1.0 at zero looks; any sensing there is
pure waste, and only voi avoids it.

**6. LLM prior (`b3(schedule_prior)` vs `b3(fremen)`).** Small, active-side only. Passive:
**+0.001 [−0.007,+0.010]** (null). Active: **+0.013 [+0.001,+0.026]** (CI-separated but small);
schedule_prior voi 0.944 vs fremen voi 0.931, and its abstention F1 is marginally higher
(0.955 vs 0.946). The LLM behavioral prior buys a little when the policy is actively probing,
essentially nothing passively — consistent with it sharpening *where to look* more than *what to
answer*. (Low-data-regime concentration: untested here, single episode — flagged for
multi-scene.)

**7. ELSEWHERE / abstention (AbstainEQA framing).** This is voi's cleanest win. 302/840
episodes (36%) are truly-elsewhere.
| policy | precision | recall | F1 | looks-to-elsewhere | over-abstention |
|---|---|---|---|---|---|
| answer_now b3f | 0.786 | 0.914 | 0.845 | 0.0 | 0.089 |
| **voi b3f** | **0.938** | **0.954** | **0.946** | **1.1** | **0.023** |
| sense_until_conf b3f | 1.000 | 1.000 | 1.000 | 6.0 | 0.000 |
voi lifts precision 0.79→0.94 and cuts over-abstention 0.089→0.023 with ~1 look; it reaches a
*correct* ELSEWHERE at 1.1 looks vs the checklist's 6.0 — a 5.5× efficiency win that is the
direct payoff of routine-conditioned absence. Note our passive recall (0.91) already dwarfs
AbstainEQA's frontier-VLM ~0.43, because our belief models elsewhere-mass *explicitly* — the
setting is different (symbolic belief, not a VLM), and our contribution over AbstainEQA is
exactly the routine-predictable-absence axis their static setting cannot express.

**8. Distance robustness.** Deferred — primary run is `distance_weight=0` per the brief;
`distance_weight` hook is implemented and one flag away.

---

## Accuracy-per-look Pareto frontier (b3f, the primary axis)

| policy | acc | looks | reading |
|---|---|---|---|
| answer_now | 0.824 | 0.00 | free, passive |
| **voi_predictive** | 0.931 | 0.68 | spends looks well — the efficient midpoint |
| sense_until_confident | 1.000 | 2.93 | accuracy ceiling, look-expensive |

All three are on the frontier — none is dominated. The brief expected the checklist to sit
*below* voi; it does not, because with 6 looks on 11 rooms exhaustive-ish search is near-perfect.
voi's defensible claim is **accuracy-per-look** and **abstention-efficiency**, not raw accuracy.

---

## Un-confounding pass (added after review — the decisive findings)

The c-vs-d comparison confounded **belief update** (eliminate vs re-predict) with **stopping
rule** (sense-until-found vs VoI-threshold). Un-confounding resolved two things:

**F1 — With per-object MARGINAL beliefs, negative sensing cannot re-rank candidate rooms
(a theorem about the belief REPRESENTATION, not the task).** Added `predictive_search` =
sense-until-found with re-prediction ordering (the missing 2×2 cell). It produced **identical
sense sequences to the elimination checklist in 810/810 episodes** at k=2 and k=3 — identical
accuracy and looks. This is provable *for our belief tiers*: each maintains a per-object
marginal categorical over rooms, and Bayesian conditioning of a categorical on ABSENT is
zero-out-and-renormalize, which **preserves the relative order** of the remaining rooms. The
scope matters: a belief with latent structure — e.g. a mixture over day-modes,
p(room) = Σ_z p(room|z)p(z) ("breakfast ran late" vs "left early") — WOULD re-rank, because a
kitchen-ABSENT result is evidence about z and updating p(z|¬kitchen) reorders the remaining
rooms. Likewise cross-object evidence (seeing the briefcase gone raises "phone left with it").
Ordering gains therefore require correlated / latent-mode beliefs, which our tiers do not
model — this is our own concrete demonstration of what per-object independence costs (cf. the
FunFact positioning note: pairwise-independent inference misses scene-wide interdependence).
Within the marginal-belief family, predictive-belief value in the active setting lives
entirely in **stopping** and **abstention**, not ordering.

**F1 corollary — the policy space collapses to ONE family.** Given a marginal belief, the
sense ORDER is fixed (belief-ranked); policies differ only in their STOPPING THRESHOLD. The
exhaustive checklist is the threshold→∞ endpoint; voi at each `cost_per_look` is another point
on the same curve; the belief tier selects WHICH curve you are on (b3's curve above b2's — the
surviving anti-hollowing result). `predictive_search` is retired as a named policy (it is
provably identical to the checklist); its code remains as the proof artifact.

**F2 — voi's only robust win is look-EFFICIENCY, not accuracy or abstention quality.** Budget
sweep k∈{1,2,3,4,6} on ep049w (median support s=4):
| k | checklist acc / looks / absten-P | voi acc / looks / absten-P |
|---|---|---|
| 6 | 1.000 / 3.44 / 1.00 | 0.964 / 0.91 / 0.94 |
| 4 | 0.978 / 2.51 / 1.00 | 0.947 / 0.84 / 0.94 |
| 3 | 0.978 / 2.04 / 1.00 | 0.947 / 0.78 / 0.94 |
| 2 | 0.962 / 1.54 / 0.97 | 0.946 / 0.71 / 0.94 |
| 1 | 0.918 / 1.00 / 0.91 | 0.909 / 0.52 / 0.90 |
The checklist's accuracy and abstention precision **degrade gracefully** as budget tightens
(P4 predicted a collapse; it does not collapse — even at k=1 it holds 0.918/0.91). At **every**
budget the checklist is ≥ voi on accuracy and abstention precision. voi is **always** far
cheaper (0.5–0.9 looks vs 1.0–3.4) and reaches correct abstention in fewer looks. So voi wins
efficiency, decisively and robustly; it does **not** win accuracy or abstention *quality* at
any budget.

**Honest thesis (the map, including where we lose).** A time-aware predictive belief enables
**budget-efficient** active localization: it lands within ~1–5 accuracy points of an exhaustive
searcher at ⅕–½ the looks, abstains correctly with far fewer looks, and spends budget
proportional to volatility (near-zero on stable objects). The predictive belief is **necessary
for the stopping quality** (voi-b3 ≫ voi-b2: b2 stops confidently-wrong on movers). It does
**not** help *where* to look — for MARGINAL beliefs the sense order is pinned by the belief
itself (F1), and re-ranking would need latent-mode or cross-object structure our tiers don't
model — and it does **not** beat exhaustive search on *accuracy*. That is the paper —
efficiency + predictive abstention + volatility-proportional sensing — written without
flinching.

## Limitations & next steps (honest)

- **Single scene.** Cross-scene conventions (per-scene-first, pool gaps not levels,
  chance-corrected, fractional-look axis) are coded but need ≥3 scenes with a room-count band to
  exercise. Log the stage1c_v2 scenes and re-run — the runner already supports it via config.
- **Budget/entropy caveat.** On ep049w objects concentrate in few rooms, so `max_looks=0.5·rooms`
  lets the checklist near-exhaustively succeed. The accuracy comparison is therefore not the
  place voi shines; the **frontier and abstention-efficiency are.** A room-count band and
  higher-entropy scenes would firm this up. Do **not** re-tune `max_looks` below the 0.5 spec to
  manufacture a voi accuracy win — report the frontier instead.
- **voi operating point is tunable** (`cost_per_look`, default 0.05): lower it and voi climbs
  toward the checklist's accuracy at more looks. The frontier, not a single point, is the result.
- **Verdict:** proceed. The two claims that must survive scrutiny — *the predictive belief is
  necessary* (Q3) and *the active advantage concentrates on the transition-inside bin* (Q4) —
  both hold with CI separation. The paper's honest framing is **accuracy-per-look + predictive
  abstention-efficiency**, with the checklist as the accuracy ceiling voi approaches at a
  fraction of the cost.
