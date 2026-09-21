# p_f3a7 — The coffee-table bookends: laptop and bottle trace the same arc

Marco commutes to his office 8:00–17:30 on weekdays; his laptop, charger, and sketchbook stay at his desk in bedroom 1 all day. Omar works from home but does not sit at his desk from the moment he wakes. The evidence is clear: at 09:00 his laptop is on the coffee table (three sightings) while at 10:00 it is at the desk (two sightings), and by 18:00 it is back on the coffee table. His water bottle follows the same arc—dish rack overnight, coffee table at 09:00, desk at 11:00 and 14:00, counter at 18:00, kitchen table at 19:00 for dinner. This is not a "laptop at the desk 9-to-5" household; the first hour of Omar's workday is spent at the coffee table reviewing notes, having coffee, and setting up before the desk block begins at roughly 10:00.

What sets this document apart: the laptop is on the coffee table from 00:00 to 10:00 and from 17:00 to 24:00, at the desk only 10:00–17:00. The water bottle is in the dish rack overnight (not the counter), moves to the coffee table in the early morning, sits at the desk during the core work block, and ends the evening at the kitchen table for dinner. Marco's laptop never leaves the house.

This document is refuted if Omar's laptop is consistently at the desk before 10:00 (i.e., the 09:00 coffee-table sightings are anomalies), or if the water bottle is out of the house during any weekday window.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is on the coffee table before his desk block starts",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Omar's laptop is at his desk during the core work block",
   "target": "laptop_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Omar's water bottle is in the dish rack overnight",
   "target": "water_bottle_omar",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Omar's water bottle is at the kitchen table during dinner",
   "target": "water_bottle_omar",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "Marco's laptop stays at his desk even while he is at the office",
   "target": "laptop_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
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
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 16,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "headphones_omar": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
