# p_8c3f — The 20:00 Weekday Dinner Plate: Service at Eight, Not Six-Thirty

The weekday dinner plate does not appear at the kitchen table until 20:00. plate_hana is in the cupboard at 18:00 and 19:00, then jumps to the kitchen table at 20:00 (3 sightings). This means the cooking happens 18:00–19:30 (pan on counter at 19:00, knife on counter at 18:00), but the plates are only set at 20:00. The 18:30–19:30 dinner window in p_a3f1 and the 18:50–19:50 window in p_b9c4 are both too early for the plate. By 21:00 the plate is back in the cupboard and the mug has migrated to the coffee table for the TV session.

What sets this apart: p_a3f1 puts class:plate at kitchen_table 18.5–19.5, p_b9c4 puts it 17.5–19.5, and p_e4b7 puts plate_hana in the cupboard until 20:00. This document pins the plate at the table specifically at 20:00–21:00, matching the 3-for-5 pass at that hour.

What would refute it: if plate_hana is at the kitchen table at 18:00 or 19:00 on multiple weekday evenings, the 20:00 service window is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's plate is on the kitchen table at 20:00 on a weekday because dinner is being served",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Hana's plate is in the cupboard at 18:00 on a weekday because dinner is not yet served",
   "target": "plate_hana",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Hana's mug is on the kitchen table at 18:00 on a weekday because she just arrived and is having a drink",
   "target": "mug_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  }
 ],
 "targets": {
  "plate_hana": [
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
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
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
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
