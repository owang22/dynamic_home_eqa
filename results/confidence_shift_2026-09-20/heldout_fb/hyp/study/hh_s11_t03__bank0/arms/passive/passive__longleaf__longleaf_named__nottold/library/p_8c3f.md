# p_8c3f — Weekend Morning; Blanket on the Bed, Hana Sleeps In

On weekends Hana is off work and sleeps in. The blanket migrates to bed_b1 and stays there through the morning: three weekend sightings at 03:00, 07:00, and 08:00 all show it on bed_b1. On weekdays the same 03:00 pass finds it on armchair_l1 or couch_l1 (her post-shift TV spot). The mixture's worst-objects list flags this: predicted couch_l1, actually bed_b1, 2×, day 4 03:00.

This hypothesis predicts that on weekends from 00:00 to about 10:00 the blanket is on bed_b1, Hana's phone is on nightstand_b1 (she's still in bed), and her book may be nearby. After 10:00 the blanket migrates to the couch or coffee table as she gets up. On weekdays the blanket is on the armchair or couch in the early morning, never on the bed. What would refute it: a weekend morning pass (03–09 h) that finds the blanket on the couch or armchair instead of the bed, or finds it on the bed on a weekday.

```json
{
 "claims": [
  {
   "claim": "On weekend mornings the blanket is on Hana's bed because she is sleeping in",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 2,
   "to": 9
  },
  {
   "claim": "On weekend mornings Hana's phone is on her nightstand",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 3,
   "to": 9
  },
  {
   "claim": "On weekday early mornings the blanket is on the couch or armchair, not the bed",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "book_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
