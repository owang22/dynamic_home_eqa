# Three mechanism findings, written down before any outcome number existed

2026-09-24, about 21:20. The live wave was a third of the way through and **no outcome
number had been computed for any arm.** Each of these is a measurement of what the arms
WROTE, not of how well they did, and each makes a prediction about the outcome that can
therefore be scored rather than told afterwards.

## 1. WITHDRAWN 2026-09-25: this measured our own display, not the model

**Do not cite this finding.** Everything below it is arithmetically correct and measures the
wrong thing. Each existing note was shown to the model as one run-together line —
`[claim_0001] statement (holds under: X; provisional; 6 sighting(s) for, 0 against; last
revised on day 2)` — and the model copied that whole string back into the condition field.
Real values from that period include `"Day 1-2, 09:00-16:00; provisional; 12 sighting(s) for,
0 against; last revised on day 2"`.

So "96.3% of claims record their condition as exactly `current`, and not one names a routine"
is a fact about our renderer. The display is fixed and notes are now shown as labelled lines;
three nights on `hh_s2_t03` then give `"Tomas is at home and working"`, `"When Tomas leaves
the office"` and `"Ines is at home"`. **Any reading of this field from before 2026-09-25 is
void, in every arm.**

How it got past me, since the lesson is the useful part: I counted how many values were the
string `current` and never read six of the others. A count cannot see that a field is echoing
the display; reading four values can, and did, in about ten minutes. The prediction I built on
this — that keeping rival beliefs cannot help because both would carry the same condition —
may still be right, but it has no evidence behind it until the field is re-measured on the
corrected display.

The original text follows, unedited, because what it claimed matters for reading anything
that cited it.

## 1. (WITHDRAWN) The condition field is degenerate, so two kept rivals cannot be told apart

`holds_under` is the field that records which routine or condition a claim is claimed
for. It is the only thing in a claim that can distinguish an ordinary-routine belief from
a disrupted-routine one, and the prompt's own rationale for keeping both rests on it: *"A
claim about one routine does not have to be undone to write a claim about another."*

Measured over **270 claims** in the claim-store arms past night 15:

| what the model wrote in `holds_under` | share |
|---|---|
| exactly `"current"` | **96.3%** |
| `"set aside for now"` — a *standing* value in the wrong field | 3.7% |
| anything naming a routine, a time, or a condition | **0** |

Not one claim in 270 named a routine.

**Prediction, written before the outcomes.** `rival_beliefs` will raise reachability — more
claims means the true place is present more often — **but will not convert that into
accuracy**, because the reader is handed two contradictory claims carrying the same
condition and nothing to choose between them. If reachability rises and accuracy does not,
this is the mechanism, and the remedy is a prompt that demands a real condition, not one
that demands more claims.

## 2. No arm's memory ever names the disruption, including the arm that was told

Checked across all six arms and sixteen cells past night 15, by regular expression and
then by reading the claim text itself, because a zero from a matcher is the kind of result
this project has been caught by before.

| arm | cells | homes whose notes name the illness |
|---|---|---|
| control | 2 | 0 |
| control_wholesale | 4 | 0 |
| describe_the_person | 3 | 0 |
| rival_and_describe | 3 | 0 |
| rival_beliefs | 1 | 0 |
| **told_unwell** | **3** | **0** |

`told_unwell` was told, in the night-14 prompt: *"Something you have been told, which you
did not see for yourself: resident_1 is unwell and is staying at home instead of going
out."* Its notes do not contain the fact. `describe_the_person` was asked to record
*"whether anything about that pattern has changed lately"* and records object places.

What the notes do contain, verbatim, from `told_unwell/hh_s2_t03` at night 18:
`mug_ines is on the sink in the kitchen`, `charger_tomas is on the bed in the bedroom_1`.
Object and place, nothing else. The one exception found anywhere was a single line in
`describe_the_person/hh_s19_t03`: `resident_2 is at home in the office from 09:00 to
18:00.`

**Prediction.** If `told_unwell` moves any outcome, it will not be through the memory,
because the memory does not carry the message. It could still move the outcome through
that night's edits alone. If it moves nothing, the finding is that telling this system the
world changed is worth nothing — a harder negative than any of the format results.

## 3. The uncapped rewrite is not rewriting

`control_wholesale/hh_s19_t03` at night 19 writes organised prose with times and grouped
categories, far past the eight lines its prompt used to demand, and one home has gone
61 → 774 → 1733 characters over three nights. Two cells have already produced 15 and 17
fact-lines, which no cell could do under the old instruction.

**Prediction, as already recorded in `PREDICTION.md`.** With nothing forcing it to drop
anything the rewrite will accumulate close to monotonically, and the two memory styles
will converge. If they do, the only thing that ever separated them was being made to
choose what to lose.

## The honest caveat on all three

One to four homes per arm, at nights 15 to 23 of 31. These are *mechanism* readings on
partial notes, not results. Finding 1 is the most robust of them — 270 claims, and the
number is 96.3% rather than a marginal split. Finding 2 is a zero across sixteen cells,
verified against the text rather than only the matcher. Finding 3 is the least settled and
rests on four cells.
