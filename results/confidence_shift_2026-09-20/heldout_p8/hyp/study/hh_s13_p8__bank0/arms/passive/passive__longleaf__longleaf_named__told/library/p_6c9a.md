# p_6c9a — Weekend Living Room: Vacuum Out, Game Ready

On weekends the living room becomes the active space of the house. The vacuum cleaner, which lives in storage on weekdays (00:00, 08:00, 16:00 all storage_floor_s1), is out on the living room floor all weekend: 00:00 floor_l_l1 x2, 08:00 floor_l_l1 x2, 16:00 floor_l_l1 x1. The board game is on the coffee table at every weekend patrol (00:00, 08:00, 16:00 all coffee_table_l1 x2), ready for play. The blanket shifts from the couch (its weekday home, 5/6 sighted days) to the armchair on weekends (armchair_l1 x1 at each weekend pass, alongside couch_l1 x1). The remote moves from the TV stand (its weekday home, 5/6 sighted days) to the coffee table on weekends (coffee_table_l1 x1 at each weekend pass, alongside tv_stand_l1 x1).

This document overlaps with p_8c4d but focuses specifically on the vacuum and board game as the high-confidence anchor objects. The blanket on the armchair and the remote on the coffee table are weekend-specific shifts that distinguish this from the weekday pattern where the blanket is on the couch and the remote is on the TV stand. Unlike p_c9d4, which models the late-night weekday TV session, this is the all-day weekend living room.

This hypothesis is refuted if the vacuum is in storage on a weekend day, if the board game is on the bookshelf on a weekend, or if the blanket is exclusively on the couch (never the armchair) on a weekend.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor on a Saturday, not in storage",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "The board game is on the coffee table on a Saturday afternoon",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The blanket is on the armchair on a Saturday afternoon, not on the couch",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The vacuum cleaner is in storage on a weekday afternoon",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "bookshelf_l1",
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
    "days": "weekend",
    "from": 7,
    "to": 20,
    "at": "armchair_l1",
    "chance": "sometimes"
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
    "days": "weekend",
    "from": 7,
    "to": 20,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
