# p_a4c7 — Kitchen cookware rests in the cupboard, not at the sink or pantry shelf

Yuki and Omar share a small kitchen. The pan and the pot are stored in the kitchen cupboard (cupboard_k1) between uses. This is the dominant resting position: the pan is found at the cupboard on 10 of 14 weekday patrol passes, and the pot on 12 of 14. The sink and pantry shelf are secondary spots where a single pass might catch them mid-transition, but they are not the home position.

This hypothesis sets itself apart from p_8c2d (which places the pan at the sink during the day) and p_5d9e (which places the pan at the sink and the pot on the pantry shelf). Those documents have been penalised: their "pan at sink 9–17 h" and "pot at pantry shelf 9–17 h" blocks failed on 10 sightings each, and the per-object evidence confirms the cupboard is where the robot actually finds these items when it looks.

The pan and pot come out to the counter only during active cooking (roughly 18:00–20:00 on weekdays, when Yuki prepares dinner). Outside that window they are put back in the cupboard. On weekends, with both residents home, the cupboard is still the resting spot; the drawer_k_k1 appears on weekend 00:00 and 08:00 passes for the pan, suggesting a weekend re-shelving habit, but the cupboard remains the primary location.

What would refute this document: if the robot repeatedly finds the pan at the sink or the pot on the pantry shelf during the 9–17 h weekday window (more than one in four looks), the cupboard-resting hypothesis is wrong and the objects genuinely live at those secondary spots.

```json
{
 "claims": [
  {
   "claim": "The pan is in the kitchen cupboard at 14:00 on a weekday because no one is cooking",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 13,
   "to": 16
  },
  {
   "claim": "The pot is in the kitchen cupboard at 14:00 on a weekday because it has not been taken out",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 13,
   "to": 16
  },
  {
   "claim": "The pan is in the kitchen cupboard at 10:00 on a Saturday morning before any cooking",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 8,
   "to": 12
  },
  {
   "claim": "The pot is in the kitchen cupboard at 10:00 on a Saturday morning",
   "target": "pot_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 8,
   "to": 12
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
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
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
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
