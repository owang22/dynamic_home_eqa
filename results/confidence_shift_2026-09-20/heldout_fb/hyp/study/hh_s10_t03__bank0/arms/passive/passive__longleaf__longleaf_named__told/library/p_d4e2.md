# p_d4e2 — The 19:00 dining table dinner: Yuki's glass, bottle, and plate in a tight window

Yuki comes home around 17:30 on weekdays. She drops her water bottle on the entry hook for a few minutes while she hangs up her jacket and keys, then carries the bottle to the dining table where she sets a simple dinner for herself around 18:45. The dinner is brief—she eats at the dining table from roughly 19:00 to 20:00, accompanied by her glass of water and the bottle. Afterward she rinses the glass and sets it on the nightstand for the night; the plate goes to the sink. This is a solo meal at the dining table, not the kitchen table, and it is distinct from Omar's later post-shift drink at the counter at 23:00.

What sets this apart: p_8d2c places Yuki's dinner at the kitchen table (solo, light assembly); p_c007 focuses on the cooking act (pan and board on the counter) rather than where the plates and glasses sit during eating. This document pins the *eating* location to the dining table and gives the water bottle its full arc from dish rack to entry hook to dining table. The glass_yuki sightings at dining_table (19:00 ×2, 20:00 ×3) and water_bottle_yuki at dining_table (19:00 ×4, 20:00 ×2) are the core support.

What would refute it: if the robot repeatedly finds Yuki's glass or water bottle at the kitchen table during 19:00–20:00 on weekdays, or if the plate is seen at the dining table before 18:30 (implying an earlier meal), this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Yuki's water bottle is at the dining table at 19:30 on a weekday during her dinner",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  },
  {
   "claim": "Yuki's glass is at the dining table at 19:30 on a weekday (dinner in progress)",
   "target": "glass_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  },
  {
   "claim": "Yuki's water bottle is in the dish rack at 03:00 on a weekday (washed after dinner, drying overnight)",
   "target": "water_bottle_yuki",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 1,
   "to": 7
  },
  {
   "claim": "Yuki's glass is at the nightstand at 22:30 on a weekday (bedtime water)",
   "target": "glass_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 23.5
  }
 ],
 "targets": {
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 1,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 1,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 1,
    "to": 7,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "plate_yuki": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
