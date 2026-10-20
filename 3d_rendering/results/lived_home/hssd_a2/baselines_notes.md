# Simple predictors on hssd_a2: patrol notes against true positions

146 objects move at least once; each is asked about at 10:00, 14:00, 18:00 and 22:00 from day 2 on (between patrols). An answer is a piece of furniture, "with <person>" or "out of the house". Notes: only what the robot's patrols saw (seed 0). True positions: every object's real place at every earlier 2-hour mark (a ceiling, not a robot).

Share of questions with the right furniture (in brackets: right room):

| fed | questions | no history | last known | usual place | usual at this hour | mix |
|---|---|---|---|---|---|---|
| patrol notes | 7592 | 13% | 62% (69%) | 47% (59%) | 48% (59%) | 55% (64%) |
| true positions | 7592 | 0% | 89% (91%) | 57% (73%) | 54% (71%) | 69% (80%) |
