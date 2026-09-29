# What the code settles about the runs the draft draws on

Written 2026-09-27 for the CSIR draft. Every answer names the file and line, or the manifest,
that settles it. Where the code does not settle something I say so instead of guessing. Six
helper scripts live in `results/self_improve/paper/scripts/`; each answer names the one that
produced its numbers, and each script's saved output sits beside it in
`results/self_improve/paper/*.txt`.

Nothing here launched a model. Ten cells of an unrelated run (our arm at 8 and 4 questions a
day) were already running when this work started and were left alone.

---

## 1. Run identity

`python3 results/self_improve/paper/scripts/run_inventory.py` → `run_inventory.txt`.

**Read this first: the cell directory is the arm, not the `how_memory_is_written` field.** The
last-seen arm and the notes-hidden arm both record `how_memory_is_written = "incremental edits"`
(`src/self_improve/overnight_wave.py:124-125`), because they change how a room is *chosen*, not
how notes are written. Any inventory keyed on that field merges three different arms.

**No manifest records the bank path.** `cell.json` holds the household name, the arm, the
budget, questions a day, last day and seed, but not `--banks`
(`src/self_improve/search_driven.py:1195-1232` builds it and writes it). The bank path has to come from the
launcher or its `pids.txt`. Household *names repeat across bank sets*, so a name alone does not
identify a household — the queue's own header says so
(`results/self_improve/the_queue_2026-09-26/run_the_queue.sh:5-9`).

### The ten-household run at 8 questions a day
`results/self_improve/overnight_wave/`

| what | value |
|---|---|
| households | hh_s2, hh_s19, hh_s20, hh_s32, hh_s48, hh_s63, hh_s93, hh_s109, hh_s123, hh_s151 (all `_t03`) |
| seeds | the `sN` in the name is the situation seed: `hh_s2_t03`'s episode id is `hh_s2_situation_seed2` |
| bank path | `results/self_improve/varied_homes/ten_homes/banks` — the launcher passes no `--banks` (`overnight_wave/launch.sh:22-23`), so the default `PILOT_BANKS` applied (`src/self_improve/three_prompts.py:111-112`) |
| days | 31 question-days (day indices 1–31; day 0 is a night with no questions, `first_question_day: 1` in the bank header) |
| questions a day | 8 |
| memory methods | `the_log_and_notes_about_the_routine`, `claim_store_told_if_it_was_right`, `a_small_working_memory_and_an_archive`, `incremental_edits`, `last_seen_no_model`, `prior_only_no_notes` — ten homes each; `wholesale_rewrite` on hh_s2 only |

**The draft's names map onto those six like this, and the mapping is not the intuitive one.**
`src/self_improve/overnight_wave.py:11-26` labels every arm:

| draft name | cell directory | what settles it |
|---|---|---|
| log and notes | `the_log_and_notes_about_the_routine` | line 11 |
| last-seen | `last_seen_no_model` | lines 14-21 |
| claim store | `incremental_edits` | line 14: "the plain claim store both are forks of" |
| constrained ACE | `claim_store_told_if_it_was_right` | line 13: "claim store told if it was right — ten homes. **ACE.** TWO model calls a night" |
| constrained MemGPT | `a_small_working_memory_and_an_archive` | lines 86-90: "MemGPT. … a write that would overflow the working memory is REFUSED" |
| notes hidden | `prior_only_no_notes` | lines 22-24, and `search_driven.py:387-396` |

I did not verify this mapping against the draft's accuracy numbers — that is the next phase.
**If the recomputed numbers disagree with the table, the mapping is what to doubt first.**

### The 24-questions-a-day runs with ACE and MemGPT as published
There are **two** such runs, not one, and they are different waves on the same banks:

| wave | households | days | memory methods |
|---|---|---|---|
| `overnight_wave_24_questions` | hh_s2, hh_s32, hh_s48 (MemGPT as published: hh_s2 only) | 31 | ACE as published, MemGPT as published, log and notes, claim store told if right, incremental edits, ours allowance derived, prior only, last-seen (last-seen on ten homes) |
| `wave_reasons_first` | hh_s2, hh_s32, hh_s48 | 31 | the same list plus eight-a-night, sixteen-a-night, told the night before, told on the first night; MemGPT as published on all three |

