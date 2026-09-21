# p_9d4c — Guitar migration: couch overnight on weekdays, bedroom floor for practice; reversed on weekends

This document focuses exclusively on Yuki's guitar and its daily migration between the living room couch and the bedroom floor. The patrol data reveals a clear weekday/weekend asymmetry.

On weekdays, the guitar is on the couch at 03:00 (two out of three sightings) and moves to the bedroom floor by 18:00 (one sighting, consistent with the afternoon practice window). The 15:00–16:30 practice window (from p_a3f1 and p_7d2a) is when Yuki sits on the bedroom floor with the guitar. So the weekday pattern is: couch from 00:00 to roughly 14:00, bedroom floor from 14:00 to 24:00 (she moves it to the bedroom for the afternoon and evening practice sessions).

On weekends, the pattern reverses. The 03:00 sightings are split (one couch, one bedroom floor), but the 14:00 sightings are unambiguous: couch_l1 three times out of three. On weekends Yuki practices on the couch in the living room, not in the bedroom. The guitar is on the bedroom floor overnight (or at least in the early morning) and moves to the couch by midday for the afternoon session.

What sets this apart from p_2c8d: p_2c8d has the guitar on the couch at 03:00 on weekdays (for 2, against 2) and on the bedroom floor at 03:00 on weekends (for 1, against 2). This document refines the transition times: on weekdays the guitar leaves the couch around 14:00 (not 15:00), and on weekends it reaches the couch by 12:00 (not 13:00). The 14:00 weekend couch × 3 is the anchor.

What would refute it: the guitar on the bedroom floor at 14:00 on a weekend (it should be on the couch); the guitar on the couch at 18:00 on a weekday (it should be on the bedroom floor for evening practice).

```json
{
 "claims": [
  {
   "claim": "Yuki's guitar is on the living room couch at 14:00 on a weekend during her afternoon practice",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Yuki's guitar is on the bedroom floor at 18:00 on a weekday during her evening practice",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 17,
   "to": 20
  },
  {
   "claim": "Yuki's guitar is on the living room couch at 03:00 on a weekday, overnight resting spot",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Yuki's guitar is on the bedroom floor at 03:00 on a weekend, overnight resting spot",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "guitar_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "bedroom_floor_b1",
    "chance": "usually"
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
