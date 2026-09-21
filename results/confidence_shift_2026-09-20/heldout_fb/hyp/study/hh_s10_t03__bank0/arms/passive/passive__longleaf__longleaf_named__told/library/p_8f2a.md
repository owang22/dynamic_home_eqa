# p_8f2a — Mug_yuki's daily arc: sink overnight, cupboard by day, coffee table for TV

Yuki's mug follows a clear three-zone daily path. Overnight (00:00–06:00) it sits in the kitchen sink, not washed before bed. In the early morning (06:00–08:00) it may be at the kitchen table while she has her first tea, or still in the sink. During the working day (08:00–20:30) it is stored in the kitchen cupboard — Yuki is at the office and the mug is put away clean. In the evening (20:30–24:00) it appears at the coffee table as her TV drink, staying there through the evening.

This document is set apart by the explicit cupboard placement during the day (08:00–20:30). Documents that predict the mug at the kitchen table or counter during the day will be contradicted by the 18:00 pass showing it in the cupboard. The overnight sink placement (00:00–06:00) is supported by the two 03:00 sightings at sink_k1.

What would refute it: the mug at the dining table during dinner (she uses a glass or water bottle instead); the mug in the sink at 21:00; the mug at the coffee table at 10:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's mug is at the coffee table at 21:30 on a weekday (her TV drink)",
   "target": "mug_yuki",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "Yuki's mug is in the kitchen cupboard at 14:00 on a weekday (stored during the day)",
   "target": "mug_yuki",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 10,
   "to": 18
  },
  {
   "claim": "Yuki's mug is in the kitchen sink at 03:00 on a weekday (overnight, not washed)",
   "target": "mug_yuki",
   "expect": "sink_k1",
   "days": "both",
   "from": 1,
   "to": 6
  },
  {
   "claim": "Yuki's mug is at the coffee table at 22:30 on a weekday (still her TV drink)",
   "target": "mug_yuki",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23.5
  }
 ],
 "targets": {
  "mug_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 20.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
