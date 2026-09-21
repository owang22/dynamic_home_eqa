# p_9b7c — The 21:00 ironing session: bed_b2 becomes a workshop on weekday evenings and weekend afternoons

The iron and ironing board live in storage (iron on storage_shelf_s1, board on storage_floor_s1) for most of the day. On weekday evenings, both migrate to bed_b2 around 20:30–21:00 for an ironing session that lasts until about 23:00. The sightings confirm this: at 20:00 the iron is still at storage_shelf_s1, but by 21:00 it is at bed_b2 (3 of 3 passes), and the ironing board follows (2 of 2 passes at 21:00). On weekends the pattern shifts earlier: the ironing board is at bed_b2 at 15:00 (1 pass) and 18:00 (1 pass), while the iron is at bed_b2 at 15:00 (1 of 2 passes). This is a weekend chore block in the mid-afternoon. The mixture's worst-objects list confirms the ironing board was predicted at storage_floor_s1 but found at bed_b2 twice on day 4 (Saturday 15:00).

This document is distinct from p_b7c4 (which also places ironing at bed_b2 but frames it as a weekday-only 21:00 session) by adding the weekend afternoon block. It is refuted if the iron and board are found at bed_b2 during the 9:00–17:00 window on multiple days, or if they remain in storage through 23:00 on weekdays.

```json
{
 "claims": [
  {
   "claim": "The iron is at bed_b2 during the weekday evening ironing session",
   "target": "iron_shared",
   "expect": "bed_b2",
   "days": "weekday",
   "from": 20.5,
   "to": 23
  },
  {
   "claim": "The ironing board is at bed_b2 during the weekend afternoon ironing",
   "target": "ironing_board_shared",
   "expect": "bed_b2",
   "days": "weekend",
   "from": 14.5,
   "to": 19
  },
  {
   "claim": "The iron is in storage at 09:00 (not yet in use)",
   "target": "iron_shared",
   "expect": "storage_shelf_s1",
   "days": "both",
   "from": 9,
   "to": 10
  },
  {
   "claim": "The ironing board is in storage at 09:00 (not yet in use)",
   "target": "ironing_board_shared",
   "expect": "storage_floor_s1",
   "days": "both",
   "from": 9,
   "to": 10
  }
 ],
 "targets": {
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14.5,
    "to": 19,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14.5,
    "to": 19,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ]
 }
}
```
