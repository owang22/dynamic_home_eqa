# p_d3f7 — The 15:00 and 18:00 Vacuum: Two Cleaning Windows on the Living Room Floor

This document models the vacuum cleaner's two active windows, which p_8f4c partially covers but with a different emphasis. The evidence: vacuum_cleaner_shared is at storage_floor_s1 at 03:00 (×3), 09:00 (×2), 10:00 (×2), and 14:00 (×1); it is at floor_l_l1 at 10:00 (×1), 15:00 (×1), and 18:00 (×2). The 18:00 floor sightings (×2) are the key new data point: the vacuum is out on the living room floor at 18:00 on 2 of 4 sighted days, while it is back in storage at 18:00 on the other 2 days. This suggests an *evening* cleaning window (17:00–19:00) that is not consistent every day but happens frequently enough to matter.

The pattern: the vacuum rests in storage from 03:00 through 14:00. A mid-afternoon cleaning happens at 14:30–16:00 (the 15:00 floor sighting). An evening cleaning happens at 17:00–19:00 (the 18:00 floor sightings). By 19:00 the vacuum is back in storage. The 10:00 floor sighting (×1) is an outlier, perhaps a quick spot-clean on a particular day.

What sets this apart: it is the only document that models *two* distinct cleaning windows (15:00 and 18:00) rather than a single mid-afternoon one. It differs from p_8f4c which places the vacuum on the floor at 15:00 but in storage at 18:00; here the 18:00 floor is an expected state (sometimes). It differs from the statistical model which would place the vacuum in storage at 18:00 (its most common location).

Refutation: vacuum_cleaner_shared at storage_floor_s1 at 15:00 on a weekday (no mid-afternoon cleaning), or at floor_l_l1 at 10:00 on multiple weekdays (the morning is also a cleaning window, not just an outlier).

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 15:00 on a weekday (mid-afternoon cleaning)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 14.5,
   "to": 16
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 18:00 on a weekday (evening cleaning)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The vacuum cleaner is in storage at 09:00 on a weekday (not yet in use)",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 8,
   "to": 14
  },
  {
   "claim": "The duster is on the storage shelf at 15:00 on a weekday (cleaning supplies are out)",
   "target": "duster_shared",
   "expect": "storage_shelf_s1",
   "days": "weekday",
   "from": 14,
   "to": 16
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "duster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "watering_can_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "almost_always"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ]
 }
}
```
