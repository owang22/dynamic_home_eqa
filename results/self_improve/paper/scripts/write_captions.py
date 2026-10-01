#!/usr/bin/env python3
"""One caption file beside each figure: the caption, then the claim it is there to make.

Anything that needs a sentence to explain belongs here rather than on the figure - the definition
of the measure, the estimator behind an annotation, what a band is, how many households, and which
arms are constrained variants rather than the published designs.

    PYTHONPATH=src python3 results/self_improve/paper/scripts/write_captions.py
"""
import pathlib

OUT = pathlib.Path("results/self_improve/paper/figures")
MEASURE = ("*First room right* is the share of questions where the object was in the first of the "
           "up to three rooms the robot opened.")

CAPTIONS = {
 "figure2_both_illnesses": (
  "Figure 2. The same sickness, twice.",
  """**Every memory collapses on the day a change begins. They separate on how fast they come
back.** Three days into the first sickness the memory that keeps both a log and a summary is at 88%,
the trail at 62% and the plain claim store at 61%. The same gap opens at the other two changes:
three days after ordinary life returns it is at 85% against the trail's 78%, and three days into
the second sickness at 91% against 81%.

**The advantage is not in guessing the new room.** On the questions where neither memory has yet
seen an object in the place it now occupies, the two are exactly level - 15.9% each. Neither can
predict where the sickness put things.

**It is in what happens after the first guess fails.** On day 14 both guess the first room about
equally, 27% against 21%; but given its three rooms the log-and-summary memory *finds* the object
57% of the time against the trail's 24%. When its first guess is wrong it reasons about where else
the thing could be, while the trail walks back through the rooms that object used to be in. One
day of that is decisive: by days 15 to 17 it has already seen the moved objects in their new places
on 95% of questions, where the trail has on 59%.

Seeing is necessary and not sufficient - the claim store reaches the same 96% exposure and still
answers 62%, because it has rewritten the sightings into summaries it cannot re-read.

Three households, the fourteen objects that move in both sicknesses.""",
  """The value of a language model here is not prediction and not steady-state accuracy, where the
trail matches it. It is recovery from a wrong guess: with three looks and a readable record, a
wrong first room becomes a found object the same day, and a found object becomes a right first
guess for the rest of the week. That compounding is what "faster adaptation" means mechanically,
and it is why the advantage grows when the robot gets fewer looks a day - every look has to
count."""),

 "figure3_told_the_cause": (
  "Figure 3. Told the cause, then retracting it.",
  """One household, the *log and notes* memory, told a single sentence on the night before the
sickness begins and asked to write down what will change. Both notes are verbatim; the ellipsis
marks one omitted sentence. The second note on night 14 is a night-13 claim that the same update
revised.

**The retraction rests on a single sighting.** Tomas was seen in the office once, at 14:08, and the
memory takes that as the hypothesis failing. But a person who is unwell and staying home can still
walk into their office once in a day; one sighting is not evidence that someone is well, and
nothing in the update asks how much evidence a standing hypothesis should need before it is
dropped.

**The evidence it needed was in its own hand, the same night.** The second note records that
Tomas's glass sat on the bedroom nightstand from 08:07 to 15:12. Across the settled fortnight that
glass spends 91% of the working day in the kitchen and is never once on the bedroom nightstand;
across the ten sickness days it is on that nightstand for 90% of it. A personal item parked in the
bedroom through seven hours of a working day is not a new fact about where the glass lives - it is
the sickness, written down. The memory does not read it that way. It files it as a standing rule
about a Tomas who is well, a few lines below the note where it deletes the hypothesis that explains
it.""",
  """The model can infer a hidden cause it was told about and turn it into specific, correct
predictions with no evidence at all - every one of the eleven questions that day landed where the
note said it would, and none in the room it ruled out. What it cannot do is hold that inference for
one day. The nightly update rewrites belief from the latest day's observations, so a single
contrary sighting retires the hypothesis while a confirming observation written in the same pass is
absorbed as an unrelated fact.

This is the mechanism behind the paper's aggregate result. A memory that rewrites itself each night
has no way to accumulate evidence for an explanation across days, which is why summary-only
memories fall as far at the second sickness as at the first: each night they are reasoning from one
day, and one day never looks like a regime."""),

 "figure4_one_notes_life": (
  "Figure 4. One note's life.",
  """One note in the claim store - claim_0005 of household hh_s2_t03, the untold arm - on four
nights: before the sickness, four days into it, the first night back, and a week after. The note
text and the condition are verbatim, and the condition is the `holds_under` field exactly as it is
stored. The bar above the row places each night against the month: the sick days, 14 to 23, are the
shaded stretch between the two rules, and the ordinary days either side are white.

The text a note carried at the end of night N is read as the text its next revision replaced: a
revision dated day N stores the previous wording under `was`. Nights 13, 18 and 24 come from the
revisions dated 16, 19 and 25. **Night 31 is read from the claim's current statement**, because the
run ends at day 31 and no revision follows it; the claim was revised on day 31, so the file holds
what that night wrote.

The four notes, and their conditions as stored:

| night | the note | `holds_under` |
|---|---|---|
| 13, normal | Tomas's glass is in the kitchen sink in the morning. It is not on the dining table during this time. | Morning (observed 09:09) |
| 18, four days sick | Tomas's glass is on the bedroom nightstand during the day. It is not in the kitchen or office. | Daytime |
| 24, first night back | Tomas's glass is on the bedroom nightstand in the morning. It moves to the kitchen dish rack by midday and stays there until evening. | Daytime |
| 31, a week after | Tomas's glass is on the kitchen cupboard in the morning and evening. | Always |""",
  """A memory that could recognise a returning situation would end the month holding two readings of
this glass - one for ordinary days, one for the days its owner is unwell - and a condition saying
which applies. This one holds a single reading and overwrites it each time.

Night 18 is the whole point. The glass is on the bedroom nightstand through the working day, which
in this household happens only while Tomas is sick, and the note files it under "Daytime" - a
condition that is true again the next morning whatever his state. Nothing marks it as belonging to
an unusual week. By night 31 the bedroom is gone from the note altogether and the condition has
widened to "Always", the most general value the format allows, on a placement that held for ten
days of the month.

Nothing here was lost by forgetting. The note was rewritten every night and every version was
correct about the day it was written on. What the memory never does is keep the old reading beside
the new one with a condition that separates them, which is what it would need to be less wrong when
the sickness comes back."""),
 "figureA1_first_illness": (
  "Figure A1. Adapting inside the first sickness.",
  f"""First room right by day on the objects the sickness moves, over the ten-household run, days 1
to 31. {MEASURE} Each line is the mean of ten households; the band is one standard error across
them. The shaded span is the sickness, days 14 to 23.

*Reduced ACE* and *tight working memory* are this run's constrained versions of the two published
designs: the ACE-shaped arm reflects once a night rather than up to three times, and the
MemGPT-shaped arm ran on a 1,200-character block, a sixteenth of the smallest block that lineage
uses. The published implementations appear in Figure 2, on three households.""",
  """Every memory, however it is built, falls to about a third on the first changed day, and every
one climbs back inside the ten days of the sickness. The second fall on day 24, when ordinary life
returns, is nearly as deep as the first - adaptation to the new routine is itself a cost when the
old one comes back."""),

 "figureA2_what_the_notes_held": (
  "Figure A2. Notes about object rules on night 31.",
  """Notes held on night 31 of the ten-household run that name an object together with a room that
object moves to while the resident is sick, split by what the note makes that object's location
depend on. A note counts when a structural matcher finds the object and the note's text contains
one of the rooms or spots that object occupied in daytime hours on days 14 to 23, read from the
simulator rather than from the text. Counts are printed on every segment large enough to hold one;
the total for each method is printed above its bar. The tight-working-memory method is left out: it
held 101 notes against the claim store's 595, too few for its bar to say anything.""",
  """The memories record where things went while someone was sick in great detail - 426 notes across
three methods - and not one of the 426 says anyone was sick. They keep the consequence and drop the
cause, which is why none of them can recognise the condition when it returns. The conditions they
do attach are the wrong ones for this. "Always" and "a time of day" are 371 of the 426, and both
are true again the next day, sick or well. The twelve that name a person being home come from one
household and one method, and say things like "Dana is at home", which is also true on a well day.
That is 383 of 426, 90%, which is what the line above the axes means by most."""),
}


def main() -> int:
    for style in ("spec", "oliver"):
        for stem, (title, caption, claim) in CAPTIONS.items():
            folder = OUT / style / stem
            if not folder.exists():
                continue
            (folder / "caption.md").write_text(
                f"# {title}\n\n{caption}\n\n## The claim this figure is here to make\n\n{claim}\n")
            print(f"  wrote {folder / 'caption.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
