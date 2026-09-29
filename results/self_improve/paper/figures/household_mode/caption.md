# Figure. A mode memory, no language model.

First room right by day on the objects the illness moves, over the ten-household run, for a
latent-state memory built without a language model: object-to-room counts under a Dirichlet prior,
each whole day assigned hard to one mode by a Chinese restaurant process, rooms ranked by the
posterior over modes. It runs in the loop exactly as last seen does, so its own searches decide what
it sees, and the loop was verified first — last seen rerun through the same driver reproduces every
recorded row of all 28 cells, field for field.

It found **one mode** in every household at every setting asked for: alpha 0.5, 1 and 2 crossed
with stay probabilities 0.8, 0.9 and 0.95. Nothing was tuned to change that.

## The claim this figure is here to make

The obvious objection to this study is that a language model is unnecessary — that a small
latent-state model would find the regime for free. Built to a reasonable specification, it does
not: it runs 15 to 20 points below both the trail and our memory through the settled fortnight,
falls to 20% on the first day of the illness, and then sits between 28 and 40 for the whole spell
while the other two are back above 80 within three days. It is the only one of the three that never
recovers *inside* the illness, which is what a single month-long average looks like from outside.

The reason is in the arithmetic rather than the household: a look records everything in the room,
so 82% to 94% of a day's sightings are of objects the illness never touched, each exactly where the
established mode expects. The movers are genuinely surprising — a water bottle in the bedroom at
p=0.009 — but they are a small minority of the evidence, and a whole-day likelihood drowns them.
Hard whole-day assignment cannot detect a shift that touches a minority of objects.
