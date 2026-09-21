# p_4d8e — Weekend 20:00 dinner cooking: pan, knife, spatula, and pot at the counter

On weekends the household prepares dinner at roughly 19:00–21:00. The pan, kitchen knife, spatula, and pot are all brought to the kitchen counter for active cooking. Before this window (00:00–19:00), the pan rests in the drawer (weekend pattern, unlike the weekday cupboard), the knife and spatula are in the drawer, and the pot is in the cupboard. The cutting board is a permanent counter item on weekends, staying at counter_k1 throughout the day.

After cooking (22:00), the pan returns to the drawer or cupboard, the knife and spatula go back to the drawer or remain on the counter briefly, and the pot returns to the cupboard. The robot's 20:00 weekend passes confirm all four implements at counter_k1 simultaneously.

This document differs from p_2f8b, which focuses on bowls, plates, and the lunchbox rather than the cooking implements. It differs from p_c4e9, which tracks the cleanup progression (counter → sink → storage) on weekdays. The key prediction is the simultaneous presence of pan, knife, spatula, and pot at counter_k1 at 20:00 on weekends.

Refutation: if the pan, knife, or spatula are not at counter_k1 at 20:00 on a weekend, or if they are at the counter during 12:00–18:00 on weekends (before the cooking window).

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter during weekend dinner cooking",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The kitchen knife is on the kitchen counter during weekend dinner cooking",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The spatula is on the kitchen counter during weekend dinner cooking",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The pot is on the kitchen counter during weekend dinner cooking",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
