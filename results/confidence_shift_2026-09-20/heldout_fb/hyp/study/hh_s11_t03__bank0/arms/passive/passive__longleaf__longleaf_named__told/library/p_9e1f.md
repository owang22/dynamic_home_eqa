# p_9e1f — The Evening Counter; Priya Cooks Light and Snacks at 19:00–21:00

Between 19:00 and 21:00 on weekdays, the kitchen counter becomes the active surface. The sightings show glass_priya at counter_k1 at both 19:00 and 21:00, snack_bowl_shared at counter_k1 at 19:00 (×3) and 23:00, pot_shared at counter_k1 at 20:00, and spatula_shared at counter_k1 at 20:00. This is Priya's light evening cooking and snacking window: she heats something in the pot, uses the spatula, pours a drink, and keeps the snack bowl within reach. Hana is out at work (home only after 23:00), so this is a solo activity.

This document is distinguished by predicting glass_priya, pot_shared, and spatula_shared at counter_k1 (not their resting spots in the cupboard or drawer) during 19:00–21:00. If the robot finds the glass in the sink or the spatula in the drawer at 20:00, this document is weakened. The snack bowl at the counter (not the cupboard or dish rack) during this window is a secondary confirmation.

The remote and blanket, by contrast, are at their living-room spots (tv_stand_l1, coffee_table_l1) during this window—Priya is in the kitchen, not watching TV yet.

```json
{
 "claims": [
  {
   "claim": "Priya's glass is on the kitchen counter during her evening cooking and snacking",
   "target": "glass_priya",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The snack bowl is on the kitchen counter during the evening, not in the cupboard",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 23
  },
  {
   "claim": "The remote stays on the TV stand during the evening counter activity (no TV yet)",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  }
 ],
 "targets": {
  "glass_priya": [
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
    "to": 21.5,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
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
    "to": 23.5,
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
    "from": 19,
    "to": 21,
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
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
