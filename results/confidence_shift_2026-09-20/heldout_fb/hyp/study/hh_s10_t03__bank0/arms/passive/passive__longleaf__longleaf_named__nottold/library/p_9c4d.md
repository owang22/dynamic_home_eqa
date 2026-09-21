# p_9c4d — Vacuum cleaner: entry floor resting, living room floor during 18:00–19:30 weekday vacuuming

The vacuum cleaner rests at the entry floor for the vast majority of the day (4/4 at 03:00, 2/2 at 08:00, 1/1 at 09:00, 1/1 at 11:00, 1/1 at 12:00, 3/3 at 14:00 on weekdays). The exception is the 18:00–19:30 window on weekdays: at 18:00 it is at the entry floor (4/5) but also at the living room floor (1/5), and at 19:00 it is at the living room floor (1/1). This indicates a brief vacuuming session around 18:30–19:30 on weekdays, likely done by Yuki after she arrives home and before or during dinner prep. On weekends, the pattern is similar but earlier: at 10:00 the vacuum is at the living room floor (1/1), suggesting a weekend morning vacuum around 10:00–11:00.

This document is distinguished by the specific in-use window at floor_l_l1. It differs from p_f5a7 (retired, "living-room vacuuming, weekday 18:00–19:30") and p_5b81 (retired, "weekday evening vacuum: living room floor, 18:00 to 19:30") in that those were retired for other reasons; this one focuses narrowly on the vacuum's two locations and the narrow in-use window.

What would refute it: the vacuum at the living room floor at 14:00 on a weekday, or the vacuum at the entry floor at 19:00 on a weekday (it should be out in the living room).

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is at the entry floor at 14:00 on a weekday (not in use, resting)",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "The vacuum cleaner is at the living room floor at 19:00 on a weekday (being used for vacuuming)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The vacuum cleaner is at the living room floor at 10:00 on a weekend (weekend morning vacuuming)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 9.5,
   "to": 11
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 19.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9.5,
    "to": 11,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
