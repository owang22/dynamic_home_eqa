# p_6d4a — Friends Evening Pattern: Kitchen First, Living Room Later, No Board Game

Friends are coming over Wednesday and Thursday evenings (per the residents' messages). The Wednesday evidence (p_7e2a's against-counts: board game 0-for-5-against at coffee table, snack bowl 0-for-8-against at coffee table during 18–21h) shows that the "friends evening" does NOT mean the board game is brought out or the snack bowl is on the coffee table early. Instead, the evening follows the standard household pattern: the kitchen is the social hub during dinner (18–20h, plates at the kitchen table, glasses at the counter, snack bowl at the counter), then the group migrates to the living room by 21h (snack bowl and mugs to the coffee table, blanket on the couch).

The board game stays on the bookshelf throughout the evening. The guitar is played by Hana (ON_PERSON) during the 19–21h window. The jacket is at the entry hook (Hana is home). This is a normal evening with extra people in the kitchen, not a rearranged "party" setup.

What sets this apart: on Wednesday and Thursday evenings, board_game_shared is at bookshelf_l1 (not coffee_table_l1) during 18–21h. The snack bowl follows the standard migration (counter 18–20h, coffee table 21h+). The kitchen table has plates during dinner (18–20h). The guitar is ON_PERSON at 19–21h.

What would refute it: board_game_shared at coffee_table_l1 at 19:00 on a Wednesday or Thursday, or snack_bowl_shared at coffee_table_l1 at 18:00 on a Wednesday or Thursday.

```json
{
 "claims": [
  {
   "claim": "The board game is on the bookshelf at 19:00 on a Wednesday evening (friends are here but the game is not out)",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 18,
   "to": 21
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 19:00 on a Thursday evening (dinner in progress, not yet moved to living room)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The guitar is being played by Hana at 20:00 on a Thursday evening (friends are here, she plays)",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Hana's jacket is at the entry hook at 19:00 on a Thursday evening (she is home for the visit)",
   "target": "jacket_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 18,
   "to": 21
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
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
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
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
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
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
