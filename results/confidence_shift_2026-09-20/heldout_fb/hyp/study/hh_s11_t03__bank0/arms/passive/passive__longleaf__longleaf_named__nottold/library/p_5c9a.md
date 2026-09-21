# p_5c9a — Priya's Evening Migration; Glass Walks Dining Table to Nightstand, Book Walks Armchair to Bed

Priya's evening follows a clear spatial migration. Her glass is at the dining table during the 19:00 meal (two sightings at 19:00 on weekdays), moves to the kitchen counter around 21:00 (one sighting), and is on her nightstand by 22:00 (six sightings at 22:00 on weekdays, three at 22:00 on weekends). Her book follows a parallel path: it is in the armchair during the 15:00 afternoon reading block (one sighting at 15:00 on weekdays, one at 13:00 on weekends), on the coffee table at 18:00 (one sighting), on her bed during the 20:00 wind-down (two sightings at 20:00 on weekdays), and back on the bookshelf by 22:00 (two sightings at 22:00 on weekdays).

This document is distinguished from p_8b4c and p_f2b8, which capture parts of the same migration but with different window boundaries. Here the glass window at the dining table is 19:00–20:00 (not 18:00–20:00), and the book's armchair window is 14:00–16:00 on both days. The nightstand is the terminal resting place for the glass after 22:00, confirmed by the heavy 22:00 pass.

What would refute it: a weekday sighting of glass_priya at the dining table after 21:00, or a weekday sighting of book_priya on the bookshelf before 21:00.

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
   "claim": "Priya's glass is on her nightstand after 22:00 on weekdays",
   "target": "glass_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Priya's book is in the armchair during her afternoon reading block",
   "target": "book_priya",
   "expect": "armchair_l1",
   "days": "both",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Priya's book is on her bed during the evening wind-down",
   "target": "book_priya",
   "expect": "bed_b2",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Priya's book is back on the bookshelf by 22:00",
   "target": "book_priya",
   "expect": "bookshelf_l1",
   "days": "both",
   "from": 22,
   "to": 24
  }
 ],
 "targets": {
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 14,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 14,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "magazine_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
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
  ]
 }
}
```
