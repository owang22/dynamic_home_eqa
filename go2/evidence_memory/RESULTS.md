# Evidence memory: results (simulation, 2026-10-19)

Design, arms and the predictions written before the full run: `DESIGN.md`. In-person script: `IN_PERSON.md`.
Results page: `out/page.html`. All scores below are on the **clean question set** (`validity.py`): the questions
that survived the independent audit (87 of 122 at 1.0 m, 65 at 0.4 m). The table with all 122 is in
`out/score_1.0.txt`; it gives the same conclusions with smaller gaps.

## The answer

1. **Answer with the strongest model, reading change notes and every picture.** Opus answering from the
   memory the local Qwen wrote (change notes plus every picture) got **89%** of the clean questions at 1.0 m. A
   fixed answer sheet with no memory at all gets **53%**, and the best Qwen memory 61%. On the 57 questions that a
   fixed sheet cannot get for free, Opus beats the fixed sheet by +63 points (2 SE 14) and Qwen on the same memory
   by +47 (2 SE 13). It also beats Qwen shown exactly the right picture by +30 (2 SE 15). At the dog's 0.4 m
   camera the Opus run covered only 28 clean questions; on those, Opus 86% vs the fixed sheet 61% (+25, 2 SE 22,
   just over the bar).
2. **Keep every picture.** With Opus, every picture beats notes alone by +23 points (2 SE 13) and beats keeping
   only the pictures marked important by +16 (2 SE 11), mostly on the look-back questions (13 of 21 vs 7 of 21):
   the detail asked later usually sits in a picture nobody marked. A day of patrol pictures is a few MB. (Using the
   importance marks to choose which of all the pictures to open was not tested: with every picture kept, every
   picture is offered.)
3. **The importance marks pick out the real changes** (Qwen answering, one random draw of the control). At the
   same budget (about 156 of 640 pictures), the pictures the writer marked important beat random before/after
   pairs by +10 points on all clean questions (2 SE 7), and by +25 on the "when" and "what was going on" questions
   (2 SE 15): they held the before and after picture of 21 of 30 changes, random pairs 2. With three draws and with
   Opus: see "Added at 16:30" (the marks help Qwen, not Opus).
4. **With the local Qwen answering, memory helps far less.** On the 57 questions a fixed sheet cannot get for
   free, Qwen memories beat it by +12 to +26 points (important pictures +23, 2 SE 13; with a fresh look +26, 2 SE 14;
   captions only +14, 2 SE 13; notes only +9 and random pairs +7 do not pass). On the whole clean set most of that
   is lost (only important pictures pass: +12, 2 SE 10), because Qwen guesses about places it never visited
   (64-73% "cannot tell" where the fixed sheet says it every time). At 0.4 m every Qwen memory scores at or below
   the fixed sheet (48-59% vs 59%). A cause found: Qwen trusts its own note over the picture. On the 25 look-back
   items that were really there (all questions), it opened the right picture every time and was right 5 times;
   shown that picture alone, 11. A "fresh look" (ask about each picture alone, then combine with the notes)
   brings it to 10: +12 on look-back over all questions (2 SE 11), +10 on the clean set (2 SE 12, does not pass);
   this arm was added after the first results.
   Opus answered well from Qwen-written notes; whether notes written by Opus would do better was not tested.
   Qwen's notes miss changes: of the 69 visits where 3 or more visible things came or went, it rated 25 below
   importance 2 and wrote 8 as "no change" (some of those are the renderer re-drawing a place).
5. **No loss seen from searching the whole memory.** Opus with all five days of notes (640 visits, 150k
   characters) and no date filter, against only the question's day: -1.8 points (2 SE 8, 56 questions), +2.7 on
   the clean ones (2 SE 9, 37). A loss of up to about 8 points cannot be ruled out.

## Added at 16:30: the Opus runs on the Max plan (clean questions)

- **Importance vs random pairs, three random draws.** With Qwen answering, the important pictures beat the mean of
  the three draws by +10 points (2 SE 6), +24 on "when" and "what was going on" (2 SE 13). With Opus answering
  there is no difference (-1, 2 SE 8; "when" alone +14, 2 SE 17). So the importance marks matter when the answering
  model is weak; Opus finds the change from the notes plus whatever pictures are there. The recommendation stays:
  keep every picture.
