# p_9f2c — Guitar Rests on the Bedroom Floor All Weekday; Couch on Saturday Afternoon

The guitar is on bedroom_floor_b1 at every single weekday sighting: 03:00 (4 sightings across four nights) and 18:00 (1 sighting). It is never seen on the coffee table, never on the couch, never ON_PERSON on any weekday. On weekends the picture shifts: at 03:00 it is on the bedroom floor (2 sightings), but at 16:00 it appears on the couch (2 sightings) alongside the bedroom floor (1 sighting). This means Hana does not play guitar on weekday evenings. The guitar is at most a weekend afternoon presence, and even then it seems to rest on the couch rather than being actively played.

This directly contradicts p_b1c6 (guitar played 19–21 every single day) and p_c9d4 (guitar at the coffee table 22–23 on weekdays). What would refute it: seeing the guitar ON_PERSON or at the coffee table on a weekday evening, or seeing it on the bedroom floor on a Saturday afternoon when the couch sightings place it elsewhere.

```json
{
 "claims": [
  {
   "claim": "The guitar is on the bedroom floor at 20:00 on a weekday because Hana does not play it in the evening",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The guitar is on the bedroom floor at 22:00 on a weekday because it is never played on weekdays",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The guitar is on the couch at 16:00 on a Saturday because it was brought out for the afternoon but is resting, not being played",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 15,
   "to": 17
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
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ]
 }
}
```
