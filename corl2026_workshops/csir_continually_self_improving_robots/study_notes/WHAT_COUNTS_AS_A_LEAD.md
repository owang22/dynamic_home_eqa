# What counts as a lead worth following, and what is a dud

Written 2026-09-25, before the overnight results land, because deciding this afterwards is how a
run becomes whatever we hoped it was. Oliver asked for the criteria in advance. Five tests. A
lead has to pass all five; failing any one makes it a thing to check, not a thing to report.

## 1. It clears a bar that was set before the number was seen

Either a paired within-household difference that clears **2 standard errors AND the rerun noise
floor** — 1.9 points on first room right, 2.2 on found within the budget, both measured from this
model's own non-determinism at temperature zero — or a **count that cannot be noise**: 0 of 428
notes mentioning the illness, 22 of 27 wrong guesses going to one room, a field that is 100%
unused across ten arms. A mechanism count does not need a standard error; it needs to be
impossible to get by chance.

## 2. It replicates across households

Same direction in **at least three of three**, or four of five once there are five. An effect in
one household is a lead to check tomorrow, never a finding tonight. Today's day-24 result was
promoted only after all three homes showed the same pull toward the illness room, and the third
home showed the mechanism while showing no accuracy gap at all — which is what an honest partial
replication looks like.

## 3. I can name the mechanism and perturb it

Every one of this project's three reversed findings came from a stable aggregate with no
mechanism behind it. So: what in the run produces this number, and what would I change to make it
go away? If the answer is "more data", it is not a lead yet.

## 4. It would change what we write

If both outcomes lead to the same sentence in the paper, it is not worth a night of GPU. State,
before looking, what the write-up says if it holds and what it says if it does not.

## 5. It is NOT explained by a limit we imposed

This is the one that caught us four times in one day. Three "findings about published methods"
turned out to be our own caps: MemGPT refusing 40% of its own memory edits because we capped the
quote at 600 characters against a 20,000-character block; ACE merging only four notes a night
because we capped it, binding on 80.5% of calls; and every room chosen before any reasoning
because a schema listed the fields in that order. **Before promoting any lead, walk the path that
produced it and list every cap, every maxItems, every token budget and every field order in it.**
If one of them is ours and it binds, the lead is about us.

## Duds, named so they are not re-reported

- an effect under the noise floor, however clean the story around it;
- an effect in one household only;
- a count off a field nobody fills — check whether the information is sitting in a free-text
  field beside it before reporting an absence;
- a null from a comparison that had no power to disagree: before believing "no difference", feed
  the comparison a case known to differ and watch it say so;
- a difference between two waves that also differ in the chooser, the bank, the object list or
  the number of questions a day. Those are not comparable and no amount of pairing fixes it.

## What I will report and what I will hold

Report immediately: anything meeting all five, and anything that contradicts something already
reported to Oliver. Hold until morning: everything else, including partial replications and
single-home effects, gathered into one list rather than dripped out.
