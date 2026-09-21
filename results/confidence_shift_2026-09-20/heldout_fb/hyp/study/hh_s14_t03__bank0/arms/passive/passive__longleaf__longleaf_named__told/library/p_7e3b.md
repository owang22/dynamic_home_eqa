# p_7e3b — Friends Evening: Living Room Gathering

Thursday evening, friends come over. Yuki is home and hosts from roughly 6:30 pm onward; Marco is at his afternoon-to-night shift until about 11 pm. The living room becomes the social centre: the couch and armchair seat guests, and the coffee table is cleared for the gathering. The board game comes down from the bookshelf, the snack bowl is brought out of the cupboard, the candle is lit for warmth, and a few glasses are set on the coffee table for drinks. The TV may run in the background, so the remote is in play. The blanket stays draped over the couch. The dog remains in the living room with its toy, and its bowl sits on the kitchen floor as usual. In the kitchen, Yuki has laid out plates and a serving dish for the food she prepared. Marco's lunchbox and vitamins are out with him at work.

This document differs from the standard-split and night-resting documents in the 18–23 h window: the board game, snack bowl, and glasses are *on the coffee table* rather than at their resting receptacles (bookshelf, cupboard). The candle, though normally on the coffee table as a resting object, is actively lit and surrounded by the social setup. The serving dish and Yuki's plate are at the kitchen table for food service, not tucked in the cupboard. If the robot finds the board game still on the bookshelf or the snack bowl still in the cupboard at 20:00 or 22:00 on this Thursday, this document is wrong about the gathering's timing or scale.

```json
{
 "claims": [
  {
   "claim": "The board game is on the coffee table during the friends' evening",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table during the friends' evening",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Yuki's keys are at the entry table because she is home hosting",
   "target": "keys_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Marco's lunchbox is out of the house because he is at his night shift",
   "target": "lunchbox_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Marco's vitamins are out of the house because he is at his night shift",
   "target": "vitamins_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "candle_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "class:glass": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "lunchbox_marco": [
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "vitamins_marco": [
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_yuki": [
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
