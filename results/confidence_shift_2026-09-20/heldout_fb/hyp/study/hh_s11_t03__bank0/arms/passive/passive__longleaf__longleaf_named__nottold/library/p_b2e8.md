# p_b2e8 — Staggered Breakfast; Priya at Eight, Hana at Nine

Hana and Priya do not eat breakfast at exactly the same time. Priya (resident_2, retired) rises early and has her bowl, mug, and tablet at the kitchen table by 08:00. Hana (resident_1) wakes later and arrives at the kitchen table around 09:00 with her bowl. The 08:00 pass shows Priya's bowl ×3 and mug ×2 at kitchen_table_k1 while Hana's bowl is still in the cupboard; the 09:00 pass shows Hana's bowl ×3 and tablet ×4 at the kitchen table. This staggered pattern means the kitchen table is occupied by one resident at a time in the early morning, not both simultaneously.

What sets this apart from p_e8b2 and p_7a3e: those predict both residents at the kitchen table in the same 07:30–09:30 window. This document separates them: Priya 07:30–08:30, Hana 08:30–10:00. What would refute it: a look at kitchen_table_k1 at 08:00 that finds Hana's bowl, or a look at 09:00 that finds no Hana bowl.

Priya's tablet is at the kitchen table during her breakfast (08:00 ×2 sightings), then moves to coffee_table_l1 by 18:00 and to nightstand_b2/bed_b2 by 20:00–22:00. Hana's tablet joins her bowl at the kitchen table at 09:00.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is at the kitchen table during her weekday breakfast",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  },
  {
   "claim": "Hana's bowl is at the kitchen table during her weekday morning meal, after Priya's",
   "target": "bowl_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 10
  },
  {
   "claim": "Priya's tablet is at the kitchen table while she eats breakfast",
   "target": "tablet_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9
  },
  {
   "claim": "Hana's tablet is at the kitchen table during her weekday morning block",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 11
  }
 ],
 "targets": {
  "bowl_priya": [
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
    "to": 8.75,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "mug_priya": [
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
    "to": 8.75,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "nightstand_b2",
    "chance": "sometimes"
   }
  ],
  "bowl_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "class:dog_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
