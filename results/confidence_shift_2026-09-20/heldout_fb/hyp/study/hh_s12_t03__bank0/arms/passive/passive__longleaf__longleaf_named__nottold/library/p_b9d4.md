# p_b9d4 — Priya's midday vacuum: living room 11:30 to 13:30

Elena is at work; Priya handles the midday chore of vacuuming the living room. The robot has seen the vacuum on the living room floor three times at 12:00 on weekdays (alongside two sightings at the entry floor at the same hour), and once each at 16:00 and 17:00 on the living room floor. This document places the vacuum in the living room during a midday window (11:30–13:30) on weekdays, when Priya is home and Elena is not. The vacuum rests at the entry floor the rest of the time. This differs from p_8c3f, which only covers 16–17h, and from the plain statistical model that predicts entry_floor_e1 at 12:00. If the vacuum is found at the entry floor at 12:00 on a weekday, this document is weakened; if it is never seen in the living room during 11–14h, it is refuted.

The late-afternoon sightings (16:00, 17:00) suggest a second, shorter vacuum pass or that the midday session runs long on some days. This document keeps the primary window at midday and allows a secondary late-afternoon appearance.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 12:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "The vacuum cleaner is back at the entry floor at 15:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 14,
   "to": 15.5
  },
  {
   "claim": "The dog bowl is on the kitchen floor at 12:00 on a weekday",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 11,
   "to": 13
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 13.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15.5,
    "to": 17.5,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
