# p_b7e2 — helmet_yuki slides to the entry floor overnight and is re-hung in the morning

Yuki cycles to work on some weekday mornings. When she comes home in the evening she hangs her helmet on the entry hook, but by the time the robot patrols at 00:00 the helmet has often slipped or been set on the entry floor (entry_floor_e1). The patrol data confirm this: at 00:00 on weekdays the helmet is at the hook 3 times and on the floor 2 times (a 60/40 split), whereas by 08:00 and 16:00 the hook dominates 3-to-1. The "worst objects" section flags three instances where the mixture predicted the hook but the helmet was actually on the floor, most recently day 6 at 08:00.

This document differs from p_f3a7 and p_a7f3, which place helmet_yuki at entry_hook_e1 for the entire weekday afternoon (9–17 h) and have each lost two claim points since the last call. It also differs from p_7a3f, which sends the helmet out of the house on weekday mornings. The evidence does not support the helmet leaving the house on most weekday mornings (9–17 h looks at the hook found it 3 times, found nothing only 1), so the cycling-commute hypothesis for Yuki is weak.

The prediction: helmet_yuki is on the entry floor during the overnight and early-morning window (18:00–08:00) with "sometimes" probability, and back on the hook from 08:00 onward when Yuki (or Omar) re-hangs it. On weekends, when neither is cycling to work, the helmet stays on the hook or in the wardrobe.

What would refute this: if the robot finds helmet_yuki on the entry floor during the 09:00–16:00 weekday window more than once in four looks, the overnight-only floor hypothesis is too narrow and the helmet is simply a floor-dweller.

```json
{
 "claims": [
  {
   "claim": "Yuki's helmet is on the entry floor at 02:00 on a weekday because it slipped off the hook overnight",
   "target": "helmet_yuki",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Yuki's helmet is back on the entry hook at 10:00 on a weekday after being re-hung in the morning",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Yuki's helmet is on the entry hook at 10:00 on a Saturday because no one is cycling to work",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "helmet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
