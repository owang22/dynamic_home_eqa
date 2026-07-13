# Judge label set — how to label

`candidates_to_label.csv` is 60 grounded object-placement candidates drawn
from the 3-scene comparison set (20 per scene), deliberately spanning the
quality range. Each was already scored by the strict LLM judge; your job is
to give each a **human band** so we can measure how well the judge (and its
Phase-2 improvements) agree with you.

## The 4 bands (strict rubric)

| band | meaning |
|---|---|
| **3** | typical — exactly what a real person doing this activity would do; you wouldn't notice it in a photo of a real home |
| **2** | plausible but noticeably less common; needs the household context to make sense |
| **1** | contrived — conceivable but you'd need a story to explain it |
| **0** | absurd — no believable behavioral connection to the activity (e.g. laptop in the fridge, food in the bathroom) |

## What to do

- Edit the **`band`** column. It is **prefilled with the machine's suggestion**
  so you only have to change the ones you disagree with. Overwrite with your
  own 0–3.
- `machine_band` / `machine_band_label` / `judge_score` are the machine's
  suggestion and raw strict-judge score — **read-only reference, do not edit.**
  Leaving them lets us measure human-vs-machine agreement.
- `flag` marks candidates a simple heuristic thinks are obviously
  good/bad (`obvious-positive` / `obvious-negative: <reason>`). It's a hint,
  not authoritative — judge each on its merits.
- Use **`notes`** freely for anything ambiguous or worth remembering.
- Score each candidate **on its own merits**, not relative to the others.

## Columns

`candidate_id, scene, occupant, activity, time_window, object_category,
target_relationship, target_anchor, room, reason, assumed_from,
judge_score, machine_band, machine_band_label, flag, band, notes`

`reason` is the generator's stated justification; `assumed_from` is the
model's guess of where the object was before the move (diagnostic only).

When done, send the CSV back. It will be split into EVAL (~48) and
EXEMPLAR (~12) by a fixed seed — the EXEMPLAR rows are reserved for
few-shot prompting and permanently excluded from every metric.
