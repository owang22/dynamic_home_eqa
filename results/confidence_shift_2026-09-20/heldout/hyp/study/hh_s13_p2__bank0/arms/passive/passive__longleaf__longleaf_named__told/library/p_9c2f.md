# p_9c2f — Priya's Two-Room Day: Kitchen Morning, Living Afternoon, Home All Day

No existing document captures Priya's full daily arc correctly. The parent documents either send her out for afternoon errands (p_a3f1, p_f7a2) or confine her to bedroom-b2 (p_d5e7). The resident sightings tell a clearer story: Priya is in the kitchen at 08:00 and 10:00 on Wednesday, Thursday, and Friday; in the living room at 10:00 and 12:00 on Thursday; in the kitchen at 14:00 on all three days; and in the living room at 16:00 on Wednesday. She is home all day. Her objects follow her between two rooms: the kitchen (morning meals, lunch) and the living room (afternoon reading, puzzles, evening TV).

Her phone is the key diagnostic. The per-object evidence shows phone_priya at nightstand_b2 4/4 sighted days, but weekday 9–17 h looks at nightstand_b2 found it 0 times out of 11. The phone is not at the nightstand during the day. Since no person sightings have caught her holding it, the most likely explanation is that she carries it in her pocket or handbag while moving between rooms (ON_PERSON). At night (00–08 h) it returns to the nightstand.

Her book: bookshelf_l1 at night (00–12 h), armchair_l1 at 16:00 (afternoon reading, seen 1/2 at that pass), nightstand_b2 at 18–24 h (bedside). Her glass: sink_k1 at night, kitchen_table_k1 at 14:00 (afternoon tea, seen 2/2 at that pass). Her mug: scattered at night (cupboard, sink, counter, pantry), kitchen_table at 08:00 (breakfast, seen 3/3), coffee_table at 22:00 (evening drink, seen 2/3). Her headphones: desk_b2 at all passes (confirmed 3/3 at 00–14 h, 2/3 at 16 h). Her notebook: desk_b2 at all passes (confirmed 4/4 days, 11/11 daytime looks).

What sets this apart: Priya never leaves the house; her objects are in the kitchen or living room during the day, not in bedroom-b2 and not OUT_OF_HOUSE. The phone is ON_PERSON 8–17 h, not at the nightstand. What would refute it: Priya's keys sighted OUT_OF_HOUSE at 14:00 on a weekday, or her headphones at bed_b2 at 10:00 on a weekday, or her phone at nightstand_b2 at 14:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Priya's glass is at the kitchen table at 14:00 on a weekday (afternoon tea)",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Priya's headphones are at desk_b2 at 15:00 on a weekday (all-day resting spot)",
   "target": "headphones_priya",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's phone is not at the nightstand at 14:00 on a weekday (she carries it with her)",
   "target": "phone_priya",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Priya's mug is at the kitchen table at 08:00 on a weekday (breakfast)",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ],
  "notebook_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 18,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 15,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
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
    "chance": "sometimes"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_priya": [
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
    "chance": "sometimes"
   }
  ]
 }
}
```
