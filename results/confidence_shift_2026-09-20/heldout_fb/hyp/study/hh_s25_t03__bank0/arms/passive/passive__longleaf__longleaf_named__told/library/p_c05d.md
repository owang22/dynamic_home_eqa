# p_c05d — p_3n8f — Morning kitchen-table ritual: vitamins and bowls at breakfast

Both residents take their vitamins at the kitchen table in the morning, and Marco's breakfast bowl lives there too. The evidence is consistent: vitamins_marco appears at kitchen_table_k1 at 08:00 (twice) and 09:00 (twice) on weekdays, and at 08:00 on a weekend. vitamins_omar appears at kitchen_table_k1 at 08:00, 09:00 on weekdays, and at 09:00 and 10:00 on weekends. bowl_marco is at the kitchen table at 07:00, 08:00 (three times), and 09:00 (twice) on weekdays. mug_marco is at the kitchen table at 09:00 on a weekday and 08:00 on a weekend. After the morning ritual, the vitamins return to the kitchen counter (seen at 03:00 and 18:00) and the bowls go back to the cupboard.

What sets this apart: no current document places the vitamins or the bowls at the kitchen table during a morning window. p_a1b2 and p_c3d4 have no vitamin or bowl blocks at all beyond a generic "counter" or "cupboard" resting spot. p_4d0c (retired day 5) captured a similar morning kitchen ritual but was retired before accumulating weight. This document isolates the 7:30–10:00 kitchen-table window for these objects.

What would refute it: finding vitamins_marco or vitamins_omar at the kitchen table after 10:00 on a weekday, or finding bowl_marco at the kitchen table during the 12:00–17:00 work window.

```json
{
 "claims": [
  {
   "claim": "Marco's vitamins are at the kitchen table during the weekday morning ritual",
   "target": "vitamins_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Omar's vitamins are at the kitchen table during the weekend morning ritual",
   "target": "vitamins_omar",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 9,
   "to": 10.5
  },
  {
   "claim": "Marco's bowl is at the kitchen table during the weekday breakfast window",
   "target": "bowl_marco",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9.5
  },
  {
   "claim": "Marco's vitamins are back at the kitchen counter in the evening",
   "target": "vitamins_marco",
   "expect": "counter_k1",
   "days": "both",
   "from": 17,
   "to": 23
  }
 ],
 "targets": {
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
   },
   {
    "days": "weekend",
    "from": 7.5,
    "to": 9,
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
   },
   {
    "days": "weekend",
    "from": 8.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
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
    "from": 7,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "days": "both",
    "from": 7.5,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
   },
   {
    "days": "weekend",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 17.5,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ]
 }
}
```
