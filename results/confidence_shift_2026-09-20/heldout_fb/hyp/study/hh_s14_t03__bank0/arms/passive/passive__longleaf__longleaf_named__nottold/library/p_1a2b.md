# p_1a2b — Weekend Blanket on the Bed, Weekday Blanket on the Couch

Marco and Yuki share a household with a dog. The shared blanket follows a clear day-type split that the statistical model misses. On weekdays the blanket rests on the living room couch through the overnight pass (03:00, three sightings), the morning (08:00), and the evening (18:00); it briefly migrates to the coffee table around 10:00 and 13:00, likely while Yuki watches TV or reads with it draped over her lap. On weekends the blanket lives on the bed: the overnight pass (03:00), the morning (08:00), the evening (19:00), and bedtime (23:00) all show bed_b1. This makes sense: on weekends both residents are home all day and sleep in the shared bed, so the blanket stays with them there. On weekdays Marco's late shift (home 23:00–~13:40) means the couple may not share the bed in the evening, and the blanket defaults to the couch where Yuki spends her hours. A single weekend 11:00 sighting at the bathroom shelf suggests a brief laundering trip.

This document sets itself apart by predicting bed_b1 on weekends and couch_l1 on weekdays, where the mixture and most existing documents default to the couch regardless of day type. The mixture's worst-objects list flags "blanket_shared: predicted couch_l1, actually bed_b1 — 3×" since the last call, all on weekend overnight passes.

What would refute this: if the blanket is consistently on the couch at 08:00 on a weekend, or on the bed at 08:00 on a weekday, the day-type split collapses.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the bed at 08:00 on a weekend",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 7,
   "to": 9
  },
  {
   "claim": "The blanket is on the couch at 08:00 on a weekday",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "The blanket is on the coffee table at 12:00 on a weekday",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 11,
   "to": 14
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
