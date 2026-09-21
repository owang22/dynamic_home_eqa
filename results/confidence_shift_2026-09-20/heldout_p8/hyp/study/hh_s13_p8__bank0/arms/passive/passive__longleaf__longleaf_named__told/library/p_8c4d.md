# p_8c4d — Weekend Living Room: Armchair, Coffee Table, and Open Floor

On weekends the living room reorganises itself into a different configuration than weekdays. The blanket, which spends its weekday hours draped over couch_l1, migrates to armchair_l1 on Saturday and Sunday. All three Saturday passes (00:00, 08:00, 16:00) found it on the armchair, and the mixture's worst-objects list flags this as a 3-for-3 miss: the model predicted couch_l1, the blanket was on the armchair. The armchair is where Priya settles in for reading or watching TV on weekends, so the blanket follows her there.

The remote, which rests on tv_stand_l1 during weekday hours, moves to coffee_table_l1 on weekends. Again, all three Saturday passes confirmed coffee_table_l1. This makes sense: on weekends the TV is used from the armchair or the couch rather than from the stand, so the remote travels to the more accessible coffee table.

The vacuum cleaner, stored on storage_floor_s1 during the week, is out on floor_l_l1 (the living room floor) on weekends. All three Saturday passes found it there. The weekend is when the house gets tidied; the vacuum is deployed and left in the open rather than put back in storage.

The board game also stays out on the coffee table on weekends (3/3 Saturday passes at coffee_table_l1), rather than cycling back to the bookshelf as it does on some weekday afternoons.

This document is distinct from p_e5f0 in that it does NOT claim the guitar is played on weekends (the evidence shows bedroom_floor_b1, not ON_PERSON) and does NOT place the puzzle box on the coffee table (it stays at bookshelf_l1, 5/5 days). It also does not assert a brunch or movie-watching schedule; it focuses purely on where the living-room objects rest.

What would refute this: finding the blanket on couch_l1 on a Saturday, the remote on tv_stand_l1 on a weekend, or the vacuum back in storage on a Saturday afternoon.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the armchair on a Saturday afternoon, not on the couch",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 12,
   "to": 20
  },
  {
   "claim": "The remote is on the coffee table on a Saturday afternoon, not on the TV stand",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 12,
   "to": 20
  },
  {
   "claim": "The vacuum cleaner is on the living room floor on a Saturday, not in storage",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 8,
   "to": 18
  },
  {
   "claim": "The board game is on the coffee table on a Saturday afternoon",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 12,
   "to": 18
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
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
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
