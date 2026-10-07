# wfh_v1 — working from home for ten days

**FAILS four checks, and the reason is structural rather than fixable.** Table:
`check.txt`, numbers: `check.json`.

## What changes in the household

Every resident who normally commutes or goes to campus stops for ten days — about half
the adults in each home, so this touches more people than the illness does. Their work
things stop living at the desk they leave from and start living where they actually
work: the laptop, charger, notebook and pen on the dining table where there is one and
the kitchen table where there is not, the afternoon's reading and their glasses on the
couch, the headset and the water bottle out on the balcony or the living-room side
table. Someone is in the house from nine to six who used to be out.

## What a memory would have to notice

That the work things have stopped travelling — that the laptop no longer goes into the
bag in the morning and no longer comes back to the desk at night — and that the working
day now has three venues rather than one.

## Why it fails, and why that is a finding rather than a bug

The change is real: the laptop's usual place goes from the office desk to the kitchen
table, the charger from the bedside to the table, the work notebook from the desk to the
table, the book from the bed to the couch. But a counting method loses only **6.1**
points on the first two disrupted days against an 8-point bar, and the reason is simple
and worth saying in the paper: **a memory can only be broken about a belief it actually
holds, and while a commuter is commuting the robot is barely ever asked where their work
things are.** Of the 1,010 settled-window questions about the ten classes this disruption
moves, only **311 concern a commuter's possessions; 699 concern the possessions of a
resident who already worked from home** — the commuter's laptop, charger and notebook are
out of the house at the hours they are used, and a question whose true answer is "out of
the house" is dropped from the bank. 131 of the 144 settled-window laptop questions
belong to residents the disruption never touches.

And the asymmetry runs the wrong way: the commuter's share rises from **311 questions in
the settled fortnight to 537 during the spell**, because the new at-home activities are
what put their things on a surface where they can be asked about at all. Much of what looks
like movement is therefore movement of objects with thin settled histories — the same
artefact that got the board game and the jigsaw thrown out of the guest scenario, arriving
here by a subtler route.

The check that says this most directly is the visibility one: even at its most visible hour
the change shows on only **38%** of the objects that moved, and only 32% overnight, against
70% for the bathroom refit.

*(An earlier draft of this verdict said the laptop's "usual place is right only 51% of the
time". That was wrong, and the mistake is worth recording: 51% was the share of settled
laptop questions whose answer was `desk_o1` **pooled across ten households**, which is a
statement about households having different desks, not about a belief being weak. Per
object the laptop is at its own commonest place 100% of the time in the settled window. A
pooled modal share and a per-object accuracy are not the same quantity.)*

## Is it merely a weaker copy of the illness scenario

**No — it is a different disruption that is weaker for a nameable reason.** Both put a
resident at home all day, and they overlap on the couch. But the illness stops them
working and moves their things to the bed and the couch, where the robot had strong
beliefs; working from home keeps them working and moves their things to the table and
the balcony, where it had weak ones. The similarity is in the cause, not in what the
memory has to do. It is not worth a night of compute, and it is worth one sentence in
the paper as the case that shows what makes a disruption detectable.
