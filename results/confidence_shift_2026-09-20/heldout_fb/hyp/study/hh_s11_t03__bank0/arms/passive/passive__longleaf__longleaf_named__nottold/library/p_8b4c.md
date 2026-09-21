# p_8b4c — Priya's Evening Migration; Glass to Nightstand, Book to Bed

Priya is retired and home most of the day. Her evening follows a clear, repeatable migration. After lunch her glass returns to the cupboard (sightings at 12:00 and 18:00). At dinner (19:00) the glass is at the dining table (two sightings), then moves to the kitchen counter for a late-evening sip (21:00), and is placed on her nightstand by 22:00 where it stays overnight (six sightings at 22:00). Her book follows a parallel path: it rests on the nightstand in the early morning, moves to the armchair for her afternoon reading block (15:00, one sighting; weekend 13:00, one sighting), drifts to the coffee table (18:00), is taken to the bed for evening reading (20:00, two sightings), and is shelved by 22:00 (two sightings). Her magazine follows the book to the armchair at 15:00 (three sightings). Her water bottle sits in the armchair during the morning reading block (09:00, two sightings) and on the dining table in the early morning. Her tablet is at the kitchen table for breakfast (08:00, three sightings) and on the nightstand or bed by 20:00–22:00.

This document differs from the top-3 documents, none of which trace Priya's glass through its four evening positions or her book through its five. The glass at nightstand by 22:00 (six sightings) and the book at bed_b2 at 20:00 (two sightings) are the strongest differentiators.

Refutation: finding glass_priya at the dining table after 22:00 on a weekday, or book_priya at the armchair after 20:00, would contradict this document. Finding the magazine at the coffee table during 15:00–18:00 would also weaken it.

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
   "from": 15,
   "to": 18
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
   "claim": "Priya's magazine is in the armchair during the afternoon reading block",
   "target": "magazine_priya",
   "expect": "armchair_l1",
   "days": "both",
   "from": 15,
   "to": 18
  }
 ],
 "targets": {
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "from": 12,
    "to": 13,
    "at": "kitchen_table_k1",
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
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 15,
    "to": 18,
    "at": "armchair_l1",
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
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 15,
    "to": 18,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 9,
    "to": 14,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
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
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "bed_b2",
    "chance": "usually"
   }
  ]
 }
}
```
