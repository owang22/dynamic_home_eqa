# Caption for F7

**Single-column figure** — reproduce at 3.27 in, its rendered width.

**Title line:** Sets break rather than widen

Paste and edit; written as a caption, not a summary.

---

Top: how often the truth was inside the list of places the rule offers, against the 90% the method promises (dashed). Bottom: how many places the set contained. At the first sick day the guarantee breaks while the set gets no wider — narrower, in fact — so the method's uncertainty does not register the change at all; it simply becomes wrong about it.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** the LLM, sampled 3
- **Questions:** all questions
- **Bands:** none: single-day rates pooled over households
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **How the line is drawn:** Drawn per day rather than as a three-day average: this figure's claim is about a single day, and even a stage-bounded average pairs day 14 with day 15 and reports 75% where the day itself is 69%.
- **About the data:** Each question was put to the model ten times at temperature 0.7 and the list of places the rule offers built from how often each place came back. Each household's first 20 questions are excluded while the threshold warms up, and a day is shown only once all households have finished it.
- **The floor under any effect here:** Some of any difference here is the run having been run again. Identical prompts at temperature zero do not reproduce on this server, so a repeat of the same arm on the same data does not give the same answers, and that sets a floor under every effect involving a memory whose answers a language model generates. Measured on 3 households by re-running each arm over the same data with byte-identical prompts, the share of answers that change is the recent-sightings list about 3%; the whole-log-in-the-prompt memory about 5% (4%, 6%, 4% by household). Across all days accuracy moves 0 to 2 points.

  But a single window in a single household moved as much as 10 points (one household's last two days, 78 to 88; another household's lead-up, 66 to 62). That is the figure to carry, not the all-days one. Every headline result in these folders is stated per window, and a reader who takes the all-days floor and applies it to a one-window effect will be badly misled. The honest form of the sentence: across all days the floor is small, and per window on a single household it can reach 10. By window, averaged across households, its mean is lead-up +1.8, first sick days -0.7, later spell 0.0, first days back +0.7, days 27-28 -2.1.

  No arm inherits another arm's floor. The recent-sightings list's share did not predict the LLM's, the counting methods have none at all, and the variation across windows is larger than the variation between memories. The floor is a property of an arm and a window, measured, not a constant for the project. Whether the longer prompt carries a genuinely larger floor is unresolved: slightly larger on average, carried by one household, and not distinguishable at three households.

  The counting methods — the timetables and the survival-time model — make no model calls and were re-run and reproduced exactly: one household's whole classical arm, all nine beliefs and 4464 rows, came back byte-identical to the stored log, as did the question bank it was scored on.

  Rerun noise is symmetric, so it does not bias a paired mean, and every spread quoted in these folders is computed across households from the runs as they happened — the noise is already inside each band, and an effect that cleared its bar cleared it with the noise included. What the per-window figure rules out is a different reading: taking one household's line in one window off this page and treating its level as measured to better than ten points.