Both used `varied_homes/ten_homes/banks` (`overnight_wave_24_questions/launch.sh:8` passes no
`--banks`; `wave_reasons_first` records `banks=…/ten_homes/banks` on 37 of 39 specs). They are
not interchangeable: every schema in `wave_reasons_first` puts the reasoning **before** the
decision and the earlier wave puts it after, which the wave's own header calls its ablation
(`wave_the_second_illness/launch.sh:1-5`, `search_driven.py:277-300`). ACE as published exists
in both; `THE_TWO_ACE_RUNS_ARE_THE_SAME_RUN.md` is about a different pair.

There is also `wave_wider_five` (five wider homes: hh_s32, hh_s48, hh_s63, hh_s93, hh_s151, on
`varied_homes/headline_five/banks`, 31 days, 24 a day) carrying ACE as published, log and notes
and last-seen.

### The 50-day second-illness run
`results/self_improve/wave_the_second_illness/`

| what | value |
|---|---|
| households | hh_s2_t03, hh_s32_t03, hh_s48_t03 |
| bank path | `results/self_improve/varied_homes/all_generated_v2_twice/banks` (recorded on every spec in `the_queue_2026-09-26/logs/*/pids.txt`) |
| days | 49 question-days (1–49) |
| questions a day | 24 |
| memory methods | ACE as published, `the_log_and_notes_about_the_routine`, `incremental_edits` (the plain claim store), `last_seen_no_model`, and — added 2026-09-27 — `ours_told_the_night_before` |

**Are the 32-day three-household run and the 50-day run the same run? No — but they share their
first 31 days exactly.** They are different waves, different bank directories and different
`last_day`. Within the banks, though, every one of the 744 questions on days 1–31 is identical
in every field between `ten_homes` and `all_generated_v2_twice` for all three homes, the episode
headers agree, and the 50-day bank adds exactly 432 questions (days 32–49). The two configs
differ only by the two extra calendar blocks, `days: 32 → 50`, the name and the sim directory
(`diff` of the two `config.yaml`). So the 50-day run is the same three homes and the same first
month, re-simulated with two more calendar blocks — which is why its first 31 days replay from
the response cache.

---

## 2. MemGPT in the 50-day run

**No.** `wave_the_second_illness/cells/` holds `ACE_as_published`, `incremental_edits`,
`last_seen_no_model`, `ours_told_the_night_before` and `the_log_and_notes_about_the_routine`.
There is no MemGPT cell, as published or constrained, and no ACE-constrained cell either.

---

## 3. Same household generation and movement rules?

**Yes.** `diff results/self_improve/varied_homes/all_generated_v2/config.yaml
results/self_improve/varied_homes/all_generated_v2_twice/config.yaml` shows four changes and no
others: the two extra calendar blocks (`sick_again` days 32–41, `return_again` days 42–49),
`days: 32 → 50`, `name`, and `sim_dir`. The activities file, the events file, the asked-about
class list, `per_day: 24`, `question_moment`, `question_min_gap_min`, `oversample` and the
floor-plan/resident generator are identical.

The draft says "`wave_the_second_illness/launch.sh` passes different banks for 50-day runs".
That is right, and its own header says why: "The optional third and fourth fields are for the
two-illness episodes, which use their own banks and run 50 days instead of 32. Everything else
takes the pilot banks and 32 days" (`launch.sh:11-14`). What differs is the calendar, not the
household or the movement rules.

---

## 4. The illness spells in the 50-day run

From `all_generated_v2_twice/config.yaml`, day indices inclusive:

| block | days | forced event |
|---|---|---|
| lead | 0–13 | none |
| sick | **14–23** | `unwell_spell`, `resident_1` |
| return | 24–31 | none |
| sick_again | **32–41** | `unwell_spell`, `resident_1` |
| return_again | 42–49 | none |

