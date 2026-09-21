# p_f9a3 — Weekend evening: Elena organises her work kit; board game out for friends

The residents' messages confirm friends are coming over both Saturday and Sunday evenings. The Saturday data (day 4) shows a quiet shift at 20:00–22:00: Elena's laptop, which has sat on the entry hook all day, moves to the dresser in the bedroom; her notebook and pen, also on the entry hook, move to the bedroom desk (desk_b1). This looks like an evening tidy-up — she's putting her work kit away properly for the week, or perhaps doing a short evening session at the desk before the friends arrive. The board game, which is on the bookshelf at every other hour, appears on the coffee table at 22:00 — the one moment it is pulled out, consistent with a group activity with visitors.

The remote stays on the TV stand all weekend (unlike weekdays where it splits between TV stand and coffee table), suggesting less TV-watching and more socialising. Priya is seen in the kitchen at 20:00 and the living room at 22:00, fitting a host pattern: cooking or clearing up, then settling in with the group.

This document is set apart from p_3d7e (which predicted baking in the morning, guitar in the living room, and blanket on the couch — all contradicted by the sightings) and from the weekday documents (which place Elena's work items at the entry hook or out of the house). It is refuted if the board game is not seen at the coffee table on a weekend evening, if Elena's laptop is not at the dresser at 20:00–22:00 on a weekend, or if the notebook and pen remain at the entry hook through the evening.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is at the bedroom dresser on a weekend evening after being at the entry hook all day",
   "target": "laptop_elena",
   "expect": "dresser_b1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The board game is on the coffee table on a weekend evening when friends are over",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 21,
   "to": 22
  },
  {
   "claim": "Elena's notebook is at the bedroom desk on a weekend evening",
   "target": "notebook_elena",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The remote stays on the TV stand throughout the weekend",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 10,
   "to": 18
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dresser_b1",
    "chance": "sometimes"
   }
  ],
  "notebook_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pen_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "board_game_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
