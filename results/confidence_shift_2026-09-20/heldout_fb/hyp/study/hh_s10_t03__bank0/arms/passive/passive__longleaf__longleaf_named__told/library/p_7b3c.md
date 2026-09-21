# p_7b3c — Vacuum cleaner: entry floor all day, living room floor 18-to-19.5h

The vacuum cleaner is stored at the entry floor for the entire day. It is sighted at the entry floor at 03:00, 08:00, 09:00, 11:00, 12:00, and 14:00 — a consistent resting spot by the door. On weekday evenings, around 18:00–19:30, Yuki (who is home) pulls it out and vacuums the living room. The vacuum appears on the living room floor at 18:00 and 19:00 in the sightings. By 20:00 it is back at the entry floor. On weekends the timing may shift or the vacuuming may not happen at all.

This document is distinguished by its prediction that the vacuum is at the entry floor at 08:00, 12:00, and 14:00 (all-day resting), AND on the living room floor at 19:00 (being used). The 18:00 sighting shows it at BOTH the entry floor (x4) and the living room floor (x1), suggesting the transition happens right around 18:00. The document places the "being used" window at 18:00–19:50.

Refuted if: the vacuum is at the entry floor at 19:00 (not being used); at the living room floor at 12:00 (used midday, wrong time); at a different receptacle entirely.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is at the entry floor at 08:00 on a weekday (all-day resting spot)",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 7,
   "to": 14
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 19:00 on a weekday (being used)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The vacuum cleaner is back at the entry floor at 20:30 on a weekday (vacuuming done)",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 20,
   "to": 23
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19.5,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:toiletry_bag": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
