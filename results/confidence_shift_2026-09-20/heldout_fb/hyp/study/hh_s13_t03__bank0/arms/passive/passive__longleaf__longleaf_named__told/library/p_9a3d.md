# p_9a3d — — No Cook Until 19: Kitchen Cold All Afternoon (fork of p_4c8f)

This is a fork of p_4c8f (No Weekday Cook at Six). The parent denies cooking at 18:00 and places the pan in the cupboard 17–19. The evidence now extends this: the pan is in the cupboard at 03:00 (2×) AND at 18:00 (2×), only appearing on the counter at 19:00 (1×). There is no evidence of any cooking at 12:00 either — the pan, pot, and cutting board are all absent from the counter during 9:00–17:00.

The parent's claim "pan in cupboard at 18:00" scored 2 for, 2 against. This fork keeps that claim but extends it: the pan is in the cupboard from 03:00 through 18:00 (the entire day until dinner). The kitchen knife is in the drawer from 03:00 through 18:00. The cutting board is in the drawer during the day (not on the counter, as the 9–17h empty looks confirm).

What changed from the parent: the no-cook window is extended from 17–19 to 11–19 (covering both the denied lunch and the denied early dinner). A cutting board block is added (drawer during the day, counter at 19–21). The mug_hana claim is retained (drinks at the kitchen table during the no-cook dinner).

What sets this apart from p_7d4e (Dinner at 19): p_7d4e is a full cooking hypothesis with a 19–21 window. This document is a negative claim: the kitchen is cold from 11:00 to 19:00. They agree on the 19:00 start but differ on whether there is a lunch cook. What would refute it: pan_shared on counter_k1 at 12:00 on a weekday, or kitchen_knife_shared on counter_k1 at 14:00 on a weekday.

_(targets the fork left unstated are inherited from p_4c8f)_

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 12:00 on a weekday (no lunch cooking)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (no early dinner)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The kitchen knife is in the drawer at 14:00 on a weekday (no knife work all afternoon)",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Hana's mug is on the kitchen table at 18:00 on a weekday (drinks, not dinner cooking)",
   "target": "mug_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
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
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 7,
    "to": 19.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
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
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekday",
    "from": 14,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 7,
    "to": 22,
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
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
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
    "from": 12,
    "to": 14,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
