# p_2c8d — Guitar: Couch by Day, Bedroom Floor by Night (Weekdays Reversed on Weekends)

Yuki practices guitar in the afternoon. The evidence shows a clear split: on weekdays the guitar rests on the living room couch overnight and through the day (03:00 sightings: couch ×2, bedroom_floor ×1), then migrates to the bedroom floor in the evening (18:00: bedroom_floor). On weekends the pattern reverses: the guitar is on the bedroom floor overnight (03:00: bedroom_floor) and on the couch in the afternoon (14:00: couch ×3), presumably because Yuki has just finished an evening practice the night before and leaves it in the bedroom, then brings it to the couch for her late-morning/afternoon session.

This differs from p_e8b3 and p_c1d7, which place the guitar on the couch at 03:00 on *both* days (their claim scored for 2, against 4 — the weekend 03:00 bedroom_floor sighting contradicts them). It also differs from p_a3f1, which only claims the guitar at bedroom_floor_b1 during weekday afternoon practice (15–16.5 h) without specifying the overnight location. If the guitar is found on the couch at 03:00 on a Saturday, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Yuki's guitar is on the living room couch at 03:00 on a weekday",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Yuki's guitar is on the bedroom floor at 03:00 on a weekend",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Yuki's guitar is on the living room couch at 14:00 on a weekend during her afternoon practice",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Yuki's guitar is on the bedroom floor at 18:00 on a weekday after she has moved it for evening practice",
   "target": "guitar_yuki",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 17,
   "to": 20
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
