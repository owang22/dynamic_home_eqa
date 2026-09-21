# p_3d8e — Omar's weekday lunch: kitchen table, 12:00–13:30

Omar is home on weekday mornings from roughly 7:00 until he leaves for his afternoon shift at about 13:40. His main meal of the day is a midday lunch at the kitchen table, eaten between 12:00 and 13:30. The evidence is unambiguous: his glass is at kitchen_table_k1 at 12:00 (×3) and 13:00 (×3), his plate is at kitchen_table_k1 at 13:00, his bowl is at kitchen_table_k1 at 09:00, 10:00, and 18:00 (the 18:00 sighting is likely a second helping or a snack after his shift), and his mug is at kitchen_table_k1 at 10:00 (×2) and 18:00. His vitamins are also at the kitchen table at 09:00, 10:00 (×2), and 18:00.

This document sets apart the 12:00–13:30 window as Omar's dedicated lunch hour. It predicts that his glass, plate, and bowl are all at the kitchen table simultaneously during that window, and that the glass migrates to the counter or dish rack by 23:00 (his post-shift drink). It does not predict a dining-table dinner for Omar on weekdays; his late meal (if any) is a quick counter-side affair.

What would refute it: glass_omar at the dining table or coffee table during 12:00–13:30 on a weekday; plate_omar at the dining table at 13:00 on a weekday; or the bowl absent from the kitchen table on three or more weekday midday passes.

```json
{
 "claims": [
  {
   "claim": "Omar's glass is at the kitchen table during his weekday lunch",
   "target": "glass_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13.5
  },
  {
   "claim": "Omar's plate is at the kitchen table during his weekday lunch",
   "target": "plate_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12.5,
   "to": 13.5
  },
  {
   "claim": "Omar's bowl is at the kitchen table during his weekday midday meal",
   "target": "bowl_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13.5
  },
  {
   "claim": "Omar's mug is at the kitchen table during his weekday midday meal",
   "target": "mug_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13.5
  }
 ],
 "targets": {
  "glass_omar": [
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
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 15.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 15.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "from": 9,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
