# What a stronger model adds - results as they land

Predictions were written first: EXPECTATIONS.md. Session dynamic-home-eqa-ba. Not for the workshop deadline.
Scripts: `compare.py` (first-room-right by window, live), `notes_on_night.py` (the notes as they stood at the
end of night N), `show_notes.py`. Usage snapshots: `usage_snapshots.txt`.

## 2026-09-30, 23:00 - one household (hh_s2_t03), Sonnet finished, Qwen thinking still early

Settings for every cell: ten_homes banks, 8 questions a day, days 1-31, 3 rooms per question, seed 0.
The resident Tomas is ill on days 14-23 (stays in bedroom/living instead of the office) and back on day 24.

First room right, % of questions (n), all questions, hh_s2_t03 only:

| cell | settled 8-13 | day 14 | 15-17 | 18-23 | day 24 | 25-27 | 28-31 | all |
|---|---|---|---|---|---|---|---|---|
| Qwen plain, log only (wave_log_only, 29 Sep) | 95.8 | 50.0 | 83.3 | 87.5 | 75.0 | 91.7 | 93.8 | 85.9 (248) |
| Qwen plain, log+notes (Table 1, 25 Sep, OLD nightly schema) | 97.9 | 50.0 | 79.2 | 97.9 | 75.0 | 87.5 | 93.8 | 90.3 (248) |
| Sonnet 5.5, log only | 91.7 | 50.0 | 91.7 | 97.9 | 75.0 | 83.3 | 100.0 | 88.7 (248) |
| Sonnet 5.5, log+notes (to day 26) | 93.8 | 62.5 | 91.7 | 95.8 | 62.5 | 85.7 | - | 88.8 (206) |

One household: no claim. A one-question difference on a day is 12.5 points.

**On the two change days the models make the same choices.** Day 14: all four cells search the kitchen,
dining or office first for Tomas's glass, charger and mug (the old routine) and miss. Day 24: all four search
the bedroom first for Tomas's bottle at 10:00 (the illness routine), find it in the office, and from 13:00
answer "office" correctly. The record decides these days, not the model. Neither model anticipates either
change, which is expected: nothing in the record announces it.

**What Sonnet's notes do that Qwen's did not (read from notes.json, night by night):**
- night 15: "Tomas in bathroom 08:15 and bedroom 11:19-11:47, not office ... holds under: Tomas not working in
  office (likely day off/weekend)"
- night 21: "Days 15-21 Tomas not in office ... Long stretch at home, 7 days; maybe leave or changed routine,
  not just weekend."
