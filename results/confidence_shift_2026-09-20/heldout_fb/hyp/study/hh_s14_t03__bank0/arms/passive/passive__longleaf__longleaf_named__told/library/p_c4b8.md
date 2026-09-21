# p_c4b8 — Evening Kitchen: Dishes to Sink, Marco Home by 23, Snack Bowl at Counter

The evening kitchen routine (18:00–24:00) is distinct from the daytime pattern. Yuki cooks dinner around 17:30–18:30; by the 18:00 patrol pass, plates are already at the sink being washed (plate_yuki sighted at sink_k1 at 18:00) while glasses are still at the table (glass_yuki at kitchen_table_k1 at 18:00). Marco is at work until 23:00, so his glass stays in the cupboard through the evening. At 22:00, glass_marco appears at the kitchen table—Yuki has set it out for his return. By 23:00, both glasses are at the counter (washing up after Marco comes home), and the snack bowl is at the counter, not the coffee table.

This document corrects the standard TV-time prediction that the snack bowl goes to the coffee table 19:30–22:00. The 22:00 and 23:00 sightings place snack_bowl_shared at counter_k1, not coffee_table_l1. The snack bowl is used for dinner or a late snack at the kitchen counter, not for TV grazing on the coffee table. The remote and blanket still follow the standard TV pattern.

What sets this apart: at 22:00 on a weekday, snack_bowl_shared is at counter_k1 (not coffee_table_l1), and glass_marco is at kitchen_table_k1 (not cupboard_k1). If the robot finds the snack bowl on the coffee table at 22:00 or Marco's glass still in the cupboard at 22:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is at the kitchen counter at 22:00 on a weekday, not the coffee table",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 21.5,
   "to": 23.5
  },
  {
   "claim": "Marco's glass is at the kitchen table at 22:00 set for his return",
   "target": "glass_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "Yuki's plate is at the kitchen sink at 18:00 being washed after dinner",
   "target": "plate_yuki",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Marco's glass is at the kitchen counter at 23:00 during wash-up",
   "target": "glass_marco",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
  }
 ],
 "targets": {
  "plate_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "mug_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
