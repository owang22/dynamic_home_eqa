# p_8f3d — Omar's water bottle: a mobile object that follows him through the day

Omar's water bottle is not a fixed object. It migrates through five locations across a typical day: the dish rack overnight (drying), the coffee table in the morning (sitting next to the laptop before he starts work), the desk during his focused work block, back to the dish rack in the late afternoon, the kitchen counter in the early evening, and the kitchen table at dinner. The sightings confirm this: 03:00 dish_rack (x3), 09:00 coffee_table (x1), 11:00 desk (x1), 14:00 desk (x1), 17:00 dish_rack (x2) and desk (x1), 18:00 counter (x1), 19:00 kitchen_table (x3).

This is the object the mixture predicts worst (predicted dish_rack, actually desk; predicted desk, actually dish_rack). No single-location hypothesis works. The bottle follows Omar's body through the house: wherever he is sitting, the bottle is nearby.

What would refute this document: finding the bottle at a single fixed location for more than three consecutive hours during the workday, or finding it out of the house (Omar does not take it on his lunch walk based on the evidence).

```json
{
 "claims": [
  {
   "claim": "Omar's water bottle is in the dish rack overnight",
   "target": "water_bottle_omar",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 3,
   "to": 4
  },
  {
   "claim": "Omar's water bottle is at his desk during the afternoon work block",
   "target": "water_bottle_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Omar's water bottle is at the kitchen table during dinner",
   "target": "water_bottle_omar",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Omar's water bottle is in the dish rack in the late afternoon",
   "target": "water_bottle_omar",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 16,
   "to": 17
  }
 ],
 "targets": {
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
    "to": 15,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
