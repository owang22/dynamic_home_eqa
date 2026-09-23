# Caption for F5

**Double-column figure** — reproduce at full text width, about 6.4 in. Do NOT squeeze it into one column: at single-column width its text lands near 4pt and is unreadable.

**Title line:** _none needed — this figure does not carry its own title; the paper caption is enough._

Paste and edit; written as a caption, not a summary.

---

The same five methods twice: accuracy per day on the left, the confidence each states in its own answer on the right, on one shared scale. A method whose right-hand line moves with its left-hand one knows when it is in trouble; the memory that follows its last sighting's, which never moves at all, is the case where the number means nothing.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** ttfrozen 10, tt3d 10, perpetua 10, longcontext 10, lastseen 10
- **Questions:** all questions
- **Bands:** ±1 standard error across households
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **How the line is drawn:** The line is a centred three-day average, computed WITHIN each stage so that it never averages across a stage boundary — a window straddling the boundary borrows the level from the other side and flattens the very change the figure is about. The band, where a figure draws one, is ±1 standard error across households computed on the daily values.
- **The floor under any effect here:** Some of any difference here is the run having been run again. Identical prompts at temperature zero do not reproduce on this server, so a repeat of the same arm on the same data does not give the same answers, and that sets a floor under every effect involving a memory whose answers a language model generates. Measured so far on 3 households, by repeating the recent-sightings list over the same data: about 3% of answers change (0 to 9% depending on the household and the window), accuracy moves 1 to 2 points typically and at most 6 in a single household-window. Pooled over all three households and every day: mean 0.0, mean absolute 1.2, spread 1.8 points.

  Two things to do with that, rather than quoting the pooled number and moving on. FIRST, the floor is NOT uniform across the run. By window its mean is lead-up +1.8, first sick days -0.7, later spell 0.0, first days back +0.7, days 27-28 -2.1 — so an effect resting on a single window has a larger floor under it than the pooled figure suggests, and quoting the pooled number beside a one-window effect understates it. SECOND, where it helps a reader, state an effect as a multiple of the floor: nineteen points against a floor of one to two is actionable in a way that a value with a spread beside it is not.

  What this floor does NOT cover: the counting methods — the timetables and the survival-time model — generate no text and reproduce exactly on the same data, so they have no rerun floor of this kind. And it is measured on ONE language memory; it is indicative for the others rather than measured on them. Rerun noise is symmetric, so it does not bias a paired mean, and every spread quoted in these folders is computed across households from the runs as they happened — the noise is already inside each band, and an effect that cleared its bar cleared it with the noise included.
