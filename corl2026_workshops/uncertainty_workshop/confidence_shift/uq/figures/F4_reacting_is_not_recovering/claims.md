# What F4 does and does not support

## Its job in the argument

SUPPORTING. Rules out the obvious objection to the whole argument: that a method could simply notice it is in trouble and decline more. They do notice, and the answers they keep are still wrong far more often than they promised. Noticing is not being calibrated.

## The claim

> Reacting is not recovering. When the routine changes these rules that decide whether to answer DO notice — every one of them roughly doubles or triples how often it declines to answer — and the answers they keep are still wrong 2.4 to 6.3 times more often than the rate they promised. Noticing that something is wrong is not the same as knowing WHICH answers are wrong, and only the second one protects a user.

## What in the figure demonstrates it

The top panel at the first dotted rule, where every line leaves the promise behind. The ranking is printed on the plot: worst is the timetable that never timetable at 6.3 times its promised rate. Then the lower panel, which shows this is not a failure to react: hand-over roughly doubles at the same moment.

## What it does NOT show

It does not show WHY the rule that decides whether to answer reacts, which differs by method and is the more interesting half. The last column of the table is that answer: the timetables' own confidence falls at the shift, by 10.1 and 8.6 points, while the LLM's moves +0.1. So LLM's entire reaction is the controller raising its bar after mistakes have already been made, and none of the four moves its confidence as far as its accuracy fell. Nor does it show what the questions it hands over would have scored: that is F6, and for one method the answer is worse than what it kept.

## The numbers

Measured on the DAILY values, not read off the plotted line.

| series | hands over, settled 9-13 | hands over, days 14-16 | wrong on what it keeps, settled | wrong on what it keeps, 14-16 | times the promised rate, 14-16 | its own confidence moved (points) |
|---|---|---|---|---|---|---|
| timetable that never forgets | 21.4 | 70.6 | 12.5 | 63.0 | 6.3 | -10.1 |
| timetable with a three-day memory | 29.1 | 70.4 | 12.5 | 41.2 | 4.1 | -8.6 |
| LLM | 45.5 | 57.9 | 19.0 | 27.7 | 2.8 | 0.1 |
| survival-time model | 48.7 | 53.3 | 16.5 | 23.9 | 2.4 | -1.3 |
