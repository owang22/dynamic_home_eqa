# p_2e9f — Priya's Morning Kitchen: Breakfast at 07:30, Lunch at 12:00, Walk at 09:00

This document models Priya's daytime routine in the kitchen, which no existing document covers in detail. The evidence: mug_priya is at kitchen_table_k1 at 07:00 (×2) and 08:00 (×6); bowl_priya is at kitchen_table_k1 at 08:00 (×6); plate_priya is at kitchen_table_k1 at 12:00 (×2) and back in the cupboard by 13:00 (×4); glass_priya is at kitchen_table_k1 at 12:00 (×4); razor_priya is at bathroom_shelf_ba1 at 07:00 (×6); towel_hana is at bathroom_shelf_ba1 at 07:00–10:00 (Hana's morning shower); phone_hana is at nightstand_b1 at 07:00–08:00 and briefly at bathroom_shelf_ba1 at 07:00.

The pattern: Priya has breakfast at the kitchen table 07:00–08:30 (mug, bowl, and plate at the table). Hana showers 07:00–09:00 (towel in the bathroom shelf, phone briefly in the bathroom). Priya's morning walk is 09:00–10:00 (keys and jacket out of the house). Lunch is at the kitchen table 12:00–13:00 (plate, glass, and mug at the table). After lunch, Priya is home until her afternoon errands.

What sets this apart: it is the only document that models the 07:00–09:00 morning window with both residents' objects in their morning locations, and the 12:00 lunch at the kitchen table specifically for Priya (not a shared lunch). It differs from p_d1e6 (Early Bird) which focuses on Hana's 7:30 departure; here the focus is on Priya's kitchen presence. It differs from p_a9b4 (Kitchen Social Hub) which places Hana's laptop at the kitchen table; here Hana is in the bathroom or out by 08:00.

Refutation: mug_priya at kitchen_table_k1 at 10:00 on a weekday (breakfast is much later than 07:00), or plate_priya at kitchen_table_k1 at 14:00 (lunch is not at 12:00).

```json
{
 "claims": [
  {
   "claim": "Priya's mug is on the kitchen table at 08:00 on a weekday (breakfast)",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "Priya's plate is on the kitchen table at 12:00 on a weekday (lunch)",
   "target": "plate_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "Priya's glass is on the kitchen table at 12:00 on a weekday (lunch drink)",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13
  },
  {
   "claim": "Priya's keys are out of the house at 09:30 on a weekday (morning walk)",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 10
  }
 ],
 "targets": {
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
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
    "to": 8.5,
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
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "towel_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 10,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "razor_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
