# Superseded: the people were still called resident_1

Stopped 2026-09-25 at about 01:07, partial and unfinished, by decision rather than failure.
**No number from these cells is usable.** Nothing deleted. The ten `newest sighting, no model`
cells are NOT here: they call no model, see no prompt, and are unaffected.

## Why

These cells were shown `resident_1` and `resident_2` in their look records while the objects
they were asked about carried real owner names like `mug_tomas`. Working out which identifier
belonged to which person is a puzzle about our data, not about the household, and it spent the
model's attention on nothing being studied. `who_lives_here.names_by_resident_id` now reads the
real names from the household's own seed and raises if they disagree with the owner names on
the objects, so every look says "People there: Tomas." instead.

## The timing, which is the part worth recording

| | |
|---|---|
| these cells started | 01:02:33 to 01:02:35 |
| the names change landed on disk | 01:04:10 to 01:04:49 |

So all fourteen running cells had loaded the OLD code and were consistent with each other.
**But the launcher was still alive**, and the next cell it started after 01:04:49 would have
loaded the new code — giving one arm some cells shown `resident_1` and others shown `Tomas`,
with nothing in any output saying which. A confound between arms is visible in a table; a
confound *within* an arm is not. The launcher was stopped inside that window, so the mixing
never happened.

The general rule this earns: **a wave must not be running while the prompts are being edited.**
Python imports at process start, so a live launcher turns any edit into a silent split of the
wave at the moment the edit lands.
