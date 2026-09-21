# p_a4f7 — The 19:00 cook: pan hits the counter, snacks stay in the kitchen, remote never leaves the TV stand

Marco commutes to his office 8:00–17:30 on weekdays; Omar works from the office desk 9:00–17:30, sometimes stepping out for lunch. The evening follows a tight sequence that the earlier "evening ritual" documents got the timing on wrong. Cooking does not start at 17:50. The pan is still in the cupboard at the 18:00 patrol pass on weekdays (confirmed 1/1) and only appears on the counter at the 19:00 pass (2/2). On weekends the pan is already on the counter at 18:00 (3/3) and 19:00 (4/4), so weekend cooking starts about an hour earlier, around 17:30. The snack bowl mirrors the pan: it is in the cupboard at 03:00, on the counter at 18:00 (2 sightings) and 20:00 (3 sightings) on weekdays — it never migrates to the coffee table. The remote sits on the TV stand at 03:00 on all six sighted days and has never been seen on the coffee table in any evening pass; the eight "against" hits on coffee-table-remote claims confirm this. The guitar rests on the bedroom floor through the day (03:00, 18:00 passes) but is on the couch at the 21:00 pass, indicating Marco picks it up for a short evening session once dinner is done.

What sets this document apart: the cooking window is 18:30–20:00 on weekdays (not 17:50–19:00), the snack bowl stays on the kitchen counter all evening (not the coffee table), the remote stays on the TV stand (not the coffee table), and the guitar is on the couch at 21:00 (not the bedroom floor). A sighting of the pan in the cupboard at 19:00 on a weekday, or the snack bowl on the coffee table during 18:00–21:00, or the remote on the coffee table during 20:00–22:00, would refute this document.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter at 19:00 on a weekday (cooking in progress)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.75,
   "to": 19.25
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 20:00 during evening TV (not the coffee table)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19.5,
   "to": 20.5
  },
  {
   "claim": "The remote is on the TV stand at 21:00 during evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20.5,
   "to": 21.5
  },
  {
   "claim": "Marco's guitar is on the couch at 21:30 during his evening playing session",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "both",
   "from": 21,
   "to": 22
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22.5,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
