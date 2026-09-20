# situation_sim baselines under the human protocol

Living document: one section per tick of the monitor. Newest first. Numbers come from
`results/situation_sim/<hh>/summary.md` (`python3 -m baselines.situation_eval --run data/situation_sim/runs/<hh> --out results/situation_sim/<hh>`).

## 2026-09-19 · tick 2 · six households (hh_s6–11), 144 questions; λ sweep; Perpetua diagnosis

**Oliver**: no g4 run in the DB yet.

**Pooled results** (`results/situation_sim/hh_s*/summary.json`; per-household floors 38–50%, mean **46%**):

| agent | acc (144 q) | looks/hh | budget/hh | forced/hh |
|---|---|---|---|---|
| HierarchyBackoff + VoI(λ=0.02) | **66.7%** | 17.5 | 32.0 | 2.5 |
| Markov1 + VoI(λ=0.02) | 64.6% | 15.0 | 25.5 | 1.3 |
| MostFrequent / HierarchyBackoff + VoIBudgetPrice | 63.9% | 18–19.5 | 42–44 | 11–12 |
| Markov1 / MostFrequent / Timetable + SequentialSearch | 62.5% | 13–14 | 44–45 | 4–6 |
| Perpetua, Perpetua\* + SequentialSearch | 61.1% | 25 | 30 | 2.5 |
| best NeverSense (floor) | 45.8% | 0 | 0 | 0 |

Marginals: by policy SequentialSearch 60.1% ≈ VoIBudgetPrice 59.4–59.9% ≈ VoI(0.02) 59.1% ≫ VoI(0.05) 50.3% > VoI(0.1) 47.7% ≈ NeverSense 45.8%. By belief HierarchyBackoff 58.6% > MostFrequent 56.7% > SmoothedRecency ≈ Timetable ≈ Perpetua ≈ Perpetua\* ≈ Markov1 ≈ PeriodicPersistence (54.4–55.5%) > DaytypeMixture 53.5% > LastObservation 47.8%. **The belief matters less than whether the agent looks at all**; among lookers the spread is ~7 points, which on 144 questions is at the edge of noise.

**λ**: on hh_s8, λ ∈ {0.005, 0.01, 0.02} all land 15–18/24 for the good beliefs; 0.03+ stops looking (VoI per look is small once a room look costs 1–4). The pacing policy overspends whatever γ is (11–15 forced answers per household at γ ∈ {0.1, 0.25, 0.5, 1.0}) — its λ₀=0.05 start and budget-rate term, not γ, drive it. Under this protocol a policy that *reserves* 1 look per remaining question would be a fairer pacing baseline; none exists in the roster.

**The 20% the baselines cannot answer**: pooled agent accuracy is 68% on spot questions (115 of 144) but **1% on OUT_OF_HOUSE (17 q) and 2% on ON_PERSON (12 q)**. No belief routes mass to the unobservable answers when every spot it knows is empty; only `SequentialSearch` reaches ON_PERSON/OUT via its remainder after a full sweep, and the room-look budget rarely allows a full sweep. The human's move ("keys and shoes are here → she is home → the phone is on her"; "shoes gone → out") is exactly this and it is absent from every model.

**Perpetua / Perpetua\***: they do ingest the empty look (a soft y=0 filter observation per edge), but with the object actually on a person every edge ends near zero and the argmax falls on the spot with the highest fitted rate — often one *just seen empty* (`phone_aisha`: looked at the kitchen, answered `counter_k1`). Their VoI then keeps asking for other spots in the same room (free), 25–45 "looks" per household for 11–30 budget. Diagnosis, not fixed: needs an explicit unobservable-remainder in the prediction, and 4 days is too little history for the periodic filters anyway.

**Question difficulty pooled** (144 q): 40 solved by all 70 agents (object never moved since Wednesday), 34 by ≤3 agents (29 of them ON_PERSON/OUT/first-time moves), 51 in the middle band. So roughly: a quarter is free, a quarter is impossible for these models, half is where beliefs compete.

**Tuning verdict**: no per-household tuning applied (it would be unfair against a single human run); the only defensible change is the λ range (0.01–0.02 instead of 0.05–0.1 defaults) which the room-level cost forces.

**Next**: side-by-side with Oliver's hh_s8 run when it lands; a reserve-per-question pacing baseline; a presence-aware ON_PERSON/OUT remainder as an ablation to quantify how much of the gap is that one inference.

## 2026-09-19 · tick 1 · hh_s8 (Felix & Aisha), first pass, no tuning

