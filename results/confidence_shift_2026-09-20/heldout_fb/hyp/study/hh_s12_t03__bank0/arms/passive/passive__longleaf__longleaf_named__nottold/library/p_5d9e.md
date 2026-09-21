# p_5d9e — Evening cook 17–19: pot and recipe book on the counter at the edges

The main weekday cooking window is 17:00–19:00, after Elena gets home at 17:30. The pot is on the counter at the start (17:00, filling and prepping) and again at the end (19:00, serving or final reduction), but in the middle it is on the stove (not a tracked receptacle) so the robot sees it in the cupboard or not at all. The recipe book is pulled from the pantry shelf to the counter at 17:00 and 19:00 but tucked back at 18:00 while the cook is actively stirring. The cutting board is on the counter throughout the evening (17–20h) since it was set out for prep. The pan is taken from the cupboard at 18:00 for a side dish. The knife stays in the drawer until 19:00 when it's brought to the kitchen table for plating, then to the counter at 20:00 for washing.

What sets this document apart: it does NOT put the pot on the counter at 18:00. The data shows the pot in the cupboard at 18:00 (2 sightings) and on the counter at 17:00 and 19:00 (1 each). A document that claims the pot is on the counter at 18:00 (like p_4f8a, which has 15 against on that claim) is wrong. The pot is on the stove at 18:00, not on the counter.

Refutation: if the pot is on the counter at 18:00 on a weekday (meaning it's not on the stove), or if the recipe book is in the pantry at 17:00 (not pulled out), this document's "edges only" pattern is wrong.

```json
{
 "claims": [
  {
   "claim": "The pot is in the cupboard at 18:00 on a weekday (on the stove, not the counter)",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "The recipe book is on the kitchen counter at 17:00 on a weekday",
   "target": "recipe_book_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17,
   "to": 17.5
  },
  {
   "claim": "The cutting board is on the kitchen counter at 18:00 on a weekday",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The pan is in the cupboard at 17:00 on a weekday (not yet taken out)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17,
   "to": 17.5
  }
 ],
 "targets": {
  "pot_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 17.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 23.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 17.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 23,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "knife_block_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
