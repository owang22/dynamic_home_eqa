# p_a7f3 — Weekend hosting: dining table becomes the serving hub

Elena and Priya are home all day on the weekend with no commute. The residents' messages confirm friends arrive "this evening" on both Saturday and Sunday. That means the kitchen is busy from about 16:00 as Elena preps food, and the dining table is set and in active service from roughly 17:00 through 22:00. Plates, glasses, mugs, the kettle, and water bottles all converge on the dining table for serving. The cutting board, pan, and knife are at the counter while Elena cooks. After the social, items are washed and returned to the cupboard or sink by 22:00.

What sets this apart: every other document in the library treats the dining table as a quiet resting spot (vase, wall clock) or a weekday breakfast anchor. This document places the *serving* objects at the dining table during the weekend evening social window, and the *cooking* objects at the counter in the prep window just before. The robot should expect to find plates and glasses at the table, not in the cupboard, during 17–22 h on a weekend.

What would refute it: if the robot finds plate_elena or glass_elena still in the cupboard at 19:00 on a weekend evening, or finds the cutting board on the counter at 21:00 (cooking long over), the hosting sequence is wrong. If friends are not actually present (no extra residents in the living room or dining room), the whole premise collapses.

```json
{
 "claims": [
  {
   "claim": "Elena's plate is at the dining table during the weekend evening social",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 18,
   "to": 21
  },
  {
   "claim": "Elena's glass is at the dining table during the weekend evening social",
   "target": "glass_elena",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 18,
   "to": 21
  },
  {
   "claim": "The kettle is at the dining table being used to serve drinks during the weekend evening",
   "target": "kettle_shared",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 17,
   "to": 20
  },
  {
   "claim": "The cutting board is at the counter while Elena cooks in the weekend prep window",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 16,
   "to": 19
  }
 ],
 "targets": {
  "plate_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "mug_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "kettle_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 15,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 15,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 15,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
