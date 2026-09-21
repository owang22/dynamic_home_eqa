# p_2f8b — 19:00 Dinner: Yuki Cooks at the Counter

The 19:00 patrol pass catches the pan, spatula, and kitchen knife all on the kitchen counter at the same time, while at 18:00 they sit in the cupboard or drawer. This is Yuki's dinner cooking, happening in the gap between the 18:00 and 20:00 passes. The window here is tighter than p_9b3f's 18.5–20 h: the cookware arrives at the counter right at 19:00 and is likely put away by 20:00, so a 19–20 h block avoids the transition minutes that generate "against" votes in the wider window. This document focuses solely on the three cooking objects and their precise in-use window. It would be refuted if any of the three is found in the cupboard or drawer at 19:00–19:30 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter during Yuki's weekday dinner cooking",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The spatula is on the kitchen counter during Yuki's weekday dinner cooking",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The kitchen knife is on the kitchen counter during Yuki's weekday dinner cooking",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
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
    "days": "weekday",
    "from": 19,
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
    "days": "weekday",
    "from": 19,
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
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
