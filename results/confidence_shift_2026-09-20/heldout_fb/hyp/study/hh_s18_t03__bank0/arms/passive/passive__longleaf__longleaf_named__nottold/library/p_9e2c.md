# p_9e2c — Evening snack migration: kitchen table until 22, then coffee table

The snack bowl rests in the kitchen overnight (sink or counter) and is put in the cupboard after the morning. During the evening it follows the residents' movement: from about 19:00 to 22:00 it sits on the kitchen table, where both women gather for dinner and early TV snacks; at 22:00, when the evening settles into the living room, the bowl is carried to the coffee table and stays there until the household winds down around 23:30. This is distinct from p_a3f7 (couch all evening) and p_7d4e / p_f7b3 (kitchen table all evening): here there is a clear 22:00 migration. The 21:00 sightings scatter (kitchen table, cupboard, coffee table, counter) reflects the transitional hour when the bowl is being passed between the kitchen and living room. The remote follows a similar migration: tv_stand until 20:00, then coffee table. The speaker stays on the couch throughout the evening. The blanket migrates from couch to coffee table at 21:00.

What sets this apart: the snack bowl is NOT on the couch at any point in the evening, and it is NOT at the kitchen table after 22:00. The 23:00 sightings (coffee_table ×2) support the late placement, while the 21:00 kitchen_table sighting supports the early placement.

Refutation: if the snack bowl is sighted on the couch during 20–23 h, or at the kitchen table after 22:30, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the kitchen table during early evening TV",
   "target": "snack_bowl_shared",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "The snack bowl is on the coffee table during late evening",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22.5,
   "to": 23.5
  },
  {
   "claim": "The remote is on the coffee table after 21:00",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The speaker is on the couch during evening entertainment",
   "target": "speaker_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
