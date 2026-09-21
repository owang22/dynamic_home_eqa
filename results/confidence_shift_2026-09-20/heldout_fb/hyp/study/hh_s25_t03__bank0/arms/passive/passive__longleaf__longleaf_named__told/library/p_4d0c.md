# p_4d0c — p_2w9x — Morning kitchen ritual: bowls, vitamins, and mugs cycle to the kitchen table at breakfast

The weekday morning in this household centres on a shared breakfast at the kitchen table around 8:00–9:30. Marco's bowl is pulled from the cupboard and placed at the kitchen table by 8:00 (sighted there at 08:00 and twice at 09:00) and returned to the cupboard by 18:00. Both residents' vitamins are taken with breakfast: Marco's are at the counter at 08:00 (being poured) and at the kitchen table by 09:00; Omar's are at the kitchen table at 08:00. Marco's mug appears at the kitchen table at 09:00 (breakfast coffee) before moving to his desk around 11:00 for a mid-morning cup. Marco's glass is at the kitchen table around 13:00 (a midday drink) and in the sink at 03:00 (washed overnight).

This document differs from the lunch-outing hypotheses (p_c3d4, p_d4e9, p_b8c2) in that it makes no claim about anyone leaving the house at midday; the kitchen-table sightings at 13:00 (plate_marco x2, glass_marco) are consistent with a home lunch. It also differs from p_a61d, which places mugs at the counter during breaks; here the mugs are at the kitchen table in the morning and at the desk in the mid-morning.

Refuted if the bowls and vitamins are consistently found at the kitchen table outside the 7:30–10:00 window, or if the kitchen table is empty at 09:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Marco's bowl is at the kitchen table during the weekday breakfast window",
   "target": "bowl_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Marco's vitamins are at the kitchen table during breakfast",
   "target": "vitamins_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Marco's mug is at the kitchen table in the morning before it moves to the desk",
   "target": "mug_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Marco's plate is at the kitchen table during the midday meal",
   "target": "plate_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12.5,
   "to": 14
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
    "from": 7.5,
    "to": 10,
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
    "from": 7.5,
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
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 13,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "plate_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
