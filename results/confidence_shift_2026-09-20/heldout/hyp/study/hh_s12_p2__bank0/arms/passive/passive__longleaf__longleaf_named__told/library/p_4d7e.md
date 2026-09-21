# p_4d7e — Tuesday friends evening: weekday guests, board game out, guitar in living room

Elena is at her office during the day (work kit at the entry hook: laptop, notebook, pen, water bottle, keys, shoes, jacket, hat, backpack all resting there while she's out 8–17:30). Priya is home all day, doing her usual morning walk and afternoon errands. Friends arrive around 19:00 on this Tuesday evening. The social gathering shifts the living room: the board game comes out of the bookshelf to the coffee table for a game night, the guitar moves from the bedroom floor to the couch so Priya can play for the group, and the blanket is pulled onto the couch for the guests to settle in. Plates and glasses are at the dining table for the shared dinner around 19:30.

What sets this apart from the weekend friends-evening documents (p_3d7e, p_7b2d): Elena was at work during the day, so her laptop and notebook are at the entry hook (not the dresser where they go on weekends after she organises her kit). The board game comes out at 19:00 rather than waiting until 22:00 as the weekend pattern suggests, because the friends are here for dinner and the evening, not just a late game. The guitar is on the couch (not the bedroom floor) because Priya is performing for the group in the living room.

What would refute this: if the board game stays on the bookshelf through the 19–22 h window on a weekday evening, if the guitar never leaves the bedroom floor on a weekday, or if Elena's laptop is found at the dresser (a weekend-only spot) on a weekday evening.

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table during the Tuesday friends evening",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Priya's guitar is on the couch during the weekday evening social gathering",
   "target": "guitar_priya",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The blanket is on the couch for guests during the weekday evening",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Elena's laptop is at the entry hook in the evening after she comes home from work",
   "target": "laptop_elena",
   "expect": "entry_hook_e1",
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
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "couch_l1",
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
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "plate_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ]
 }
}
```
