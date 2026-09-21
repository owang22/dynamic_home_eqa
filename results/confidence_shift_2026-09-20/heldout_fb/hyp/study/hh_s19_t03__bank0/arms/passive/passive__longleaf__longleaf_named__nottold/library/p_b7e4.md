# p_b7e4 — Water bottles in the dish rack overnight, never at the counter

The failed block in p_3a7f ("class:water_bottle at counter_k1", 0.16 on 13 sightings) is the clearest signal in the library: water bottles do NOT rest at the counter. The 03:00 passes show both bottles in the dish_rack_k1 (Marco ×2, Omar ×3). During the day, Omar's bottle migrates to the coffee table (09:00), his desk (11:00, 14:00), back to the dish rack (17:00), the counter briefly (18:00), and the kitchen table at dinner (19:00 ×3). Marco's bottle goes to the coffee table (10:00), the dish rack or kitchen table (18:00), and the kitchen table (20:00).

This document differs from p_3a7f (which put the class default at the counter) and from p_4f8e/p_7e3a (which put Omar's bottle at the dish rack overnight but don't specify the daytime arc) by giving a full daytime trajectory for both bottles. The counter at 18:00 for Omar's bottle is a transient (he's moving from desk to kitchen for dinner), not a resting spot.

Refutation: if either water bottle is at the counter at 03:00, if Omar's bottle is out of the house during the workday (not at the desk or coffee table), or if Marco's bottle is at the entry hook during the workday.

```json
{
 "claims": [
  {
   "claim": "Omar's water bottle is in the dish rack at 03:00 overnight",
   "target": "water_bottle_omar",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 3,
   "to": 3.5
  },
  {
   "claim": "Marco's water bottle is in the dish rack at 03:00 overnight",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 3,
   "to": 3.5
  },
  {
   "claim": "Omar's water bottle is at his desk during the core work block",
   "target": "water_bottle_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Omar's water bottle is at the kitchen table during dinner",
   "target": "water_bottle_omar",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
  "class:water_bottle": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
    "from": 11,
    "to": 15,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
