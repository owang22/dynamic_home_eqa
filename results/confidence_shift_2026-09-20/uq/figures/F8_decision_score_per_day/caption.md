# Caption for F8

**Single-column figure** — reproduce at 3.09 in, its rendered width.

**Title line:** _none needed — this figure does not carry its own title; the paper caption is enough._

Paste and edit; written as a caption, not a summary.

---

Daily decision score under a rule that needs no target to explain: +1 for a right answer, −1 for a wrong one, 0 for declining to answer. Each method uses its own best fixed confidence threshold. Both timetables collapse on the first sick day; the survival-time model and the whole-log-in-the-prompt memory do not.

---

- **Population:** one resident off sick, that resident's own things
- **Households:** ttfrozen 10, tt3d 10, perpetua 10, longcontext 10
- **Questions:** all questions
- **Bands:** none: this is a score, not an average with a spread
- **Dotted vertical rules:** the stage boundaries — the first sick day and the first day back. Nothing is shaded, so the lines and their bands sit on a plain ground.
- **How the line is drawn:** The line is a centred three-day average computed within each stage, never across a boundary. These are rates rather than averages over households, so no band is drawn.
- **About the data:** Each method uses its OWN best fixed threshold, because the comparison would otherwise measure their confidence scales rather than their judgement — the timetables spread mass over dozens of places and rarely exceed 0.5, the whole-log-in-the-prompt memory says 0.95 to almost everything. Every window figure in the table below is the mean of the DRAWN daily series, computed from it rather than recomputed beside it. That is the structural fix, not a repair: this table previously held per-window refits — a different estimator, in the same units, with values close enough that a reader comparing table to line saw an agreement that was not there. Wherever a table sits beside a line, compute the table from the line.
- **The floor under any effect here:** Some of any difference here is the run having been run again. Identical prompts at temperature zero do not reproduce on this server, so a repeat of the same arm on the same data does not give the same answers, and that sets a floor under every effect involving a memory whose answers a language model generates. Measured so far on 3 households, by repeating the recent-sightings list over the same data: about 3% of answers change (0 to 9% depending on the household and the window), accuracy moves 1 to 2 points typically and at most 6 in a single household-window. Pooled over all three households and every day: mean 0.0, mean absolute 1.2, spread 1.8 points.

  Two things to do with that, rather than quoting the pooled number and moving on. FIRST, the floor is NOT uniform across the run. By window its mean is lead-up +1.8, first sick days -0.7, later spell 0.0, first days back +0.7, days 27-28 -2.1 — so an effect resting on a single window has a larger floor under it than the pooled figure suggests, and quoting the pooled number beside a one-window effect understates it. SECOND, where it helps a reader, state an effect as a multiple of the floor: nineteen points against a floor of one to two is actionable in a way that a value with a spread beside it is not.

  What this floor does NOT cover: the counting methods — the timetables and the survival-time model — generate no text and reproduce exactly on the same data, so they have no rerun floor of this kind. And it is measured on ONE language memory; it is indicative for the others rather than measured on them. Rerun noise is symmetric, so it does not bias a paired mean, and every spread quoted in these folders is computed across households from the runs as they happened — the noise is already inside each band, and an effect that cleared its bar cleared it with the noise included.
- **How much hindsight this figure uses:** The three decision figures use three different amounts of hindsight, and each should be described with the words that match it. F8: ONE threshold per method for the whole run, then scored day by day — oracular in that the constant was chosen knowing the whole run, but it is at least a single policy someone could hold. F9: one threshold per method per WINDOW, chosen knowing that window's outcomes, and one per household. F10: one threshold per method per DAY, chosen knowing that day. None of the three is refitted on held-out data: every threshold in all three is chosen knowing the outcomes it is then scored on, which is what makes them upper bounds on what declining could be worth rather than policies. F8 is the tightest of the three and F10 the loosest.
- **Read with care:** one threshold per method, chosen knowing the whole run, so this is an upper bound rather than a deployable policy, which makes the negative result stronger: even handed the answers in advance, declining buys the counters almost nothing exactly when it would matter
