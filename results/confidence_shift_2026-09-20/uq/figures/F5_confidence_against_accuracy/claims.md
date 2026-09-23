# What F5 does and does not support

## The claim

> A confidence number can be perfectly stable and mean nothing at all. Last seen states near-total confidence every day of the month while being right about half the time, and the timetables hold theirs steady through a 40-point collapse in their own accuracy. Stability in a confidence signal is not evidence it is tracking anything — it is what a signal looks like when it is ignoring the world. The timetables do not move their stated confidence when they break, so the gap between what they claim and what they achieve opens at the shift; last seen states 98% while being right 58% of the time, a confidence number carrying no information at all; Perpetua* is the one whose stated confidence tracks its own accuracy through the change.

## What in the figure demonstrates it

Compare each method's two lines at the first dotted rule. The never-forgets timetable's accuracy falls 47 points between day 13 and day 14 while the confidence it states moves 14. Perpetua*'s two lines move together: its stated-versus-actual gap at day 14 is +24.8 points against the never-forgets timetable's +10.3. Last seen is the reductio: its right-hand line sits near the top of the scale all month at about 98% while its left-hand line sits near 46%.

## What it does NOT show

Being well-tracked is not being accurate: Perpetua* is the least accurate of the counters here, which is the point of the pairing rather than an inconsistency. The right panel is each method's own number on its own scale, so heights are not comparable between methods — only each line against its own left-hand partner.

## The numbers

Measured on the DAILY values, not read off the plotted line.

| series | accuracy day 13 | confidence day 13 | accuracy day 14 | confidence day 14 | gap at day 14 |
|---|---|---|---|---|---|
| never-forgets timetable | 87.3 | 63.9 | 40.0 | 50.3 | 10.3 |
| 3-day timetable | 83.3 | 47.5 | 42.5 | 38.9 | -3.6 |
| Perpetua* | 69.3 | 71.1 | 44.4 | 69.1 | 24.8 |
| long-context | 79.4 | 88.1 | 61.5 | 91.3 | 29.8 |
| last seen | 46.5 | 98.1 | 57.5 | 98.1 | 40.6 |
