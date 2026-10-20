# Simple predictors on hssd_a: patrol notes against true positions

145 objects move at least once; each is asked about at 10:00, 14:00, 18:00 and 22:00 from day 2 on (between patrols). An answer is a piece of furniture, "with <person>" or "out of the house". Notes: only what the robot's patrols saw (seed 0). True positions: every object's real place at every earlier 2-hour mark (a ceiling, not a robot).

Share of questions with the right furniture (in brackets: right room):

| fed | questions | no history | last known | usual place | usual at this hour | mix |
|---|---|---|---|---|---|---|
| patrol notes | 7540 | 16% | 65% (71%) | 48% (59%) | 47% (58%) | 57% (65%) |
| true positions | 7540 | 0% | 90% (92%) | 58% (72%) | 52% (68%) | 68% (79%) |
