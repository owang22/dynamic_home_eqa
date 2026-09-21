# p_8b3c — The Guitar Rests: Bedroom Floor All Week, Couch on Weekend Afternoons

The guitar has never been sighted ON_PERSON in any of the seven days of data. On weekdays it sits on bedroom_floor_b1 from 03:00 through 18:00 (and presumably all night). On weekends it migrates to the couch during the afternoon (15:00–17:00 sightings on Saturday) but returns to the bedroom floor by evening. Hana's stated hobby is guitar, but the robot's patrol windows (which catch objects between activities, not during them) never catch her mid-strum. The "guitar is being played at 20:00" claims in p_b1c6 and p_c4f1 have produced against-hits on the remote (which is at the coffee table, not the TV stand, at that hour) and no positive ON_PERSON sightings. This document simply says: the guitar is a piece of furniture on the bedroom floor, with a weekend couch migration. If the guitar is ever sighted ON_PERSON, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "The guitar is on the bedroom floor at 12:00 on a weekday (never moved during the day)",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The guitar is on the bedroom floor at 20:00 on a weekday (not being played, not on the coffee table)",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The guitar is on the couch at 16:00 on a Saturday (afternoon migration, not being played)",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 15,
   "to": 17
  },
  {
   "claim": "The guitar is on the bedroom floor at 09:00 on a weekday (resting, Hana is at work)",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 8,
   "to": 11
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
