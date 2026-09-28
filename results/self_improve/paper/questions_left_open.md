# The five questions left open, answered from the runs

Written 2026-09-28, phase 2 of the CSIR paper work. Every number names the script that produced
it; the scripts are in `results/self_improve/paper/scripts/` and their output is saved beside them.
Nothing here launched a model.

**Two answers change how the paper must describe its own numbers. They are §2 and §3.**

---

## 1. Which 24-a-day wave each diagnostic comes from

`python3 results/self_improve/paper/scripts/which_wave_diagnostics.py` →
`which_wave_diagnostics.txt`, and `ace_merges_and_cap.py` → `ace_merges_and_cap.txt`.

Both waves hold ACE-as-published on the same banks, so the diagnostics had to be measured per
cell rather than assumed.

### The MemGPT-style freeze: **neither wave matches the sentence in the draft**

| wave | home | block reaches | archive at night 31 | nights a write was refused |
|---|---|---|---|---|
| `overnight_wave_24_questions` | hh_s2 (the only MemGPT cell there) | 19,967, frozen from night 27 | **0 passages** | 28, 29, 30, 31 |
| `wave_reasons_first` | hh_s2 | 19,972 | 10 passages | 18, 21, 22, 23, 26, 27, 30, 31 |
| `wave_reasons_first` | hh_s32 | 18,936 (ends 16,392) | 21 passages | 31 |
| `wave_reasons_first` | hh_s48 | 14,291 | 3 passages | none |

The draft says the block sits at about 19,900 and refuses writes **every night from day 19 or 20
through 31, in 2 of 3 households, with 0 passages in the archive**. The only cell with an empty
archive is the single 24-a-day cell, and it refused four nights, not thirteen. The only wave with
three households is `wave_reasons_first`, where two of three refused at all — which is probably
where "2 of 3" comes from — but there the archives hold 10, 21 and 3 passages and only one cell
refuses more than once. **The sentence as written cannot be sourced to either wave.** What is true
of every MemGPT-as-published cell: the block does fill (71% to 99.9% of 20,000 at the end) and the
refusal mechanism does fire in 3 of 4 cells.

### The ACE merges and the credit concentration: `overnight_wave_24_questions`

The 26-merge cell is `overnight_wave_24_questions/cells/ACE_as_published/hh_s2_t03` — no other
cell on disk applied 26 merges (the others: 12, 29 in that wave; 4, 0, 0 in `wave_reasons_first`;
5, 2, 0 in the 50-day run; 0, 0, 0, 1, 1 in `wave_wider_five`).

Of those 26, how many join claims with **no object in common** depends on how an object is
recognised, because the claims name things in prose ("Tomas's water bottle"), never by id:

| rule | count |
|---|---|
| no object **kind** word in common | **14 of 26** |
| no (person, object kind) pair in common | **20 of 26** |
| no object **id** in common | 26 of 26 — an artefact, the ids never appear in the prose |

The draft's **16 of 26** sits inside that bracket. Quote it with the rule stated, or use 14 of 26
and say "no object kind in common".

Credit concentration, measured over live claims at the end of each run
(`which_wave_diagnostics.py`):

| wave | top 11% of live claims hold | top 20% hold |
|---|---|---|
| `overnight_wave_24_questions` | 55% to 71% | 74% to 91% |
| `wave_reasons_first` | 43% to 79% | 63% to 98% |
| 50-day run | 46% to 88% | 74% to 100% |
| `wave_wider_five` | 31% to 43% | 52% to 58% |

The draft's "11 to 20% of live claims hold 22 to 62% of credit" is **lower than every wave**. The
closest is `wave_wider_five` at 31% to 58%. Name the wave and use its numbers.

### The time-threshold trace: `overnight_wave_24_questions`, hh_s2, claim_0006

`overnight_wave_24_questions/cells/ACE_as_published/hh_s2_t03/notes.json`, claim_0006, Tomas's
charger. The word "evening" survives while the hour it stands for walks backwards into late
morning:

- night 14: "In the evening (20:00+), it moves to the bedroom_1 desk"
- night 15: "In the evening (13:00+), it moves to the bedroom_1 (bed or floor)"
- night 16: "on the bedroom_1 bed in the evening (11:47+)", condition "Evening hours (11:47+)"
- night 21: "in the evening (11:00+)"

So the draft's 20:00 → 13:00 → 11:47 is right, on nights 14, 15 and 16, and it continues to 11:00
by night 21. Verbatim text is in `appendix_material.md`.

---

## 2. Did the room-choice schema put the reason before the room?

> **CORRECTED 2026-09-28, see `does_the_chooser_matter.md`.** The measurements below stand: those
> two waves did name the room first, with a third of their explanations truncated. The conclusions
> I drew from them - that Table 1 measures a different system, that it cannot sit beside the
> recurrence figures, and that it might need rebuilding - do NOT stand. Measured paired on the same
> three homes and arms, with LastSeen as a control that is identical across both waves, the chooser
> does not move the day curves and every window difference sits inside its own 2 SE.