- **Opus as the note writer did not help.** Opus answering from Opus-written notes, against Qwen-written: -5
  points (2 SE 9). Qwen writing the notes is enough; a gain of more than about 4 points from Opus notes is
  unlikely, a loss of up to 13 is possible. (5 of the 640 Opus notes failed and were left blank.)
- **Opus rerun noise:** the same arm asked again scored +2 points (2 SE 7).
- **0.4 m, all 122 questions.** Opus with every picture: 83% of the 65 clean questions. Against the fixed sheet
  +22 (2 SE 14); against Qwen on the same memory +26 (2 SE 13); against Qwen shown the right picture +5 (2 SE 11).

## Not shown (the headline examples need the in-person trial)

- **"They forgot their keys."** The left-behind questions are not valid yet: the truth used a hidden list of
  usual belongings, two positives came from a generator slip, and no arm beat always answering "no" (7/11).
- **"Who did it."** People are never in the pictures. Qwen names the chef whenever it sees cooking (7-21%
  right on the clean set); Opus uses the work hours and belongings and gets 43%. Not a strength of any method yet.
- **"What was going on."** A guess from the room alone ("cooking" in the kitchen) gets 9 of 14; Opus 12 of 14,
  with a specific true detail in 3. This kind barely measures memory as built.

## Numbers (clean questions, share right)

| memory (answering model) | overall | look-back yes | when | what was going on | never visited: "cannot tell" | pictures kept |
|---|---|---|---|---|---|---|
| fixed answers, no memory | 53% | 0/21 | 0/22 | 9/14 | 100% | 0 |
| captions only (Qwen) | 54% | 1/21 | 8/22 | 8/14 | 73% | 0 |
| captions + every picture (Qwen) | 53% | 1/21 | 7/22 | 8/14 | 73% | 640 |
| captions + every picture, fresh look (Qwen) | 54% | 6/21 | 9/22 | 7/14 | 64% | 640 |
| change notes only (Qwen) | 50% | 2/21 | 5/22 | 7/14 | 73% | 0 |
| change notes + every picture (Qwen) | 53% | 2/21 | 10/22 | 6/14 | 73% | 640 |
| change notes + important pictures (Qwen) | 60% | 1/21 | 13/22 | 8/14 | 73% | 156 |
| change notes + random pairs, same budget (Qwen) | 48% | 1/21 | 7/22 | 5/14 | 73% | 158 |
| shown exactly the right picture (Qwen) | 70% | 7/21 | 14/22 | 7/14 | (free) | – |
| change notes only (Opus) | 77% | 6/21 | 14/22 | 12/14 | 100% | 0 |
| change notes + important pictures (Opus) | 81% | 7/21 | 18/22 | 11/14 | 100% | 156 |
| **change notes + every picture (Opus)** | **89%** | **13/21** | **20/22** | **12/14** | 100% | 640 |

Overall = mean of the four kinds (look-back counts its 19 "no" items too, which nearly every arm gets right:
18 or 19). At 0.4 m (`out/score_0.4_clean.txt`, 65 questions): fixed 59%, Qwen arms 48-59%, Qwen shown the right
picture 77%; Opus (every picture) 86% on the 28 clean questions it was run on, where the fixed sheet gets 61%.
At 0.4 m, 28 of the look-back and when items are not visible at all: the dog sees floors, seats and low shelves,
and the edge of counters and tables (the 0.4 m camera stands see 6-26% of the counter, table and desk tops on
the patrol: `render/spot_views_0p4.json`, surface_share_seen).

## What the audit found, and what changed (14:40)

An independent agent read the code and data with no stake in the result. Findings and responses:

