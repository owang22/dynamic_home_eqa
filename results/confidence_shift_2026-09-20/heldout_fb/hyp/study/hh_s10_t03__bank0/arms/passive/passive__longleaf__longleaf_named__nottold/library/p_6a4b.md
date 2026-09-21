# p_6a4b — Weekend cook leaves knife and spatula on the counter overnight

Weekend cooking is more involved than the weekday quick-fix. On a weekend evening around 19:00, the pan, knife, and spatula all come out, and the cooking session runs longer (pot_shared is on the counter at both 19:00 and 20:00 on weekends). When the cooking ends, the pan gets put away properly in the drawer (as p_4b7e notes), but the smaller items — the kitchen knife and the spatula — are left on the counter. They are found back at the counter at 03:00 on the following weekend morning, not in the drawer. This is a "lazy cleanup" for small tools: the big items get shelved, the small ones stay out.

This document is distinct from p_4b7e (which predicts thorough cleanup putting the pan in the drawer) in that it predicts the knife and spatula remain on the counter despite the pan being put away. It is distinct from the weekday cooking documents (p_c007, p_8d2c, p_6f3a) in that it applies only to weekends, where the cooking is longer and the cleanup is partial. If the robot finds the knife in the drawer or the spatula in the drawer at a weekend 03:00 pass, this is refuted.

```json
{
 "claims": [
  {
   "claim": "The kitchen knife is on the kitchen counter at 03:00 on a weekend (left out after cooking, not returned to the drawer)",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "The spatula is on the kitchen counter at 03:00 on a weekend (left out after cooking)",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "The pan is in the kitchen drawer at 03:00 on a weekend (put away properly overnight, unlike the smaller tools)",
   "target": "pan_shared",
   "expect": "drawer_k_k1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "The kitchen knife is on the counter at 19:30 on a weekend (in use during the longer weekend cook)",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ]
 }
}
```
