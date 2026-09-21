# p_7b2d — Weekend friends evening: guitar stays in bedroom, board game at 22 h, blanket on armchair

Both residents messaged that friends are coming over on Saturday and Sunday evenings. The natural assumption is that the living room gets set up: guitar out for music, board game on the coffee table, blanket on the couch for guests. The sightings say otherwise. Priya's guitar is at bedroom_floor_b1 on 7 of 7 sighted days with 16-for-16 weekday midday looks confirming it there; it does not appear in the living room at any hour on any day. The blanket is at armchair_l1 at every single weekend pass (2-for-2 at all twelve hours), never on the couch. The board game sits on the bookshelf through the weekend day and the 20:00 pass, then appears on the coffee table at the 22:00 pass—suggesting it comes out for a late-evening game after the main dinner and conversation have settled. The remote stays on the TV stand all weekend.

What sets this apart: p_3d7e predicts the guitar at floor_l_l1, the board game at coffee_table_l1, and the blanket at couch_l1 during 19–22 h on weekends—all four claims have scored against. p_e5f6 also puts the guitar in the living room on Saturday evening (against 4). This document says the guitar never leaves the bedroom, the blanket never leaves the armchair on weekends, and the board game comes out only at 22 h.

What would refute: a sighting of guitar_priya at any living-room receptacle on a weekend, the blanket on the couch on a weekend, or the board game on the coffee table before 21:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "Priya's guitar is on the bedroom floor during the weekend evening when friends are over",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The blanket is on the armchair during the weekend evening with guests",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The board game is still on the bookshelf at 20:00 on a weekend evening, before it comes out for the late game",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The remote is on the TV stand throughout the weekend evening",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
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
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
