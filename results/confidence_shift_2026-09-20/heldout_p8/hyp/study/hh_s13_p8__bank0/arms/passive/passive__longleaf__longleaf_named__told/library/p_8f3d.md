# p_8f3d — Wednesday-Thursday Guest Dinner: The Kitchen is the Stage (fork of p_4e8a)

The parent hypothesis (p_4e8a) predicted a living-room social: board game on the coffee table, snack bowl on the coffee table, guitar sidelined. Four claims went against in the first two days. The sightings tell a different story. At 18:00 on Wednesday both residents were in the kitchen; plate_priya was on the kitchen table, mug_hana was on the kitchen table, glass_hana was at the counter, and the snack bowl was at the counter. The board game was still on the bookshelf. The guitar was still on the bedroom floor. The remote was still on the TV stand. The living room was untouched.

This fork reinterprets the guest evening as a **kitchen dinner gathering**, not a living-room party. Friends arrive around 18:00–18:30 for a cooked meal. The kitchen table fills with plates, mugs, and glasses. The counter holds the snack bowl (for between courses or as a side). The living room is a quiet background space: the board game stays on the bookshelf, the guitar stays on the bedroom floor, the remote stays on the TV stand. Hana has just come home from work (her water bottle, charger, scarf, and shoes are at the entry) and goes straight into the kitchen to help Priya serve. The event runs from about 18:00 to 21:00.

What changed from the parent: the board game and snack bowl are NOT on the coffee table; they stay in their resting spots (bookshelf and kitchen). The kitchen table is the social surface, not the coffee table. The guitar and remote claims are retained because they held (FOR 1 each). New claims target the kitchen table and counter during the guest window.

What would refute this: if the board game is sighted on the coffee table or anywhere outside the bookshelf during 18–22h on Wednesday or Thursday, or if the snack bowl is on the coffee table, or if both residents are in the living room at 19:00 while the kitchen is empty.

_(targets the fork left unstated are inherited from p_4e8a)_

```json
{
 "claims": [
  {
   "claim": "The board game stays on the bookshelf during the Wednesday guest dinner",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The snack bowl is at the kitchen counter during the Wednesday guest dinner",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 21
  },
  {
   "claim": "Priya's plate is on the kitchen table during the Wednesday guest dinner",
   "target": "plate_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Hana's mug is on the kitchen table during the Wednesday guest dinner",
   "target": "mug_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
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
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "coasters_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
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
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
