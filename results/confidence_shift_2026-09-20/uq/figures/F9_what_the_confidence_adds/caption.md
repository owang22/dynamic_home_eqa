# Caption for F9

**Wider than a single column** — reproduce at about 4.1 in. Do NOT squeeze it into one column; its labels are set for this width and shrinking them puts the smallest text near 4pt.

**Title line:** _none needed — this figure does not carry its own title; the paper caption is enough._

Paste and edit; written as a caption, not a summary.

---

What the ORDER of a method's confidences is worth at each stage: the score under the best threshold for that window, minus the score from the best all-or-nothing choice, so that only the part needing the confidence to carry information is shown. The black line on each bar is what the same procedure extracts from shuffled labels, and it is drawn per bar because it moves: a method that is right about half the time hands hindsight far more to work with, so the floor rises at the shift for exactly the methods whose bars rise there. A bar that does not clear its own line is not a result.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** timetable that never forgets 10 (8 in the first days back 24-26), timetable with a three-day memory 10 (8 in the first days back 24-26), survival-time model 10 (8 in the first days back 24-26), whole-log-in-the-prompt memory 10 (8 in the first days back 24-26)
- **Questions:** all questions
- **Bands:** none: the black line on each bar is a noise floor, not an error bar
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **About the data:** Threshold chosen PER HOUSEHOLD with hindsight, which is the generous reading and suits a figure whose point is that even given hindsight the timetables gain nothing from their own confidence. The floor is that same quantity computed on shuffled labels.
- **How much hindsight this figure uses:** The three decision figures use three different amounts of hindsight, and each should be described with the words that match it. F8: ONE threshold per method for the whole run, then scored day by day — oracular in that the constant was chosen knowing the whole run, but it is at least a single policy someone could hold. F9: one threshold per method per WINDOW, chosen knowing that window's outcomes, and one per household. F10: one threshold per method per DAY, chosen knowing that day. None of the three is refitted on held-out data: every threshold in all three is chosen knowing the outcomes it is then scored on, which is what makes them upper bounds on what declining could be worth rather than policies. F8 is the tightest of the three and F10 the loosest.
- **Read with care:** The household count is not the same in every window. A household enters a window only if it answered twenty or more questions inside it, and the first-days-back window is three days long, so two households fall out of it. The first-days-back bars therefore rest on eight households and the rest on ten; the claim above argues from the first sick days, where all ten are present.
