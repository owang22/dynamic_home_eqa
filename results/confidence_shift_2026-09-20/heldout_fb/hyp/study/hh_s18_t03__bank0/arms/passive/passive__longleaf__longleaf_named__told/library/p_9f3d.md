# p_9f3d — Ines works in two desk blocks (10–11:30 and 14–17:30) with a kitchen break 12–14

Ines's weekday work is not a continuous 9-to-5:30 sit at the office desk. The sightings show her objects at desk_o1 in two clusters: a short morning block around 10:00 (laptop ×1, water bottle ×2) and a long afternoon block from 14:00 through 18:00 (charger ×1, ×3; headphones ×1, ×2, ×6, ×5; water bottle ×3, ×2; laptop ×1, ×2). Between roughly 11:00 and 14:00 the objects leave the desk, and glass_ines appears at the kitchen table at 12:00 (×1) and 13:00 (×2), marking a lunch break. The 24 empty looks at desk_o1 for laptop_ines during 9–17 h are explained by this gap: the laptop is closed and set aside, or Ines is working in the kitchen, during the break.

The charger is the most desk-loyal object: it is at desk_o1 at 12:00 (×1) and 14:00 (×1) even during the break, suggesting it stays plugged in. The pen is at desk_o1 six out of six sighted days but only 4/26 times during 9–17 h, consistent with being under the laptop or in a drawer during active work. The headphones are at the desk from 14:00 onward and go to the bed at 21:00 (×1). The water bottle is at the desk at 08:00 and 10:00, at the sink at 14:00 (refill), then back at the desk at 15:00 (×3) and 17:00 (×2).

At 18:00 the laptop moves to the office floor (floor_o_o1 ×1), marking the end of the workday. The charger stays at the desk until 23:00, when it moves to the office shelf (×2) or the nightstand (×1).

This document would be refuted if the laptop is consistently found at the desk during 12:00–14:00 on weekdays, or if Ines's objects are at the kitchen table during the afternoon block (14:00–17:00).

```json
{
 "claims": [
  {
   "claim": "Ines's laptop is at the office desk at 10:30 on weekdays",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Ines's laptop is at the kitchen table during the midday break on weekdays",
   "target": "laptop_ines",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Ines's laptop is at the office desk at 16:30 on weekdays",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 16,
   "to": 17
  },
  {
   "claim": "Ines's mug is at the kitchen table during the midday break on weekdays",
   "target": "mug_ines",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Ines's water bottle is at the kitchen sink at 14:00 on weekdays",
   "target": "water_bottle_ines",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 14,
   "to": 15
  }
 ],
 "targets": {
  "laptop_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 11.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "floor_o_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_ines": [
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
    "to": 12,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "usually"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   }
  ]
 }
}
```