**Protocol** (`baselines.harness.RoomLook`, new): walkthrough of every room Wed 18:00 delivered as `room_visit` rows; the page's exact 24 questions (its PRNG ported to Python, verified bit-identical in Node); a Sense of any spot runs as a look at its whole room, cost 1 + 3 travel, free again within the same question; budget 12/day; people in a looked room are listed, pockets are never seen (person senses refused). 10 beliefs × 7 policies = 70 agents.

**Floor**: every belief with NeverSense answers 11/24 = 46% — that is how many questions the Wednesday walkthrough alone still answers on Thu–Sun (things that never moved). Any look-using agent below ~50% is wasting its looks.

**Top agents**

| agent | acc | looks | budget | forced answers |
|---|---|---|---|---|
| HierarchyBackoff(po=5,pc=5,hl=24h)+VoIThresholdSense(lambda=0.02) | 18/24 (75%) | 16 | 43.0 | 5 |
| Markov1(a=1,cut=24h,hl=24h)+SequentialSearch | 17/24 (71%) | 12 | 48.0 | 0 |
| Markov1(a=1,cut=24h,hl=24h)+VoIBudgetPriceSense(gamma=1,lambda0=0.05) | 17/24 (71%) | 16 | 43.0 | 13 |
| SmoothedRecency(hl=6h,freq=24h)+VoIThresholdSense(lambda=0.02) | 16/24 (67%) | 13 | 37.0 | 3 |
| MostFrequentLocation+VoIThresholdSense(lambda=0.02) | 16/24 (67%) | 15 | 39.0 | 4 |
| TimetableLookup(bin=1h,days=all)+VoIThresholdSense(lambda=0.02) | 16/24 (67%) | 15 | 39.0 | 4 |

**Human reference**: Oliver's hh_s0 run (old sim, different household) was 19/24 = 79% with 18 looks / ~42 budget. His hh_s8 run is pending; the same 24 questions will be scored side by side when it lands.

**What the baselines get wrong**

- **ON_PERSON is nearly unsolvable for them**: q04/q08/q20 (`phone_aisha` on Aisha) were answered right by 1–2 of 70 agents. The beliefs put no mass on ON_PERSON unless a search exhausts the house; only `Markov1+SequentialSearch` ends up there (3/3) because its remainder after a fruitless sweep lands on the unsensable answers. The human reasoned 'her keys and shoes are here, so she is home, so the phone is on her' — presence + object co-location inference that no baseline does.
- **Nobody predicts a first-time move**: q17 (`vacuum_cleaner_shared` → coffee table, a tidy-mood/whim placement) 0/70; q06 (`dog_leash_shared` on the entry hook after the morning dog walk) 2/70, yet q10 (same object, same spot, later) 34/70 once a look had shown it. They learn by being told, not by reasoning about activities (dog walk → leash at the door).
- **Budget pacing**: `VoIBudgetPriceSense` forces 11–17 answers per run (budget exhausted early in the day) at gamma 0.5/1.0 — it overspends on morning questions. `VoIThresholdSense(λ=0.1)` never looks at all (VoI per look is small because a look is priced 1–4 and beliefs are confident); λ=0.02 is the useful setting here. λ needs re-tuning for room-level costs; the old receptacle-level defaults do not transfer.
- **Perpetua / Perpetua\*** are weak on 4 days of data (50–62%): they are periodic-persistence models built for weeks of observations; with VoI(0.02) they make 45 looks but only 13 budget worth — mostly free re-looks of the same room in one question, i.e. they keep asking for spots the look already revealed. The belief is not integrating the room-visit evidence as 'seen empty'. Worth checking whether `absence_location` handles room_visit-delivered empties.
- **Whole-room looks change the game**: SequentialSearch with room looks sees 4–9 spots per look, so 12 looks cover most of the house; its errors are now belief errors (wrong room chosen), not coverage.

**Question difficulty** (agents right / 70): 6 questions are solved by all 70 (never moved since walkthrough), 5 by ≤3 agents (three ON_PERSON, a first-time whim, a first-time activity placement). The middle band (11–39/70) is where belief quality matters: `pan_shared` back in the cupboard after cooking (14/70), `toiletry_bag_felix` on the bathroom shelf (19/70), `mug_felix` in the sink (39/70).

**Next**: (1) tune λ ∈ {0.005, 0.01, 0.02, 0.03} and a pacing variant that reserves budget per question; (2) run hh_s6/7/9/10/11 to see whether the ordering holds; (3) look at why Perpetua re-senses seen spots; (4) side-by-side with Oliver's hh_s8 run when it lands.