`python3 results/self_improve/paper/scripts/reason_before_room.py` → `reason_before_room.txt`.

Measured from the rows, not from dates. The old schema named the room first and capped the
explanation at 240 characters; the new one reasons first and allows 1,200
(`src/self_improve/search_driven.py:277-305`). A cell that ran under the old cap cannot have an
explanation longer than 240 and piles up at exactly 240.

| run | explanations | at exactly 240 | over 240 | which schema |
|---|---|---|---|---|
| **ten-household run** (`overnight_wave`, 8 a day) | 18,624 | **6,676 (35.8%)** | 0 | **room before the reason** |
| **`overnight_wave_24_questions`** | 20,080 | **8,491 (42.3%)** | 0 | **room before the reason** |
| `wave_reasons_first` | 27,444 | 62 | 22,130 | reason before the room |
| `wave_the_family_reads_the_log` | 23,089 | 78 | 17,362 | reason before the room |
| **50-day run** | 17,166 | 42 | 12,834 | reason before the room |
| `wave_told_on_the_wider_homes` | 21,315 | 56 | 17,289 | reason before the room |
| `wave_wider_five` | 8,975 | 19 | 7,532 | reason before the room |
| **budget sweep, 8 a day** | 1,510 | 1 | 1,308 | reason before the room |
| **budget sweep, 4 a day** | 770 | 3 | 700 | reason before the room |

**This splits the draft in two.** Table 1 — the six-method comparison, the paper's main table — and
every ACE and MemGPT diagnostic come from the old chooser, where the room was named after zero
tokens of deliberation and a third of the explanations were cut off mid-word. The recurrence
result, the budget sweep and the told arms come from the new one.

Three consequences to decide on before writing:

1. Table 1 cannot be presented as measuring the same system as the recurrence figures. Either say
   so in the table caption, or rebuild Table 1 from `wave_reasons_first` — which has three
   households, not ten, and no ten-home small-working-memory or notes-hidden arm.
2. Any sentence that compares a Table 1 number with a 50-day number is comparing across a change
   in the chooser. `WHAT_COUNTS_AS_A_LEAD.md` names that as a dud.
3. The budget sweep is internally consistent (all three budgets ran under the new chooser), so the
   four-a-day result is unaffected.

---

## 3. Which ACE cells ran under the 4-item merge cap: **all of them**

`ace_merges_and_cap.py`. **And the cap is not the one the code comment blames.**

`MERGE_SCHEMA`'s `maxItems` was raised from 4 to 12 on 2026-09-26 at 20:49 (commit `b4207b7b3`),
with a comment saying the old 4 "BOUND ON 80.5% OF CALLS". But the pairs are not proposed by the
model — they are proposed by a deterministic grouper, and that grouper has its own limit:

    grouping_by_meaning.py:28   HOW_MANY_PAIRS_TO_PROPOSE = 4
    grouping_by_meaning.py:83   return out[:how_many]

So raising the schema's cap lifted nothing. Every ACE cell on disk still sees at most 4 pairs a
night, including the two that **started after** the commit (50-day hh_s32 at 21:21 on 2026-09-26
and hh_s48 at 03:02 on 2026-09-27, from their first heartbeats):

| wave | home | most pairs proposed in a night | nights at exactly 4 |
|---|---|---|---|
| `overnight_wave_24_questions` | hh_s2 / hh_s32 / hh_s48 | 4 / 4 / 4 | 22 / 31 / 31 of 31 |
| `wave_reasons_first` | hh_s2 / hh_s32 / hh_s48 | 4 / 4 / 4 | 21 / 31 / 23 of 31 |
| **50-day run** | hh_s2 / hh_s32 / hh_s48 | 4 / 4 / 4 | 39 / **49 of 49** / 41 of 49 |
| `wave_wider_five` | five homes | 4 | 15 to 31 of 31 |

So: **the 50-day ACE cells ran under the 4-pair limit; the cells behind the 26 merges ran under
it; and the limit is still in force today.** Every count of how much ACE merges remains a count of
our ceiling, and the comment claiming it was fixed is wrong. Two limits, and the smaller one — the
one nobody looked at — is the one that binds.

For the ten-household reduced ACE (`claim_store_told_if_it_was_right`): confirmed irrelevant. All
ten cells record `n_pairs_proposed = 0` and `n_merged = 0` on every night, because that arm only
merges when it is over a line budget that never fired
(`write_the_notes_told_if_right.py:701-705`).

One more thing found while checking this, and it explains the merges themselves: the grouper's
docstring says "Only pairs that hold under the same condition **and share an object** are
proposed", but the code tests only the condition (`grouping_by_meaning.py:79-81`). Nothing
requires a shared object, which is why most applied merges join claims about different things.

---

## 4. Which wave and cells produced each told-arm count

