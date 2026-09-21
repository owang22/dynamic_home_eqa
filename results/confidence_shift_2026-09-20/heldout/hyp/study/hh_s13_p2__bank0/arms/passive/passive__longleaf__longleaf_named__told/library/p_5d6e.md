# p_5d6e — The Long Dinner: Kitchen Objects at the Table 19-to-21, Then Dishes and the Coffee Table

The existing documents place dinner at 18:30–19:30 (p_a3f1) or 18–20 (p_c1d6). The sightings tell a later story. At 18:00, plates are still in the cupboard (3/3), the pan is in the cupboard (3/3), and the knife is in the drawer (3/3). At 20:00, plates are at the kitchen_table (3/3 for both plate_hana and plate_priya), glasses are at the kitchen_table (3/3 for glass_hana, 3/3 for glass_priya), and mugs are at the kitchen_table (1/3 each, mixed with cupboard and sink). At 22:00, plates are back in the cupboard/sink, the pan is in the sink (2/3), the cutting board is back on the counter, and the mugs and glasses have migrated to the coffee_table (2/3 for both mugs, 2/3 for glass_hana, 1/3 for glass_priya).

This means the dinner window is 19:00–21:00, not 18:30–19:30. The cooking happens 18:30–19:30 (pan on counter, knife on counter), the eating 19:30–20:30 (plates and glasses at the table), and the cleanup 20:30–21:30 (pan to sink, cutting board to sink, knife to drawer). Then the evening drink phase 21:00–23:00 moves mugs and glasses to the coffee_table for the living-room TV session.

The pot is a special case: at 20:00 it is on the counter (3/3), not in the sink. This suggests the pot is used for something other than a single meal (perhaps a soup or stew that stays on the counter) or is washed later. The cutting board at 20:00 is in the sink (2/3) or drawer (1/3), confirming it was used and is being washed.

What sets this apart: the dinner window is 19–21 h (not 18.5–19.5), the pot stays on the counter at 20:00, and the mug/glass migration to coffee_table happens at 21–23 h as a distinct "evening drink" phase separate from dinner. What would refute it: plates at the kitchen_table at 18:00 (dinner would have started earlier), or mugs at the coffee_table at 18:00 (the evening phase would have started before dinner).

```json
{
 "claims": [
  {
   "claim": "Hana's plate is at the kitchen table at 20:00 on a weekday (dinner in progress)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The pot is on the kitchen counter at 20:00 on a weekday (still in use, not yet washed)",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Priya's mug is at the coffee table at 22:00 on a weekday (evening drink in the living room)",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The cutting board is in the sink at 20:00 on a weekday (being washed after cooking)",
   "target": "cutting_board_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
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
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
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
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:pan": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
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
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
