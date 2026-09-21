# p_7b2f — Afternoon Board Game: Out for Friends, Shelved by Eight

The board game lives on the bookshelf overnight and in the morning. On weekday afternoons (14:00–17:00) it comes out to the coffee table when Priya has friends over for tea and a game. By 18:00 it is back on the bookshelf. The snack bowl, however, does NOT join the board game on the coffee table — it stays at the kitchen sink during the social visit and only moves to the counter in the evening.

What sets this apart from the other documents: "Priya's Social Circle" (p_a7b2) puts the snack bowl on the coffee table during social visits; this document says the bowl stays at the sink. "Wednesday Guest Evening" (p_4e8a) and "Thursday Guest Evening" (p_5e2a) put the board game on the coffee table at 18–22 h; this document says it is back on the bookshelf by 18:00. "Kitchen Social Visits, No Board Game" (p_6a1b) says the board game never leaves the bookshelf; this document says it does come out in the afternoon.

What would refute this document: finding the board game on the bookshelf at 16:00 on a weekday when friends are visiting, finding it on the coffee table at 19:00, or finding the snack bowl on the coffee table at 16:00.

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table at 16:00 on a weekday afternoon",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The snack bowl is at the kitchen sink at 16:00 on a weekday, not on the coffee table",
   "target": "snack_bowl_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The board game is back on the bookshelf at 19:00 on a weekday",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