`python3 results/self_improve/paper/scripts/told_arm_counts.py` → `told_arm_counts.txt`.

A note on the matcher, because the first one I wrote was wrong: testing the whole claim record for
`"ill "` marks every claim, since `"still standing"` ends in `"ill "`. The matcher used here is
word-boundary and reads only what the model wrote — the statement and the condition.

### "361 of 361 claims fill the condition field, across six told runs" — reproduced, **no log**

The six runs are the two told arms of `wave_reasons_first` on three homes each:

| arm | hh_s2 | hh_s32 | hh_s48 | total |
|---|---|---|---|---|
| told on the first night | 33 | 19 | 106 | 158 |
| told the night before | 32 | 30 | 141 | 203 |
| | | | | **361** |

361 of 361 fill `holds_under`. **These are the cells that searched and answered with no sighting
log** (`prompt_sizes.txt`: 9,463 and 9,760 characters a call against the parent arm's 18,699), and
they also ran under the old room-first chooser. Both facts belong beside the number.

### "8 claims name the illness, 7 reworded within three nights (2 to 1, 5 to 0, 1 to 0)" — **not reproducible**

No cell, and no combination of cells, gives 8 with a 2 / 5 / 1 split. Counting claims written on
the first changed day whose statement or condition names being unwell, the largest count in any
cell is 3, and in most cells it is 0 or 1. Widening the words to include "resting", "in bed",
"stays home", "recovering" changes little: the biggest is 3 (`wave_reasons_first`, told the night
before, hh_s48), and no cell loses the wording within three nights — where the phrase appears at
all it tends to persist. Both matchers are in the script. This number needs its own provenance
before it can go in the paper.

### "7 of 24 on day 14 mention the illness, and all 7 choose the office or kitchen" — half reproduced

7 of 24 reproduces exactly, in `wave_the_family_reads_the_log/ours_told_the_night_before/hh_s2_t03`,
**which had the log** (18,981 characters a call). Two corrections:

- these are **room-choice** reasons, not answers: the answer step's reasoning is not stored per
  row, so the quotable count is about where it chose to look.
- **not all 7 choose the office or kitchen.** The step whose reason names being unwell went to
  office 3, kitchen 1, bedroom_1 2, living 1. Taking the first room opened instead: kitchen 3,
  office 2, bedroom_1 1, dining 1.

The same measurement on the told-and-committed cell for the same home and day is the more
interesting one, and it is also 7 of 24: there the naming step went to **bedroom_1 five times of
seven**, and **5 of those 7 questions were answered from the first room** against **1 of 7** for
told-the-night-before. Same home, same day, same information, and only the arm made to write down
what would change turned the stated cause into the right room.

---

## 5. Residents and objects per household

`python3 results/self_improve/paper/scripts/household_table.py` → `household_table.txt`.

**The five "wider" homes are five of the pilot ten, not new households.** Same seeds, same floor
plans, same residents, same tracked objects; what widens is the asked-about list.

### The pilot ten (8 a day, and the 24-a-day waves)

| household | type | residents | rooms | tracked objects | asked about | kinds | movers |
|---|---|---|---|---|---|---|---|
| hh_s2 | couple | 2 | 9 | 76 | 11 | 7 | 8 |
| hh_s19 | flatmates | 2 | 9 | 81 | 13 | 7 | 7 |
| hh_s20 | couple | 2 | 8 | 84 | 16 | 10 | 9 |
| hh_s32 | flatmates | 3 | 8 | 104 | 20 | 8 | 8 |
| hh_s48 | flatmates | 2 | 8 | 98 | 15 | 9 | 6 |
| hh_s63 | couple | 2 | 9 | 79 | 16 | 10 | 9 |
| hh_s93 | flatmates | 2 | 8 | 79 | 14 | 9 | 9 |
| hh_s109 | flatmates | 2 | 9 | 80 | 15 | 8 | 6 |
| hh_s123 | flatmates | 2 | 8 | 84 | 12 | 8 | 5 |
| hh_s151 | flatmates | 2 | 8 | 86 | 13 | 9 | 8 |

Two residents in nine homes, three in hh_s32; 76 to 104 tracked objects; 11 to 20 asked about; 5
to 9 movers.

### The five wider homes (budget sweep, `wave_wider_five`, the told wave)

| household | asked about | kinds | movers | same home as the pilot |
|---|---|---|---|---|
| hh_s32 | 34 | 18 | 9 | yes |
| hh_s48 | 27 | 18 | 11 | yes |
| hh_s63 | 27 | 19 | 14 | yes |
| hh_s93 | 24 | 17 | 13 | yes |
| hh_s151 | 25 | 19 | 11 | yes |

Rooms, residents and tracked objects are identical to the pilot rows above. The 50-day bank is
hh_s2, hh_s32 and hh_s48 with the pilot's narrow asked-about list (11, 20, 15 objects).

Occupations, age bands and household types for every home are in `household_table.txt`, ready for
the appendix.
