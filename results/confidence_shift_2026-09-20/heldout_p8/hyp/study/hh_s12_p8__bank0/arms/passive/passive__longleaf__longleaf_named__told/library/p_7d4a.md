# p_7d4a — Weekend social evening: living room becomes the hub

Elena and Priya are home all Saturday, and friends arrive in the evening. During the day the house is quiet and objects rest in their usual spots, but from about 18:00 the living room and coffee table become the active zone: the board game comes off the bookshelf, the blanket gets pulled onto the couch for the extra guests, the remote migrates from the TV stand to the coffee table, and the dog's toy ends up on the living room floor as the dog circulates among the visitors. This hypothesis is distinct from the weekday documents in that it predicts a *shift* of social objects from storage to the living room on weekend evenings, rather than the kitchen-and-desk split that dominates weekdays.

What would refute it: if the board game is still on the bookshelf at 20:00 on Saturday, or if the blanket is not on the couch but still folded on the coffee table, the "social hub" prediction fails. If the dog toy is in the kitchen or bedroom rather than the living room floor in the afternoon, the relaxed-weekend assumption is wrong.

```json
{
 "claims": [
  {
   "claim": "The board game is at the coffee table on Saturday evening when friends play",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The blanket is on the couch on Saturday evening as guests settle in",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The remote is on the coffee table on Saturday evening during group TV",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The dog toy is on the living room floor on Saturday afternoon while the dog roams",
   "target": "dog_toy_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:cushion": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "cushion_1_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "cushion_2_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ]
 }
}
```
