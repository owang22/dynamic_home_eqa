# p_b6d3 — The Living Room Day; Hana's Mug, Book, and Bottle Migrate to the Couch by 10:00

The aggregate weekday sightings reveal a consistent midday pattern that no current document captures: between 10:00 and 17:00, Hana's mug is at coffee_table_l1 (sighted at 10:00, 13:00, and 17:00), her book is at coffee_table_l1 or couch_l1 (12:00, 13:00, 17:00), and her water bottle is at coffee_table_l1 (10:00, 17:00). This is not the kitchen-table work block that p_f4b2 and p_3e7a predict, nor the desk block that p_b8c2 predicts. Hana's daytime activity centre is the living room—she sits on the couch or at the coffee table, scrolls on her tablet (which at 10:00 is also at coffee_table_l1 x2), reads, and sips tea.

The tablet's 09:00 kitchen_table_k1 x4 sightings are real but represent a brief morning transition: she starts at the kitchen table with breakfast, then moves to the living room by 10:00. The 12:00 nightstand_b1 sighting is an outlier or a brief return to the bedroom. The 18:00 nightstand_b1 x1 and kitchen_table_k1 x1 show her winding down.

This document is set apart by placing mug_hana, book_hana, and water_bottle_hana at coffee_table_l1 from 10:00 to 17:00 on weekdays, and tablet_hana at coffee_table_l1 (not kitchen_table_k1) from 10:00 to 13:00. It is refuted if the mug is at cupboard_k1 during 10:00–17:00, or if the book is at nightstand_b1 during that window.

```json
{
 "claims": [
  {
   "claim": "Hana's mug is at the coffee table during the weekday afternoon, not the cupboard",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 17
  },
  {
   "claim": "Hana's book is in the living room during the weekday afternoon",
   "target": "book_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "Hana's tablet is at the coffee table, not the kitchen table, by 10:00 on weekdays",
   "target": "tablet_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 13
  },
  {
   "claim": "Hana's water bottle is at the coffee table during the weekday afternoon",
   "target": "water_bottle_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 17
  }
 ],
 "targets": {
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "book_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 13,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
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
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
