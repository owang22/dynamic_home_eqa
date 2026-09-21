# p_8d4c — Cooking tools rest in drawers and cupboards, not on the counter

The per-object statistics list the sink as the "usual place" for the cutting board, knife, pan, and spatula, but that is an artefact of the robot catching them after washing. Their true resting places between uses are the kitchen drawer (knife, spatula), the cupboard (pan, pot), and the sink area (cutting board, stored beside the sink). The 18:00 Tuesday pass confirms this: the knife is in the drawer, the spatula in the drawer, the pan in the cupboard, the pot in the cupboard. They only appear on the counter during the short active-cooking window (roughly 18:30–19:30 on weekdays).

This hypothesis corrects p_c007, which places the pan at the counter during 18–19.5 h; the pan is in the cupboard at 18:00 and only comes out for a few minutes of actual cooking. It also explains the mixture's worst-objects entries for the pan, knife, and spatula (predicted ON_PERSON, actually sink): the models are wrong about both the resting place and the in-use location. The pot's resting place is the pantry shelf, not the cupboard, as the 20:00 and 22:00 sightings confirm.

Refutation: if the pan or knife is consistently found on the counter at 18:00 (before cooking starts), or if they are stored in a receptacle other than the drawer or cupboard.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard before Yuki starts cooking on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 18.5
  },
  {
   "claim": "The kitchen knife is in the drawer before cooking on a weekday",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17,
   "to": 18.5
  },
  {
   "claim": "The spatula is in the drawer before cooking on a weekday",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17,
   "to": 18.5
  },
  {
   "claim": "The pot is stored in the pantry shelf after cooking on a weekday",
   "target": "pot_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 20,
   "to": 24
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
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
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
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "knife_block_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
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
  ],
  "class:razor": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
