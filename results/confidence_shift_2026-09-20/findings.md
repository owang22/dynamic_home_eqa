## Findings (read this first)

**Setup in one line.** 64 activity-driven questions a day for 7 days (Wed-Tue) in 20 held-out households; the robot
sees a nightly round (03:00) plus the resident's found-it answer 10 minutes after each question; no active sensing.
About half the questions (52%) ask about an object that moved since the nightly round ("moved"); the other half
("still") is answered by the last sighting almost by definition, so every number below is read on the moved half
unless stated. LLM agents ran on 8 of the 20 households: the naive Qwen3.8-27B with a stated confidence on s10-14, s18, s19, s25,
the hypothesis mixture on six of those (s10, s11, s14, s18, s19, s25; s12/s13 are queued behind them and were
not reached by 10:00); the paper tables are over the six households that have every agent, the classical
agents ran on all 20.

**1. The only counter that learns is the only counter that breaks.** On the moved half the timetable (2 h clock
bins over the sightings it has received) climbs 13 -> 26 -> 37% Wed-Fri, drops to 31% on Saturday, and is at 52%
by Monday/Tuesday (20 households). Its confidence stays at 0.38-0.44 throughout: it does not know it is on a shift
day. Per household (Thu-Tue, moved half) it is at 45% on plain days and 35% on the household's own shift days at the
same confidence (0.41), worse on the shift days in 17/20 households; the neighbouring-day view says the same
(Fri 37 -> Sat 31, Sun 37 -> Mon 52). Note the plain days are on average later in the week than the shift days,
which flatters the plain number by a few points. Most frequent, periodic and Perpetua* never learn a time-of-day routine
(20-28% on that half all week); last seen is flat at 17% with confidence 0.98 (the "stays confident, is wrong on
every moved question" corner of the story, by construction).

**2. The naive LLM learns from the same feedback and breaks the same way, at a flat 0.8 confidence.** Told or
not told makes no difference (27 vs 28% moved-half accuracy over the week on the 8 households, and the told
message days are not better). Six paper households, moved half: Wed-Fri 21 -> 21 -> 35%, Saturday 15%, Sunday 23,
back to 29-37% Mon/Tue; stated confidence 0.81-0.84 on every day, 0.88-0.91 on the still half (the mixture on
the same questions: 17 -> 30 -> 36, Sat 27, Sun 35, Mon/Tue 42-43 at 0.27-0.32; the timetable 12 -> 29 -> 37,
Sat 29, Sun 38, Mon/Tue 53-51 at 0.4). Its reliability is two clusters, both overconfident; ECE 0.28-0.29 (the
mixture 0.21-0.23 from the opposite side: 0.3 stated for 33-83% observed; the timetable 0.13). The prompt-leak
check on all 8 households (7,169 prompts) found no household-file content in any prompt.

**3. The hypothesis mixture learns less than the timetable, breaks half as much, and its confident half is
the best of any agent on shift days - but its confidence does not move.** Coverage-matched table (driver
session, `driver/weekend_table.py`, final at 06:50 with all six told arms complete; moved-since-round
questions Thu-Tue, each household's own shift days vs its plain days, pooled over hh_s10/s11/s14/s18/s19/s25;
cells = accuracy / mean confidence / selective accuracy at 25|50|75% coverage by the agent's own confidence;
n = 541 plain / 682 shift questions):

| agent | plain days | own shift days | change (acc, sel@50) |
|---|---|---|---|
| hypothesis mixture, told | 39% / 0.29 / 48-46-44 | 32% / 0.30 / 44-41-36 | -7, -5 |
| timetable | 47% / 0.42 / 61-59-51 | 32% / 0.42 / 33-37-36 | -15, -23 |
| naive LLM | 31% / 0.81 / 39-33-35 | 23% / 0.83 / 32-28-24 | -8, -5 |
| most frequent | 22% / 0.44 / 20-23-27 | 20% / 0.47 / 18-19-20 | -1, -4 |
| last seen | 18% / 0.98 / 27-21-20 | 19% / 0.98 / 21-21-19 | +1, 0 |

Per household (mixture d acc / d sel@50 vs timetable): s10 -7/-5 vs -13/-30; s11 -3/+8 vs -10/-11; s14 -10/-14
vs -11/-10; s18 -16/-17 vs -20/-44; s19 +3/+5 vs -30/-54; s25 -12/-24 vs -16/-24. Caveat: part of the
mixture's smaller break is a smaller rise (39 vs 47 on plain days; on hh_s19 33 vs 62, the household where
its library stays widest, ESS ~16). The naive LLM's Saturdays are the "confident and wrong" corner (hh_s11
12%, hh_s14 5%, hh_s25 11% on the moved half at c0.82-0.83, from 32-48 on Friday; hh_s11 Monday 14% while the
routine learners are back at 43-54). Mean confidence falls on shift days for no agent (mixture 0.29 -> 0.30;
the one household where it dips is hh_s25, 0.30 -> 0.26).

