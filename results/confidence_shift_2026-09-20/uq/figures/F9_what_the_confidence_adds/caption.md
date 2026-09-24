# Caption for F9

**Wider than a single column** — reproduce at about 3.9 in. Do NOT squeeze it into one column; its labels are set for this width and shrinking them puts the smallest text near 4pt.

**Title line:** What the confidence adds

Paste and edit; written as a caption, not a summary.

---

What the ORDER of a method's confidences is worth at each stage: the score under the best threshold for that window, minus the score from the best all-or-nothing choice, so that only the part needing the confidence to carry information is shown. The black line on each bar is what the same procedure extracts from shuffled labels, and it is drawn per bar because it moves: a method that is right about half the time hands hindsight far more to work with, so the floor rises at the shift for exactly the methods whose bars rise there. A bar that does not clear its own line is not a result.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** timetable that never forgets 10 (8 in the first days back 24-26), timetable with a three-day memory 10 (8 in the first days back 24-26), survival-time model 10 (8 in the first days back 24-26), LLM 10 (8 in the first days back 24-26)
- **Questions:** all questions
- **Bands:** none: the black line on each bar is a noise floor, not an error bar
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **About the data:** Threshold chosen PER HOUSEHOLD with hindsight, which is the generous reading and suits a figure whose point is that even given hindsight the timetables gain nothing from their own confidence. The floor is that same quantity computed on shuffled labels.
- **The floor under any effect here:** Some of any difference here is the run having been run again. Identical prompts at temperature zero do not reproduce on this server, so a repeat of the same arm on the same data does not give the same answers, and that sets a floor under every effect involving a memory whose answers a language model generates. Measured on 3 households by re-running each arm over the same data with byte-identical prompts, the share of answers that change is the recent-sightings list about 3%; the whole-log-in-the-prompt memory about 5% (4%, 6%, 4% by household). Across all days accuracy moves 0 to 2 points.

  But a single window in a single household moved as much as 10 points (one household's last two days, 78 to 88; another household's lead-up, 66 to 62). That is the figure to carry, not the all-days one. Every headline result in these folders is stated per window, and a reader who takes the all-days floor and applies it to a one-window effect will be badly misled. The honest form of the sentence: across all days the floor is small, and per window on a single household it can reach 10. By window, averaged across households, its mean is lead-up +1.8, first sick days -0.7, later spell 0.0, first days back +0.7, days 27-28 -2.1.

  No arm inherits another arm's floor. The recent-sightings list's share did not predict the LLM's, the counting methods have none at all, and the variation across windows is larger than the variation between memories. The floor is a property of an arm and a window, measured, not a constant for the project. Whether the longer prompt carries a genuinely larger floor is unresolved: slightly larger on average, carried by one household, and not distinguishable at three households.

  The counting methods — the timetables and the survival-time model — make no model calls and were re-run and reproduced exactly: one household's whole classical arm, all nine beliefs and 4464 rows, came back byte-identical to the stored log, as did the question bank it was scored on.

  Rerun noise is symmetric, so it does not bias a paired mean, and every spread quoted in these folders is computed across households from the runs as they happened — the noise is already inside each band, and an effect that cleared its bar cleared it with the noise included. What the per-window figure rules out is a different reading: taking one household's line in one window off this page and treating its level as measured to better than ten points.
- **How much hindsight this figure uses:** The three decision figures use three different amounts of hindsight, and each should be described with the words that match it. F8: ONE threshold per method for the whole run, then scored day by day — oracular in that the constant was chosen knowing the whole run, but it is at least a single policy someone could hold. F9: one threshold per method per WINDOW, chosen knowing that window's outcomes, and one per household. F10: one threshold per method per DAY, chosen knowing that day. None of the three is refitted on held-out data: every threshold in all three is chosen knowing the outcomes it is then scored on, which is what makes them upper bounds on what declining could be worth rather than policies. F8 is the tightest of the three and F10 the loosest.
- **Read with care:** The household count is not the same in every window. A household enters a window only if it answered twenty or more questions inside it, and the first-days-back window is three days long, so two households fall out of it. The first-days-back bars therefore rest on eight households and the rest on ten; the claim above argues from the first sick days, where all ten are present.
