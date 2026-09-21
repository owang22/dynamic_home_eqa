# p_5c8f — The 07:30 Breakfast, 09:00 Walk, 11:30 Grocery

Priya's weekday morning is a three-act sequence. Act one: breakfast at the kitchen table from 7:00 to 8:30. The mug is seen at the kitchen table 8 times in the 07:00–08:00 window, the bowl 6 times at 08:00, and the glass and plate appear in the same window. Act two: a morning walk from 9:00 to 10:00. Priya's keys and jacket leave the house for the walk. Act three: a grocery run from 11:00 to 12:30. The shopping bag dominates the counter at 12:00 (5 sightings) and 13:00 (3 sightings), and Priya's keys and jacket are out during this window. Between acts, Priya is at desk_b2 or the bookshelf, reading or working on puzzles. Her book is at the nightstand in the early afternoon (seen at 15:00, 2 sightings) and at the bookshelf at 03:00.

This document differs from p_2e9f (which bundles breakfast, lunch, and walk into one document and places the walk at 09:00 with the grocery implicit) and from p_a3f1 (which places Priya's errands at 14:00–16:00). The evidence pins the grocery to 11:30–12:30: the bag is at the counter at the 12:00 and 13:00 passes, not at 15:00 or 16:00. The breakfast is at 07:00–08:00, not 08:00–09:00: the mug and bowl are at the kitchen table at the 07:00 and 08:00 passes, and by 09:00 they are back in the cupboard or sink.

This document is refuted if Priya's keys are in the house at 09:30 (no walk), if the shopping bag is at the counter at 15:00 (a later grocery), if the breakfast items are at the kitchen table at 10:00 (a much later breakfast), or if Priya's jacket is at the entry hook at noon on a weekday (no grocery run).

```json
{
 "claims": [
  {
   "claim": "Priya's mug is at the kitchen table at 07:30 on a weekday (breakfast)",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Priya's keys are out of the house at 09:30 on a weekday (morning walk)",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 10
  },
  {
   "claim": "The shopping bag is at the kitchen counter at 12:00 on a weekday (grocery unpacking)",
   "target": "shopping_bag_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 12.5
  },
  {
   "claim": "Priya's glass is at the kitchen table at 12:00 on a weekday (lunch drink)",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "Priya's jacket is out of the house at 11:30 on a weekday (grocery run)",
   "target": "jacket_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 11,
   "to": 12.5
  }
 ],
 "targets": {
  "mug_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "class:plate": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.75,
    "to": 10,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 12.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.75,
    "to": 10,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 12.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 11,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
