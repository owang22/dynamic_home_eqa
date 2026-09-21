# p_f2a9 — Priya's Kitchen Table Rhythm: 07:30 Breakfast, 12:00 Lunch, 15:00 Tea, 21:00 TV

Priya's day orbits the kitchen table in three sittings: breakfast at 07:30 (mug and glass at the table 07:00–09:00), lunch at 12:00 (glass at the table 11:00–14:00), and an afternoon tea at 15:00 (mug at the table 14:00–16:00). Between sittings the mug goes to the cupboard and the glass goes to the nightstand or cupboard. In the evening, both migrate to the coffee table for TV (20:00–23:00). Her book is at the nightstand during her afternoon reading (14:00–19:00), not at the kitchen table as p_a9b4 claims. The p_a9b4 "kitchen social hub" document placed her mug at the kitchen table at 10:00 and her book at the kitchen table at 15:00 — both contradicted by sightings (mug at cupboard at 14:00, book at nightstand at 15:00). If Priya's mug is found at the kitchen table at 10:00, or her book is found at the kitchen table, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Priya's mug is on the kitchen table at 15:00 on a weekday (afternoon tea)",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Priya's book is at the nightstand at 15:00 on a weekday (afternoon reading, not the kitchen table)",
   "target": "book_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's glass is on the kitchen table at 12:30 on a weekday (lunch drink)",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13.5
  },
  {
   "claim": "Priya's mug is on the coffee table at 21:30 on a weekday (evening TV session)",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "mug_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 19.5,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 11,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 19.5,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 23,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
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
    "to": 19,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 11.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
