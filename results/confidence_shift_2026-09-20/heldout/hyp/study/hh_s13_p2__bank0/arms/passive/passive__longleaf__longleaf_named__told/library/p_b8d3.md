# p_b8d3 — The 22:00 Transit: Objects Caught Mid-Move, Not a Clean Phase Shift (fork of p_2f9b)

The parent document (p_2f9b) described a clean two-phase evening: kitchen until 21:00, then everything shifts to the coffee table. The evidence from both Tuesday and Wednesday 22:00 passes contradicts the "clean" part. At 22:00, the blanket shows 1× couch + 1× coffee_table, the remote shows 1× tv_stand + 1× coffee_table, and the board game shows 1× bookshelf + 1× coffee_table. These are not noise — they are systematic 50/50 splits that appear on both evenings. The robot makes its 22:00 pass while the residents are still settling in, catching objects mid-transition. By contrast, the snack bowl (2×/2× on the coffee table), the glasses (on the coffee table), and the mugs (on the coffee table) have already been placed deliberately and show no split.

This fork lowers the confidence on the "ambient" objects (blanket, remote, board game) from "usually" to "sometimes" in the 21–23 h window, reflecting that they are in transit rather than firmly at the coffee table. The "deliberate" objects (snack bowl, glasses, mugs) keep "usually" because they are set down intentionally as part of the evening routine. The transition window is widened: the kitchen phase runs to about 21:00, the transit window is 21:00–23:00, and the objects do not all arrive at the coffee table simultaneously.

What changed from the parent: (1) blanket coffee_table block lowered from "usually" to "sometimes"; (2) remote coffee_table block lowered from "usually" to "sometimes"; (3) added board_game_shared target with a "sometimes" coffee_table block (the parent had no board game target); (4) class:glass 21–23 h block changed from cupboard_k1 to coffee_table_l1 (Wednesday evidence shows glasses on the coffee table, not the cupboard); (5) class:mug 21–23 h block changed from cupboard_k1 to coffee_table_l1 (Wednesday evidence shows mugs on the coffee table); (6) the prose reframes the model as "transit" rather than "two clean phases."

What would refute it: if at 22:00 the snack bowl is NOT on the coffee table (still at the sink), or if the blanket is on the couch at 20:00 AND at 22:00 with no coffee_table sighting (no transit at all), or if the residents are still in the kitchen at 22:00.

Travelling objects: Hana's laptop, jacket, keys, handbag, wallet, pen, and water bottle are out with her at work 8:00–17:30. Priya's keys and jacket are out on the afternoon errand 14:00–16:00.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch at 20:00 on a weekday (before the evening transit)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The remote is on the TV stand at 20:00 on a weekday (before the evening transit)",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The snack bowl is on the coffee table at 22:00 on a weekday (deliberately placed, not in transit)",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Priya's mug is on the coffee table at 22:00 on a weekday (deliberately placed for the evening)",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
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
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 20,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "class:plate": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
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
    "to": 22.5,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
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
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
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
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
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
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
