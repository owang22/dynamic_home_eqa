# Counting-method sweeps (CPU only), 10 households each — 2026-09-23 19:32
Tables: gap_table.txt, spell_table.txt (sweep_table.py). Predictions: EXPECTATIONS.md (written 19:08, before any run).
Check passed: the 30-minute gap run reproduces the frozen sick10_owner counting-method logs exactly (37,170/37,170 rows). The
10-day spell run, on regenerated households, reproduces the same table exactly. Every spell length's lead-up and first sick
days are identical to each other (same seeds), as they must be.

## Sweep 2: length of the sick spell (lead-up 14 days and return 8 days held fixed) — a clean dose-response
All questions. "Return loss" = settled accuracy (days 9-13) minus the first 3 days back.
| spell | 3-day memory minus never-forgets, from day 14 (paired, se) | same, first 3 days back | return loss: never forgets | 3-day memory | most frequent | Perpetua* |
|---|---|---|---|---|---|---|
| 3 days | +1.5 (1.4) | -1.9 (2.9) | +2 | +3 | 0 | +13 |
| 6 days | +2.5 (0.7) | -10.8 (5.2) | 0 | +10 | -2 | +10 |
| 10 days | +4.8 (1.1) | -15.6 (5.6) | +3 | +18 | +8 | +11 |
| 20 days | +8.2 (3.0) | -9.9 (3.3) | **+10** | +19 | **+26** | +18 |
Reading:
- The forgetting memory's advantage over the one that never forgets grows steadily with the length of the disruption:
  +1.5, +2.5, +4.8, +8.2 points from day 14 on. At 3 days they tie; the forgetting memory never loses overall.
- Its cost on the return grows and then levels off: +3, +10, +18, +19 points of return loss.
- The memory that never forgets is stable only while the routine outvotes the disruption. With 20 sick days against 14 settled
  ones it breaks on the return too (+10, se ~3), and so does most-frequent (+26). Its "stability" is a vote count.
- Perpetua* pays a return cost of 10-18 points at every length, even for a 3-day spell.
Predictions: the coordinator's "never-forgets best overall at 3 days" was NOT supported (a tie, +1.5, se 1.4). The
coordinator's "3-day memory wins clearly by 20 days" HELD (+8.2, se 3.0). The coordinator's "never-forgets return break stays
near zero" held up to 10 days and FAILED at 20. Mine: "crossover between 6 and 10 days" was WRONG (there is no crossover; the
forgetting memory is never worse). "Return loss saturates by about 6 days" was PARTLY right (it levels off between 10 and 20,
not by 6). "At 20 days the never-forgets memory also breaks on the return" HELD, as did most-frequent's.

## Sweep 1: minimum gap between questions about the same object (0, 5, 15, 30 min) — the gap changes WHICH questions are asked
| gap | questions per day, lead-up / sick | share of questions repeating an object already asked that day |
|---|---|---|
| 30 | 11.2 / 16.0 | 65% |
| 15 | 13.0 / 16.0 | 69% |
| 5 | 14.8 / 16.0 | 72% |
| 0 | 14.9 / 16.0 | 72% |
The sick days are capped at 16 questions at every gap, so a smaller gap there does not add questions; it changes which
objects fill the 16 (gap 0: glass rises to the 2nd most asked class, book falls from 302 to 182).
Results (full table in gap_table.txt; all questions, then first-of-day):
- Settled accuracy barely moves for the timetables (82/82/85/83; 3-day 80/83/84/82). Most frequent and Perpetua* FALL at gap 0
  (60->58, 66->58).
- The break shrinks at gap 0 for the timetables (30->23, 23->21) and most frequent (36->27), but grows for Perpetua* (11->16).
- Re-learning inside the spell FALLS as the gap shrinks, for every method and on first-of-day questions too: most frequent
  cold 53 -> 46 -> 39 -> 28; 3-day memory cold 85 -> 88 -> 89 -> 81; Perpetua* cold 73 -> 58 -> 55 -> 41.
Predictions: the coordinator's "all-question accuracy rises and the break shrinks" was PARTLY supported (the break shrinks for
three of four methods; accuracy does not rise). "First-of-day barely moves" was NOT supported: first-of-day numbers move as much
as all-question ones. So the gap is NOT redundant with the first-of-day split. It changes the question population, not only
the repeats, which is the caveat I noted in advance. Mine: "+5 to +10 settled at gap 0" was WRONG (about 0).
Recommendation: keep a gap, or replace it with a design that holds the sick-day object mix fixed. Dropping it and relying on the
first-of-day split does not isolate memory here.

## Cells worth LLM time
1. Spell length 3 vs 20 on the recent-sightings list and one other language memory, no message and with the message: this
   tests whether language memories follow the same dose-response and whether the unretracted message's return cost grows with
   the spell.
2. Spell 20: the never-forgets break on the return is the new effect; does a language memory that "remembers everything"
   (the whole-log memory) show it?
3. The gap sweep is NOT a good use of LLM time. Its effect is a change in question population, not in memory.
