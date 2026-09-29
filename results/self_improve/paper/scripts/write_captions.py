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
  "Figure 2. The same illness, twice.",
  f"""First room right by day on the fourteen objects whose usual room changes in **both**
illnesses, over the fifty-day run. {MEASURE} Each line is the mean of three households; the band
behind it is one standard error across them. The strip beneath counts the questions those fourteen
objects carried each day, 12 to 29. Shaded spans are the two illnesses, days 14 to 23 and 32 to 41.

A fall is measured from that line's own mean over the four days before the illness starts, which is
what the two annotations report. Zeros are real: on the days the lines touch zero, every question
was answered with the wrong first room, not lost.

Method names are as in the text. Objects are counted as moving in both illnesses because the mover
set is otherwise fixed from the first illness alone, and eight of its twenty-two objects do not
move the second time.""",
  """On the first illness all four memories fall together, by 51 to 59 points. On the second they
do not: the trail and the memory that reads the raw log fall about half as far as the two that keep
only summaries, and the summary-only memories fall as far the second time as the first. Repeating a
condition helps the memories that kept the observations and does not help the memories that
rewrote them away."""),

 "figure3_told_the_cause": (
  "Figure 3. Told the cause, then retracting it.",
  """One household, the *log and notes* memory, told a single sentence on the night before the
illness begins and asked to write down what will change. **Night 13**: the note it wrote, before it
had seen anything. **Day 14**: all eleven questions asked about that resident's moved objects, and
where the answers actually were - every one in a room the note had named, none in the office, the
room the note ruled out. **Night 14**: the same memory's next update, beside the other note it
revised on the same night. Both quotes are verbatim; the ellipsis marks one omitted sentence.""",
  """A language model given a cause it cannot observe writes a useful, specific prediction from it -
and the update rule then discards that prediction the moment the first day's evidence arrives,
while the same night's other note records evidence consistent with the illness. The failure is not
in the inference; it is in the rewriting."""),

 "figureA1_first_illness": (
  "Figure A1. Adapting inside the first illness.",
  f"""First room right by day on the objects the illness moves, over the ten-household run, days 1
to 31. {MEASURE} Each line is the mean of ten households; the band is one standard error across
them. The shaded span is the illness, days 14 to 23.

*Reduced ACE* and *tight working memory* are this run's constrained versions of the two published
designs: the ACE-shaped arm reflects once a night rather than up to three times, and the
MemGPT-shaped arm ran on a 1,200-character block, a sixteenth of the smallest block that lineage
uses. The published implementations appear in Figure 2, on three households.""",
  """Every memory, however it is built, falls to about a third on the first changed day, and every
one climbs back inside the ten days of the illness. The second fall on day 24, when ordinary life
returns, is nearly as deep as the first - adaptation to the new routine is itself a cost when the
old one comes back."""),

 "figureA2_what_the_notes_held": (
  "Figure A2. What the memory held, and what one word came to mean.",
  """**(a)** Live notes on night 31 of the ten-household run that name an object together with a
room that object moves to while the resident is ill, split by the condition the note attaches to
itself. A note counts when a structural matcher finds the object and the note's text contains one
of the rooms or spots that object occupied in daytime hours on days 14 to 23, read from the
simulator rather than from the text. Counts are printed on every segment large enough to hold one.

**(b)** One ACE-style note in one household, nights 13 to 22: the hour that note states as the
beginning of "evening". The resident was in the house every hour of every one of these days.""",
  """The memories record where things went while someone was ill in great detail - 453 notes across
four methods - and not one of the 453 says anyone was ill. They keep the consequence and drop the
cause, which is why none of them can recognise the condition when it returns. Panel (b) is the same
failure inside a single note: with the resident home all day, "evening" no longer divides anything,
and the note keeps the word while sliding the hour it names from 20:00 to 11:47."""),
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