| finding | response |
|---|---|
| Look-back "no" items are free (every arm says no); 4 have a near match in view (a thermos asked as "water bottle") | near matches dropped; "no" items reported apart; the non-free comparisons use look-back yes, when and what was going on only |
| The judge credits one fitting word ("cooking"); 2 questions fell back to whole-house truth | fixed-answer arm added (room guess gets 9/14); those 2 dropped; this kind is reported as not measuring memory |
| Control E (evenly spaced) could never keep a before/after pair (0/30) | new control: random before/after pairs at the same budget (result 3 above) |
| The renderer re-draws objects that did not move (11% of unmoved pairs change size >2x): fake changes | 7 "when" questions with a re-drawn asked thing dropped; the real robot will not have this |
| Left-behind kind invalid (hidden list, generator slip, nobody beats always-no) | taken out of every score; marked "not shown" |
| Opus ran Bash to crop pictures in ~10 sessions despite `--allowedTools Read`; folders also hold truth files | transcripts checked: no read outside the kept pictures, no truth file read; Opus now runs with `--tools Read --strict-mcp-config`; the lab copies pictures to their own folder |
| 14 smoke-test questions shaped the prompts and were scored | dropped from the clean set |
| Questions came from 1.0 m truth; 40 visits have no 0.4 m picture | 0.4 m scores use only items visible at 0.4 m |
| The oracle gets "never visited" free and 8 pictures on "when" | non-free comparisons leave "never visited" out |
| Fresh-look arms were added after the first results; 45 paired cuts printed | said here: the fresh-look result is post hoc and does not pass on the clean set; about 2 of the printed cuts would pass by chance |

Rerun noise (same Qwen arm, fresh calls, clean set; `out/score_1.0_rerun.txt`): captions only gave identical
answers on rerun; captions + every picture with a fresh look moved +1.1 points overall (2 SE 4.0), between -2.5
and +4.6 on single kinds. Differences of a few points between Qwen arms are within rerun noise; the Opus
effects (+16 to +63) are far outside it. The Opus rerun noise was not measured.

## Answers to the auditor's ten questions

1. Fixed answers ("no", "cannot tell", "cooking" in the kitchen) score 53% on the clean set; on that whole set
   only the important-pictures Qwen memories beat them (+12, 2 SE 10). On the 57 non-free questions most Qwen
   memories do (+12 to +26). That is why both are reported.
2. E was evenly spaced over (time, place) order, so the same place never came twice in a row. The fair control
   (random pairs, one draw) loses to important pictures by 10 points (2 SE 7), and by 25 on "when" and "what was
   going on" (2 SE 15). Not run with Opus or with more draws.
3. 7 of 30 "when" questions had the asked thing re-drawn or hidden; they are dropped. The fake "moved" notes
   remain in the memory for every arm alike; keeping unmoved things fixed would need a change to the committed
   renderer (not done tonight).
4. It is a generator slip (Mara "leaves with the tote" and never picks it up). No positive left question was
   checked against the records before the audit; the kind is now out.
5. Not fair, as the auditor says: the thermos answer is reasonable. The in-person question 1 stays, because there
   the stager decides what was forgotten and writes it down; the simulation does not support it either way.
6. A person would say yes to a thermos for "water bottle"; those items are dropped.
7. The judge is lenient; it is no longer used to support any claim.
8. Now `--tools Read --strict-mcp-config`; the lab's picture folder holds only the robot's own pictures. The
   6-picture limit is a request in the prompt; in the simulation Opus never opened more than 6.
9. The "unremarkable picture" sentence now rests on the non-free comparison (every picture vs important only,
   +16, 2 SE 11), mostly from look-back (13 vs 7 of 21). The rerun noise floor for Qwen is above (about 1-5
   points); for Opus it was not measured (it would cost another ~$20).
10. Yes: 0.4 m scores use only items visible at 0.4 m (65 clean questions).

## Spend

Local: about 10,000 Qwen calls (no cost). Opus via `claude -p` on Oliver's Max plan (counts against the plan's
usage limit; no API account): 493 calls by 15:00 (including 5 test calls; the CLI's API-price estimate $163), then
about 1,500 more at 15:45-16:25 (the runs above). The dollar figures are the CLI's API-price estimates, not charges.
(Earlier text: 493 calls, about $163
usage-equivalent (approved as "small, roughly 300-600 calls").

## Files

`common.py`, `questions.py`, `write_memory.py`, `answer.py`, `opus.py`, `score.py`, `validity.py`,
`fixed_answers.py`, `analyze.py`, `page.py`, `lab.py` (the real-robot tool), `serve_vlm.sh`. Data in `out/`;
logs and the frozen run scripts in `logs/`. 0.4 m renders: `3d_rendering/results/vlm_night/render/*_0p4.py`,
pictures in `/mnt/nvme/oliver/robot/render_methods/vlm_night/hssd_a_0p4/`.
