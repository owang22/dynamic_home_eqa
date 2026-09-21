# p_9b4d — Thursday Friends' Evening: Serving Dish and Board Game Migrate to the Living Room

On Thursday evening (the friends' visit announced in the residents' message), the kitchen is set for dinner around 18:00, the serving dish moves from the cupboard to the kitchen table for the meal, and then migrates to the coffee table once the gathering shifts to the living room around 20:00. The board game comes off the bookshelf for the evening. The snack bowl leaves the counter and joins the coffee table spread. By 23:00 the serving dish and board game remain on the coffee table as the evening winds down.

This differs from p_7e3b, which places the board game and snack bowl on the coffee table from 19:00 (too early; the 18:00 pass still shows the serving dish in the cupboard and the board game on the bookshelf). It also differs from p_4c8d, which captures the serving dish on the coffee table at 22:00 but does not model the intermediate kitchen-table stop at 20:00. The 20:00 pass finding the serving dish on the kitchen table (x2) is the key intermediate step.

What would refute this: a Thursday pass at 20:00 finding the serving dish already on the coffee table (skipping the kitchen-table stop), or the board game still on the bookshelf at 22:00.

```json
{
 "claims": [
  {
   "claim": "The serving dish is on the kitchen table at 20:00 on Thursday during dinner",
   "target": "serving_dish_shared",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The serving dish is on the coffee table at 22:00 on Thursday during the gathering",
   "target": "serving_dish_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The board game is on the bookshelf at 18:00 on Thursday, not yet brought out",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The snack bowl is on the counter at 18:00 on Thursday, before the gathering begins",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "serving_dish_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "board_game_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 20,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
