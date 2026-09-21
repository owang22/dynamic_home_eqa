# p_9b3f — 19:00 Dinner Cooking: Yuki at the Counter

On weekdays Marco is at work from 13:40 to 22:00, so Yuki cooks dinner alone. The sightings are consistent: at 19:00 the pan is at counter_k1 (2×), the spatula is at counter_k1 (3×), and the kitchen knife is at counter_k1 (1×). By 18:00 all three are still in their resting places (cupboard, drawer), so the cooking window opens between 18:00 and 19:00. By 23:00 the spatula and pan are back in the drawer and cupboard, so cooking ends well before then.

This document focuses on the 18:50–20:00 cooking window on weekdays. It sets itself apart from p_b7c2 (which places cooking at 17:50–19:00) by shifting the window later: the 18:00 passes still show the pan in the cupboard and the spatula in the drawer, so they have not yet been brought out. The actual use is at 19:00, and the window should cover that.

Refutation: if the pan or spatula is found at the counter at 18:00 on a weekday (meaning cooking started earlier than this document allows), or if neither is at the counter at 19:00 on three consecutive weekdays, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter during Yuki's weekday dinner cooking",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "The spatula is on the kitchen counter during Yuki's weekday dinner cooking",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "The kitchen knife is on the kitchen counter during Yuki's weekday dinner cooking",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
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
    "chance": "almost_always"
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
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
