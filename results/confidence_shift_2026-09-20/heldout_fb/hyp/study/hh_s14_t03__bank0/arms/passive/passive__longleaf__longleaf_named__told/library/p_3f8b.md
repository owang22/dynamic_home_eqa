# p_3f8b — Yuki's Morning Tablet and Midday Return: Kitchen Table 07:30–09:00, Nightstand After

Yuki's tablet follows a clear morning pattern. It is at the kitchen table at 08:00 (sighted there on a weekday), then back at the nightstand by 11:00 (sighted at both nightstand and counter on the same 11:00 pass—the counter sighting may be a brief mid-morning use). At 03:00 and 18:00 it is at the nightstand. The tablet is her morning reading companion: she takes it from the nightstand to the kitchen table around 07:30 for breakfast reading, uses it until about 09:00, then returns it to the nightstand. The 11:00 counter sighting suggests a brief second use (checking a recipe before baking, perhaps).

This document is narrower than p_2d9c, which also covers the dog bowl and Marco's glasses. Here the focus is solely on the tablet's morning trajectory and its interaction with the midday baking window (the 11:00 counter sighting may be Yuki looking up a recipe).

What sets this apart: at 08:00 on a weekday, tablet_yuki is at kitchen_table_k1, and at 11:00 it is at nightstand_b1 (or briefly at counter_k1). If the robot finds the tablet at the nightstand at 08:00 or at the kitchen table at 11:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Yuki's tablet is at the kitchen table during her 08:00 morning reading",
   "target": "tablet_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9
  },
  {
   "claim": "Yuki's tablet is at the nightstand at 11:00 on a weekday",
   "target": "tablet_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 10.5,
   "to": 12
  },
  {
   "claim": "Yuki's tablet is at the nightstand at 03:00",
   "target": "tablet_yuki",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Yuki's tablet is at the nightstand at 18:00 on a weekday",
   "target": "tablet_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 17,
   "to": 19.5
  }
 ],
 "targets": {
  "tablet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 11.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
