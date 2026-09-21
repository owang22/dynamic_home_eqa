# p_9c4e — Morning kitchen ritual: breakfast and vitamins at the kitchen table 8–9:30

Both residents share a morning ritual around 8:00–9:30 on weekdays in which they eat breakfast and take their vitamins at the kitchen table. The 08:00 and 09:00 patrol passes confirm this: bowl_marco is at kitchen_table_k1 at both 08:00 and 09:00; mug_marco is at kitchen_table_k1 at 09:00; vitamins_omar is at kitchen_table_k1 at 08:00; vitamins_marco is at kitchen_table_k1 at 09:00. After the ritual, everything returns to its resting spot — bowls and mugs to cupboard_k1, vitamins to counter_k1 — as confirmed by the 18:00 passes. The 03:00 passes show the items already at their resting spots, meaning the kitchen-table window is a brief mid-morning excursion, not an all-day placement.

This document is distinct from the library's existing entries, none of which model the 8–9:30 kitchen-table window for these items. It does not conflict with the "class:bowl at cupboard_k1" blocks that held up in p_e1a5, p_d4e9, and p_a3f7, because those blocks cover the rest of the day; this document overrides only the 8–9:30 window.

What would refute it: a weekday look at kitchen_table_k1 between 8:00 and 9:30 that finds none of the four items, or a sighting of any of them at a different receptacle during that window.

```json
{
 "claims": [
  {
   "claim": "Marco's bowl is at the kitchen table during the weekday breakfast window",
   "target": "bowl_marco",
   "expect": "kitchen_table_k1",
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
  },
  {
   "claim": "Omar's vitamins are at the kitchen table during the weekday breakfast window",
   "target": "vitamins_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  }
 ],
 "targets": {
  "bowl_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "vitamins_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "vitamins_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
