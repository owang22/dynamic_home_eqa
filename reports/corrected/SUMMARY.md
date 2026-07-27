# Corrected results (2026-07-26)

Three results whose earlier versions were **artifacts of my own setup**, not of the
models. Each is restated with the bug, the fix, and how the conclusion changed.
Figures in this folder. DeepSeek-V4-Flash unless noted.

---

## C1 — Anonymization: how much of the LLM's edge is *semantic* prior?

`C1_anonymization_corrected.png`

**The bug.** The `llm_anon` arm predicts ANONYMIZED receptacle ids (`recep_3`), but
it was scored against the NAMED ground truth (`craft_desk`). A string comparison of
`recep_3 == craft_desk` is false essentially always, so the arm scored **0.003 —
1/300 — by construction.** Every previous claim that "the LLM collapses without
names" was measuring a scoring bug, not a model. Fixed at
[confirm.py:193](src/dynbelief/h2/confirm.py#L193) by mapping truth through the same
anonymization map before comparison.

| arm | before | **after fix** |
|---|---|---|
| llm_named | 0.500 | 0.433 |
| llm_anon | 0.003 *(bug)* | **0.237** |
| class_freq | 0.377 | 0.377 |
| e4_hybrid | 0.450 | 0.390 |

(`llm_named` moved 0.500→0.433 between identical runs — that is the vLLM
non-determinism noise floor, ≈0.06, not an effect. It applies to every LLM number
in this project.)

**What it actually shows.** Anonymized accuracy is 0.237 — well above the 1/14 ≈
0.071 chance floor, so the LLM *does* extract real structure from co-occurrence and
recency alone. But the named−anon gap is **≈0.20**, and anonymized performance falls
**below the class-frequency baseline (0.377)**. So: roughly half the LLM's headline
accuracy is semantic prior over receptacle names, and once names are stripped it no
longer beats a model that just counts. This **reverses the pre-registration**, which
predicted the anonymized arm would hold most of its accuracy.

### All three models, split by object kind — the asymmetry

| | classical | class_freq | llm_named | llm_anon |
|---|---|---|---|---|
| **DeepSeek** target / conv | 0.000 / 0.000 | 0.106 / 0.783 | 0.422 / 0.450 | **0.361 / 0.050** |
| **Qwen3.6** target / conv | 0.000 / 0.000 | 0.106 / 0.783 | 0.389 / 0.283 | **0.317 / 0.033** |
| **GLM-4.5-Air** target / conv | 0.000 / 0.000 | 0.106 / 0.783 | 0.322 / 0.042 | **0.422 / 0.067** |

`llm_anon` is ~7x better on regime-flipped targets than on conventional objects, in
all three models. This is **not** the anon model being better at the harder objects.
It is a coverage effect, measured directly:

> P(the query's true receptacle is one the digest actually mentions)
> = **0.450 on targets, 0.067 on conventional** (chance = 0.065).

The digest only ever reports DIAGNOSTIC objects, and the persona's routine
co-locates the targets with them. So the digest names the target's answer about
half the time and the conventional object's answer essentially never. An
anonymized model has *nothing but* the digest, so its accuracy tracks that ceiling
(0.361 of an available 0.450 on targets — it converts ~80% of what it's given —
and chance on conventional). Answering "where is the plate" requires exactly the
world knowledge the anonymization removed.

`class_freq` is the exact mirror (0.106 target / 0.783 conventional): it knows
conventions and nothing else. `classical` is 0.000 on **both** kinds — the queried
objects are held out, so it has no edge to fit either way.

*Status: all three models complete with the fix.*

---

## C2 — Per-model calibration: τ and α do not transfer

`C2_per_model_calibration.png`

**The bug.** τ=0.45 and α=6.07 were calibrated on DeepSeek and then frozen across
ALL models. τ=0.45 sits **below Qwen's and GLM's entire confidence distribution**, so
those models could never fire the decision rule — they were pinned into one action.
The resulting "weak models fail with fusion" conclusion was my artifact.

**The fix.** Sweep τ and estimate α per model, on the dev bank only
(`frozen_dev_params.json` → `per_model`).

| model | τ* | α* | reward/hh, old frozen | **per-model** |
|---|---|---|---|---|
| DeepSeek-V4-Flash | 0.45 | 2.72 | 5.73 | 5.26 |
| Qwen3.6-35B-A3B | 0.70 | 2.75 | *(pinned)* | **5.42** |
| GLM-4.5-Air | 0.70 | 0.65 | *(pinned)* | **5.19** |
| classical baseline | 0.75 | — | 5.04 | 5.04 |

**What it actually shows.** With its own calibration, **every model beats classical**
— including both "weak" ones, and Qwen beats DeepSeek. Note the correction is not
uniformly favorable: DeepSeek *loses* 0.47 once α is estimated rather than inherited,
i.e. the old number was partly borrowed optimism. The honest statement is that the
fusion mechanism generalizes across models; the *constants* do not.

**What α does.** α is the precision weight in `w = α/(α+n)`: the number of
observations the LLM's prior is worth. n is the object's own observation count, so
at n=0 the fused belief is entirely prior and at n=α it is a 50/50 blend, decaying
smoothly after. Small α (GLM, 0.65) = "this model's prior is worth less than one
look"; larger α (DeepSeek 2.72, Qwen 2.75) = "worth ~3 looks". α is **estimated from
the model's own dev track record, not tuned for test reward** — that is what makes
the fusion honest rather than a second free parameter.

---

## C3 — P1 at the household level, by day

`C3_P1_accuracy_by_day.png` (typical | atypical panels, no oracle)

**The problem.** P1/P2 were pre-registered over typical vs atypical *households*, but
tested with an object-level split inside the 24 idiosyncratic households — because no
typical-household bank existed. Additionally, the object-level split had a
**query-ordering confound**: `picks` was built as [atypical…, typical…] and zipped
against sorted hours, so every atypical query drew an earlier hour than every typical
one (mean hour 11.5 vs 17.5) and got first claim on the daily resense budget. Fixed
by shuffling before assigning hours ([env.py](src/dynbelief/answer_or_resense/env.py)).
Cross-arm comparisons were unaffected (all arms saw the same ordering).

**The fix.** Authored `version22_typ` — 6 conventional-placement households — and
re-ran P1 at the household level.

**What it actually shows.** The scaffolded LLM beats classical on **both** household
classes, and its edge is **larger on atypical (+0.74) than typical (+0.30)**. This
contradicts P2's predicted direction. The by-day curves show why: the fusion arm's
advantage is concentrated in the **early days** and narrows as the classical model
accumulates evidence — consistent with the design intent. Fusion was built for
**sample efficiency**, not a higher asymptote; the prior buys days, not a ceiling.

---

## C4 — Anonymized learning curves: a NULL, and partly my design's fault

`C4_anon_learning_curves.png` (3 models x {targets, conventional})

Built `h2/confirm_curve.py` to give the anonymization line a real learning axis:
truncate the digest at cutoff D and sweep D, so x = *days of observation available*
and all arms see the identical evidence at each point. (The single-point harness has
no such axis — its digest is built once over days 0-11 and only the query time moves.)

**Result: every curve is flat.** Fitted slopes over D=0..11, targets:
DeepSeek llm_anon +0.003/day, Qwen −0.007/day, GLM +0.001/day. Nothing learns.

**Before reading that as "LLMs can't learn structure", note the design flaw.** The
sweep grows evidence VOLUME but not CONTENT:

| D | digest lines | distinct (obj, recep) facts | distinct receptacles |
|---|---|---|---|
| 0 | 15 | 15 | 9 |
| 3 | 60 | 22 | 16 |
| 11 | 185 | 27 | 19 |

Lines grow 12x; distinct facts grow 1.8x and saturate by D=5. Days 1-11 mostly
*restate* what day 0 already said, because the diagnostic set is fixed at 3 objects
observed at fixed hours. The models correctly gain nothing from repetition.

The defensible claim is therefore **saturation, not incapacity**: persona inference
is essentially complete after the first sighting of each diagnostic object, and 30
further observations add nothing. A genuine learning-rate test needs a digest whose
*content* grows — more distinct objects and receptacles revealed over time — which
this bank's fixed diagnostic set cannot produce. Do not cite C4 as a learning-rate
measurement.

Also note the D=11 point is NOT the frozen confirmatory number: the curve lifts the
2-sightings-per-object cap and uses 4 query days. Same `_SYS`, schema, line format,
CFG, anon maps, and anon scoring fix.

## Standing caveats

- **LLM = best scaffolded implementation.** Raw-log arms are ablations only. An
  earlier "LLM loses in the active setting" result was really two different systems
  (reflection scaffold vs raw log) sharing one label.
- **Noise floor ≈0.06** on any single LLM accuracy number (vLLM non-determinism).
  Differences smaller than that are not effects.
- **Phase-averaged.** All learning curves average over start weekday; a Monday-start
  alignment artifact otherwise produces a spurious hump.
- All hyperparameters frozen on `version22_dev` (4 hh) before any confirmatory call.
