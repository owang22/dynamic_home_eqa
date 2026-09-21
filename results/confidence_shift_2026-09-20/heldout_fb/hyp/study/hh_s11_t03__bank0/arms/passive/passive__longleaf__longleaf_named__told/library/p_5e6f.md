# p_5e6f — Hana's Living Room Afternoon; Mug, Book, and Bottle Rest at the Coffee Table from 10:00 to 17:00

On weekdays, Hana's morning routine takes her from the kitchen table (where she works with her tablet from 09:00) to the living room by 10:00. Once in the living room, her personal items — mug, water bottle, book — settle at the coffee table (or on the couch beside it) and stay there. When she leaves for work at 13:40, she does not gather her things; the mug, bottle, and book remain at the coffee table or couch until she returns at 23:00. This is why the robot sees mug_hana at coffee_table_l1 at 10:00, 13:00, and 17:00, and water_bottle_hana at coffee_table_l1 at 10:00 and 17:00, even though Hana is at work during the 13:40–23:00 window.

This document differs from the desk-based hypotheses (p_b8c2, p_a1b2) by placing Hana's tablet at the kitchen table in the morning and at the coffee table in the late morning, never at desk_b1. It differs from the sick-day documents by applying to normal weekdays. The notebook, by contrast, stays at desk_b1 all day — it is a work item that does not migrate.

Refutation: if mug_hana or water_bottle_hana is found at the cupboard or entry table at 14:00 or 16:00 on a weekday (i.e., Hana gathered her things before leaving), or if the tablet is at desk_b1 at 10:00, this hypothesis is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's mug is at the coffee table at 14:00 on a weekday, not at the cupboard",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "Hana's water bottle is at the coffee table at 16:00 on a weekday, not at the entry table",
   "target": "water_bottle_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "Hana's tablet is at the kitchen table at 09:30 on a weekday, not at the desk",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 10.5
  },
  {
   "claim": "Hana's notebook stays at her desk all day and does not move to the kitchen table or coffee table",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "mug_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "entry_table_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "book_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 12,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 13.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
