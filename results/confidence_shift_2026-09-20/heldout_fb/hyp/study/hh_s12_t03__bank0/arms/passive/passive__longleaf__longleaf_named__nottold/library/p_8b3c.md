# p_8b3c — Staggered dinner: Priya at 19, Elena at 20, table clear by 21

Priya is home all day and sets the table in the late afternoon. She sits down to eat around 19:00 with her glass and water bottle already at the place setting. Elena, home from work at 17:30, spends the hour changing, having a snack, and settling in; she joins the table at 20:00, bringing her own glass, plate, and bottle. The meal runs until about 21:00, after which the table is cleared and the residents drift to the living room for TV. On weekends the timing shifts later: Priya's items appear at 20:00 and Elena's at 21:00.

What sets this document apart from p_a1b2 (dinner 18.5–20) and p_4c7d (dinner 19.5–21): it splits the dinner into two arrival times. Priya's glass and bottle are at the table at 19:00 while Elena's items are not yet there. A document that puts all plates at the table simultaneously at 19:00 or 20:00 will be contradicted by the 19:00 look that shows Priya's glass but not Elena's plate.

Refutation: if Elena's plate is at the dining table at 19:00 on a weekday (she arrived early), or if Priya's glass is not at the table at 19:00 (she sat down later), this document's staggered timing is wrong.

```json
{
 "claims": [
  {
   "claim": "Priya's glass is at the dining table at 19:00 on a weekday",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Elena's plate is at the dining table at 20:00 on a weekday",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21
  },
  {
   "claim": "Elena's water bottle is at the dining table at 20:00 on a weekday",
   "target": "water_bottle_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21
  },
  {
   "claim": "Priya's water bottle is at the dining table at 19:00 on a weekday",
   "target": "water_bottle_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
  "glass_priya": [
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_elena": [
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "plate_elena": [
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 20,
    "to": 21.5,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 23.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
