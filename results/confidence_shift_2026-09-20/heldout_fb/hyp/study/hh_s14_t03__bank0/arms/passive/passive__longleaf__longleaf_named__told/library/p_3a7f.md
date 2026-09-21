# p_3a7f — Monday Sick Day: Work Kit Stays Home, Marco Rests, Yuki Anchors

Marco is home sick on Monday. He does not go to work, so his lunchbox remains in the kitchen cupboard, his vitamins stay on the counter, and his keys, jacket, and backpack are all at the entry all day. In the morning he does his usual yoga and a baking session, then settles into the bedroom or couch to rest through the afternoon, phone beside him on the bed. Yuki, caring for him, skips her usual afternoon errand; her keys, wallet, and sunglasses stay at the entry table from midday onward. The dog's morning walk and feeding proceed exactly as on any other weekday. In the evening both residents are home in the living room.

This document is set apart from the standard-split hypotheses (p_a3f1, p_4a7c, p_7d2a) by predicting that Marco's work kit—lunchbox, vitamins, keys, jacket, backpack—stays IN the house during the 14–22 h window on this weekday, rather than being OUT_OF_HOUSE. It also predicts Yuki's keys and wallet at the entry table during 13–17 h, where the standard split (p_c9d4) has them out with her. The phone-at-bed block is unique: on a normal weekday Marco's phone is at the coffee table or nightstand in the afternoon because he is at work; here it is at the bed because he is resting.

This document is refuted if Marco's lunchbox or vitamins are sighted OUT_OF_HOUSE during 14–22 h on this weekday, or if Yuki's keys are sighted anywhere other than the entry table during 14–17 h, or if Marco's phone is sighted at the coffee table or entry table during 14–18 h.

```json
{
 "claims": [
  {
   "claim": "Marco's yoga mat is on the living room floor during his morning yoga session",
   "target": "yoga_mat_marco",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 6,
   "to": 7
  },
  {
   "claim": "The dog bowl is on the kitchen floor during the morning feeding",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 7,
   "to": 7.5
  },
  {
   "claim": "Marco's phone is at the bed during his afternoon rest",
   "target": "phone_marco",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Yuki's keys remain at the entry table in the afternoon because she stays home to care for Marco",
   "target": "keys_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
  "lunchbox_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "vitamins_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "backpack_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "phone_marco": [
   {
    "days": "weekday",
    "from": 13,
    "to": 19,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 13,
    "to": 17,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "wallet_yuki": [
   {
    "days": "weekday",
    "from": 13,
    "to": 17,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_yuki": [
   {
    "days": "weekday",
    "from": 13,
    "to": 17,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "yoga_mat_marco": [
   {
    "days": "weekday",
    "from": 6,
    "to": 7,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "journal_marco": [
   {
    "days": "weekday",
    "from": 10,
    "to": 13,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 2,
    "to": 6,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ],
  "guitar_yuki": [
   {
    "days": "both",
    "from": 2,
    "to": 5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 13,
    "to": 19,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 2,
    "to": 5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
