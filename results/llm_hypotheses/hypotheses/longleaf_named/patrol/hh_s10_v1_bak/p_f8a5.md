# p_f8a5 — The kitchen table is Omar's morning station; Yuki clears it before she leaves

Omar makes his breakfast and coffee at the kitchen table every weekday morning (06:00–09:00). His mug, bowl, and vitamins are out there. Yuki, leaving at 08:00, clears his things into the cupboard and sink before she goes. So by 09:00, the kitchen table is mostly clear of Omar's personal items (only the fruit bowl and shared items remain). On weekends, Omar is home all day and the table stays messier. What sets this hypothesis apart: mug_omar and bowl_omar are at the cupboard by 09:00 on weekdays (cleared by Yuki), not still on the table at 13:00. What would refute it: mug_omar sighted at kitchen_table_k1 between 09:00 and 13:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Omar's mug is back in the cupboard by 9am on weekdays",
   "target": "mug_omar",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Omar's bowl is back in the cupboard by 9am on weekdays",
   "target": "bowl_omar",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Omar's mug is on the kitchen table at 7am on weekdays",
   "target": "mug_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 6,
   "to": 8
  },
  {
   "claim": "Omar's vitamins are on the kitchen table in the morning",
   "target": "vitamins_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 6,
   "to": 9
  }
 ],
 "targets": {
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
    "from": 6,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13.5,
    "at": "cupboard_k1",
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
    "from": 6,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13.5,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "vitamins_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
