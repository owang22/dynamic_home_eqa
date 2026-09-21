# p_2e8c — Saturday Kitchen and Living Room: The Shared Weekend Table

The residents' Saturday message—"It's the weekend, so we're off our usual routine and around the house more"—points to a specific spatial pattern: both residents orbit the kitchen and living room simultaneously, rather than the weekday split where Hana is gone and Priya occupies the kitchen alone in the morning and the living room in the afternoon. On a Saturday, the kitchen table is set for a late breakfast or brunch (10:00–12:00) with both residents present, mugs and plates out of the cupboard and onto the table. The fruit bowl stays at the kitchen table as a shared centerpiece. After brunch, the kitchen clears and the living room becomes the shared space: Priya reads in the armchair or works on her puzzle (box at bookshelf_l1, pieces spread on the coffee table), Hana plays guitar or reads, and the snack bowl appears on the coffee table.

This document differs from p_a9b4 (Kitchen Social Hub, which places Priya's book at the kitchen table) by keeping Priya's reading in the living room armchair or at her nightstand, and from p_e5f0 (Weekend Transformation) by placing the puzzle box at bookshelf_l1 rather than the coffee table. It also differs from the weekday cooking documents (p_b9c4, p_c1d6, p_7c2f) by having a single late-morning meal rather than separate lunch and dinner cooking windows, and by having both residents at the table for it.

The snack bowl, which the evidence shows is mostly at sink_k1 (2/4 days) but appears at kitchen_table_k1 (1/4 days) and counter_k1 (1/4 days), is predicted here at the kitchen table during brunch and at the coffee table during the afternoon living-room session. The mug pattern follows: out of the cupboard at the table during meals, back in the cupboard or at the sink between.

What would refute this: finding the kitchen table empty of plates and mugs at 11:00 on a Saturday (no brunch), finding Priya's book at the kitchen table (she reads in the living room), or finding the puzzle box at desk_b2 (it rests on the bookshelf).

```json
{
 "claims": [
  {
   "claim": "Both residents' plates are on the kitchen table during Saturday brunch",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Priya's mug is on the kitchen table during Saturday brunch",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 10,
   "to": 12
  },
  {
   "claim": "The snack bowl is at the kitchen sink on a Saturday morning, not yet out for the afternoon",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "weekend",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Priya's book is on the bookshelf on a Saturday afternoon, not at the kitchen table",
   "target": "book_priya",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 13,
   "to": 17
  },
  {
   "claim": "The puzzle box is on the bookshelf on a Saturday afternoon, not at desk_b2",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 13,
   "to": 17
  }
 ],
 "targets": {
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
  ],
  "plate_priya": [
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
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
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
  "bowl_priya": [
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
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
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
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
