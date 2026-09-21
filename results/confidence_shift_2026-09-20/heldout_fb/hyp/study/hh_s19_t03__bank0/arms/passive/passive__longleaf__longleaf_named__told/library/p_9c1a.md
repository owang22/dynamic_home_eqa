# p_9c1a — The weekend cook at six: the kitchen wakes an hour early on Saturday and Sunday

The pan sightings draw a sharp line between weekday and weekend cooking. On weekdays the pan is in the cupboard at 18:00 (1 sighting) and on the counter at 19:00 (2 sightings), back in the cupboard by 20:00. On weekends the pan is already on the counter at 18:00 (3 sightings) and still on the counter at 19:00 (4 sightings). The weekend meal is prepared roughly 30–60 minutes earlier because both residents are home and the kitchen is shared from the start. The cutting board, knife, and spatula follow the pan to the counter during the cooking window.

Once cooking is done, the snack bowl sits on the kitchen counter during the evening (weekday 18:00: counter x2; 20:00: counter x3), not on the coffee table. The coffee table is for the blanket, the laptop, and the candle — not for snacks.

This document is refuted if the pan is in the cupboard at 18:00 on a weekend, or if the snack bowl is on the coffee table during the 19:00–21:00 evening window.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter at 18:00 on a weekend because cooking has already started",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday because cooking has not started yet",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 20:00 during the evening, not on the coffee table",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19.75,
   "to": 20.25
  },
  {
   "claim": "The kitchen knife is on the counter at 18:30 on a weekend during the early cooking window",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 18,
   "to": 18.75
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
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
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
    "days": "both",
    "from": 17.5,
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
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 17.5,
    "to": 20,
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
    "to": 20.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 17.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
