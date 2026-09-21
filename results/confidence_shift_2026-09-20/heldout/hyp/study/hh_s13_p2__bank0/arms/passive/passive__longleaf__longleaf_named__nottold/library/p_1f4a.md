# p_1f4a — The Floor Remote: It Drops on the Living Room Floor 20 Percent of the Time

The mixture's worst-objects list shows remote_shared predicted at tv_stand_l1 but actually at floor_l_l1 seven times on day 7 alone. The clock-hour data confirms this is not a one-off: on every weekday pass from 00:00 to 16:00 the remote is tv_stand_l1 ×4 and floor_l_l1 ×1 — a consistent 80/20 split. At 18:00 and 20:00 it is tv_stand_l1 ×5 (TV time, remote in hand then set back). At 22:00 it shifts: tv_stand_l1 ×3, coffee_table_l1 ×2. On weekends the remote is coffee_table_l1 ×1 and tv_stand_l1 ×1 at every pass — a 50/50 split, with a late-night drift to armchair_l1.

What sets this apart: at 10:00 on a weekday, remote_shared has a meaningful chance of being at floor_l_l1 (not just tv_stand_l1); at 12:00 on a Saturday, remote_shared is equally likely at coffee_table_l1 or tv_stand_l1 (not "usually at tv_stand"). What would refute it: remote at tv_stand_l1 at 10:00 on a weekday five times in a row with zero floor sightings, or remote at tv_stand_l1 exclusively on a weekend.

```json
{
 "claims": [
  {
   "claim": "The remote is on the living room floor at 10:00 on a weekday",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The remote is on the coffee table at 12:00 on a Saturday",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 14
  },
  {
   "claim": "The remote is on the TV stand at 20:00 on a weekday",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The remote is on the coffee table at 22:00 on a weekday",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
