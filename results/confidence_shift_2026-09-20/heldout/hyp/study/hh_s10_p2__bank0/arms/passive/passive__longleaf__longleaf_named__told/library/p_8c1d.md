# p_8c1d — 20:00 dinner at the dining table; cooking 18–20 h; cleanup by 22:00

On weekdays Yuki comes home around 17:30, starts cooking at 18:00, and serves dinner at the dining table at 20:00. Omar is at work (back at 23:00), so this is effectively a one-person dinner, but the table is set for two. The cutting board goes on the counter during prep (18:00–19:30), the pan and knife come out to the counter for active cooking (18:00–20:00), and by 20:00 the plates, glasses, and water bottle are at the dining table. Cleanup runs 20:00–22:00: dirty items go to the sink, and by 22:00 the pan, knife, and cutting board are back in the cupboard or drawer.

This differs from p_c007 (which puts the cutting board and pan on the counter at 18:00–19:30 but gets 9 "against" hits, suggesting the window is too early or the location shifts) and from p_9a4c (which puts the pan at the sink by 20:00, but the 20:00 pass still shows it on the counter in one sighting). The key distinction: the pan is on the *counter* during active cooking (18:00–20:00) and only moves to the *sink* after the meal (20:00–22:00).

Refuted if the robot finds the plate in the cupboard at 20:00 on a weekday (no dinner at the table) or finds the pan still on the counter at 22:00 (no cleanup happened).

```json
{
 "claims": [
  {
   "claim": "Yuki's plate is at the dining table during the 20:00 meal on weekdays",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Yuki's glass is at the dining table during the 20:00 meal on weekdays",
   "target": "glass_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The pan is on the counter during active cooking at 18:30 on weekdays",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The cutting board is on the counter during dinner prep at 18:30 on weekdays",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "The pan is at the sink (washed) by 21:00 on weekdays, not still on the counter",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 20.5,
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
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
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
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 18.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "pan_shared": [
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
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
