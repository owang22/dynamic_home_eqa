# Rate sweep findings: more observation does not help Perpetua, and widens the gap

Authored analysis of `summary.md` and `explainer.md` (both generated) and
the per-rate reports beside them. 2026-09-04. Grid: 0.5x / 1x / 2x / 4x
of the fleet's passive patrol density (3 / 6 / 12 / 24 room visits a
day), 28-day episodes, 20 homes, seeds 0 and 1, models LastObs, Periodic,
DaytypeMix, SmoothedRec, Perpetua, PerpetuaStar, PerpetuaStarFlat and the
routine oracle. Every comparison is inside one age-of-last-sighting band;
homes are never pooled with each other; no cell under 30 questions is
quoted. `explainer.md` defines every term used here.

**Correction to the first pass.** An earlier draft of this file claimed
"per-case accuracies do not move with the rate; only the case mix does."
The decomposition in `explainer.md` refutes that. It is true in two of
the four situations and false in the one that ends up dominating at high
rates. The corrected account follows.

## The three questions

**Does the 12-24 h loss shrink as the rate grows? No, it grows.** The
question-weighted PerpetuaStar minus LastObs difference at 12-24 h is
-0.092, -0.089, -0.137, -0.311 across the four rates, with household
bootstrap intervals that separate 1x from 4x. The earlier paired-median
figure (-0.116, -0.098, -0.017, -0.030) looked like the gap closing; it
was the median over homes of a per-home delta, which flattens as the bin
empties. The decomposition attributes the -0.223 move from 1x to 4x
almost entirely to accuracy changing WITHIN a situation (-0.231), not to
the mix (+0.009).

**Does the 1d+ advantage grow? No, it reverses, and there the mix is the
cause.** At 1-2d the difference goes -0.080, -0.016, +0.059, -0.219, and
at 2d+ +0.049, -0.006, -0.093, -0.252. In these bands the decomposition
puts the move on the mix term (2d+ at 4x: -0.284 of a -0.246 move). The
in-house share of the 1-2d band falls 0.87 / 0.76 / 0.64 / 0.29 as the
rate rises, and Perpetua cannot answer the rest.

**How many days until the fallback share drops below 0.25? Never, at any
rate.** Day-27 shares are 0.61 / 0.54 / 0.53 / 0.52, flat from day 12 at
2x and above; edges never completing two persistence segments go 0.48 /
0.42 / 0.41 / 0.39. Restricted to in-house questions the survival models
sit at 0.45-0.58 in every band at every rate. Two independent signs that
learning is not the bottleneck.

## The mechanism, which is one sentence

Whenever a later visit has found the object's last-seen receptacle empty,
elimination has ruled out every sensable receptacle and LastObs answers
OUT_OF_HOUSE — in 100% of such questions, at every rate. It is then right
exactly as often as the object really is out of the house, and that
fraction rises with the patrol rate: 0.41 / 0.56 / 0.69 at 1x / 2x / 4x
in the "moved away, old spot checked, empty" situation at 12-24 h.
Perpetua has no OUT_OF_HOUSE edge — the pseudo-receptacle is unsensable,
so it is never sighted and no edge is ever created for it — so it cannot
participate, and its accuracy in that same situation falls 0.21 / 0.14 /
0.09 as that situation swells to 69% of the band.

So the extra observations are worth a great deal, but only to a model
that can say "not in the house". Perpetua's own in-house accuracy is
flat. The two rate-invariant situations bracket the model class: where
the object is still where it was last seen and nobody re-checked,
PerpetuaStar scores 0.68-0.76 against LastObs's structural 1.00 at every
rate (its survival prior decays an edge nobody has contradicted); where
the object left, was seen gone and came back, it scores 0.35-0.61
against every classical model's structural 0.00.

## What this changes

- The fleet's 1x result stands but is now explained: 1x is roughly the
  rate at which the came-back situation still outweighs the eliminated
  situation. It is not a sweet spot in the model, it is a property of how
  often that patrol density catches an absence.
- The blocking gap for Perpetua on these banks is not learning and not
  observation volume. It is the missing absence hypothesis. The paper has
  one (a threshold δ on the belief, arXiv 2605.00121 §IV-B.1); our
  absence signal was measured and is not thresholdable as it stands. That
  is the next thing to build, and it is a model change, so it is a
  decision, not a silent edit.
- An exclusion that expires is still worth building as the cheap
  comparator, but it is now clearly the smaller of the two effects.

## Cost

160 banks, 71 minutes wall on four 40-worker pools, about 43 CPU-hours;
the explain stage adds two minutes. Banks are regenerable in two minutes
by `python -m baselines.rate_sweep --stage export` and are gitignored.
