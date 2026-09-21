# p_d5f8 — Weekend Living Room: Both Home, Blanket Migrates, Evening TV

With both residents home all day, the living room becomes the social center. The blanket migrates from the couch to the coffee table during the middle of the day (roughly 9:00–18:00) for TV, reading, or napping, then returns to the couch in the evening. Marco's phone and water bottle are in the living room area when he is home, and go out with him during his midday errands. The remote stays at the TV stand. The snack bowl is at the kitchen counter in the afternoon and may migrate to the coffee table in the evening.

What sets this apart from the weekday documents: on weekdays Marco is absent 13:40–23:00, so the living room is Yuki's alone in the afternoon and the blanket stays on the couch. Here, both are present and the coffee table is the active surface for the middle of the day. The evidence already shows the blanket at coffee_table_l1 at 10:00 and 13:00 on weekdays (when Marco should be out), suggesting the migration happens whenever someone is settled in for the afternoon.

This is refuted if the blanket is on the couch at 12:00 on a weekend (no migration), or if Marco's phone is at the coffee table at 13:00 (he should be out on errands).

```json
{
 "claims": [
  {
   "claim": "The blanket is on the coffee table during the weekend midday while both residents relax in the living room",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Marco's phone is out of the house during his weekend midday errand",
   "target": "phone_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The remote is at the TV stand during the weekend evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Marco's water bottle is back on the coffee table after his errand",
   "target": "water_bottle_marco",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 15,
   "to": 18
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "phone_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "tissue_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
