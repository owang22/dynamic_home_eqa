# Caption for F3

**Single-column figure** — reproduce at 3.15 in, its rendered width.

**Title line:** What one sentence buys

Paste and edit; written as a caption, not a summary.

---

One the LLM told three different things, on the same ten households. The darkest line is never told; the middle line is told “Yuki is home sick today” on the first sick day (A); the lightest is told that again and then told on the first day of the return that the resident is back (A & B). Each told arm is the same run as the one above it until the day it is told, so it is drawn only from the day it departs after being told.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** longcontext (matched across all three arms) 10
- **Questions:** all questions
- **Bands:** ±1 standard error across households
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **How the line is drawn:** The line is a centred three-day average, computed WITHIN each stage so that it never averages across a stage boundary — a window straddling the boundary borrows the level from the other side and flattens the very change the figure is about. The band, where a figure draws one, is ±1 standard error across households computed on the daily values. On this figure's axis the effect of getting that wrong is concrete: an unbounded window renders the timetable with a three-day memory's 40.8-point fall at day 14 as 6.8.
- **About the data:** Each told arm is drawn from the day it departs from the arm above it, measured from the data rather than taken from the calendar, with the search starting at that arm's own message day. Departure days are in the numbers below, and so is any day an arm differed from the one above it BEFORE its message. Those earlier differences are rerun artefacts rather than design facts: identical prompts at temperature zero are not reproducible on this server, so the arms are identical before their message because those prompts are cache hits, not because generation is deterministic. A cache miss means a fresh generation, which can differ. The twice-told arm differs on two such days by 0.625 points — one answer in a hundred and sixty — and used to be drawn from the first of them, three days before it was told anything.
- **The floor under any effect here:** Some of any difference here is the run having been run again. Identical prompts at temperature zero do not reproduce on this server, so a repeat of the same arm on the same data does not give the same answers, and that sets a floor under every effect involving a memory whose answers a language model generates. Measured on 3 households by re-running each arm over the same data with byte-identical prompts, the share of answers that change is the recent-sightings list about 3%; the whole-log-in-the-prompt memory about 5% (4%, 6%, 4% by household). Across all days accuracy moves 0 to 2 points.

  But a single window in a single household moved as much as 10 points (one household's last two days, 78 to 88; another household's lead-up, 66 to 62). That is the figure to carry, not the all-days one. Every headline result in these folders is stated per window, and a reader who takes the all-days floor and applies it to a one-window effect will be badly misled. The honest form of the sentence: across all days the floor is small, and per window on a single household it can reach 10. By window, averaged across households, its mean is lead-up +1.8, first sick days -0.7, later spell 0.0, first days back +0.7, days 27-28 -2.1.

  No arm inherits another arm's floor. The recent-sightings list's share did not predict the LLM's, the counting methods have none at all, and the variation across windows is larger than the variation between memories. The floor is a property of an arm and a window, measured, not a constant for the project. Whether the longer prompt carries a genuinely larger floor is unresolved: slightly larger on average, carried by one household, and not distinguishable at three households.

  The counting methods — the timetables and the survival-time model — make no model calls and were re-run and reproduced exactly: one household's whole classical arm, all nine beliefs and 4464 rows, came back byte-identical to the stored log, as did the question bank it was scored on.

  Rerun noise is symmetric, so it does not bias a paired mean, and every spread quoted in these folders is computed across households from the runs as they happened — the noise is already inside each band, and an effect that cleared its bar cleared it with the noise included. What the per-window figure rules out is a different reading: taking one household's line in one window off this page and treating its level as measured to better than ten points.
