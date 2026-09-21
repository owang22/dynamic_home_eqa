# p_b9c4 — Hana Cooks Dinner: the kitchen counter is the evening stage

Hana is the primary cook for dinner. On weekdays she starts cooking at 17:30 and serves at 19:00. During this window the pan, pot, cutting board, and kitchen knife are on the counter. Priya sits at the kitchen table or helps at the counter. On weekends Hana cooks brunch 11:00–13:00 (same objects on the counter). Lunch on weekdays is a simple affair: Priya makes a sandwich or heats something, minimal counter use.

What sets this apart: at 18:00 on a weekday, pan_shared and pot_shared are on counter_k1 (not in cupboard_k1). cutting_board_shared is on counter_k1. kitchen_knife_shared is on counter_k1 (not in the drawer). At 12:00 on a weekday the pan is still in the cupboard. What would refute it: pan_shared at cupboard_k1 at 18:00 on a weekday, or cutting_board_shared at counter_k1 at 12:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter at 18:00 on a weekday",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The cutting board is on the counter during dinner cooking",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The kitchen knife is on the counter during dinner cooking",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The pan is in the cupboard at noon on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 11,
   "to": 14
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
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
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
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
    "from": 18.5,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
