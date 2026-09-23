# Caption for F7

**Single-column figure** — reproduce at 3.27 in, its rendered width.

**Title line:** _none needed — this figure does not carry its own title; the paper caption is enough._

Paste and edit; written as a caption, not a summary.

---

Top: how often the truth was inside the list of places the rule offers, against the 90% the method promises (dashed). Bottom: how many places the set contained. At the first sick day the guarantee breaks while the set gets no wider — narrower, in fact — so the method's uncertainty does not register the change at all; it simply becomes wrong about it.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** the whole-log-in-the-prompt memory, sampled 3
- **Questions:** all questions
- **Bands:** none: single-day rates pooled over households
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **How the line is drawn:** Drawn per day rather than as a three-day average: this figure's claim is about a single day, and even a stage-bounded average pairs day 14 with day 15 and reports 75% where the day itself is 69%.
- **About the data:** Each question was put to the model ten times at temperature 0.7 and the list of places the rule offers built from how often each place came back. Each household's first 20 questions are excluded while the threshold warms up, and a day is shown only once all households have finished it.
- **The floor under any effect here:** Some of any difference here is the run having been run again. Identical prompts at temperature zero do not reproduce on this server, so a repeat of the same arm on the same data does not give the same answers, and that sets a floor under every effect involving a memory whose answers a language model generates. Measured so far on 3 households, by repeating the recent-sightings list over the same data: about 3% of answers change (0 to 9% depending on the household and the window), accuracy moves 1 to 2 points typically and at most 6 in a single household-window. Pooled over all three households and every day: mean 0.0, mean absolute 1.2, spread 1.8 points.

  Two things to do with that, rather than quoting the pooled number and moving on. FIRST, the floor is NOT uniform across the run. By window its mean is lead-up +1.8, first sick days -0.7, later spell 0.0, first days back +0.7, days 27-28 -2.1 — so an effect resting on a single window has a larger floor under it than the pooled figure suggests, and quoting the pooled number beside a one-window effect understates it. SECOND, where it helps a reader, state an effect as a multiple of the floor: nineteen points against a floor of one to two is actionable in a way that a value with a spread beside it is not.

  What this floor does NOT cover: the counting methods — the timetables and the survival-time model — generate no text and reproduce exactly on the same data, so they have no rerun floor of this kind. And it is measured on ONE language memory; it is indicative for the others rather than measured on them. Rerun noise is symmetric, so it does not bias a paired mean, and every spread quoted in these folders is computed across households from the runs as they happened — the noise is already inside each band, and an effect that cleared its bar cleared it with the noise included.
