# p_c8f3 — The weekday 22:00 coffee table: blanket, mug, remote, and snack bowl converge

On weekday evenings, after Yuki's 19:00 dinner and Omar's 23:00 return, the living room becomes the evening anchor. Around 21:00 the blanket slides from the couch to the coffee table, Yuki's mug appears there (from the cupboard or her desk), the remote migrates from the TV stand to the coffee table by 22:00, and the snack bowl is pulled out. This is the "TV hour" setup. Omar, if home by then (he arrives at 23:00), joins at the coffee table or the couch. The setup is transient: by 23:30 the mug and snack bowl may be cleared, but the blanket and remote linger.

What sets this apart: p_9f4a and p_6e7d cover the weekend version; p_f1a6 and p_a3f7 (both retired) attempted the weekday version. This document focuses specifically on the weekday 21:00–23:00 window and the convergence of four items at the coffee table. The sightings (blanket at coffee_table 21:00 ×3, 22:00 ×4; mug_yuki at coffee_table 21:00 ×3, 22:00 ×2, 23:00 ×1; remote at coffee_table 22:00 ×1, 23:00 ×3; snack_bowl at coffee_table 22:00 ×2, 23:00 ×2) are the core support.

What would refute it: if the blanket stays on the couch through 22:00–23:00 on weekdays, or if the mug is not at the coffee table during this window (stays at the desk or cupboard), this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the coffee table at 22:00 on a weekday (TV hour)",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Yuki's mug is on the coffee table at 22:00 on a weekday (evening drink while watching TV)",
   "target": "mug_yuki",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The remote is on the coffee table at 23:00 on a weekday (migrated from the TV stand for the evening)",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "The blanket is on the couch at 09:00 on a weekday (resting spot during the day)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 21,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "mug_yuki": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 22,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
