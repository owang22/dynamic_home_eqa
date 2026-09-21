# p_7b1f — Omar's water bottle follows him: a mobile object

Omar's water bottle is a mobile object that tracks his activity through the day. Overnight it dries in the dish rack (confirmed at 03:00 on both observed nights). In the morning it is at the coffee table (he is having breakfast or starting his day). By mid-afternoon it is at his desk (he is working). In the early evening it is at the kitchen counter, and by dinner time it is at the kitchen table. It is never in one fixed spot for more than a few hours.

This is distinct from Marco's water bottle, which is more fixed: dish rack overnight, entry hook when he leaves for work. Omar's bottle has 5 distinct receptacles across 8 sightings — it genuinely moves. The "weekday 9-17h looks at kitchen_table_k1 found it 0, found nothing 3" confirms it is NOT at the kitchen table during work hours (it is at the desk or coffee table then).

What would refute this: finding the water bottle at the same receptacle for 6+ consecutive hours during waking hours, or at the dish rack at 14:00.

```json
{
 "claims": [
  {
   "claim": "Omar's water bottle is in the dish rack overnight",
   "target": "water_bottle_omar",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 2.5,
   "to": 4
  },
  {
   "claim": "Omar's water bottle is at his desk during the afternoon work block",
   "target": "water_bottle_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13,
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
  "water_bottle_omar": [
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
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
