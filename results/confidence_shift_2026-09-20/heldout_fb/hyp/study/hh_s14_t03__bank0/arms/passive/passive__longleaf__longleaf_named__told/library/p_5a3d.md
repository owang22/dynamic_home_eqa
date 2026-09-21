# p_5a3d — Midday Baking: Tray and Bowl on Counter 10:00–12:00 Weekdays

The baking evidence contradicts the early-morning (06:30–08:30) window assumed by p_d1e6. The baking_tray_shared is sighted at counter_k1 at 11:00 (alongside pantry_shelf_k1 on the same pass), and the mixing_bowl_shared is at counter_k1 at 11:00. Both are back at the pantry shelf by 18:00. There is no sighting of either object at the counter during the 06:00–09:00 window. The baking session is a midday activity (10:00–12:00) on weekdays, likely Yuki's (she is home all day) or Marco's before his 13:40 departure.

This document sets the baking window to 10:00–12:00 on weekdays, not 06:30–08:30. The tray and bowl come out of the pantry, are used on the counter, and return to the pantry by 13:00. The spatula and knife follow the same midday pattern. On weekends, Yuki bakes in the afternoon (14:00–16:30) as previously assumed.

What sets this apart from p_d1e6: at 07:00 on a weekday, the baking tray is at pantry_shelf_k1 (not counter_k1), and at 11:00 it is at counter_k1 (not pantry_shelf_k1). If the robot finds the tray on the counter at 07:00 or in the pantry at 11:00 on a weekday, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The baking tray is on the kitchen counter at 11:00 on a weekday",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "The mixing bowl is on the kitchen counter at 11:00 on a weekday",
   "target": "mixing_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "The baking tray is on the pantry shelf at 07:00 on a weekday (not yet in use)",
   "target": "baking_tray_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 6,
   "to": 9
  },
  {
   "claim": "The mixing bowl is on the pantry shelf at 18:00 on a weekday (baking finished)",
   "target": "mixing_bowl_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 17,
   "to": 20
  }
 ],
 "targets": {
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
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
    "from": 10,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