**Same resident, same event definition, but a fresh draw — not a replay.** Both blocks force the
same `unwell_spell` event on `resident_1` with random events suppressed, so the distribution is
the same; the placements are drawn again, and they are not identical day for day.
`python3 results/self_improve/paper/scripts/spells_and_movers.py` → `spells_and_movers.txt`
prints every mover's commonest daytime place in all five windows. Where the object belongs to
the ill resident, the second spell usually sends it to the same room and often the same spot.
Where it belongs to somebody else, it often does not move in the second spell at all.

**This is a confound for every day-14-against-day-32 comparison in the draft, and it should be
stated before the numbers are.** The mover set is fixed once per run from days 14–23 only
(`search_driven.py:261-272`, and §14 below), so "moved objects" on day 32 includes objects the
second spell leaves where they normally are:

| household | movers (spot level, spell 1) | change **room** in spell 1 | change **room** in spell 2 |
|---|---|---|---|
| hh_s2_t03 | 8 | 6 | 4 |
| hh_s32_t03 | 8 | 6 | 5 |
| hh_s48_t03 | 6 | 6 | 5 |
| total | 22 | 18 | 14 |

Four of the 22 change room in the first spell and not in the second (`glass_ines`, `mug_ines`,
`water_bottle_aisha`, `water_bottle_priya` — all of them objects of a resident who is not the
one who falls ill). An object that does not move is easy, so part of any day-32 improvement is
the question set, not the memory. The "same objects on both illness days" analysis the draft
asks for does **not** fix this; restricting to objects asked on both days keeps objects that
moved once and not twice. The fix is to report the second spell on the objects that move in the
second spell, and to say so.

---

## 5. What opening a room reveals

Opening a room records **every object in it**, at spot granularity.
`TheHouseAsSeen.look` (`src/self_improve/looking.py:179-215`) walks every place behind the
target and writes one `Sighting` per object found, carrying `object_id`, `object_class`,
`place_id`, `room`, `day`, `time` and which target revealed it. It also records which residents
were in the room, and, for every object the robot already knows of, each place it looked at and
did not find it (`looking.py:216-235`).

Those incidental sightings reach all three consumers, with no filter for "was this the object I
was asked about":

- **last-seen's trail** — `search_driven.py:551-556` loops over *every* sighting in the look and
  calls `_remember_where_it_was_seen`.
- **The search-time log block** — built from `eyes.sightings_of(object_id)`
  (`the_log_the_robot_reads.py:83`), which is the same stream.
- **The nightly update** — `looks_today = eyes.looks[looks_before:]`
  (`search_driven.py:1067`) is handed whole to every note writer.

So a room opened for the mug updates the robot's record of the book that was on the same shelf,
for every arm.

---

## 6. Sighting format and scoring level

