# p_9c2d — Yuki's solo weekday dinner: cook at six, eat at eight, TV at ten

On weekdays Omar is at his afternoon-to-night shift from roughly 13:40 to 23:00, so the entire evening kitchen-and-living-room sequence belongs to Yuki alone. The robot's clock passes confirm the rhythm: at 18:00 the cutting board appears on the counter (chopping), the pan and knife are being pulled from their resting spots; by 20:00 the plate, glass, and water bottle are at the dining table (eating); by 22:00 the snack bowl has migrated to the coffee table, the remote is at the side table, and the blanket is on the couch (TV). Cleanup happens in the last hour—dishes back at the sink, mug to the cupboard.

This document is set apart from p_c007 (shared dinner cooking) by the absence of Omar in the kitchen after 13:40: the resident-look log shows only resident_1 in the kitchen at 18:00 and in the dining room at 20:00 on both observed weekday evenings. It differs from p_f3a7 in that it specifies the *full* three-act sequence (cook → eat → TV) with the snack bowl and remote as the TV-act markers, and it places the cutting board at the counter only during the 18:00–19:00 cooking window rather than all evening.

Refutation: sighting Omar (resident_2) in the kitchen or dining room between 14:00 and 22:00 on a weekday; finding the cutting board at the counter at 20:00 or later (cooking is over by then); finding the snack bowl at the counter at 22:00 (it should have moved to the coffee table for TV).

```json
{
 "claims": [
  {
   "claim": "The cutting board is on the kitchen counter at 18:30 on a weekday while Yuki chops",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Yuki's plate is at the dining table at 20:00 on a weekday during her solo dinner",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The snack bowl is at the coffee table at 22:00 on a weekday during Yuki's TV time",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Yuki's water bottle is at the dining table at 20:00 on a weekday",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The pan is back at the kitchen sink at 21:00 on a weekday after cooking is done",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "plate_yuki": [
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
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
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
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 17.5,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
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
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 20,
    "at": "side_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "side_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "mug_yuki": [
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
    "to": 21,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
