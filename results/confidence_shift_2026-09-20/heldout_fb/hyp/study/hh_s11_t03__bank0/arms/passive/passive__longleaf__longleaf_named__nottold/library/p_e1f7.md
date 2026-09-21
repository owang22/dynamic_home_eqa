# p_e1f7 — Priya's Book Walks the Room; Armchair, Coffee Table, Bed, Shelf

Priya's book follows a four-step evening migration that the library has only partially captured. It starts the day at nightstand_b2 (seen at 03:00 on both weekdays and weekends). By the mid-afternoon it is at armchair_l1 (one sighting at 15:00 on weekdays, one at 13:00 on weekends) where she reads alongside her magazine. At 18:00 it moves to coffee_table_l1 (one weekday sighting). By 20:00 it is on bed_b2 for her evening wind-down (two weekday sightings). By 22:00 it is back on bookshelf_l1 for the night (two weekday sightings). The magazine follows a shorter path: coffee_table_l1 in the morning, armchair_l1 at 15:00 (three weekday sightings), coffee_table_l1 again at 18:00.

This document extends p_9b3d (which covers only the armchair window) and p_8b4c (which covers armchair-to-bed) by adding the coffee-table step at 17–19 h and the bookshelf step at 22–24 h. The book at coffee_table_l1 at 18:00 and at bookshelf_l1 at 22:00 are the two transitions the mixture has been missing: the "worst objects" list shows book_priya predicted at couch_l1 when it was actually at bookshelf_l1.

What would refute this document: if the book is found at the armchair after 17:00, or at the bookshelf before 21:00, the four-step migration breaks down.

```json
{
 "claims": [
  {
   "claim": "Priya's book is in the armchair during her afternoon reading",
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
   "to": 21
  },
  {
   "claim": "Priya's book is back on the bookshelf by 22:00",
   "target": "book_priya",
   "expect": "bookshelf_l1",
   "days": "both",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Priya's magazine is in the armchair during the afternoon reading block",
   "target": "magazine_priya",
   "expect": "armchair_l1",
   "days": "both",
   "from": 14,
   "to": 16
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
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
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
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ]
 }
}
```
