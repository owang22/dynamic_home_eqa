# p_e8a1 — Weekend Puzzle on the Kitchen Floor, Not the Living Room

p_e5f0 claimed the puzzle box was on the coffee table at 14:00 Saturday and was refuted twice. The Saturday 12:00 pass found the puzzle box at floor_k_k1 (the kitchen floor) and at bookshelf_l1. Priya, who is retired and home most of the day, works on her jigsaw puzzle in the kitchen area on Saturday afternoons, not in the living room. The puzzle box sits on the kitchen floor where she can spread the pieces out, or it goes back to the bookshelf between sessions. On weekdays the puzzle box stays at bookshelf_l1 (seen there at 03:00 x3 and 18:00 x1), consistent with Priya's weekday routine of a morning walk and afternoon errands that leave little puzzle time.

What sets this apart: it places the puzzle in the kitchen on weekends, not the living room. If the robot sees the puzzle box on the coffee table or at desk_b2 on a Saturday between 11:00 and 14:00, this document is wrong. If it is on the kitchen floor or back on the bookshelf, this document is right.

```json
{
 "claims": [
  {
   "claim": "The puzzle box is on the kitchen floor on a Saturday afternoon while Priya works on it",
   "target": "puzzle_box_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The puzzle box is on the bookshelf on a Saturday morning before Priya starts",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 0,
   "to": 10
  },
  {
   "claim": "The puzzle box is on the bookshelf on a weekday afternoon",
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
    "from": 11,
    "to": 15,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
