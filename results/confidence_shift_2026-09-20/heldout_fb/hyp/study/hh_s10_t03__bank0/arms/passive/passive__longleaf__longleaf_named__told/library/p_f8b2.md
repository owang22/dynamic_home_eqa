# p_f8b2 — The 19-to-23h evening arc: dining table dinner, then coffee table TV

On a weekday evening the household runs a clear spatial arc. Yuki arrives at 17:30; for the next half-hour she is in the entry zone (jacket at the hook, keys on the floor, water bottle at the hook). By 19:00 she is seated at the dining table for dinner: the water bottle, her glass, and her plate are all at the dining table. The mug stays in the kitchen cupboard during dinner. At 21:00 the TV phase begins: the shared blanket migrates from the couch to the coffee table, the mug appears at the coffee table (or briefly at the bedroom desk if she journals first), and the remote stays at the TV stand until 23:00. By 22:00 the glass has moved to the bedroom nightstand for the bedtime phase. The plate goes to the sink after dinner is finished.

This document is distinguished by its precise hour-by-hour tracking of four objects (water bottle, glass, mug, blanket) across three receptacles in the evening. It predicts the glass at the dining table at 19:30 (not the kitchen table, not the coffee table), the blanket at the couch at 20:00 (not yet at the coffee table), and the mug at the coffee table at 22:30 (not the desk, not the cupboard).

Refuted if: the glass is at the kitchen table or coffee table at 19:30; the blanket is at the coffee table before 20:30; the water bottle is at the kitchen table (not dining table) at 19:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's water bottle is at the dining table at 19:30 on a weekday (dinner phase)",
   "target": "water_bottle_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Yuki's glass is at the dining table at 19:30 on a weekday (dinner phase)",
   "target": "glass_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Yuki's glass is at the bedroom nightstand at 22:30 on a weekday (bedtime phase)",
   "target": "glass_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "The shared blanket is on the coffee table at 21:30 on a weekday (TV phase)",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The shared blanket is still on the couch at 20:00 on a weekday (TV has not started)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  }
 ],
 "targets": {
  "water_bottle_yuki": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23.5,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "plate_yuki": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 21.5,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 23,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
