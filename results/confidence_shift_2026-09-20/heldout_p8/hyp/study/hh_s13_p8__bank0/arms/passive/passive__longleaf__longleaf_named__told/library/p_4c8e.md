# p_4c8e — The Armchair Afternoon: Priya Reads, the Kitchen Rests

Hana (late twenties, office worker) leaves at 8 with her laptop, pen, charger, water bottle, keys, jacket, handbag, scarf, shoes, sunglasses, and wallet; they are all OUT_OF_HOUSE from 8 to 17:30. She returns at 17:30 and sets them at the entry hook. Priya (seventies, retired) is the anchor at home all day.

What this hypothesis predicts that sets it apart: Priya's afternoon (14:00–18:00) is spent reading in the living-room armchair. Her book leaves the nightstand around 14:00 and returns by 18:00. The puzzle box does NOT come out of the bookshelf — she is reading, not puzzling. Her headphones remain at desk_b2 until 18:00, then move to the bed. The kitchen is quiet: the pan, pot, and knife stay in the cupboard and drawer through 18:00; no dinner cooking has started. The snack bowl sits at the sink all day and only moves to the counter in the evening. Priya's glass moves from the nightstand to the kitchen sink in the afternoon. Hana's glass is at her nightstand (not the pantry) during the day.

This refutes the "Kitchen Social Hub" (book at kitchen table at 15:00), "Priya's Bedroom Fortress" (book at nightstand, puzzle at desk_b2, headphones at bed_b2 during the day), "Hana Cooks Dinner" and "Split Cooking" (pan on counter at 18:00), and "Priya's Social Circle" (snack bowl on coffee table at 16:00).

What would refute this document: finding the book at the kitchen table or desk_b2 at 15:00, the puzzle box at desk_b2 or coffee_table during the day, the pan on the counter at 18:00, or the snack bowl on the coffee table at 16:00.

```json
{
 "claims": [
  {
   "claim": "Priya's book is in the living room armchair at 16:00 on a weekday",
   "target": "book_priya",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The puzzle box stays on the bookshelf at 16:00 on a weekday",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's headphones are at desk_b2 at 16:00 on a weekday",
   "target": "headphones_priya",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The snack bowl is at the kitchen sink at 16:00 on a weekday",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "headphones_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "charger_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
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
