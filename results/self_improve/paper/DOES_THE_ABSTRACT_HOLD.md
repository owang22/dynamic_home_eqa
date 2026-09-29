# The abstract, sentence by sentence, against what is measured

Written 2026-09-28. Every number names the script in `paper/scripts/`. Verdict first: **the
argument holds, three sentences need rewording, and one of those is a real overstatement.**

## Holds as written

**The setting.** "The robot learns only from the rooms it searches and is not told about the
illness." Checked in the code: a look records every object in the room and those sightings are the
only input to the trail, the log and the nightly writer (`questions_answered.md` §5); no arm but
the told ones ever receives the cause.

**The central positive claim, and it is the strongest thing here.** "Giving the same summaries
access to the raw sightings closes that gap: this memory is competitive with the rule and pulls
ahead when the robot observes little."

- competitive: log and notes minus LastSeen over ten households is **+3.5 first room right (2 SE
  4.2, 9 of 10) and +1.5 found within 3 (2 SE 2.0)** — neither clears, which is what "competitive"
  should mean.
- pulls ahead when it observes little: on the five wider homes, **+4.4 / +5.0 at four questions a
  day (2 SE 1.9 / 2.4, 5 of 5 households)** against **+1.2 / +0.1 at twenty-four**. Both measures
  clear 2 SE and the noise floor at four a day and neither does at 24.
- and the obvious confound is excluded: the 40-sighting cap on the log bites 5% of questions at
  four a day and 75% at 24, but restricted to questions where it never bit, the trend is unchanged
  (+4.4 → +0.0). `does_the_log_cap_cost_anything.md`.

**The diagnostic case.** "In one diagnostic case, a language model told about the illness predicts
useful locations, then retracts the prediction in its next update." Verbatim, verified against the
claim's own history: the night-13 note, all eleven of that resident's moved-object questions on day
14 answered in a room it named and none in the room it ruled out, and the night-14 revision.
Framed as one case, which is what it is.

## Needs rewording

**1. "before, during and after the illness" — not during.**

LastSeen minus each summary-only memory, ten households, first room right:

| window | claim store | reduced ACE | MemGPT-shaped |
|---|---|---|---|
| before, days 1-13 | +9.7 (2 SE 10.6) | +10.5 (2 SE 9.8) | +12.1 (2 SE 10.2) |
| **during, days 14-23** | **−0.2 (2 SE 4.3)** | **+0.5 (2 SE 3.9)** | +10.4 (2 SE 4.9) |
| after, days 24-31 | +4.2 (2 SE 4.6) | +5.8 (2 SE 8.6) | +10.3 (2 SE 9.3) |

During the illness the rule does **not** beat the two summary memories that matter — it draws level.
Only the MemGPT-shaped arm is beaten throughout. This is not new: `the_log_the_robot_reads.py:14`
already says "the notes only draw level during the ten disrupted days", measured on three homes.

Suggested: *"…outperforms popular memory methods that keep only language-model summaries before and
after the illness, and draws level with them during it."* That is also a more interesting sentence,
because drawing level exactly when the world changes is the thing a summary is supposed to be good
at.

**2. "popular memory methods" — in the ten-household run they are the constrained variants.**

The ten-household run contains no ACE-as-published and no MemGPT-as-published cell. Its ACE-shaped
arm is `claim_store_told_if_it_was_right`, and its MemGPT-shaped arm ran on a **1,200-character**
block — a sixteenth of MemGPT's own smallest, which `memory_notes.py:196-200` says must be called
the tight variant and never MemGPT. The published implementations exist only at 24 questions a day
on three households.

Either name them as variants in the abstract, or move the published-method comparison onto the
three-household run and say ten households only for the arms that ran there.

**3. "summary-only memories do not improve on average" — they improve slightly; the true statement
is stronger.**

Day 14 against day 32, both-illness movers, first room right: claim store 6.4 → 12.8, ACE-style
8.6 → 12.8. Those are improvements, small ones. What is sharp is the fall:

| method | falls on day 14 | falls on day 32 |
|---|---|---|
| LastSeen | 58.8 | **31.4** |
| log and notes | 57.3 | **29.2** |
| claim store | 51.3 | **47.8** |
| ACE-style | 53.1 | **54.9** |

(each measured from that method's own mean over the four preceding days)

Suggested: *"…summary-only memories fall as far at the second illness as at the first, while
memories with a log fall about half as far."* ACE-style falls **further** the second time.

## Caveats that belong in the paper whatever the wording

- The second-illness result is **three households**, with 4 to 11 questions per household on days 14
  and 32, and 14 both-illness movers in total. The 2 SE on the day-32 change runs from 5 to 46
  points depending on the method.
- "Moved objects" is fixed from the **first** illness at spot level, so 8 of the 22 do not change
  room in the second spell. Every day-14-against-day-32 number uses the 14 that move in both.
- The ten-household run and the 24-a-day waves chose the room *before* reasoning, with a third of
  their explanations truncated. Measured paired, that does not move the day curves
  (`does_the_chooser_matter.md`), but it is a property of those two waves worth one line.

## What is usable right now

Figure 2 and Figure 3 are in shape. Figure A1 needs a leader line, its legend moved and the day-24
dip named. Figure A2 needs splitting into two captioned panels. All the numbers behind all four are
in `FIGURES.md` and `figures/NUMBERS_DRAWN.txt`.
