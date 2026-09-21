# p_9e4a — Ines's midday kitchen: glass at the table 12–13:30, bottle at the sink 14–15

Ines works from the office desk every weekday, but she does not leave the house for lunch. Instead, she takes a midday break at the kitchen table: her glass is seen at the kitchen table at 12:00 and 13:00, and her water bottle is seen at the kitchen sink at 14:00 (refill). Her mug, laptop, charger, headphones, and pen all stay at the office desk through the midday window. This is distinct from the hypothesis that Ines goes out for lunch (p_c9d4): here her work objects remain at the desk and her glass and water bottle appear in the kitchen.

Elena is at her office in town from 8:00 to 17:30 on weekdays, so her personal items are out of the house during that window. Ines's keys, jacket, shoes, umbrella, sunglasses, and wallet stay at the entry all day.

The evening follows the standard pattern: laptop to the office floor at 18:00, mug to the coffee table at 22:00, remote and blanket to the coffee table at 21:00, speaker to the couch at 21:00.

This document is set apart by its midday kitchen-break prediction: the glass at the kitchen table 12:00–13:30 and the water bottle at the sink 14:00–15:00, while the laptop and pen remain at the desk. It is refuted if Ines's laptop or pen is found out of the house at midday, or if the glass is never seen at the kitchen table between 12:00 and 13:30 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Ines's glass is at the kitchen table at 12:30 on weekdays",
   "target": "glass_ines",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12,
   "to": 13.5
  },
  {
   "claim": "Ines's water bottle is at the kitchen sink at 14:00 on weekdays",
   "target": "water_bottle_ines",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 14,
   "to": 15
  },
  {
   "claim": "Ines's laptop is at the office desk at 13:00 on weekdays",
   "target": "laptop_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Ines's pen is at the office desk at 13:00 on weekdays",
   "target": "pen_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Elena's keys are out of the house at 13:00 on weekdays",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 12,
   "to": 14
  }
 ],
 "targets": {
  "glass_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13.5,
    "to": 18,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 14,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 15,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "laptop_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "floor_o_o1",
    "chance": "usually"
   }
  ],
  "pen_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 14,
    "at": "desk_o1",
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
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 22,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "office_shelf_o1",
    "chance": "usually"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
