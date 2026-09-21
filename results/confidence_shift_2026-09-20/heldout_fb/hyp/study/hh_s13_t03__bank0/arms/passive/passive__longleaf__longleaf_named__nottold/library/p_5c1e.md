# p_5c1e — Overnight Pantry: mugs, glasses, and bowls go to the cupboard and pantry at night

The 03:00 patrol on day 1 revealed a pattern the library had missed: mug_hana was at cupboard_k1 (predicted kitchen_table_k1), mug_priya at pantry_shelf_k1 (predicted sink_k1), glass_hana at pantry_shelf_k1 (predicted sink_k1), glass_priya at nightstand_b2 (predicted sink_k1), bowl_hana at cupboard_k1 (predicted sink_k1), and plate_priya at cupboard_k1 (predicted kitchen_table_k1). The "usual place" for mugs and glasses in most documents is sink_k1, but at 3 AM they are in the cupboard or pantry. This means that after the evening wash-up (around 21:00–22:00), clean mugs and glasses are put away in the cupboard and pantry for storage, not left in the sink. The sink is only a transient location during active use. The glass_priya at nightstand_b2 at 03:00 is a one-off (she was reading in bed with a glass of water).

What sets this apart: at 03:00 on any day, mug_hana is at cupboard_k1, glass_hana is at pantry_shelf_k1, and bowl_hana is at cupboard_k1. The sink is empty of clean dishes overnight. What would refute it: mug_hana at sink_k1 at 03:00, or glass_hana at sink_k1 at 03:00.

```json
{
 "claims": [
  {
   "claim": "Hana's mug is in the cupboard at 03:00 on a weekday",
   "target": "mug_hana",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Hana's glass is in the pantry shelf at 03:00 on a weekday",
   "target": "glass_hana",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Hana's bowl is in the cupboard at 03:00 on a weekday",
   "target": "bowl_hana",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Priya's mug is in the pantry shelf at 03:00 on a weekday",
   "target": "mug_priya",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 2,
   "to": 6
  }
 ],
 "targets": {
  "class:mug": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:plate": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "charger_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
