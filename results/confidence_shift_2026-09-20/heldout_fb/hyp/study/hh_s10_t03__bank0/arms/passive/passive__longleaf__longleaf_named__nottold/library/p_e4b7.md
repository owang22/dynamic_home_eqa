# p_e4b7 — Omar's tablet sleeps at the nightstand, not the kitchen chair

Omar's tablet does not rest at the kitchen chair overnight. The 03:00 passes show it at the bedroom nightstand two out of three times, with a single sighting at the kitchen chair. By 09:00 it is still at the nightstand (2×) or has just moved to the kitchen table (1×). By 10:00 it is firmly at the kitchen table (2×), where Omar scrolls through music and messages over his morning coffee and vitamins before his 1:40 shift. By 18:00 it is back at the kitchen chair, where it sits while he is at work until 23:00. The kitchen chair is its daytime resting spot, but the nightstand is where it charges overnight — the p_3e8d claim of chair_k1 from 0–7 h collected four "against" tallies against one "for," confirming the error.

This document sets itself apart from p_3e8d (which puts the tablet at chair_k1 overnight) and from the plain statistical model (which, seeing 2/4 days at nightstand, still lags behind on the 03:00 pass). It agrees with p_3e8d on the mid-morning kitchen-table window and the 18:00 kitchen-chair spot.

What would refute it: a 03:00 or 04:00 pass that finds the tablet at the kitchen chair on two or more consecutive nights, or a 10:00 pass that finds it still at the nightstand rather than the kitchen table.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 03:00 on a weekday",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Omar's tablet is at the kitchen table at 10:00 on a weekday during his morning",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.5,
   "to": 12
  },
  {
   "claim": "Omar's tablet is at the kitchen chair at 18:00 on a weekday while he is at work",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 17,
   "to": 22
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 10,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   }
  ]
 }
}
```
