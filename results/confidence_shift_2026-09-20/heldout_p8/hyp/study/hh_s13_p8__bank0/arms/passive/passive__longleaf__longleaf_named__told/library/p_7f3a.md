# p_7f3a — Weekend At Home: Hana's Objects Return to the House

On weekends the fundamental rhythm of this household inverts. Hana, who is out of the house from roughly 8 to 5:30 on weekdays, sleeps in on Saturday and Sunday, rising around 9 or 10. Her laptop, pen, charger, and water bottle—which vanish from the house entirely on weekday mornings and reappear only at 18:00 at the entry hook—stay at desk_b1 (laptop, pen, charger) or the kitchen (water bottle) for the whole weekend day. Her keys, wallet, sunglasses, and handbag sit at the entry table and hook rather than riding in her bag to the office. Her jacket hangs at entry_hook_e1 instead of being worn to work.

The one gap in Hana's weekend presence is a midday errand run, roughly 12:00 to 14:00, when she takes her keys, wallet, handbag, jacket, phone, and sunglasses out to the shops. Priya anchors the house during that window: she is home, likely at the kitchen table or in the living room with a book or her puzzle. Priya's own weekend pattern is a late-morning walk (around 10:00–11:30) during which her phone, keys, and jacket are briefly ON_PERSON or OUT_OF_HOUSE, after which she settles back in.

This hypothesis sets itself apart from the weekday-commuter documents (p_a3f1, p_b7c2, p_f5a0, p_9d3b) by asserting that on weekends Hana's "work objects" are IN the house. It also differs from p_e5f0 in that it places the puzzle box at bookshelf_l1 (its confirmed resting spot, seen 4/4 days) rather than on the coffee table, and it gives Hana a specific midday errand window during which her going-out objects are briefly OUT_OF_HOUSE.

What would refute this document: finding Hana's laptop OUT_OF_HOUSE on a Saturday morning, finding her keys at the entry table on a weekday at noon, or finding the puzzle box at bookshelf_l1 when a document places it on the coffee table during an active puzzle session.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at desk_b1 on a Saturday morning because she is home and not at work",
   "target": "laptop_hana",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Hana's keys are at the entry table on a Saturday morning before her midday errand",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Hana's guitar is being played in the afternoon on a Saturday",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Hana's jacket is at the entry hook on a Saturday morning, not out at work",
   "target": "jacket_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The puzzle box rests on the bookshelf on a Saturday afternoon",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 13,
   "to": 17
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "charger_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "wallet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "sunglasses_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
