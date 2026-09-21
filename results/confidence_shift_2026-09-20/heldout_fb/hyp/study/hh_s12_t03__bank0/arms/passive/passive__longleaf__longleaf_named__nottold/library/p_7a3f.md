# p_7a3f — Staggered dinner: Priya 19, Elena 20, table clear by 20:30

Elena and Priya eat at different times on weekdays. Priya, retired and home all day, sits down at the dining table at 19:00 and lingers until roughly 20:30, finishing her water and clearing her glass. Elena, coming home from work at 17:30 and cooking or reheating, sits at 20:00 and finishes by 20:30. The table is clear of both their plates and glasses by 21:00. On weekends the timing shifts: both eat around 12:00–14:00 at the kitchen table (where weekend sightings place plates and glasses).

What sets this apart from p_8b3c and p_3e9f (which use 20–21h windows for Elena): the evidence shows Elena's objects at the table only at the 20:00 pass, never at 21:00. Her plate, glass, and water bottle are all at dining_table_d1 at 20:00 and gone by the next pass. Priya's water bottle, by contrast, is still at the table at 21:00, confirming she stays longer. The narrow 20–20.5h window for Elena avoids the "against" hits that wider windows accumulated.

Refutation: if Elena's plate or glass is sighted at the dining table at 20:30 or 21:00 on a weekday, or if Priya's glass is absent from the table at 19:00 on multiple weekday evenings, this document's core timing is wrong.

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
   "claim": "Elena's glass is at the dining table at 20:00 on a weekday",
   "target": "glass_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 20.5
  },
  {
   "claim": "Elena's plate is at the dining table at 20:00 on a weekday",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 20.5
  },
  {
   "claim": "Priya's water bottle is still at the dining table at 20:30 on a weekday",
   "target": "water_bottle_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21
  }
 ],
 "targets": {
  "glass_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "from": 19,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
