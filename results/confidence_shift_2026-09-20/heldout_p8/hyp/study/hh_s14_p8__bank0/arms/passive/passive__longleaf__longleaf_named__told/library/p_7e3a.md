# p_7e3a — Thursday friends: Yuki hosts, kitchen and living room open

Marco and Yuki share this home. Marco works afternoon-to-night shifts (out roughly 13:40–23:00 on weekdays); Yuki is retired and anchors the house. On Thursday the couple has friends coming over in the evening. Because Marco is at work during the gathering, Yuki hosts alone from about 18:00 until the guests leave near 22:00. The kitchen goes into active service: Yuki brings plates, glasses, mugs, and serving dishes out of the cupboard to the kitchen table. The board game comes off the bookshelf to the coffee table for the guests. The snack bowl is on the coffee table. The candle keeps its permanent spot on the coffee table. The guitar stays on the couch—Yuki is entertaining, not practicing. The blanket is on the couch for the guests to use. The dog is in the living room with its toy, and its bowl is on the kitchen floor.

This document predicts that on a weekday evening (specifically Thursday), the kitchen table is set with plates, glasses, and serving dishes, and the coffee table holds the board game and snack bowl. On a normal weekday evening without guests, these items remain in the cupboard and on the bookshelf. The "sometimes" chance on the override blocks reflects that this is a one-evening-in-the-week event, not a daily pattern.

What would refute it: If on a weekday 18–22 h the plates are still in the cupboard, the board game is still on the bookshelf, and the snack bowl is in the cupboard, the friends' prediction fails. If the guitar is moved off the couch (e.g., into the bedroom for practice) during that window, the document is also weakened.

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table during the friends' evening",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Yuki's plate is at the kitchen table during the friends' evening",
   "target": "plate_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table during the friends' evening",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The guitar remains on the couch during the friends' evening",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "plate_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "guitar_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ]
 }
}
```
