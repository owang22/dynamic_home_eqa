# p_d38a — p_8r2n — Marco's water bottle cycles desk to dish rack to sink to dinner table

Marco keeps his water bottle at his desk during the morning work session (roughly 8:00–11:00), where the robot can see it beside the laptop. After the morning block, the bottle is set down in the kitchen—specifically in the dish rack—where it sits for the rest of the workday. The patrol data confirms this: the bottle is at desk_b1 at 08:00, 09:00, 10:00, and 11:00 on weekdays, and at dish_rack_k1 at 18:00. The per-object statistics show dish_rack_k1 as the most common location (5/7 sighted days), and the one 9–17 h look at the dish rack that found the bottle (with zero empty looks) confirms it is there mid-day.

In the evening, the bottle moves to the kitchen sink around 19:00 (seen at sink_k1 at 19:00 on weekdays) and then to the dining table at 20:00 for dinner (seen at dining_table_d1 at 20:00, x2 on weekdays, and at 23:00 on weekends). On weekends the bottle is at the dish rack at 20:00 and at the desk at 20:00, with a final sighting at the dining table at 23:00.

This cycle—desk (morning) → dish rack (mid-day) → sink (pre-dinner) → dining table (dinner)—is the distinguishing feature of this document. It differs from documents that place the bottle at the desk all day (which are penalized by the empty 9–17 h looks at desk_b1) or that place it at the dining table for a long window (which are penalized by the 12 empty looks at dining_table_d1 during 19:30–21:00 in other documents).

What would refute this: if the bottle is consistently found at the desk during 12–16 h on multiple days, the "dish rack mid-day" block is wrong. If it is never seen at the sink or dining table in the evening, the later blocks fail.

```json
{
 "claims": [
  {
   "claim": "Marco's water bottle is at his desk during the morning work window",
   "target": "water_bottle_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 8,
   "to": 11
  },
  {
   "claim": "Marco's water bottle is in the dish rack area during the mid-day work gap",
   "target": "water_bottle_marco",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 12,
   "to": 17
  },
  {
   "claim": "Marco's water bottle is at the dining table during dinner",
   "target": "water_bottle_marco",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "Marco's water bottle is in the kitchen sink just before dinner",
   "target": "water_bottle_marco",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 18.5,
   "to": 20
  }
 ],
 "targets": {
  "water_bottle_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 11,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 18,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
