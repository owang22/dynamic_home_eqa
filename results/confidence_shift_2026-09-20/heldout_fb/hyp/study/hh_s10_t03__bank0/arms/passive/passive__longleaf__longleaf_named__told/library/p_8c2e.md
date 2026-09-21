# p_8c2e — Overnight kitchen: dirty items sleep in the sink, clean items in the cupboard

By 03:00 on a weekday the kitchen is in its overnight state. Yuki ate dinner around 19:00–20:00 and did not do a full wash-up before bed; the dirty plate, mug, glass, cutting board, pan, and spatula are all sitting in the kitchen sink. The pot, which was not used for dinner (it was in the cupboard at 18:00), is in the pantry shelf. Clean plates and bowls are in the cupboard. The kettle is back on the counter. This is the state the robot sees on its 03:00 patrol, and it persists until the next morning's routine (around 06:00–07:00) when someone starts the day.

What sets this apart: it explicitly places *six* items in the sink simultaneously (not just one or two), and it distinguishes the pot (pantry) from the pan (sink). It also confirms the kettle is on the counter overnight, not in the cupboard.

Refutation: if the 03:00 patrol finds the plate or mug in the cupboard (washed up) or the pan on the counter, the overnight-dump hypothesis is wrong for that item.

```json
{
 "claims": [
  {
   "claim": "Yuki's plate is in the kitchen sink at 03:00 on a weekday (overnight dish dump)",
   "target": "plate_yuki",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 1,
   "to": 6
  },
  {
   "claim": "The shared pan is in the kitchen sink at 03:00 on a weekday (not washed before bed)",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 1,
   "to": 6
  },
  {
   "claim": "The shared pot is in the pantry shelf at 03:00 on a weekday (not used for dinner)",
   "target": "pot_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 1,
   "to": 6
  },
  {
   "claim": "Yuki's mug is in the kitchen sink at 03:00 on a weekday",
   "target": "mug_yuki",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 1,
   "to": 6
  }
 ],
 "targets": {
  "plate_yuki": [
   {
    "days": "weekday",
    "from": 1,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekday",
    "from": 1,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekday",
    "from": 1,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekday",
    "from": 1,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekday",
    "from": 1,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 1,
    "to": 6,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "weekday",
    "from": 1,
    "to": 6,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
