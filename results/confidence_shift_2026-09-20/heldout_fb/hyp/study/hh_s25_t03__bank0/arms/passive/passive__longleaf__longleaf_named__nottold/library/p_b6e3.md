# p_b6e3 — Morning kitchen arc: vitamins, mugs, and glasses trace the 7-to-9:30 path

The morning in this household is a slow migration from the bedroom to the kitchen table and then to the desks. At 07:00, Omar's glasses leave the nightstand for the bathroom shelf (shaving, washing). Marco's glasses go straight to his desk at 09:00 when he starts work. At 08:00, both residents' vitamins (bottles of pills) come off the kitchen counter to the kitchen table for the morning dose. Mugs follow: Marco's mug goes from the sink (where it dried overnight) to the kitchen table at 08:00–09:00, then to his desk by 09:30. Omar's mug goes from the cupboard or sink to his desk by 09:00. Marco's bowl is at the kitchen table from 07:00 (breakfast cereal) and back in the cupboard by 09:00. By 09:30 the kitchen table is clear and both residents are at their desks.

This document is distinguished by its focus on the 7:00–9:30 window, where most other documents are silent or only give a single resting spot. It predicts that vitamins are at the kitchen table (not the counter) between 08:00 and 09:30, and that Omar's glasses are at the bathroom shelf (not the desk) between 07:00 and 08:30. It would be refuted if vitamins were found at the counter at 08:30 on a weekday, or if Omar's glasses were at his desk at 07:30.

```json
{
 "claims": [
  {
   "claim": "Marco's vitamins are at the kitchen table during the 8:00 morning dose window on weekdays",
   "target": "vitamins_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Omar's glasses are on the bathroom shelf during his 7:00 morning routine on weekdays",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "Marco's mug is at the kitchen table during the 8:00 breakfast window on weekdays",
   "target": "mug_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Marco's glasses are on his desk during weekday work hours, not on the nightstand",
   "target": "glasses_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Omar's vitamins are at the kitchen table during the 8:00 morning dose window on weekdays",
   "target": "vitamins_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  }
 ],
 "targets": {
  "vitamins_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9.5,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "vitamins_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9.5,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "rarely"
   }
  ],
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 16,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 18,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "bowl_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 9,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
