# p_a3f7 — Yuki's dinner prep starts at 19:00, not 18:00

Yuki arrives home at 17:30 after a full day at the office. She does not walk straight into the kitchen and start chopping. The first hour after she gets home is for decompressing: a cup of tea, a quick shower, maybe ten minutes of journaling at the bedroom desk. The kitchen stays quiet from 17:30 to 19:00. At 19:00 she pulls the pan from the cupboard, the cutting board is already at its resting spot on the counter, and she begins actual dinner preparation for roughly an hour. Plates and glasses go to the dining table around 19:30. She eats alone; Omar is at his night shift until 23:00.

This document directly challenges the 18:00–19:30 cooking window used by p_c007 and p_a1b2. The evidence is unambiguous: the pan claim at the counter during 18–19.5 h has been scored against 9 times, and the cutting board against 7. The pan's resting spot is the cupboard, so "against" most likely means the pan was still in the cupboard — no cooking had started. Yuki simply needs an hour to settle in before she cooks. What would refute this document: a sighting of the pan at the counter before 18:55 on a weekday, or plates at the dining table before 19:00.

```json
{
 "claims": [
  {
   "claim": "The pan is still in the cupboard at 18:30 on a weekday because Yuki has not started cooking yet",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The pan is on the counter at 19:30 on a weekday while Yuki cooks dinner",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Yuki's plate is set at the dining table at 20:00 on a weekday for her solo dinner",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 20.5
  },
  {
   "claim": "The cutting board is at the counter at 19:30 on a weekday in use for dinner prep",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
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
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
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
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "almost_always"
   }
  ],
  "plate_omar": [
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
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "glass_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ]
 }
}
```