A sighting is a **spot with its room attached**: `place_id` and `room` are separate fields
(`looking.py:42-43`, `69-70`), e.g. `nightstand_b1` in `bedroom_1`. The log prints both ("on the
`nightstand_b1` in the `bedroom_1`", `the_log_the_robot_reads.py:100-101`).

Scoring is at **both** levels, and the draft's two headline measures are room-level by
construction:

- searches only ever open rooms (`LookTarget(room, "room")`, `search_driven.py:550`), so
  "first room right" (`found_at_step == 1`) and "found within 3 rooms" (`found_it`) are
  room-level;
- the spoken answer is scored twice: `correct_place` (exact spot) and `correct_room`
  (`search_driven.py:618-620`).

---

## 7. Search-time input, per method

All of it is built in one function, `choice_prompt` (`search_driven.py:308-400`), called once per
room opened. **Every arm that calls a model sees**: who lives here and the three things it has
(log-reading arms only, line 344-347); the question, the object, the day and the clock; which
search this is out of the budget; every room and the spots in it; how long since it last looked
in each room; and the rooms it may still choose. Nothing about the simulator's ground truth.

| arm | notes shown | log shown | log limited to the asked object | rooms already opened this question | what those rooms held |
|---|---|---|---|---|---|
| last-seen | — no model call at all | — | — | it is excluded from the rooms left (line 547) | — |
| claim store (`incremental_edits`) | yes | **no** | — | yes | yes |
| claim store told if right (constrained ACE) | yes | **no** | — | yes | yes |
| ACE as published | yes | **no** | — | yes | yes |
| MemGPT as published | yes, the block, searched for this object (line 331) | **no** | — | yes | yes |
| constrained MemGPT | yes, working memory in full plus its archive searched for this object (line 333-337) | **no** | — | yes | yes |
| log and notes, and all its variants | yes | **yes** | **yes** | yes | yes |
| notes hidden (`prior_only_no_notes`) | **no** | no | — | yes | yes |
| every told arm | yes | **yes, after 2026-09-26; no before** — see §10 | yes | yes | yes |

Which arms are in "all its variants" is one tuple, `THE_LOG_AND_THE_ROUTINE_FAMILY`
(`search_driven.py:165-172`): the parent, the derived allowance, eight a night, sixteen a night,
a profile of each person, a profile and told, told and committed, told the night before, told on
the first night.

Rooms already opened on this question are named and the objects seen in each are listed
(lines 372-377); an arm that opened a room and did not find the object is told so in words. The
list is per question and is not carried across questions. Nothing shows earlier *failed
searches from other questions* — only the per-room "how long since you last looked" line carries
anything across questions.

**The log's caps.** `the_log_block` (`the_log_the_robot_reads.py:152-162`) prints
`what_you_have_seen_of`, which is:

- every sighting **of the asked object only**, newest first, capped at
  `HOW_MANY_SIGHTINGS_TO_SHOW = 40` (line 29);
- up to `HOW_MANY_THINGS_BESIDE_IT = 6` other objects seen in that room at that moment
  (line 33), with "and N other things" after that;
- one summary line for everything past 40: how many, the rooms with counts, and the oldest day;
- then where looking did **not** find it, summarised **by room** rather than by spot
  (lines 112-120);
- bounded by `up_to_time`, which is required and has no default, so no future sighting can leak
  (lines 71-82).

**How far back it reaches on day 32, measured.**
`python3 results/self_improve/paper/scripts/log_window_reach.py` → `log_window_reach.txt`, on the
50-day run's log-and-notes cells, for the moved-object questions asked on day 32:

| household | moved-object questions on day 32 | sightings held per object (median) | the 40 shown reach back to day (median) | still show a day 14–23 sighting |
|---|---|---|---|---|
| hh_s2_t03 | 13 | 122 | 22 | 7 of 13 |
| hh_s32_t03 | 6 | 289 | 28 | **0 of 6** |
| hh_s48_t03 | 12 | 156 | 25 | 4 of 12 |

So on day 32 the dated lines typically reach back only a week or two, and **11 of 31**
moved-object questions have any first-spell sighting among them. The draft's "answers on days
32–35 that cite a sighting from days 14–23" is therefore bounded by a cap we imposed, and the
count cannot be read as what the method chose to use. The summary line still names the rooms of
the older sightings and the oldest day, so the older evidence is not wholly absent — it is
undated and unranked.

**At answer time** (`answer_prompt`, `search_driven.py:711-781`) the same split holds: the log
block goes in for the same family and nobody else (line 744, gated at lines 599-604); the notes
go in for every arm that writes notes; the rooms just ruled out and what was seen in them go in
when `tell_it_what_it_ruled_out` (true in all these runs, recorded per row). The notes are cut
to `read_budget_lines = 8` lines about the asked object (`study_settings.py:122`), and that
budget **never bound in any search-driven run**: 0 of 135,774 rows have
`the_read_budget_bit` true.

---

## 8. What the notes-hidden arm sees

Not nothing, and not the log. `prior_only_no_notes` gets the whole choice prompt with the notes
block omitted and **nothing put in its place** — the comment at `search_driven.py:389-396` says
a line like "you have no notes" would be false and would itself be an instruction. So it sees
the question, the rooms and their spots, how long since each room was last looked in, the rooms
already opened on this question and what they held, and the rooms left. Its notes are still
written every night and still used to answer; they are withheld at the choice step only.

---

## 9. Is there an LLM arm that sees the log but no notes?

**No.** The log is gated on `notes.how_memory_is_written` being in
`THE_LOG_AND_THE_ROUTINE_FAMILY` (`search_driven.py:490-497`), and every member of that tuple is
a memory-guided arm that is also shown its notes. `prior_only_no_notes` records
`how_memory_is_written = "incremental edits"` (`overnight_wave.py:125`, and the same for last-seen at 124), which is not in the
tuple, so it gets neither. The "log alone, no notes" cell does not exist.

---

## 10. Which told runs searched without the log

`python3 results/self_improve/paper/scripts/prompt_sizes.py` → `prompt_sizes.txt`. This is
measured from each cell's own `call_times.jsonl` rather than inferred from a date: the log is
thousands of characters, so it shows in the mean prompt size.

| cell | model calls | mean prompt characters | had the log |
|---|---|---|---|
| `wave_reasons_first` log and notes, hh_s2 | 897 | 18,699 | yes (the parent) |
| `wave_reasons_first` **told the night before**, hh_s2 | 1,075 | **9,463** | **no** |
| `wave_reasons_first` **told on the first night**, hh_s2 | 1,083 | **9,760** | **no** |
| `wave_the_family_reads_the_log` log and notes, hh_s2 | 897 | 18,699 | yes |
| `wave_the_family_reads_the_log` **told the night before**, hh_s2 | 889 | **18,981** | **yes** |
| `wave_the_family_reads_the_log` **told and committed**, hh_s2 | 874 | **19,043** | **yes** |
| `wave_the_second_illness` told the night before, hh_s2 | 1,384 | 20,155 | yes |
| `wave_told_on_the_wider_homes` told the night before, hh_s32 | 848 | 19,774 | yes |

So: **the told cells in `wave_reasons_first` (and the other three variants named in
`wave_reasons_first/THE_FIVE_VARIANTS_READ_NO_LOG.md`) searched and answered with no log. Every
told cell in `wave_the_family_reads_the_log`, `wave_told_on_the_wider_homes` and
`wave_the_second_illness` had it.** The cause was `==` against one arm name where membership was
meant; the fix is `search_driven.py:490-497` and `:601-604`.

On the draft's two specific cells:

- **The told-with-the-log run on hh_s2** — if that is
  `wave_the_family_reads_the_log/ours_told_the_night_before/hh_s2_t03`, then **yes**, it had the
  log at search time (18,981 characters a call against the parent's 18,699). Which cell produced
  "7 of 24 answers mention the illness" is a counting question for the next phase; the same arm
  exists in `wave_reasons_first` without the log, so the count must name its wave.
- **The told-and-committed run** (`ours_told_and_asked_what_changes`, the night-13 prediction) —
  **yes**, it had the log. It exists only in `wave_the_family_reads_the_log` and
  `wave_told_on_the_wider_homes`, both after the fix, and it is in the tuple
  (`search_driven.py:170`).

Note the side effect: without the log the told cells made **more** model calls (1,075 against
889 on hh_s2), because more searches needed a second and third room.

---

## 11. Model and decoding

One model served every arm in every run named here: **`Qwen/Qwen3.8-27B`**, on a local vLLM at
`http://127.0.0.1:8300` (`src/baselines/patrol/llm.py:50-51`; `study_settings.py:203-204`).
`Qwen/Qwen3.6-35B-A3B` appears only under `src/dynamic_home_eqa/` and `src/dynbelief/` — dataset
generation, the clutter catalogue and judges — and never in `src/self_improve`.

Checked rather than assumed: the response cache records the model in every entry, and a random
5,000 of the 177,160 entries in `llm_prior_cache/self_improve/` all say `Qwen/Qwen3.8-27B`. The
cache key is a sha256 of `{model, messages, schema, max_tokens, temperature, seed}`
(`llm.py:136-139`), so a different model could not have replayed these entries.

Decoding, identical for every arm (`llm.py:203-205`):

| setting | value |
|---|---|
| temperature | 0 |
| seed | 0 |
| thinking | `chat_template_kwargs: {"enable_thinking": False}` — off everywhere |
| guided decoding | a JSON schema on every call, enforced during generation |

`max_tokens` is per call site, not global: 900 for the room choice
(`search_driven.py:510`, raised from 250 on 2026-09-25) and 900 for the answer (line 606, raised
from 400); 1,200 for ACE's judgement call
(`write_the_notes_told_if_right.py:323`); `300 + 420 × cap` for the nightly edit call
(line 431); 900 for ACE's merge (line 568); 9,000 for the wholesale rewrite
(`three_prompts.py:109`).

Two things worth saying in the paper because they shape every arm: the schema enforces field
order while generating, so **the field order is the reasoning order** — until 2026-09-25 the
room-choice schema named the room before the reason, and with thinking off that meant every room
was chosen after zero tokens of deliberation (`search_driven.py:277-300`, measured on 2,206 of
2,206 cached completions). And temperature 0 is not deterministic on this server: identical
prompts give different completions, which is what the noise floor in §17 measures.

---

## 12. Is the question schedule identical across methods?

**Yes, and by construction.** `questions_spread_across_the_day`
(`search_driven.py:206-227`) takes evenly spaced positions from the day's bank list: "The same
list for every arm, because it depends on nothing but the bank" (line 214). It is not
`questions[:n]` — that slice used to select only the first hours of the day and biased
everything that used it. `answerable_questions_on_day` (lines 231-241) then drops questions
whose answer no look could reach, using only the bank. Nothing in either function reads the
arm, the notes or any earlier search. Confirmed on disk: every arm of the ten-household run has
exactly 2,480 rows and every arm of each 24-a-day wave the same count as its siblings
(`run_inventory.txt`).

---

## 13. The question count

`python3 results/self_improve/paper/scripts/scored_counts.py results/self_improve/overnight_wave`
→ `scored_counts_overnight_wave.txt`.

**10 × 32 × 8 = 2,560 is the wrong scheduled total; it is 10 × 31 × 8 = 2,480.** The month has
32 day indices (0–31) but questions start on day 1 (`first_question_day: 1` in the bank header;
day 0 is the first night), so there are 31 question-days. Every arm has exactly 2,480 rows, and
nothing was dropped.

**2,456 does not match any arm.** What varies is the denominator of *exact-place* accuracy:
`correct_place` is None when the arm produced no place at all — an unparsed completion, or
last-seen having never seen the object:

| arm | rows | no place answered | place-scored |
|---|---|---|---|
| log and notes | 2,480 | 0 | **2,480** |
| claim store (`incremental_edits`) | 2,480 | 10 | 2,470 |
| claim store told if right | 2,480 | 21 | 2,459 |
| last-seen | 2,480 | 26 | **2,454** |
| constrained MemGPT | 2,480 | 36 | 2,444 |
| notes hidden | 2,480 | 37 | 2,443 |
| wholesale rewrite (hh_s2 only) | 248 | 5 | 243 |

First-room-right and found-within-3 use all 2,480 for every arm, because `found_at_step` and
`found_it` are always filled. So the draft's single "2,456 scored questions" should become two
numbers: 2,480 for the two headline measures, and 2,443–2,480 per arm for exact place. I could
not reproduce 2,456 from this run by any filter I tried; it is closest to last-seen's 2,454.

---

## 14. What "moved object" means

Fixed **once per run, per object**, never per question. `the_movers`
(`search_driven.py:261-272`) takes each asked-about object's commonest daytime place over the
settled days and over the disrupted days and calls it a mover when the two differ. The set is
computed once in `run_one_cell` and passed to every question; each row carries `is_a_mover`.
Three properties matter for the write-up:

1. **It is spot level, not room level.** `_commonest_place_over` returns a `place_id`, so an
   object that moves from one shelf to another in the same room counts as a mover. Measured: of
   22 movers in the three 50-day homes, 18 change room in the first spell — four move only
   within a room (`spells_and_movers.txt`).
2. **Daytime hours only** — `DAYTIME_HOURS = range(8, 23)`, `SETTLED_DAYS = range(0, 14)`,
   `DISRUPTED_DAYS = range(14, 24)` (lines 245-247).
3. **On the 50-day bank it is still days 14–23**, because those constants are module-level. The
   mover set of the 50-day run is the *first* spell's mover set. See §4 for what that does to a
   day-32 comparison.

Counts per household are in `run_inventory.txt` and, for the pilot ten, 5 to 9 movers per home
out of 11 to 20 asked objects (75 movers over ten homes).

---

## 15. last-seen's order and ties

`_remember_where_it_was_seen` (`search_driven.py:635-658`) keeps **one entry per room**: seeing a
thing again in a room it has already been seen in moves that room to the front instead of adding
an entry. So the trail is the *rooms* it has been seen in, newest first, and **yes, it dedupes
before picking its second and third rooms**. It also raises if sightings arrive out of order
rather than trusting it (lines 650-654).

`_the_next_room_it_was_seen_in` (lines 661-694) walks that trail newest first and takes the
first room not already opened on this search. Two fallbacks, both named in the row's reason:

1. the room where other objects **of the same class** were most recently seen — ties broken by
   room name, explicitly so the choice cannot depend on dictionary order (line 689);
2. a seeded random room, when the object has never been seen and nothing of its class either.

The answer, as opposed to the search, uses only the newest entry — the exact spot it was last
seen on (lines 573-587). A failed search leaves the previous sighting standing.

---

## 16. Constrained ACE and MemGPT against the published versions

### ACE
Both run through `write_the_notes_told_if_right`, and **one flag separates them**:
`as_published` (line 683). Its three effects:

| | constrained (`claim store told if it was right`) | as published |
|---|---|---|
| Reflector rounds | 1, unconditional, every night (line 693) | up to 3, only while something went wrong, stopping early when nothing did |
| grow-and-refine merge | only when over its line budget, which never fired: `{"n_pairs_proposed": 0, "n_merged": 0}` (lines 701-705) | every night: pairs proposed by sentence embedding, merge text written by the model |
| edit allowance | `max_edits = edits_tonight`, the derived allowance | the same |

The module's own header (`write_the_notes_told_if_right.py:34-56`) lists where **both** versions
still differ from the real ACE, checked against `github.com/ace-agent/ace`: their grouping uses
all-mpnet-base-v2 at cosine 0.90 and an LLM-authored merge while ours uses word overlap and a
deterministic concatenation; their bullets have no condition field at all, so `holds_under` is
this study's addition and must not be presented as ACE's; their shipped code defines ADD,
UPDATE, MERGE and DELETE but executes only ADD, while ours really runs revise, attach-evidence
and join; and ours never deletes. That paragraph should be quoted in the paper, not summarised.

One cap to check per run rather than per arm: the merge schema's `maxItems` **was 4 and bound on
80.5% of calls (66 of 82)**; it is 12 now (`write_the_notes_told_if_right.py:513-518`). Any
as-published ACE number quoted from a cell that ran before that change is a number about our
cap. Which cells those are is a question for the numbers phase — the per-night reports record
`how_it_merged`.

### MemGPT
Two different modules, `write_the_notes_memgpt` (constrained) and
`write_the_notes_memgpt_as_published`, dispatched at `search_driven.py:1077-1092`.

| | constrained (`a small working memory and an archive`) | as published |
|---|---|---|
| block size | **1,200 characters in the ten-household run** (measured, below) | 20,000, from `letta/constants.py` (`write_the_notes_memgpt_as_published.py:18`; `memory_notes.py:178-194`) |
| how the block is edited | itemised edits with a 240-character statement and a 120-character condition (`write_the_notes_memgpt.py:55-56`) | exact substring replacement, with `the_piece_to_replace` and `text` both allowed the block's full 20,000 (lines 58-81) |
| archive | reached by searching for the asked object | paginated, 5 passages a page (line 42) |
| overflow | the write is refused and the refusal handed back | the same |

**The ten-household run's MemGPT-shaped arm ran at 1,200 characters, and the code now says a run
at that size must not be called MemGPT.**
`python3 results/self_improve/paper/scripts/working_memory_size.py` →
`working_memory_size.txt` recovers each cell's limit from `characters ÷ share` in its own nightly
records: all ten `a_small_working_memory_and_an_archive` cells ran at **1,200**; every
`MemGPT_as_published` cell ran at **20,000**. `memory_notes.py:196-200` keeps 1,200 as
`A_DELIBERATELY_TIGHT_WORKING_MEMORY` and says: "A run at this size is labelled the tight
variant and never as MemGPT." So the draft's "constrained MemGPT" row in the ten-household table
is the tight variant at a sixteenth of MemGPT's smallest real block, and its 70.9 / 82.0 is not
evidence about MemGPT. The paper should either rename that row or say the size in the row.

---

## 17. The noise floor

`results/self_improve/three_prompts/the_rerun_noise_floor.json`, whose own `what_it_is` field
states the method: "control and told_unwell have byte-identical prompts on days 0-13, so their
difference over that window is rerun noise", and `why_any_noise_exists`: "two cells miss the
prompt cache at the same moment, each calls the server, and vLLM returns different completions
at temperature 0."

So the floor is **not** a rerun of one cell: it is the difference between two arms over the
window where their prompts are identical. Run: the `three_prompts` wave, 8 questions a day,
**days 0–13**, **7 households**, 96–104 questions per home.

| measure | mean absolute difference | largest single home |
|---|---|---|
| first room right | 0.0190 → **1.9 points** | 6.3 points |
| found within budget | 0.0219 → **2.2 points** | 7.3 points |
| correct room | 0.0173 → 1.7 points | 5.2 points |
| exact spot | 0.0145 → 1.5 points | 5.2 points |
| rooms opened | 0.0279 | 0.10 rooms |

Two caveats to state wherever the floor is quoted. It is the **mean** absolute move, not the
largest: two of seven homes agreed on every question, and one home moved 6.3 points. And it was
measured on a different wave, at 8 questions a day, in the settled window — not on the waves the
draft quotes, and not in a disrupted window. `results/self_improve/rerun_noise_floor.json` is a
different and older thing (the patrol runs, 6 cells, on the day-23-minus-day-13 difference, mean
absolute move 0.56 points) and should not be cited for these numbers.

---

## 18. The effective moved-object count

**Cannot be settled from the code.** The claim "the effective number of independent movers per
household is 2.4 to 2.9 … 2.65 to 2.89 with twice the kinds" appears once, as prose, in
`results/self_improve/THE_MAIN_POINTS.md:118-126`. A repo-wide search for the numbers and for
the words "effective", "independent movers", "design effect" and "intraclass" finds no script
that computes them, no JSON holding them and no recorded command. The related claims in
`varied_homes/make_the_guest*.py:8` give a different range ("effectively 2.4 to 3.4 independent
movers out of 6 to 14") and also cite no computation.

What the code *does* define is a different quantity: `check_scenario.py:508-518` treats the
effective sample size as the count of **moved objects** per household (its gate needs at least
8 distinct asked objects in the disrupted window) and says "Cluster every interval on household
and object."

So the 2.4–2.9 figure should not go in the paper as it stands. It can be recomputed — the
natural estimator is a design effect from the day-by-day agreement among movers within a home,
`n_eff = n / (1 + (n − 1) ρ̄)` — but that would be a new number with a new definition, not a
reproduction of the quoted one. Say the word and I will compute it and write down the estimator.

---

## Two things the draft should change before the numbers phase

1. **The ten-household "constrained MemGPT" is the 1,200-character tight variant** (§16). The
   code itself forbids the MemGPT label at that size.
2. **"Moved objects" on day 32 are the *first* spell's movers** (§4, §14), and 8 of the 22 do not change room in the
   second spell — four that moved rooms in the first spell and stay put in the second, and four
   that only ever moved between spots inside one room. Every day-14-against-day-32 number in the draft inherits
   this, including the figures.

And one measurement to keep in view: on day 32 the log shows the newest 40 sightings, which
reach back a median of 22–28 days, so **11 of 31** day-32 moved-object questions can see a
first-spell sighting at all (§7). The draft's "cites a sighting from days 14–23" counts are
bounded by that cap.
