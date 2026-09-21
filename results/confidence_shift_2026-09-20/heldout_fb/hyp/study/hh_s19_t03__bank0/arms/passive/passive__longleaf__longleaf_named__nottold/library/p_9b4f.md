# p_9b4f — The home lunch: kitchen table at noon, laptop stays put

Omar does not leave the house for lunch. The 12:00 patrol passes show his plate at the kitchen table (two sightings) and his glass at the kitchen table (one sighting), while his laptop is at the desk (the 13:00 pass finds it at desk_o1). His water bottle is at the desk at 11:00 and 14:00, bracketing the meal. This directly contradicts p_c3d4, which claims laptop, water bottle, and notebook all leave the house 12–14 h; that document's laptop claim has been against once and its notebook claim against twice, with the 13:00 desk sighting as the refutation.

The pattern here is: Omar's work station (desk, laptop, water bottle, mouse, pen) stays assembled through the lunch hour. He walks to the kitchen table, sets out a plate and glass, eats, and walks back. His mug is at the kitchen table in the early morning (08:00, 10:00 sightings) for coffee, then drifts to the coffee table by 09:00 and 18:00. The plate goes from the cupboard to the kitchen table at 11:30 and back at 13:00; at dinner (19:00) it is at the kitchen table again.

This document is refuted if: the laptop is sighted out of the house during 12–14 h; the water bottle is out of the house at lunch; or the plate is not at the kitchen table at 12:00.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at his desk during his midday lunch",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 12,
   "to": 13.5
  },
  {
   "claim": "Omar's plate is at the kitchen table during his lunch",
   "target": "plate_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "Omar's water bottle is at his desk during lunch, not out of the house",
   "target": "water_bottle_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Omar's glass is at the kitchen table during lunch",
   "target": "glass_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "water_bottle_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 11.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glass_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 11.5,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "sometimes"
   }
  ],
  "mug_omar": [
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
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 11,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mouse_omar": [
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "pen_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ]
 }
}
```
