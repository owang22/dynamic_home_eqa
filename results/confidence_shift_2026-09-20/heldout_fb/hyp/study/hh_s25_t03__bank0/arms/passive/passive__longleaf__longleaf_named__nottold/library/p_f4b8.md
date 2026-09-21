# p_f4b8 — Marco's active work: laptop and charger in hand; notebook, pen, and water bottle on the desk

Marco sits at desk_b1 from about 9:00 to 17:30 on weekdays. His working posture is: laptop open on his lap or held in his hands (ON_PERSON), charger plugged into the laptop and therefore also ON_PERSON, notebook flat on the desk surface for reference, pen in the desk's pen holder, and water bottle within reach on the desk in the morning but picked up and held (ON_PERSON) once he settles in around 10:00. The mug starts at the kitchen table for coffee around 8:30–9:00, moves to the desk by 11:00, and is washed and returned to the cupboard or sink by 18:00.

This document is distinct from p_7a3e (the fork) in that it adds the water bottle and mug trajectories and makes the notebook/pen distinction explicit. It is distinct from p_7f2a (which put the notebook ON_PERSON) because the notebook clearly stays on the desk: 10 sightings at desk_b1 across 2 of 3 days, with the 9-17h window showing 5 finds vs 18 misses (the misses being the robot looking at the desk while the notebook is briefly in his hand or the look is at a different moment).

What would refute it: if the water bottle is consistently sighted at a fixed receptacle (not ON_PERSON) during 10–16 h, or if the notebook is found at the desk in 80%+ of midday looks (suggesting it never leaves the surface), the ON_PERSON blocks for those items are wrong.

```json
{
 "claims": [
  {
   "claim": "Marco's water bottle is in his hands during midday work on weekdays",
   "target": "water_bottle_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 11,
   "to": 16
  },
  {
   "claim": "Marco's notebook remains on the desk surface during weekday work hours",
   "target": "notebook_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Marco's pen is on the desk during weekday work hours",
   "target": "pen_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's water bottle is at the desk in the early morning before work",
   "target": "water_bottle_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Marco's mug is at the kitchen table during the weekday breakfast window",
   "target": "mug_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "charger_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 10,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17.5,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "mug_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
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
    "from": 10,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
