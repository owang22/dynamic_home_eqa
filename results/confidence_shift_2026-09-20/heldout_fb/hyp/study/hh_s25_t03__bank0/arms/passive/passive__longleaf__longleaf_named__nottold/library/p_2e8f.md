# p_2e8f — Morning kitchen arc: vitamins, mugs, and glasses trace the 7-to-9:30 path

The morning follows a predictable arc through the kitchen and bathrooms. Both residents take their vitamins at the kitchen table around 08:00 (Marco's vitamins sighted at kitchen_table_k1 at 08:00 ×2 and 09:00 ×2; Omar's at 08:00 and 09:00). Omar's glasses move from the nightstand (overnight, sighted at 03:00 ×4) to the bathroom shelf (07:00 ×5) to the office desk (09:00 onward). Marco's glasses go from the nightstand (03:00 ×3, 07:00) to the desk (09:00, 11:00 ×2). Mugs cycle from the sink or cupboard (overnight) to the kitchen table (08:00 breakfast: Marco's mug at kitchen_table at 09:00, Omar's at 08:00) to the respective desks (09:00 onward). Marco's bowl appears at the kitchen table during breakfast (07:00, 08:00 ×3, 09:00 ×2). The fruit bowl is a permanent fixture at the kitchen table but the robot's work-hour looks find it absent 21 out of 21 times, suggesting it is obscured by other items or briefly moved during the workday.

This is distinguished from p_a1b2 (which has no morning sequence) and from p_b6e3 (which places Marco's mug at the kitchen table 8–9.5 h but the evidence shows it at the kitchen table only briefly at 09:00 and then at the desk by 11:00).

Refutation: if the vitamins are found at the counter at 08:30 on a weekday, or if Omar's glasses are at the nightstand at 07:30.

```json
{
 "claims": [
  {
   "claim": "Marco's vitamins are at the kitchen table during the 8:00 morning dose window",
   "target": "vitamins_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Omar's glasses are on the bathroom shelf during his 7:00 morning routine",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "Marco's mug is at the kitchen table during the 8:00 breakfast window",
   "target": "mug_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9
  },
  {
   "claim": "Omar's vitamins are at the kitchen table during the 8:00 morning dose window",
   "target": "vitamins_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Marco's glasses are on the nightstand in the early morning before work",
   "target": "glasses_marco",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 0,
   "to": 7
  }
 ],
 "targets": {
  "vitamins_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "vitamins_omar": [
   {
    "days": "weekday",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "mug_marco": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "mug_omar": [
   {
    "days": "weekday",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "glasses_omar": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "bowl_marco": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
