# p_8c3d — The 20:00 Coffee Table; Snack Bowl, Remote, and Blanket Converge for Evening TV

The evening TV window (roughly 19:30–22:00) is when three objects converge on the coffee table. The snack bowl, which rests on the kitchen counter through the day (three weekday 03:00 sightings at counter_k1), is carried to the coffee table around 19:30–20:00 for the evening snack session (two sightings at coffee_table_l1 at 20:00, one at 21:00). The remote, which spends most of the day on the tv_stand (five of seven sighted days), is picked up for TV and set down on the coffee table or the floor beside the couch. The blanket, which lives on the couch through the weekday afternoon (sightings at couch_l1 at 07:00, 16:00, 17:00, 19:00), is pulled onto the coffee table or the armchair for the TV session.

By 22:00 the snack bowl is washed and put away (one sighting at sink_k1), and by 23:00 it is back on the counter (three sightings). The remote returns to the tv_stand. The blanket settles back on the couch.

This document differs from p_7b2e, which places the snack bowl on the coffee table from 19:00 to 22:00 and accumulates "against" votes (4 for, 11 against) because the bowl is still on the counter at the 19:00 pass on many evenings. Here the coffee-table window starts at 19.5, after the 19:00 pass. It also differs from p_a1b2, which places the remote on the coffee table at 23:00–24:00; the evidence shows the remote back on the tv_stand by then.

The document would be refuted if the snack bowl is consistently on the counter at the 20:00 pass (meaning the TV snack session does not happen or happens at a different hour), or if the remote is found on the coffee table at the 03:00 pass (meaning it is not returned to the tv_stand).

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the coffee table during the 20:00\u201321:00 weekday TV window",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 21
  },
  {
   "claim": "The snack bowl is back on the kitchen counter at the 23:00 weekday pass",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "The remote is on the tv_stand at the 03:00 pass",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 0,
   "to": 3
  },
  {
   "claim": "The blanket is on the couch at the 16:00 weekday pass",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 16,
   "to": 17
  }
 ],
 "targets": {
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19.5,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19.5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
