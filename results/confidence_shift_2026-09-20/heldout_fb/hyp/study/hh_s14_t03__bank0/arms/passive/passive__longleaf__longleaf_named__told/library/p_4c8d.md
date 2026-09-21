# p_4c8d — Friends Evening: Kitchen to Living Room, 18:00–23:30

Thursday evening, friends came over. The robot's sightings reveal a clear progression: the evening started in the kitchen and dining area (serving dish at the kitchen table at 20:00, Yuki's glass at the kitchen table at 18:00 and 20:00, phone_yuki at the kitchen table at 21:00) and gradually migrated to the living room (serving dish on the coffee table at 21:00 and 23:00, snack bowl at the counter at 22:00 and 23:00, board game on the coffee table at 23:00, glass_yuki at the coffee table at 23:00). The gathering was a dinner-and-drinks that moved to the living room for games and snacks, not a living-room-only affair from the start.

This corrects p_7e3b, which placed the board game and snack bowl at the coffee table during 19–22h. The actual sightings show the board game was still on the bookshelf at 18:00 and only appeared on the coffee table at 23:00 — well after the 19–22h window. The snack bowl was at the counter at 22:00 and 23:00, not the coffee table. The serving dish moved from the kitchen table (20:00) to the coffee table (21:00, 23:00), marking the transition from dining to lounging.

Marco was at his night shift during this gathering (the sick message was for Friday, not Thursday). His lunchbox and vitamins were out of the house. Yuki hosted alone.

What would refute: if the board game is seen on the coffee table before 21:00, or the snack bowl is on the coffee table at 20:00, or the serving dish is on the coffee table before 20:30.

```json
{
 "claims": [
  {
   "claim": "The board game is still on the bookshelf at 20:00, not yet brought out for the gathering",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The snack bowl is at the kitchen counter at 22:00, not on the coffee table",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  },
  {
   "claim": "The serving dish is on the coffee table at 22:00 after migrating from the kitchen",
   "target": "serving_dish_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Yuki's glass is at the kitchen table at 19:00 during the dinner portion of the gathering",
   "target": "glass_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20.5
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 21,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 21,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
