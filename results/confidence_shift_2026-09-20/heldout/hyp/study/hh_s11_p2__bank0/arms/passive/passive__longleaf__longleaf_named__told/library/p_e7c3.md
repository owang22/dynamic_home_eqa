# p_e7c3 — Friends Evening; the Kitchen Serves, the Living Room Hosts

Friends are coming over this Friday evening. The normal split-shift evening — Hana back from work at 23:00, the two of them settling in for quiet TV — is replaced by a social gathering. The kitchen will be in serving mode: the serving dish comes out of the cupboard to the dining table, the fruit bowl moves from the kitchen table to the dining table as a centrepiece, and extra plates and glasses are laid out. The snack bowl, which usually sits in the cupboard and only occasionally appears on the coffee table, will be out on the coffee table for guests to graze on.

In the living room the blanket shifts to the couch for the guests, and the remote is at the coffee table or TV stand for whatever is being watched. Priya's board-game hobby gives a reason for the puzzle box to leave the bookshelf and land on the dining table. The dog, sensing the excitement, gets the toy dragged out onto the living room floor.

This document is refuted if the serving dish stays in the cupboard or at the sink through the evening, if the puzzle box remains on the bookshelf, if the snack bowl is not on the coffee table, or if the fruit bowl stays at the kitchen table. A quiet evening with no social objects out would kill this hypothesis.

```json
{
 "claims": [
  {
   "claim": "The serving dish is at the dining table in the evening because food is being served to friends",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The fruit bowl is at the dining table as a centrepiece for the evening gathering",
   "target": "fruit_bowl_shared",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table for guests to graze on during the evening",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The puzzle box comes out to the dining table for board games with the friends",
   "target": "puzzle_box_shared",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "serving_dish_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "rarely"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "glass_hana": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "weekday",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ]
 }
}
```
