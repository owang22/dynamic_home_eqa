# p_c4e9 — Kitchen cleanup progression: counter, sink, then storage by 22:00

The household's evening kitchen routine follows a strict three-stage progression that the mixture keeps getting wrong. Active cooking happens around 17:30–19:00, with the cutting board, pan, and pot on the counter. Washing-up follows at 19:00–21:00, with items in the sink. By 21:00–22:00, items are put away to their storage spots: cutting board and pan to the cupboard, pot to the counter (where it is left for overnight use or the next morning), knife and spatula to the drawer.

This is the step the mixture misses. The "worst objects" list shows the model predicting sink_k1 for the cutting board, pan, knife, and spatula, and pantry_shelf_k1 for the pot, but the actual 22:00 sightings find them in the cupboard, drawer, or counter. The items have already been stored by the time the robot looks.

This differs from p_c007, which places the cutting board on the counter during 18:00–19:30 (correct for active cooking) but does not model the 21:00+ storage step, and from p_d7f3, which correctly puts the pan at the sink by 20:00 but does not extend the progression to the cupboard by 22:00.

What would refute this document: finding the cutting board on the counter at 22:00, the pan on the counter at 22:00, or the knife in the sink at 22:00.

```json
{
 "claims": [
  {
   "claim": "The cutting board is in the cupboard by 22:00 on weekdays, not still in the sink",
   "target": "cutting_board_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The pan is in the cupboard by 22:00 on weekdays, not still in the sink",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The kitchen knife is in the drawer by 22:00 on weekdays, not still in the sink",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "usually"
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
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "usually"
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
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "usually"
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
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "usually"
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
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ]
 }
}
```
