# p_6f1c — Yuki's glass: dining table at dinner, nightstand at bedtime

Yuki's glass follows a clean two-phase arc on weekday evenings. It leaves the cupboard (or counter) around 18:30, sits at the dining table through dinner (19:00–20:00 passes show it at dining_table_d1: 1 sighting at 19:00, 3 at 20:00), and then is carried to the bedroom nightstand for the evening (22:00–23:00 passes show it at nightstand_b1: 3 sightings at each hour). The glass is not at the coffee table during the TV phase; it goes straight from dinner to the bedroom. This is consistent with the 21:00 desk-session pattern: she finishes dinner, carries her glass to the bedroom, and does not bring it back to the living room.

What sets this apart: p_9c82 and p_c2f9 place glass_yuki at the nightstand at 22:00 (matching), but they do not specify the dining-table phase at 19:00–20:00. p_f1a6 places the glass at the nightstand at 22:00 but does not account for the dinner phase. This document explicitly covers both phases and predicts the glass is at the dining table (not the coffee table, not the nightstand) at 19:30. If the robot finds the glass at the coffee table at 19:30, or at the nightstand at 19:30, this document is wrong.

What would refute it: the glass consistently at the coffee table during the 19:00–20:00 window, or at the dish rack at 22:00 rather than the nightstand.

```json
{
 "claims": [
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
   "claim": "Yuki's plate is at the dining table at 19:30 on a weekday (dinner phase)",
   "target": "plate_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  }
 ],
 "targets": {
  "glass_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0.5,
    "to": 6,
    "at": "sink_k1",
    "chance": "sometimes"
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
    "from": 21.5,
    "to": 23.5,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "plate_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
