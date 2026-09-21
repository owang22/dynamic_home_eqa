# p_6a3b — Omar's water bottle: a nomad that follows him room to room

Omar's water bottle is the most mobile object in the house. It dries in the dish rack overnight (03:00: dish_rack x3), moves to the coffee table for his morning coffee and laptop browsing (09:00: coffee_table x1), sits at his desk during the work block (11:00: desk_o1, 14:00: desk_o1), returns to the dish rack or lingers at the desk in the late afternoon (17:00: dish_rack x2, desk x1), is on the counter during the pre-dinner transition (18:00: counter x1), and ends up at the kitchen table for dinner (19:00: kitchen_table x3). On weekends it is in the dish rack overnight and at the kitchen table in the evening (20:00: kitchen_table x1).

The 9–17h looks at the dish rack found the bottle 0 times and found nothing 0 times (no looks were made there in that window), and the bottle was never sighted at the counter during the workday. This distinguishes it from the "bottle sits on the counter all day" model.

This document is refuted if the water bottle is at the counter during the 9–17h workday, or if it is at the desk at 03:00, or if it is at the kitchen table at 11:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Omar's water bottle is in the dish rack at 03:00 drying overnight",
   "target": "water_bottle_omar",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 2.75,
   "to": 3.25
  },
  {
   "claim": "Omar's water bottle is at his desk at 14:00 on a weekday during the work block",
   "target": "water_bottle_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 13.75,
   "to": 14.25
  },
  {
   "claim": "Omar's water bottle is at the kitchen table at 19:00 during dinner",
   "target": "water_bottle_omar",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 18.75,
   "to": 19.25
  },
  {
   "claim": "Omar's water bottle is at the coffee table at 09:00 on a weekday during his morning coffee",
   "target": "water_bottle_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 8.75,
   "to": 9.25
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
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ]
 }
}
```
