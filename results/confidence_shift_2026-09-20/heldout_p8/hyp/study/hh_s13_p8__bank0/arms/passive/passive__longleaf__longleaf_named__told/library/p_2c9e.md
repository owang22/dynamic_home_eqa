# p_2c9e — Priya's Afternoon in the Armchair: Book Moves to the Living Room

The 16:00 Wednesday sighting put book_priya at armchair_l1 while Priya was in the living room. On the other three passes (00:00, 08:00, 18:00) the book was at nightstand_b2. This is a clean pattern: during the mid-afternoon (roughly 14:00–17:00) Priya takes her book to the living room and reads in the armchair. Before and after that window the book is on her nightstand. Hana is at work during this window, so the living room is Priya's alone.

What sets this apart: p_2a6e put the puzzle box at desk_b2 during Priya's afternoon (against 2), and p_a9b4 put the book at the kitchen table (against 2). This document says the book goes to the armchair in the living room, not to the kitchen or to desk_b2. The puzzle box stays on the bookshelf (its resting spot, confirmed by sightings).

What would refute it: if book_priya is sighted at nightstand_b2 at 15:00 or 16:00 on a weekday, or if it is at the kitchen table or desk_b2 during the afternoon window.

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
   "claim": "Priya's book is back on the nightstand at 18:00 on a weekday",
   "target": "book_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The puzzle box stays on the bookshelf during Priya's afternoon reading",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 22,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
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
    "from": 15,
    "to": 18,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
