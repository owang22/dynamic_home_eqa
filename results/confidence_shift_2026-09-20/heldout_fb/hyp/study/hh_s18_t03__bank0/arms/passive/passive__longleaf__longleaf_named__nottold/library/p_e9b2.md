# p_e9b2 — Evening convergence: the 21:00 migration to the coffee table and couch

Between 20:00 and 23:00 the household's objects perform a coordinated migration from their daytime resting spots to the living room. The remote leaves the TV stand for the coffee table at 21:00 (sighted there at 21:00 and 22:00). The blanket moves from the couch to the coffee table at 21:00. The snack bowl, which rests in the cupboard or on the counter during the day, appears on the coffee table at 21:00 and 23:00. The speaker stays on the couch throughout. Ines's mug appears at the coffee table at 22:00, and her headphones move to the bedroom at 21:00 (she is winding down). Elena's yoga mat, seen at the coffee table, bed, and living room floor in the morning, is at the wardrobe by 18:00 (stored after use). The kitchen items (plates, glasses, mugs) are at the kitchen table or sink during the 19:00–21:00 dinner window, then the residents move to the living room.

This document focuses exclusively on the evening window and the specific migration times, differentiating itself from p_a3f7 and p_7d4e (which place the snack bowl on the couch or kitchen table) by anchoring the snack bowl and remote on the coffee table after 21:00. It would be refuted if the remote is found on the TV stand at 22:00, or if the blanket is on the couch at 21:00.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table at 22:00",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table at 22:00",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table at 23:00",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23
  },
  {
   "claim": "Ines's headphones are in the bedroom at 21:00",
   "target": "headphones_ines",
   "expect": "bed_b1",
   "days": "both",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Ines's glass is at the kitchen table during dinner",
   "target": "glass_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 18,
   "to": 21
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
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
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "glass_ines": [
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "plate_ines": [
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
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
  ]
 }
}
```
