# Caption for F10

**Wider than a single column** — reproduce at about 3.7 in. Do NOT squeeze it into one column; its labels are set for this width and shrinking them puts the smallest text near 4pt.

**Title line:** _none needed — this figure does not carry its own title; the paper caption is enough._

Paste and edit; written as a caption, not a summary.

---

Per day, the score under the best threshold for that day minus the score from answering everything, with the same quantity on shuffled labels subtracted off. Zero means the confidence tells you nothing a coin could not have told you, once hindsight is paid for. The subtraction matters most exactly where the figure does: a method that is right about half the time hands hindsight far more to work with, so at the shift the shuffled-label floor under the timetables climbs from about 0.02 to 1.23. Their raw gain climbs at the shift too — which is why the unfloored number looks like a result — but no faster than the floor beneath it.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** ttfrozen 10, tt3d 10, perpetua 10, longcontext 10
- **Questions:** all questions
- **Bands:** none: the zero line IS the noise floor, because what is plotted is already the excess over it
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **About the data:** One threshold per DAY, shared across the ten households, chosen knowing that day's outcomes. The floor subtracted from it is the same procedure run on labels shuffled inside each household on that day, averaged over 40 shuffles.
- **The floor under any effect here:** Some of any difference here is the run having been run again. Identical prompts at temperature zero do not reproduce on this server, so a repeat of the same arm on the same data does not give the same answers, and that sets a floor under every effect involving a memory whose answers a language model generates. Measured on 3 households by re-running each arm over the same data with byte-identical prompts, the share of answers that change is the recent-sightings list about 3%; the whole-log-in-the-prompt memory about 5% (4%, 6%, 4% by household). Across all days accuracy moves 0 to 2 points.

  But a single window in a single household moved as much as 10 points (one household's last two days, 78 to 88; another household's lead-up, 66 to 62). That is the figure to carry, not the all-days one. Every headline result in these folders is stated per window, and a reader who takes the all-days floor and applies it to a one-window effect will be badly misled. The honest form of the sentence: across all days the floor is small, and per window on a single household it can reach 10. By window, averaged across households, its mean is lead-up +1.8, first sick days -0.7, later spell 0.0, first days back +0.7, days 27-28 -2.1.

  No arm inherits another arm's floor. The recent-sightings list's share did not predict the whole-log memory's, the counting methods have none at all, and the variation across windows is larger than the variation between memories. The floor is a property of an arm and a window, measured, not a constant for the project. Whether the longer prompt carries a genuinely larger floor is unresolved: slightly larger on average, carried by one household, and not distinguishable at three households.

  The counting methods — the timetables and the survival-time model — make no model calls and were re-run and reproduced exactly: one household's whole classical arm, all nine beliefs and 4464 rows, came back byte-identical to the stored log, as did the question bank it was scored on.

  Rerun noise is symmetric, so it does not bias a paired mean, and every spread quoted in these folders is computed across households from the runs as they happened — the noise is already inside each band, and an effect that cleared its bar cleared it with the noise included. What the per-window figure rules out is a different reading: taking one household's line in one window off this page and treating its level as measured to better than ten points.
- **How much hindsight this figure uses:** The three decision figures use three different amounts of hindsight, and each should be described with the words that match it. F8: ONE threshold per method for the whole run, then scored day by day — oracular in that the constant was chosen knowing the whole run, but it is at least a single policy someone could hold. F9: one threshold per method per WINDOW, chosen knowing that window's outcomes, and one per household. F10: one threshold per method per DAY, chosen knowing that day. None of the three is refitted on held-out data: every threshold in all three is chosen knowing the outcomes it is then scored on, which is what makes them upper bounds on what declining could be worth rather than policies. F8 is the tightest of the three and F10 the loosest.
