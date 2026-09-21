# p_1a4c — Weekday 21:00 TV migration; the remote stays on the TV stand on weekends

On weekdays the evening TV ritual triggers a migration of the remote and the blanket from the TV stand and couch to the coffee table around 20:30–21:00. The speaker is already on the couch and stays there. On weekends, however, the remote remains on the TV stand through the evening (weekend 21:00 tv_stand ×1), and the blanket splits between the couch and the bed rather than settling on the coffee table. This document separates the two day-of-week patterns that the "both" day claims in p_6d3b, p_8a3e, and p_c4f8 conflate, and which have been scoring against on weekend sightings (remote on coffee table "both" days: against 3 since the last call).

The speaker is on the couch in both weekday and weekend evenings (couch_l1 at 21:00 weekdays ×3, 22:00 weekends ×2), so it does not distinguish the two patterns. The remote is the sharpest tell: weekday 21:00 coffee_table ×2, 22:00 coffee_table ×3; weekend 21:00 tv_stand ×1. The blanket follows the remote on weekdays (coffee_table 21:00 ×3, 22:00 ×1, 23:00 ×3) but on weekends splits between coffee_table (×1) and couch (×1) at 21:00, and drifts to the bed during the morning (03:00 bed ×1, 12:00 bed ×1, 15:00 bed ×1).

This document would be refuted if the remote is found on the coffee table on a weekend evening, or if the blanket is consistently on the coffee table (rather than the couch or bed) on weekend evenings.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table during weekday evening TV",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The remote is on the TV stand during weekend evening TV",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table during weekday evening TV",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The blanket is on the couch during weekend evening TV",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
