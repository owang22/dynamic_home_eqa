# p_9c1d — Weekend friends: both evenings, living-room social

The residents' messages confirm friends are coming over both Saturday and Sunday evenings. The living room becomes the social hub: the board game moves from the bookshelf to the coffee table, Priya's guitar comes out of the bedroom to the living-room floor for playing, and the blanket shifts to the armchair or couch for guests. Drinks and snacks are at the dining table (glasses, mugs). Elena is home all day—no commute—so her laptop rests at the coffee table or entry hook during the afternoon. Saturday morning still includes baking (tray at the counter 9–12), after which the tray returns to the pantry shelf.

What sets this apart from p_3f7a (Saturday only): this document applies the friends-evening pattern to BOTH weekend days, and it places the board game at the coffee table (where the single weekend 22:00 sighting put it) rather than the dining table (where p_3f7a's claim failed twice). It also predicts the guitar in the living room on Sunday evening, which p_3f7a does not cover.

Refutation: if the board game is sighted at the dining table during a weekend evening, or if the guitar is not in the living room on a Sunday evening when friends are present, or if Elena's laptop is out of the house on a weekend midday, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table during the weekend friends evening",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Priya's guitar is on the living-room floor during the weekend friends evening",
   "target": "guitar_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Priya's glass is at the dining table during the weekend friends evening",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Elena's laptop is at the coffee table on a weekend midday because she is home",
   "target": "laptop_elena",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The baking tray is at the kitchen counter during Saturday morning baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 11
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "usually"
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
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
