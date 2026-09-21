# p_2c7a — Weekend evening: the TV stand keeps the remote, the couch keeps the blanket, the kitchen keeps the snacks until 22:00

On weekends the evening is more relaxed and less ritualised than on weekdays. The remote stays on the TV stand (weekend 21:00 tv_stand ×1), the blanket drifts between the couch and the bed rather than migrating to the coffee table, and the snack bowl appears at the coffee table only after 22:00 (weekend 22:00 coffee_table ×1). The speaker is on the couch at 22:00 (×2). The laundry basket moves from the bathroom shelf to the bedroom floor in the evening (weekend 19:00 ×1, 20:00 ×2), reflecting the weekend chore routine that does not happen on weekdays (where the basket stays on the bathroom shelf through 19:00).

This document is the weekend complement to p_1a4c (weekday migration). Together they cover the full week. The key difference from the "both" day documents is that the weekend does NOT trigger the 21:00 coffee-table migration of the remote and blanket, and the snack bowl's arrival at the coffee table is delayed to 22:00 or later.

This document would be refuted if the remote is found on the coffee table on a weekend evening, if the blanket is consistently on the coffee table (rather than the couch or bed) on weekend evenings, or if the laundry basket stays on the bathroom shelf through the weekend evening.

```json
{
 "claims": [
  {
   "claim": "The remote is on the TV stand at 21:30 on weekends",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The blanket is on the couch at 21:30 on weekends",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The laundry basket is on the bedroom floor at 20:00 on weekends",
   "target": "laundry_basket_shared",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The snack bowl is in the kitchen at 21:00 on weekends, not yet at the coffee table",
   "target": "snack_bowl_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "speaker_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ]
 }
}
```
