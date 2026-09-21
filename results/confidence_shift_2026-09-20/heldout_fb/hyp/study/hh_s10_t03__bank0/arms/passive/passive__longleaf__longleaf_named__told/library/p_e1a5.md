# p_e1a5 — Weekday 18-to-19.5h cooking: pan and board on the counter, pot and knife stay put

On a weekday evening there is a brief but real cooking window. Yuki arrives at 17:30 and by 18:00 is in the kitchen. The cutting board is on the counter from 18:00 through 19:30 (prep and cooking). The pan comes out of the cupboard around 18:30 and is on the counter at 19:00 (active cooking). The pot stays in the cupboard — dinner uses the pan, not the pot. The kitchen knife mostly stays in the drawer (light prep, not heavy chopping), and the spatula stays in the drawer. By 19:30 cooking is done; the pan goes back to the cupboard, the board to the sink or counter.

This document is distinguished by predicting the pan ON the counter at 19:00 (not in the cupboard, not in the sink) while simultaneously predicting the pot IN the cupboard at the same time. It also predicts the knife in the drawer at 19:00 (not on the counter). The contrast between pan-on-counter and pot-in-cupboard is the key differentiator from documents that predict all cookware in the cupboard (no cooking) or all on the counter (heavy cooking).

Refuted if: the pan is in the cupboard at 19:00 (no cooking happened); the pot is on the counter at 19:00 (wrong vessel); the knife is on the counter at 19:00 (heavy chopping, not light prep).

```json
{
 "claims": [
  {
   "claim": "The shared pan is on the kitchen counter at 19:00 on a weekday (active cooking)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The shared cutting board is on the kitchen counter at 18:30 on a weekday (prep in progress)",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19.5
  },
  {
   "claim": "The shared pot stays in the cupboard at 19:00 on a weekday (dinner uses the pan, not the pot)",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The kitchen knife stays in the drawer at 19:00 on a weekday (light prep, no heavy chopping)",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
