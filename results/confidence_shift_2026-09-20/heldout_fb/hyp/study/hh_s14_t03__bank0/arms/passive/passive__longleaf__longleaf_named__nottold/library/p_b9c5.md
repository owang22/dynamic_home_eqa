# p_b9c5 — Guitar on the Couch by Day, Bedroom Floor for Evening Practice, Back on the Couch for TV

Yuki plays guitar as a hobby and practices in the living room during the day, with the guitar resting on or beside the couch. In the early evening (around 17:00–18:00) she moves it to the bedroom floor for a quieter practice session, away from the living room. By 21:00, when the household settles in for TV, the guitar is back on the couch. Overnight the guitar is sometimes left on the couch and sometimes on the bedroom floor (the 03:00 weekday pass shows an even split), so this document does not pin it down for the 0–6 hour window and lets the robot's own statistics handle those hours. On weekends the pattern is the same: couch during the day (the 14:00 weekend pass shows couch x3), bedroom floor in the evening, couch for late-night TV.

This document differs from p_5d8a, which places the guitar on the couch at 14:00 (supported) but at the bedroom floor at 03:00 on weekends (1 for, 2 against — the split data doesn't support a single resting spot overnight). It also differs from p_a3f1, which puts the guitar on the bedroom floor at 15:00–16:30 on weekdays (a time when the data shows it on the couch). This document would be refuted if the guitar were sighted on the bedroom floor at 14:00 on a weekday (contradicting the daytime-couch block) or on the couch at 19:00 (contradicting the evening-bedroom-floor block).

```json
{
 "claims": [
  {
   "claim": "Yuki's guitar is on the living room couch at 14:00 on a weekday",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Yuki's guitar is on the bedroom floor at 19:00 on a weekday during her evening practice",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Yuki's guitar is on the living room couch at 22:00 on a weekday during TV time",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Yuki's guitar is on the living room couch at 14:00 on a weekend",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 13,
   "to": 16
  }
 ],
 "targets": {
  "guitar_yuki": [
   {
    "days": "both",
    "from": 6,
    "to": 17,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
