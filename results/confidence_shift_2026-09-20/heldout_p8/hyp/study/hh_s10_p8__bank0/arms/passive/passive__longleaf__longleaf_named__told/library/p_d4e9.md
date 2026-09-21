# p_d4e9 — Omar's night-shift cycle: home 23:00 to 13:40, night gaming, late breakfast

Omar's day is inverted. He comes home at 23:00 after his afternoon-to-night shift and is active until roughly 01:00: he games (controller at the TV stand), watches TV, or listens to music. He sleeps from 01:00 to about 12:30. He wakes, has a late breakfast around 12:30–13:15 at the kitchen table — his mug, bowl, and tablet are all there — and leaves for work at 13:40. His tablet stays at the kitchen chair throughout his waking morning, a fact already confirmed by sightings (for 1 in both p_4e91 and p_7a3f).

On weekdays Omar does not cycle to work. His helmet stays at the entry hook or gets moved to the bedroom at night. The p_a1b2 claim that the helmet is out of the house during 14–22 h has been scored against 1 (it was in the house) and weak-for 6 (not at the entry hook, probably in the bedroom). On weekends he does cycle, and the helmet and bike lock go out during a Saturday-morning ride.

This document complements p_e5f6 (which covers Omar's 10:00–13:00 morning gaming block) by adding the 23:00–01:00 night gaming block and the late-breakfast routine. What would refute it: the controller found at the TV stand before 22:30 on a weekday, the tablet found anywhere other than the kitchen chair during 7–13 h, or the helmet found out of the house on a weekday between 14 and 22 h.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the kitchen chair at 10:00 on a weekday, his morning workspace",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 7,
   "to": 13
  },
  {
   "claim": "Omar's controller is at the TV stand at 23:30 on a weekday during his post-shift gaming",
   "target": "controller_omar",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Omar's helmet is at the entry hook at 9:00 on a weekday because he drives to work, not cycles",
   "target": "helmet_omar",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 7,
   "to": 13
  },
  {
   "claim": "Omar's mug is at the kitchen table at 13:00 on a weekday during his late breakfast",
   "target": "mug_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 12.5,
   "to": 13.5
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 7,
    "to": 13,
    "at": "chair_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "chair_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "chair_k1",
    "chance": "sometimes"
   }
  ],
  "controller_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 13,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   }
  ],
  "helmet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 23,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ],
  "bowl_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
