# p_c2d8 — Omar's laptop sleeps on the bookshelf, works at the desk, naps at the coffee table

The per-object evidence for laptop_omar shows it at coffee_table_l1 at 09:00 (3 sightings), desk_o1 at 10:00 (2), 13:00 (1), 15:00 (3), 16:00 (1), 17:00 (1), coffee_table_l1 at 18:00 (1), and bookshelf_l1 at 03:00 (2) and 17:00 (1). On weekends it is at bookshelf_l1 at 03:00 (2). The overnight resting spot is the bookshelf, not the coffee table — this distinguishes it from p_3f7c, p_4f8e, and p_7e2a which all place it at the coffee table overnight. The morning coffee-table phase (8:50–10:00) is when Omar has breakfast and reviews his day before settling at the desk. The desk block runs 10:00–17:00. After 17:00 the laptop goes to the coffee table for an evening check or moves to the bookshelf to sleep. Omar's water bottle follows a parallel path: dish rack overnight (3/3 at 03:00), coffee table at 09:00 (1), desk at 11:00 (1) and 14:00 (1), dish rack at 17:00 (2), counter at 18:00 (1), kitchen table at 19:00 (3). His headphones are at the desk during work hours (10:00, 11:00, 14:00, 16:00, 17:00 passes) and on the couch at 18:00.

What sets this apart: the laptop's overnight home is the bookshelf (not coffee table), the morning coffee-table window is 8:50–10:00 (not 8:00–10:00 or 9:00–10:00), and the water bottle is at the kitchen table at 19:00 (dinner), not the counter. A sighting of the laptop at the coffee table at 03:00, or the water bottle at the desk at 19:00, would refute this document.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is on the bookshelf at 03:00 (overnight resting spot)",
   "target": "laptop_omar",
   "expect": "bookshelf_l1",
   "days": "both",
   "from": 3,
   "to": 3.5
  },
  {
   "claim": "Omar's laptop is at the coffee table at 09:00 on a weekday (morning coffee before desk work)",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 8.75,
   "to": 9.25
  },
  {
   "claim": "Omar's water bottle is at the kitchen table at 19:00 (dinner)",
   "target": "water_bottle_omar",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 18.75,
   "to": 19.25
  },
  {
   "claim": "Omar's headphones are at his desk at 14:00 on a weekday (in use during work)",
   "target": "headphones_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13.5,
   "to": 14.5
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
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
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "from": 8.5,
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
    "from": 18,
    "to": 19,
    "at": "counter_k1",
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
  "headphones_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
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
    "from": 18,
    "to": 19,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "mouse_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "notebook_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
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
