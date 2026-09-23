# Caption for F3

**Single-column figure** — reproduce at 3.15 in, its rendered width.

**Title line:** _none needed — this figure does not carry its own title; the paper caption is enough._

Paste and edit; written as a caption, not a summary.

---

One the whole-log-in-the-prompt memory told three different things, on the same ten households. The darkest line is never told; the middle line is told “Yuki is home sick today” on the first sick day (A); the lightest is told that again and then told on the first day of the return that the resident is back (A & B). Each told arm is the same run as the one above it until the day it is told, so it is drawn only from the day it departs after being told.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** longcontext (matched across all three arms) 10
- **Questions:** all questions
- **Bands:** ±1 standard error across households
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **How the line is drawn:** The line is a centred three-day average, computed WITHIN each stage so that it never averages across a stage boundary — a window straddling the boundary borrows the level from the other side and flattens the very change the figure is about. The band, where a figure draws one, is ±1 standard error across households computed on the daily values. On this figure's axis the effect of getting that wrong is concrete: an unbounded window renders the timetable with a three-day memory's 40.8-point fall at day 14 as 6.8.
- **About the data:** Each told arm is drawn from the day it departs from the arm above it, measured from the data rather than taken from the calendar, with the search starting at that arm's own message day. Departure days are in the numbers below, and so is any day an arm differed from the one above it BEFORE its message. Those earlier differences are rerun artefacts rather than design facts: identical prompts at temperature zero are not reproducible on this server, so the arms are identical before their message because those prompts are cache hits, not because generation is deterministic. A cache miss means a fresh generation, which can differ. The twice-told arm differs on two such days by 0.625 points — one answer in a hundred and sixty — and used to be drawn from the first of them, three days before it was told anything.
