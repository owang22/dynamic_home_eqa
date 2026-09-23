# Caption for F4

**Single-column figure** — reproduce at 3.27 in, its rendered width.

**Title line:** _none needed — this figure does not carry its own title; the paper caption is enough._

Paste and edit; written as a caption, not a summary.

---

The figure in each legend entry is that method's miss rate over the first sick days (14–16), as a multiple of what it promised, worst first. Top: how often each method is wrong on the questions it chose to answer, as a multiple of the error rate it was set to hold; the dashed line at 1 is that promise. Bottom: how often it declined to answer. The rule that decides whether to answers react to the change — the lower panel roughly doubles — and the upper panel shows that reacting did not make the kept answers reliable.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** timetable that never forgets 10, timetable with a three-day memory 10, whole-log-in-the-prompt memory 10, survival-time model 10
- **Questions:** all questions
- **Bands:** none: these are rates
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **How the line is drawn:** The line is a centred three-day average computed within each stage, never across a boundary. These are rates rather than averages over households, so no band is drawn.
- **About the data:** The top axis is the miss rate among ANSWERED questions divided by the rate the rule that decides whether to answer was set to hold (alpha=0.1), so the dashed line at 1 is the promise and 3 means three times as many wrong answers as promised. The lower panel is the evidence that the rule that decides whether to answer did react.
- **The floor under any effect here:** Some of any difference here is the run having been run again. Identical prompts at temperature zero do not reproduce on this server, so a repeat of the same arm on the same data does not give the same answers, and that sets a floor under every effect involving a memory whose answers a language model generates. Measured so far on 3 households, by repeating the recent-sightings list over the same data: about 3% of answers change (0 to 9% depending on the household and the window), accuracy moves 1 to 2 points typically and at most 6 in a single household-window. Pooled over all three households and every day: mean 0.0, mean absolute 1.2, spread 1.8 points.

  Two things to do with that, rather than quoting the pooled number and moving on. FIRST, the floor is NOT uniform across the run. By window its mean is lead-up +1.8, first sick days -0.7, later spell 0.0, first days back +0.7, days 27-28 -2.1 — so an effect resting on a single window has a larger floor under it than the pooled figure suggests, and quoting the pooled number beside a one-window effect understates it. SECOND, where it helps a reader, state an effect as a multiple of the floor: nineteen points against a floor of one to two is actionable in a way that a value with a spread beside it is not.

  What this floor does NOT cover: the counting methods — the timetables and the survival-time model — generate no text and reproduce exactly on the same data, so they have no rerun floor of this kind. And it is measured on ONE language memory; it is indicative for the others rather than measured on them. Rerun noise is symmetric, so it does not bias a paired mean, and every spread quoted in these folders is computed across households from the runs as they happened — the noise is already inside each band, and an effect that cleared its bar cleared it with the noise included.
