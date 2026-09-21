# p_9b4c — Guitar: couch by day, bedroom floor for practice

The guitar's resting spot is the couch during the day, but Yuki moves it to the bedroom floor when she sits down to practice. On weekdays the practice window is the evening (17:00–21:00), after both residents are home; the 18:00 pass shows it on the bedroom floor while 00:00, 08:00, and 16:00 show it on the couch. On weekends the pattern inverts: the 00:00 and 08:00 passes show it on the bedroom floor (morning practice) and the 16:00 pass shows it back on the couch. This document differs from p_7a3d and p_c4e9, which place the guitar on the bedroom floor during a 17:30–19:00 weekday window but do not account for the weekend inversion or the broader 17:00–21:00 practice span. A look that finds the guitar on the couch at 19:00 on a weekday would refute the evening-practice claim; a look that finds it on the couch at 10:00 on a weekend would refute the weekend-morning-practice claim.

```json
{
 "claims": [
  {
   "claim": "The guitar is on the couch during the weekday afternoon",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The guitar is on the bedroom floor during Yuki's weekday evening practice",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 18,
   "to": 21
  },
  {
   "claim": "The guitar is on the couch during the weekend afternoon",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "guitar_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
