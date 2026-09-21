# p_a2c8 — Ines's mug travels through the day; Elena's morning transition at the armchair and bathroom shelf

Ines's mug follows a clear daily path: kitchen table in the early morning (before 9), office desk during the afternoon (13–18h), and the sink in the evening (18–20h). Her water bottle is at the sink at night, at the desk from 8 to 18, and at the kitchen table at 19. Elena's morning is distinctive: her water bottle is at the dish rack at 03:00 (washed overnight), at the armchair at 07:00 (she's getting ready, sitting down to put on shoes or check her phone), and at the entry floor by 18:00 (back from work). Her towel is on the rack at 03:00 and 08:00 but on the bathroom shelf at 07:00 (she's in the bathroom getting ready for work). Her razor is at the sink at 03:00 and 18:00 but on the bathroom shelf at 07:00. Ines's glass is at the sink at night, at the kitchen table during lunch and dinner, at the counter in the evening, and at the nightstand at bedtime. This document captures the transition objects of the morning and the meal-to-sink cycle.

What would refute it: If Ines's mug is at the desk before 13:00 on a weekday, or if Elena's water bottle is at the entry floor at 07:00 instead of the armchair, or if Elena's towel is on the rack at 07:00.

```json
{
 "claims": [
  {
   "claim": "Ines's mug is at the office desk in the afternoon on weekdays",
   "target": "mug_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13,
   "to": 17
  },
  {
   "claim": "Elena's water bottle is at the armchair in the early morning",
   "target": "water_bottle_elena",
   "expect": "armchair_l1",
   "days": "both",
   "from": 6.5,
   "to": 7.5
  },
  {
   "claim": "Elena's towel is on the bathroom shelf in the early morning",
   "target": "towel_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 6.5,
   "to": 7.5
  },
  {
   "claim": "Ines's water bottle is at the office desk during weekday work hours",
   "target": "water_bottle_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 18,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "desk_o1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 2,
    "to": 6,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "towel_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "razor_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "glass_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
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
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
