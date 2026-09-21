# p_d9f4 — Priya's Dining Table Evening; Glass and Plate at 19:00, Then Bed by 21:00

Priya (resident_2) has a light evening meal or snack at the **dining table** around 19:00 on weekdays. The 19:00 pass shows glass_priya at dining_table_d1 ×2 (plus counter_k1 ×1) and plate_priya at dining_table_d1 ×1. By 20:00 she has moved to her bedroom area: tablet_priya at nightstand_b2, book_priya at bed_b2 ×2. By 22:00 she is fully in bed: tablet_priya at bed_b2 ×2, phone_priya at nightstand_b2, glass_priya at sink_k1 ×2 and nightstand_b2.

What sets this apart from p_9e1f (which places Priya at the kitchen counter for evening cooking and snacking at 19:00–21:00): this document has her at the dining table, not the counter, for the 19:00 meal. The glass is at dining_table_d1, not counter_k1. What would refute it: a look at dining_table_d1 at 19:30 that finds no glass_priya, or a look at nightstand_b2 at 21:00 that finds no tablet_priya.

Hana (resident_1) is out of the house at 19:00 (at work until 23:00), so the dining table is Priya's alone.

```json
{
 "claims": [
  {
   "claim": "Priya's glass is at the dining table during her weekday evening meal",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Priya's plate is at the dining table during her weekday evening meal",
   "target": "plate_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Priya's tablet is on her nightstand by 21:00 on weekdays",
   "target": "tablet_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "Priya's book is on her bed during the evening wind-down",
   "target": "book_priya",
   "expect": "bed_b2",
   "days": "both",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
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
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "nightstand_b2",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "sink_k1",
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
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "entry_table_e1",
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
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "magazine_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
