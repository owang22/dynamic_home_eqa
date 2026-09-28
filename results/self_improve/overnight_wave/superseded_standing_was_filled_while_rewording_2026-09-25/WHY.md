# Superseded: `standing` was being filled while the model reworded

Stopped 2026-09-25 at about 02:35, partial, by decision rather than failure. **No set-aside
number from these cells is usable.** Nothing deleted. The ten `newest sighting, no model` cells
are not here: they write no notes.

## What was wrong

`standing` was an optional field on every edit, so the model filled it while doing something
else. In `hh_s109_t03`, **23 of 24** set-asides happened in the same edit as a change of
wording; in `hh_s123_t03`, **30 of 30**. The model's own stated reasons for those edits were
reasons for KEEPING the note:

* "Consistent with Day 1 and Day 2 morning sightings. **No new evidence to change status.**"
* "Felix was seen in the office at 17:13 with his items on the desk. **This supports the
  routine.**"

Both set the note aside. So about **85%** of notes carried "set aside for now" whatever the
routine was doing. That destroys the one measure this study reads off the field — whether a
belief written for the ordinary routine survives the disrupted one — and it also means the
robot answered from thirty notes all flagged as not currently true.

It is visible in what the wave agent extracted and flagged before computing anything: 17 of 20
notes at the end of day 14 were already set aside, which is what prompted the check.

## The fix

Setting a note aside is its own action now, `"set a note aside"`, alongside a new
`"bring a note back"` — which the study needs anyway, since the whole point is that routines
return. `standing` is gone from every edit schema and a revision cannot touch it.

## What is NOT affected, and it is the good news

**The content of the notes is untouched.** The conditions and the hypotheses about people are
real and were what we were trying to get: "When Hana returns to the office after dinner",
"Hana moves her pen from the office desk to the office shelf in the evening". The display fix
held. Only the standing field was corrupted, and only because of how it was offered. The
extracted notes are kept at `../arm1_notes_at_day_14_and_24.txt`.

## The pattern, third instance tonight

An optional field the model can fill while doing something else **will** be filled while doing
something else. Tonight: the condition field (filled by copying our own display back), the
working-memory flag (flipped with no day recorded), and now standing. The rule taken from it:
anything whose value is a measurement needs its own action, not a field on an action that does
something else.
