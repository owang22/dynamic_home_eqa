# p_7b3d — The Invisible Cook: Tools Stay in Storage

The cooking-at-the-counter model is being refuted across the board. The pan-at-counter claims accumulated 13 against votes, the pot-at-counter claims 12, the knife-at-counter 8, and the cutting-board-at-counter 5. Meanwhile the pan's usual place is the cupboard (3 sightings), the pot's is the cupboard, the knife's is the drawer, and the spatula's is the drawer. What the evidence supports is a "invisible cook" pattern: a pot goes on the stove for a brief heat (the robot cannot see the stove), the food is warmed, and the pot returns to the cupboard. The knife and spatula never leave the drawer. The cutting board rests on the counter but is not actively deployed during the observed windows.

This document is distinct from p_3b8c (which places tools in the sink) and p_4a7e (which focuses on the desk evening). Here the prediction is specifically: at 18:00 on a weekday, the pan is in the cupboard, the knife is in the drawer, the pot is in the cupboard, and the spatula is in the drawer. If the robot ever catches the pan or knife on the counter during the 17:30–19:30 window, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The kitchen knife is in the drawer at 18:00 on a weekday",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The pot is in the cupboard at 18:00 on a weekday",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The spatula is in the drawer at 18:00 on a weekday",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19.5,
    "at": "cupboard_k1",
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
    "days": "weekday",
    "from": 17.5,
    "to": 19.5,
    "at": "cupboard_k1",
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
    "days": "weekday",
    "from": 17.5,
    "to": 19.5,
    "at": "drawer_k_k1",
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
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