Told = not told for the mixture (hh_s10 99% and hh_s11 100% identical answers after the message day; hh_s14
guest Thursday and Friday identical to the digit), and this is structural: every document predicts 0.7 x the
shared hour-bin statistics + 0.3 x its own claims, so the library cannot disagree with its own statistics;
giving the message documents a full share of the mixture (v5, `problems_found.md` #23) moved their weights
from 0.02 to 0.10 and changed not one answer. The blend is what makes the documents learn from feedback
(without it the mixture never beat the counters) and the same blend is what makes them agree. The way out is
per-document conditional statistics (a guest document counting only guest evenings, a weekend document only
weekend days) - not built tonight.

**4. The shift is small at the day level, by the numbers.** Pooled over all questions the best agents move 4-8
points between a plain weekday and a shift day (criteria table: rise Wed->Fri +7, drop Fri->Sat +4 for the
timetable; the brief asked for >10 on both). On the moved half the rise is +24 and the drop -6 to -10 for the
timetable, and the weekend is *not* uniformly harder: several households' weekends look like their weekdays
(hh_s11, hh_s12, hh_s28), and the event days matter only when the event touches the objects asked about. A
self-monitoring confidence (top_prob scaled by the agent's own running hit rate on the feedback it has already
received today, table "confidence = self-monitored") moves every agent's confidence by only 3-5 points on shift
days, which is exactly the size of the day-level accuracy change.

**5. The one agent whose confidence tracks the shift is the one that knows what it has not seen yet.** A
calendar-aware timetable with an honest empty bin (separate weekend bins; a bin with no sighting answers
last-seen at confidence 0.3; tuning_log #46, post-freeze, tuning set then once on held-out; the line
"timetable wd/we, honest empty bin") has coverage at 0.5 of 3/7/12% Wed-Fri, 2/5% on the weekend and 17/25%
Mon/Tue on the moved half, confidence 0.33/0.34/0.37 -> 0.32/0.34 -> 0.37/0.40: it stops answering on
Saturday because it has no weekend timetable, and pays for that honesty with Saturday's moved-half accuracy
(14% vs the frozen timetable's 31%, whose weekday bins are half right on a Saturday). Day-level accuracy is
the same (53/56/58 -> 53/51 -> 59/61). This is the shape the brief asked for, at the coverage level and at a
small size; the frozen agents do not have it.

**6. What this means for the paper story.** The accuracy side of the story is present in the learning agents
(timetable, naive LLM, mixture: learn Wed-Fri, break on Saturday and on the household's own event days) and the
confidence side is present only where an agent's design encodes what it cannot know yet (finding 5). No stated
or derived confidence (top_prob, library agreement, self-monitoring) drops by more than a few points on shift
days, because the day-level effect of a shift in this simulator is a few points. The coverage-matched view
(each agent answering its most confident 25/50/75% of a day's questions) is the fair comparison and is in the
tables: at 25% coverage the mixture's confident quarter is right 74/73/85% Wed-Fri, 66/67% on the weekend and
84/90% Mon/Tue (all questions, six households), the timetable's 58/81/73 -> 64/65 -> 80/85, the naive LLM's
70/76/74 -> 60/65 -> 79/82; on the moved half, own shift days vs plain days, the mixture's top quarter goes
48 -> 44 where the timetable's goes 61 -> 33. The brief's numeric criteria (>10 points rise Wed->Fri and drop
Fri->Sat, all questions) are not met by any agent (best: timetable +8/-8, naive +3/-10); on the moved half
they are (timetable +25/-8, naive +14/-20, mixture +19/-9).

**Status of the runs at hand-over (2026-09-21, 09:00).** Told and not-told arms complete for all six mixture
households (s10/s11/s14/s18/s19/s25; the two arms' pooled rows are identical to the point on every day); s12/s13
told on their Sunday (not in the tables; their partial days read like the others - hh_s12 Saturday: mixture
42 -> 21% on the moved half, timetable 42 -> 21, so the 8 h protocol's "reverse case" does not repeat under
feedback). Everything ran on the local vLLM server; hosted spend $0.

**Protocol changes made tonight, in order** (all in `tuning_log.md`): uniform -> activity-driven questions
(#20-24); 2 h -> 8 h patrol (#25-29); simulator-regularity variants and truth-only oracles showing that
patrol-only observation makes recency unbeatable at any regularity (#33); found-it feedback + nightly round,
accepted on the tuning set (#34-36); negative-evidence suppression switched off for the classical agents (#31);
mixture defects fixed one at a time on single questions (#37-41). The 8 h protocol results are kept as a
secondary section at the end.
