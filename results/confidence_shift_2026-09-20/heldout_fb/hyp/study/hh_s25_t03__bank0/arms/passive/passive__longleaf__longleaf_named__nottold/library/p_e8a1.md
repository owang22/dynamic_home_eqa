# p_e8a1 — Overnight kitchen: used dishes rest in sink and dish rack; the counter is clear by 03:00

After the evening meal and TV wind-down, the kitchen does not get fully tidied before bed. Used glasses, the water bottle, the snack bowl, and the spatula are set in the sink or the dish rack to dry overnight. The counter is clear by 03:00 (the robot's overnight pass). The pan goes to the dish rack after cooking. The fruit bowl and kettle stay on the counter as permanent fixtures. In the morning, the residents pull their mugs and glasses from the sink/rack, use them at the kitchen table, and the cycle repeats. This is a "lazy overnight" pattern: no one washes dishes at 23:00; the sink and rack are the overnight parking spots.

This document is distinguished by its overnight (00:00–07:00) predictions for kitchen objects. It predicts the snack bowl is in the sink at 03:00 (confirmed by two weekday sightings), the water bottle is in the dish rack at 03:00 (confirmed), and the spatula is in the dish rack at 03:00 (confirmed once). It would be refuted if the snack bowl were found on the coffee table at 03:00, or if the water bottle were at the desk at 03:00.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is in the kitchen sink overnight after the evening TV snacks",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Marco's water bottle is in the dish rack overnight after being used at dinner",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "The spatula is in the dish rack overnight after the evening cooking",
   "target": "spatula_shared",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Marco's glass is in the kitchen sink overnight after being used at dinner",
   "target": "glass_marco",
   "expect": "sink_k1",
   "days": "both",
   "from": 0,
   "to": 7
  },
  {
   "claim": "The kettle remains on the kitchen counter at all times as a permanent fixture",
   "target": "kettle_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21.5,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "glass_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
