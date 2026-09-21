# p_2f8e — Cooking at 19:00; the counter is the active workstation

The p_65d6 document placed the cooking window at 17:30–19:00 and accumulated 8 "against" on every claim. The sightings tell a different story: the pan is at cupboard_k1 at 18:00 and at counter_k1 at 19:00; the spatula is at drawer_k_k1 at 18:00 and at counter_k1 at 19:00 (twice). The actual cooking window is 18:50–20:00, after dinner plates are set. The kitchen knife and cutting board join the pan and spatula at the counter. After cooking, the pan returns to the cupboard, the spatula and knife to the drawer, and the cutting board stays at the counter (it is a permanent counter resident). This document corrects the timing and keeps the resting spots the overnight passes confirm.

What would refute this: a look at the counter during 19:00–20:00 that finds no pan or spatula; or a look at the cupboard/drawer at 19:00 that still finds them there.

```json
{
 "claims": [
  {
   "claim": "The pan is on the counter during the 19:00 cooking window",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The spatula is on the counter during the 19:00 cooking window",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The kitchen knife is on the counter during the 19:00 cooking window",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The pan is back in the cupboard by 20:30 after cooking",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 20.5,
   "to": 22
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
    "days": "both",
    "from": 18.5,
    "to": 20,
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
    "days": "both",
    "from": 18.5,
    "to": 20,
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
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
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
    "chance": "almost_always"
   }
  ]
 }
}
```
