# p_4a7c — Weekend Puzzle on the Couch

Priya works on her jigsaw puzzle in the living room on weekend afternoons. On weekdays the puzzle box sits on the bookshelf and never moves, but on Saturday and Sunday afternoons she carries it to the couch and works on it there. The 16:00 weekend patrol confirmed the box on the couch_l1, while the 00:00 and 08:00 weekend patrols still show it on the bookshelf. This is a weekend-only behaviour: the box is on the bookshelf every single weekday pass (00:00, 08:00, 16:00, 18:00 all bookshelf_l1), so the couch placement is a clear weekend shift.

This document sets itself apart from p_2e8c and p_7f3a, which keep the puzzle box on the bookshelf through the entire weekend, and from p_d5e7, which places it at desk_b2. The couch is the distinguishing receptacle: Priya is in the living room on weekends (the Saturday message confirms "around the house more"), and the couch is where she settles in to work on the puzzle.

This hypothesis is refuted if the puzzle box is consistently found on the bookshelf or at desk_b2 during weekend afternoons (14–18 h), or if it is seen on the coffee table, the floor, or anywhere other than the couch during that window.

```json
{
 "claims": [
  {
   "claim": "The puzzle box is on the couch during Priya's weekend afternoon puzzle session",
   "target": "puzzle_box_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The puzzle box is on the bookshelf on a weekend morning before the afternoon session",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 7,
   "to": 11
  },
  {
   "claim": "The puzzle box stays on the bookshelf on a weekday afternoon",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 19,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