- night 22: "8 days: routine changed (leave/time off), not just weekend. Expect him in bedroom/living by day."
- night 24 (the return): the SAME note revised to "Days 15-22 Tomas not seen in office; day 24 he is back in
  office all day ... holds under: Tomas away from office routine on days 15-22; back to office work by day 24".
  It closed the episode on the first night back. With Qwen, 3 of 8 told runs dropped the illness condition
  within three nights (-37's measurement), and those were TOLD.
- It never names illness (it is never told), and calls the spell "leave/time off".

**What it does badly:** about half its notes are snapshots of one moment ("Day 22 14:29 kitchen: bowls, ...
in cupboard ..."), which the prompt asks it not to write (the record already holds them). It never sets a
note aside: 69 notes standing by night 26, growing by ~2-3 a night.

**The notes still add nothing measurable on top of the record:** Sonnet log+notes 88.8 vs Sonnet log only
88.7 over the same days. Same as Qwen. A model that understands the change does not convert that
understanding into better first guesses here, because the record already shows where each thing was last
seen, and the change days are decided by the first sighting after the change.

**Does it lose context it had before?** Not that this household shows: on day 24 it returns to the office
after one sighting, same as Qwen, and its pre-illness office notes were still standing. So the long-lived
agent (Oliver: try it "if it seems like the agents are losing context they knew before") is not triggered yet.

**Cuts to schema limits (Sonnet):** only `supporting_observation_ids` lists cut to the 6-item limit (Qwen's
grammar enforces the same limit). No reasoning or note text has been cut. So the note limits were not relaxed
(Oliver: only if reasoning is consistently cut short).

**Usage:** weekly all-models went 37% -> 39% across ~1.8 Sonnet households plus everything else running on the
account; so at most ~1% of a week per Sonnet household.

**Next:** Sonnet on hh_s19_t03 and hh_s20_t03 (next two in the study's fixed order, not chosen by result),
plain-Qwen log+notes reruns on all three under today's code, Qwen thinking (4,000 cap) on hh_s2 overnight.

## 2026-09-30, ~23:05 - hh_s2 plain-Qwen rerun landed; Sonnet on hh_s19 / hh_s20 past the return

**Correction to the cuts line above:** besides the evidence-id lists, 6 note statements across all Sonnet calls
so far were 3-20 characters over the 240-character limit and were cut to it. No `why` (reasoning) field was cut.
Still not "reasoning consistently cut short", so the limits stay.

**Plain Qwen, log+notes, rerun under today's code (hh_s2):** 85.9 first room right / 95.6 found within 3,
against the Table 1 cell's 90.3 / 97.6. The gap is days 28-31 (81.2 vs 93.8; movers 70.6 vs 94.1).
Mechanism, from the answers: during the illness Qwen revised a standing rule to "Tomas moves his charger from the
office desk to the bedroom at the end of the work day" and never withdrew it; after the return 4 of its 9
first-room misses on days 25-31 cite that rule and look in the bedroom first. Qwen's notes during the illness
overwrote where things are "kept" ("Tomas's vitamins are kept on the bedroom nightstand ... holds under: Tomas is in
the home") and on the first night back changed nothing.

**Sonnet's misses after the return have a different cause:** each is a guess from recent sightings about the
evening routine ("on days 24 and 27 the mug moved from the office desk to the kitchen sink in the evening"),
none cites the illness, except day 24's first question (unknowable for every model).

**Sonnet on two more households, what its notes did with the change (nothing told):**
- hh_s20 (Hana): night 15 "Daytime may be a home/off day; check people present"; night 16 "Home days may come in
  runs; check which room Hana is in first"; night 17 "Days 15, 16, 17 Hana home: bedroom ~10-12 ... living from ~14
  through evening ... Check bedroom before noon, living after." It tracks her medication moving bathroom -> bedroom
  but never concludes she is ill. At the return (night 24) it folded the spell into a standing note as "Some days
  (22-23) she works from living/bedroom instead" - it did NOT close the episode as cleanly as on hh_s2.
- hh_s19 (Marco): from night 14 a note "Marco is home by 16:05 / 13:57 / 12:53 on weekdays ... weekday afternoon when
  Marco is home". It treats it as a pattern of his, never as a change, and has no note marking the return.
So the clean "away days 15-22, back by day 24" closure is one household of three so far.

**Bar for any single-household difference here:** the project's rerun floor (identical prompts, temperature 0,
seven households, days 0-13) is 1.9 / 2.2 points as a MEAN over households, but 6.2 / 7.3 for the largest single
household (figures from -37, 30 Sep). Over 31 days a single divergent note compounds further. So every
one-household gap in this file under ~6 points is not distinguishable from a rerun. Claims wait for the
three-household paired comparison, read against that spread.

## 2026-09-30, 23:15 - Sonnet finished on three households (hh_s2, hh_s19, hh_s20)

Paired within household, `paired.py`. Difference in first-room-right points, standard error over the three
households, and how many households share the sign. Qwen log only is the 29 Sep wave_log_only cell (current code).

| Sonnet log only minus Qwen log only | all 1-31 | settled 8-13 | illness 14-23 | 15-17 | return 24-31 |
|---|---|---|---|---|---|
| all questions | +4.8 (se 1.8, 3/3) | +1.4 (3.0, 2/3) | **+8.8 (2.2, 3/3)** | +11.1 (5.0, 3/3) | +2.1 (1.0, 2/3) |
| movers only | +5.8 (1.2, 3/3) | +0.9 (4.0, 2/3) | **+13.6 (1.3, 3/3)** | +22.4 (1.4, 3/3) | +3.4 (3.8, 2/3) |
| found within 3, all | +3.5 (2.8, 2/3) | +1.4 | +5.0 (5.6, 1/3) | +6.9 | +0.5 |

Sonnet log+notes minus Sonnet log only: +0.8 (se 0.4) all days; illness +0.8; return -0.5. The notes add nothing
measurable for Sonnet either.

**Prediction 2 was wrong.** I predicted Sonnet log-only within a few points of Qwen log-only. It is level when
nothing is changing (settled +1.4) and clearly better in the days after the change. The illness-window difference
clears 2 SE (8.8 vs 4.4) and the 1.9 rerun floor, same sign in 3 of 3; but three households, one cell each, and
the Qwen cells come from a different session (29 Sep). The 15-17 window was named in the predictions before the run.

**Mechanism, read from the 16 questions on days 15-19 where the two disagree on the first room:** Sonnet is right
13 times. In those it either trusts the newest sightings when they break with the long history ("Since day 15 the
bottle has been on the bedroom nightstand every time I saw it ... The pattern shifted around day 14") where Qwen
goes by the long-run majority and calls the new sighting "an outlier"; or it uses time of day (dining table at
dinner) where Qwen uses the commonest room. Qwen is right 3 times, each where Sonnet predicted an evening move a
little early.

**It is not that Sonnet looks in more places:** it opens 4-13% fewer rooms a day (it finds things sooner). The two
records do differ, because each model chooses where the robot looks: e.g. hh_s20 glass_aisha before day 15 20:33 -
Qwen's record 17 sightings, all kitchen (it said "17/17", which was TRUE of its record); Sonnet's record 23, 9 of them
dining in the evening. Distinct object-room pairs in the record: Sonnet +10, +2, +8 over Qwen. Small.

**Usage:** weekly all-models 37% before, 41% after all six Sonnet cells (~1,900 calls), with everything else on the account running too; the 5-hour window went 0% -> 25%. So at most ~0.7% of a week per Sonnet cell.

## 2026-09-30, ~23:50 - independent audit; the mechanism claim above is WITHDRAWN

An auditor subagent with no context recomputed everything from the raw files with its own code. Confirmed: the
numbers (+8.8 illness, se 2.2, 3/3; movers +13.6), that the comparison is paired question by question (same ids,
objects, times, true rooms), the settings (same banks, budget, seed, days; no src/self_improve change between the
runs), and no leakage (10 of Sonnet's right first guesses on days 14-17 each backed by an earlier sighting in its
own record).

**Not supported, and I checked it myself:** "Sonnet trusts the newest sighting where Qwen goes by the majority".
On days 14-23, when the newest sighting and the commonest room in the model's own record disagree, both models open
the newest room first equally often (Qwen 65 of 84, Sonnet 65 of 86). When they agree, the newest sighting is the
right room more often in Sonnet's record (135 of 154) than in Qwen's (121 of 156). So a large part of the gap is
that Sonnet's own earlier choices left it a fresher record, not that it reads the same record differently. My 16
hand-read disagreements were too few and I read them as the story I expected.

Other points from the audit, accepted:
- "level outside the illness" is weak: days 8-13 is +1.4 with se 3.0 (cannot exclude ~7 points); hh_s20 is already
  +6.2 there. Against days 1-13 the extra gain during the illness is +8.8, +3.1, +3.8 (mean +5.2).
- 8.8 / 2.2 = 4.0 clears the project's 2-SE bar (the permissive one) but not a t-test with 2 degrees of freedom
  (4.30). The movers se of 1.3 rests on three numbers.
- Supported wording: "Sonnet was ahead during the illness in all three households." Not supported yet: the size,
  or that it reasons better on the same evidence.

**What separates the two, running now (`src/stronger_model/swap_records.py`):** each finished log-only cell is
replayed by feeding back its own recorded choices (verified: the replay reproduces every question's rooms opened
and finds, all 6 cells), recording the exact prompt behind each question's first room choice. The replayed Qwen
prompts hit the shared cache and return Qwen's own first room 744 of 744 - the prompts are byte-identical. Then each
model answers the OTHER model's prompts: a two-by-two of who reads by whose record (`swap_scores.py`).

Side finding: the cache is last-writer-wins. On day 1 the log-only and log+notes prompts are byte-identical (both
notes blocks empty); the two Sonnet cells ran at once and Sonnet is not deterministic, so one cell's entries were
overwritten by the other's answers. The runs themselves are unaffected (each used its own answers); only an exact
cache replay drifts. The same can happen to any two concurrent Qwen cells (vLLM is not deterministic either).

**Notes vs no notes, split by whether the two arms opened the same rooms (method from -37, 30 Sep):** for Sonnet
on three households, the two arms open identical room sequences on 682 of 744 questions (91.7%), with identical
first-room-right there (94.4 / 94.4, the expected data check). On the 62 questions where they diverge, log+notes
38.7 vs log only 29.0 - about 6 questions, not separable from noise. So for Sonnet too, "notes add nothing" is a
pooled number diluted by the questions where the notes cannot matter; the notes change the search on ~1 question
in 12 and may help a little there. (For Qwen, -37 measured 13.5% divergent, +2.7 there, over ten households.)

## 2026-09-30, ~23:55 - same-record swap, first half: Sonnet reading Qwen's records

`swap_scores.py`. First room right on Qwen's own record (its exact first-choice prompts), Qwen's answers from its
run vs Sonnet's fresh answers to the same prompts. Paired over three households:

| Sonnet minus Qwen, same (Qwen's) record | all 1-31 | settled 8-13 | illness 14-23 | 15-17 | return 24-31 |
|---|---|---|---|---|---|
| all questions | +2.8 (se 0.5, 3/3) | +0.7 (1.4, 2/3) | **+4.6 (1.8, 3/3)** | +6.9 (2.8, 3/3) | +1.6 (1.6, 2/3) |
| movers | +4.3 (0.6, 3/3) | -0.2 (3.2) | +9.8 (3.9, 3/3) | +12.8 (4.8, 3/3) | +1.6 (3.5) |

Per household, illness: hh_s2 +7.5, hh_s19 +5.0, hh_s20 +1.3.

**Sonnet's own rerun floor** (`sonnet_rerun_floor.py`, its own first-choice prompts days 8-23 re-asked with a fresh
cache, 384 calls): same first room on 95.1% (settled) and 95.0% (illness) of questions; first-room-right changes by
+0.7 / -0.8 points on average, at most 2.5 in any household-window. So two of the three household reader effects
(7.5, 5.0) are well outside Sonnet's own rerun spread; hh_s20's 1.3 is not.

Reading so far: on the same record, Sonnet's first guesses are better during the illness by about +4.6, roughly half
of the end-to-end +8.8; the rest would be the fresher record its own looking built. The other half of the two-by-two
(Qwen reading Sonnet's records) is running and decides whether that split holds.

## 2026-09-30, ~23:59 - the full two-by-two: who answers, by whose record

`swap_scores.py`. First room right; the record was built by one model's own looking, the first room was chosen by
the other or the same model from exactly the same prompt. Own-record cells are the runs themselves; swapped cells
are fresh answers (Sonnet: 744 calls; Qwen: 744 calls on the local server). Mean over three households, days 14-23:

| | Qwen's record | Sonnet's record | effect of Sonnet's record |
|---|---|---|---|
| Qwen answers | 80.8 | 87.1 | +6.2 (se 2.2, 3/3) |
| Sonnet answers | 85.4 | 89.6 | +4.2 (se 3.6, 2/3) |
| effect of Sonnet answering | +4.6 (se 1.8, 3/3) | +2.5 (se 0.0, 3/3) | |

Whole month: answering +2.8 (Qwen's record) / +0.4 (Sonnet's record); record +4.4 (Qwen answering) / +2.0 (Sonnet
answering). Settled days 8-13: answering +0.7 / -2.8; record +4.2 / +0.7, all with se 1.4-5.2.

**What it says (wording revised after -37's review).** Lead finding: in ordinary times Sonnet's value is in where
it looks, not how it answers (settled answering effect about zero). During the change the record component is above
both rerun floors on both paths (+4.2, +6.2); the answering component runs from AT Sonnet's floor (+2.5, on its own
record) to clearly above it (+4.6, on Qwen's poorer record) - so the answering gain is contingent on the record being
poor. The two paths close on the same end-to-end number (+4.6 then +4.2; +6.2 then +2.5; both 8.8). Earlier phrasing,
kept for the record: During the change both parts count and they roughly add: Sonnet answers the same record better by
+2.5 to +4.6, and its own room choices leave a better record worth +4 to +6. Together that is the end-to-end +8.8.
Outside the change Sonnet does not answer better (on its own record Qwen is 2.8 ahead in the settled days, se 3.7),
and on hh_s20 Qwen answering from Sonnet's record (89.5 over the month) beats Sonnet's own run (88.3). So most of
what Sonnet adds in ordinary times is in where it chooses to look; during a change, it adds by both.

**Floors.** Sonnet re-asked its own prompts: same first room 95%, accuracy within 2.5 points per household-window.
Qwen's fresh answers on Sonnet's records carry Qwen's rerun spread (mean 1.9, up to 6.2 per household). The
"+2.5, se 0.0" reader effect on Sonnet's record is three households each at +2.4 to +2.6, i.e. about 6 questions
of 240 each - it is at the edge of both floors. Three households throughout.

**Not yet identified:** what in Sonnet's looking makes the record better. Its rooms opened per day are fewer, so it
is which rooms and when, not how many.

**Method note (for -37 and the paper):** this swap is the test that separates "answers better from what it has" from
"collected better evidence" for any two arms that choose their own looks. It needs: a replay that follows the
cell's own recorded choices (not the cache), a check that the replay reproduces every question, a check that the
replayed prompts are byte-identical (Qwen: 744/744 cache hits returning its own first room), and a rerun floor for
whichever side answers fresh.

## 2026-10-01, ~00:05 - a caution on the Qwen log-only reference, and a fresh rerun

With all three plain-Qwen log+notes reruns in: during the illness Qwen log+notes beats Qwen log only by +7.9 (se 1.8,
3/3); on the questions where the two open different rooms, notes 26 right vs log-only 7. But the wins I read cite
record patterns (e.g. Aisha's glass on the dining table in the evening) that the log-only run's record never had,
and Qwen log+notes during the illness (87.5, 91.2, 87.5) is level with Sonnet log only (91.2, 88.8, 88.8). The Qwen
log-only cells used as the reference everywhere above are ONE run each from a different session (29 Sep). If they
were unlucky runs, Sonnet's end-to-end lead over Qwen is partly that luck (the same-record swap is not affected:
it compares answers to identical prompts).

Running: Qwen log only rerun on the three households with a FRESH cache (llm_prior_cache/stronger_model/
qwen38_plain_fresh, so nothing is replayed), out results/stronger_model/qwen38_plain_rerun2. This is also the first
31-day rerun floor for Qwen on this arm.

## 2026-10-01, ~00:25 - fresh Qwen log-only reruns: the end-to-end Sonnet lead was half a lucky reference

Qwen log only rerun on the three households with a fresh cache (results/stronger_model/qwen38_plain_rerun2/), same
code and settings (verified: the 29 Sep run's first-choice prompts are byte-identical to the rerun's until the two
runs first choose differently, at question 5 / 18 / 10). Rerun minus the 29 Sep run, first room right (found within 3):

| | whole month | days 1-13 | illness 14-23 | return 24-31 | identical room sequences |
|---|---|---|---|---|---|
| hh_s2 | +2.8 (0.0) | +1.0 | +6.2 (0.0) | +1.6 | 217/248 |
| hh_s19 | +1.6 (0.0) | 0.0 | +2.5 (0.0) | +3.1 | 242/248 |
| hh_s20 | +0.8 (0.0) | +1.0 | +5.0 (+5.0) | -4.7 (-6.2) | 223/248 |

This is the first 31-day rerun floor for Qwen on this arm. Days 1-13 agree with the old floor (about 1 point); the
illness window spreads 2.5 to 6.2 points per household from rerun alone, the window where every effect of interest
here lives. All three in the same direction is 1 chance in 8; the prompts match, so I read it as chance, not a
setting difference.

**Corrected end-to-end comparison, first room right, days 14-23:** Sonnet log only minus Qwen log only is
**+8.8 (se 2.2, 3/3) against the 29 Sep Qwen run and +4.2 (se 1.7, 3/3) against the fresh rerun**. Whole month +4.8
vs +3.1; settled +1.4 vs +0.7. Sonnet is ahead during the change in all three households against both Qwen runs; the
size is +4 to +9 depending on which Qwen run is the reference, and two Qwen runs differ by 4.6 on average here.

**Consequence for the two-by-two above:** it used the 29 Sep run as "Qwen's record". The answering effect on that
record (+4.6) compares answers to identical prompts, so it stands, but it was measured on a record now known to be a
weak one, which fits "the answering gain is contingent on the record being poor". The record effect (+6.2 / +4.2) is
likely inflated by the same weak record. A cleaner two-by-two would use the fresh rerun's record as well; not run.

**Plainly, what survives tonight:** with the same prompts Qwen gets, Sonnet is at least as good everywhere and better
during a change in the routine by roughly 4 points of first-room-right (about 3 questions in 80 per household), in
three households of three; it notices and describes the change in its notes without being told; its notes do not
add measurable accuracy. Everything else in this file about sizes should be read against a 31-day rerun spread of
up to ~6 points per household in the change window.

## 2026-10-01, 00:45 - the two-by-two redone on the fresh Qwen record (suggested by -37)

Same method; Qwen's record is now the fresh rerun's (prompts verified byte-identical, 744/744 own first room from its
own cache); Sonnet answered its 744 first-choice prompts. Days 14-23, first room right, mean over three households:

| | on the weak 29 Sep Qwen record | on the fresh Qwen record |
|---|---|---|
| Sonnet answering the same record, minus Qwen | +4.6 (se 1.8, 3/3) | +1.7 (se 0.4, 3/3) |
| Sonnet's record minus Qwen's, Sonnet answering | +4.2 (se 3.6, 2/3) | +2.5 (se 1.9, 2/3) |
| Sonnet's record minus Qwen's, Qwen answering | +6.2 (se 2.2, 3/3) | +1.7 (se 1.7, 1/3) |

Against a typical Qwen run both components fall to about 2 points, each within the rerun floors (Sonnet: up to 2.5
per household-window; Qwen: 2.5-6.2 in this window). The answering gain was largest on the weak record (+4.6 vs +1.7),
consistent with "a stronger model helps most when the evidence is poor", but that is one weak record, not a test.

## Where this stands (for Oliver, morning of 1 Oct)

1. **Qwen3.8 with thinking works with structured output** on vLLM 0.25: the grammar applies after </think>; cap the
   thinking with `thinking_token_budget` (uncapped: 6k tokens a room choice, 23k a night); name the answer fields in
   the system message. Client: `src/stronger_model/clients.py`. Full runs on hh_s2 (4,000 cap) still going overnight.
2. **Sonnet given exactly Qwen's prompts** (fresh `claude -p` per call, no tools, no settings; ~500 tokens of harness
   context it cannot avoid): at least as good everywhere; during a routine change ahead by about 4 points of
   first-room-right against a fresh Qwen run (+4.2, se 1.7, 3/3), +8.8 against the older Qwen runs. Half of my first
   headline was the baseline moving.
3. **Why it is ahead is not resolved** at three households: better answering from the same record and a better
   record from its own looking each come to ~2 points against a typical Qwen run, inside rerun noise.
4. **Behaviours worth showing** (qualitative, from the notes): it notices the change without being told in all three
   homes ("routine changed (leave/time off), not just weekend"); in one it turns it into a search rule ("Check bedroom
   before noon, living after"); in one it closes the episode the night the resident returns; it never infers illness.
   Qwen instead rewrites illness-time habits as permanent facts and keeps them, costing 4 first guesses after the
   return on hh_s2. But Sonnet's notes are half diary snapshots, never pruned (69 notes by night 26), and they add
   no measurable accuracy (+0.8; they change the rooms opened on 8% of questions).
5. **Method results that matter beyond this strand:** a 31-day Qwen rerun moves first-room-right by 2.5-6.2 points
   per household inside the change window (about 1 outside it); the response cache is last-writer-wins, so replays
   must follow the cell's recorded choices; the same-record swap (`swap_records.py`) separates answering from looking.
6. **Not done:** Opus; the long-lived agent (no sign of lost context, so not triggered); relaxing note limits (no
   reasoning was cut); more households (the decisive next step for any size claim).
7. **Usage:** weekly all-models 37% before any of this, 45% at 00:48 (all sessions on the account included); ~4,500 Sonnet calls in total.

## 2026-10-01, 02:10 - Qwen3.8 WITH thinking (4,000-token cap), log only, hh_s2 finished

280 calls, 3.5 h, ~800 thinking tokens a call on average, the cap reached on 4 calls. hh_s2, log only, first room right:

| | all | settled 8-13 | illness 14-23 | movers, illness | return 24-31 | found within 3 |
|---|---|---|---|---|---|---|
| Qwen plain, 29 Sep | 85.9 | 95.8 | 82.5 | 65.8 | 90.6 | 96.8 |
| Qwen plain, fresh rerun | 88.7 | 97.9 | 88.8 | 78.9 | 92.2 | 96.8 |
| **Qwen thinking** | **91.9** | 95.8 | **92.5** | **84.2** | 92.2 | 98.4 |
| Sonnet | 88.7 | 91.7 | 91.2 | 81.6 | 90.6 | 98.8 |

One household: +3.2 over the fresh plain rerun for the month, inside hh_s2's own whole-month rerun spread (2.8);
prediction 1 (thinking within ~2 points of plain) is not confirmed either way yet. Thinking and plain (fresh) differ
on only 7 first rooms in the illness; thinking wins 5. Its traces in the wins weigh staleness explicitly ("Office is
habitual but stale"; "That recent shift away from its usual office desk suggests Tomas has been spending time..."),
use today's empty looks to rule rooms out, and put rough probabilities on the remaining rooms ("Kitchen ... 0.45 ...
Bedroom ... 0.35"). Its two losses are on days 14-15, still trusting the old meal pattern.

Running: thinking log-only on hh_s19 and hh_s20 (~3.5 h each), and thinking log+notes on hh_s2 (day 17 at 02:08).

## 2026-10-01, 04:35 - Qwen thinking, log+notes, hh_s2 finished

311 calls, 5.9 h, thinking cap reached on 9 calls. First room right, hh_s2: all 89.1, settled 93.8, illness 91.2,
return 85.9, days 28-31 90.6 - identical to Sonnet log+notes on this household, and below thinking log-only (91.9;
return 92.2). Plain Qwen log+notes (rerun): 85.9 / illness 87.5 / return 82.8.

**Its notes are a third style.** Not Qwen-plain's short rules, not Sonnet's diary-plus-episodes: a ledger of latest
positions with explicit staleness - "Prefer the bedroom bed now unless a later check moves it", "Kitchen, office,
living ... remain unconfirmed; use older defaults cautiously", "Do not guess; check bedroom/entry or ask", and a
nightly "Day N routine: who was where". It never names the change as a change; at the return it records "Day 24
routine: Tomas in office 10:24-16:11" as one more day. Two of its post-return first-room misses cite the illness
habit (d25 charger: "On recent mornings it has often still been in bedroom_1 (day 21 ... day 23)"; d30 glass: "from
day 14 through day 24 it was repeatedly on the bedroom nightstand"). One household; the notes-vs-no-notes gap for
thinking (-2.8 month, -6.3 return) is inside the rerun spread.

## 2026-10-01, 06:20 - Qwen WITH THINKING on all three households: the largest gain of the night

All runs finished; vLLM server stopped at 06:17. Log only, first room right, per household (s2 / s19 / s20) and mean:

| | whole month | settled 8-13 | illness 14-23 | return 24-31 |
|---|---|---|---|---|
| Qwen plain, 29 Sep | 85.9 / 86.7 / 79.8 = 84.1 | 90.3 | 80.8 | 88.5 |
| Qwen plain, fresh rerun | 88.7 / 88.3 / 80.6 = 85.9 | 91.0 | 85.4 | 88.5 |
| **Qwen thinking (4,000 cap)** | **91.9 / 92.3 / 88.3 = 90.9** | **93.1** | **90.4** | **92.7** |
| Sonnet 5.5 | 88.7 / 89.9 / 88.3 = 89.0 | 91.7 | 89.6 | 90.6 |

Paired over the three households:
- thinking minus plain (fresh rerun): month **+5.0 (se 1.4, 3/3)**, illness **+5.0 (se 0.7, 3/3)**, settled +2.1 (2.4,
  2/3), return +4.2 (2.8, 2/3). Against the 29 Sep plain runs: month +6.7 (0.9, 3/3), illness +9.6 (0.4, 3/3).
  The month figure clears 2 SE and the 31-day rerun spread (whole month 0.8-2.8 per household); 3/3 against both plain
  runs.
- Sonnet minus thinking Qwen: month -1.9 (se 1.0, 0/3), illness -0.8 (1.8, 1/3), return -2.1 (0.5, 0/3).

**Prediction 1 was wrong.** I predicted thinking would land within ~2 points of plain Qwen. It is the largest gain of
the night: switching thinking on (with a 4,000-token cap) makes the local model at least as good as Sonnet 5.5 with
the same prompts, in all three households.

Caveats: one thinking run per household (its own rerun spread is unmeasured; plain Qwen's is up to 6.2 points per
household in the change window); the thinking runs carry one extra system-prompt line naming the answer fields
(nothing about the home); cost is ~3.5 h of GPU per household for log only against ~15 min plain; log+notes with
thinking ran on hh_s2 only (89.1, below thinking log-only's 91.9 there).

## Where this stands (replaces the summary above), 06:20, 1 Oct

1. **Thinking is the cheap big win.** Qwen3.8 with thinking, capped at 4,000 tokens, with JSON enforced after the think
   block: +5.0 first-room-right over the month and during the change, 3/3 households, and level with or above Sonnet.
   How: `src/stronger_model/clients.py` QwenThinkingClient; vLLM 0.25, `thinking_token_budget` in the request body.
2. **Sonnet with the same prompts** is about +3 over plain Qwen (+4 during the change, 3/3), but not better than
   thinking Qwen. Why it beats plain Qwen (better answering vs better looking) is not separable at three households.
3. **What the stronger models do differently, from their own words:** both thinking Qwen and Sonnet treat an old
   habit as stale once newer sightings break from it, and use today's empty looks to rule rooms out. In its notes,
   Sonnet alone names the change and (in one home of three) closes it on the return; thinking Qwen keeps a ledger of
   latest positions; plain Qwen rewrites habits as permanent facts and keeps illness-time ones after the return.
4. **Notes do not add accuracy** for any model here (and with thinking they cost points on hh_s2 after the return).
5. **Method:** a 31-day rerun moves plain Qwen 2.5-6.2 points per household inside the change window; single runs per
   household cannot resolve effects of this size there. The cache is last-writer-wins. The same-record swap separates
   answering from looking.
6. **Not run:** Opus; the long-lived agent (no lost context seen); relaxed note limits (no reasoning cut); more
   households and repeat runs (the next step for any size claim); thinking on the told arms.

**Qualification (06:35, after -37's review), applies to the thinking table above.** The whole-month +5.0 (per household
+3.2 / +4.0 / +7.7) clears the measured whole-month rerun spread (0.8-2.8) and stands. The illness-window +5.0 is the
same size as the change-window rerun spread of a single household (2.5-6.2), and its se of 0.7 cannot see run-to-run
noise: with one run per condition per household it only measures how consistent the difference is ACROSS households.
Until repeated, the illness figure reads "same size as the change-window rerun spread". The same applies to every
Sonnet-vs-Qwen difference under ~5 points in this file. Running (06:30): a second thinking log-only run on hh_s20 and
a second Sonnet log-only run on hh_s20, each with a new empty cache (0 cache hits checked at start), to measure each
model's own 31-day rerun spread.

## 2026-10-01, 09:40 - repeats on hh_s20: the thinking effect survives its own rerun there

Second runs of thinking-Qwen log-only and Sonnet log-only on hh_s20, each with a new empty cache (0 cache hits of 288
and 287 calls, checked after the run). First room right, run 1 / run 2 (difference):

| hh_s20 | whole month | days 1-13 | illness 14-23 | return 24-31 | identical room sequences |
|---|---|---|---|---|---|
| Qwen thinking | 88.3 / 89.5 (+1.2) | 86.5 / 88.5 (+1.9) | 86.2 / 90.0 (+3.8) | 93.8 / 90.6 (-3.1) | 232/248 |
| Sonnet | 88.3 / 90.3 (+2.0) | 85.6 / 89.4 (+3.8) | 88.8 / 90.0 (+1.2) | 92.2 / 92.2 (0.0) | 232/248 |
| Qwen plain (29 Sep / fresh) | 79.8 / 80.6 (+0.8) | | 76.2 / 81.2 (+5.0) | 89.1 / 84.4 (-4.7) | 223/248 |

On hh_s20, with two runs of each, every thinking run beats every plain run: month 88.3-89.5 against 79.8-80.6 (gap at
least +7.7), illness 86.2-90.0 against 76.2-81.2 (gap at least +5.0). So on the household that moved most, the
illness-window thinking effect is larger than the runs' own spread. One household repeated; s2 and s19 still rest
on one thinking run each.

Sonnet and thinking-Qwen on hh_s20: month 88.3 / 90.3 vs 88.3 / 89.5 - level, as in the three-household means.
Each model's own month-long rerun spread on hh_s20 is about 1-4 points in any window.

**Reading of the repeats (with -37):** on hh_s20 the ranges separate thinking from plain in both windows (worst
thinking run minus best plain run: +7.7 month, +5.0 illness) and do not separate thinking from Sonnet (ranges overlap
by 1.2 in both). With the three-household Sonnet - thinking of -1.9 (0/3): **the gain comes from thinking, not from
changing model.** hh_s20 is the load-bearing household; s2 and s19 (single thinking runs) are consistent with it.
The change-window rerun spread depends on the arm: on hh_s20, 5.0 for plain Qwen, 3.8 for thinking Qwen, 1.2 for
Sonnet (plain Qwen across households: 2.5-6.2).

**Next to run (open):** thinking on "the log and notes about the routine" across the three households, with repeats.
Everything above is log only except one thinking log+notes run on hh_s2 (89.1, against thinking log-only's 91.9; the
notes cost points after the return). Whether thinking widens or closes the notes-vs-no-notes gap, which the paper's
second finding rests on, is unmeasured.
