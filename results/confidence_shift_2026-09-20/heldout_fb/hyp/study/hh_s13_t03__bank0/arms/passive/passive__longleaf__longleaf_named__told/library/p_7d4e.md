# p_7d4e — — Dinner at 19: The Kitchen Wakes Late (fork of p_c1d6)

This is a fork of p_c1d6 (Split Cooking). The evidence has shifted the dinner window later: the pan is in the cupboard at 18:00 (seen twice) and on the counter at 19:00 (seen once). The pot shows the same pattern (cupboard at 18:00, counter at 18:00 on one day only). The spatula is in the drawer at 18:00 and on the counter at 19:00. Dinner cooking is 19:00–21:00, not 18:00–20:00.

More importantly, the lunch cooking window (11:00–13:00) is removed entirely. The pan, pot, and cutting board are never seen on the counter during 9:00–17:00 (the robot looks at the counter 8 times in that window and finds the cutting board zero times). The shopping bag IS on the counter at 12:00–13:00, but that is Priya unpacking groceries from her afternoon errands, not cooking. The kitchen is cold from morning until the 19:00 dinner.

What changed from the parent: the 11:00–13:00 cooking blocks are deleted; the 18:00–20:00 dinner blocks are shifted to 19:00–21:00; the cutting board's daytime resting place is now the drawer (it is not on the counter during 9–17). The weekend brunch window is retained but weakened to "sometimes" since there is no weekend data yet to confirm it.

What sets this apart from p_4c8f (No Cook at Six): p_4c8f only denies cooking at 18:00. This document denies cooking at 12:00 AND 18:00, and positively places the cooking at 19:00. What would refute it: pan_shared on counter_k1 at 12:00 on a weekday, or pan_shared on counter_k1 at 18:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (no cooking yet)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The pan is on the counter at 19:30 on a weekday (dinner cooking underway)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The cutting board is in the drawer at 14:00 on a weekday (not on the counter during the day)",
   "target": "cutting_board_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "The pot is in the cupboard at 12:00 on a weekday (no lunch cooking)",
   "target": "pot_shared",
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
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 9,
    "to": 17,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
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
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
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
    "from": 19,
    "to": 21,
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
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
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
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
