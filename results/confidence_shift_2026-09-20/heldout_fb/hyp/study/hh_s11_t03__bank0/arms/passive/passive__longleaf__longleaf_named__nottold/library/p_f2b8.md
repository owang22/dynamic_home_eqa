# p_f2b8 — Priya's Evening Glass: Dining Table, Counter, Nightstand

Priya's glass follows a clear three-step evening path on weekdays. At 19:00 it is at the dining table for dinner (2 sightings). By 21:00 it has moved to the kitchen counter for a late snack (1 sighting). By 22:00 it is on her nightstand, ready for bed (6 sightings — the strongest single-hour signal for this glass). On weekends the pattern compresses: the glass appears at the kitchen table at 12:00 (lunch) and is on the nightstand by 22:00.

This hypothesis predicts the three-step migration on weekdays: dining_table_d1 → counter_k1 → nightstand_b2, each in its own hour window. The plate follows a parallel path: dining_table_d1 at 19:00, then sink_k1 by 21:00. What would refute it: a weekday 22:00 pass that finds the glass still at the counter or dining table, or a 19:00 pass that finds it already on the nightstand.

```json
{
 "claims": [
  {
   "claim": "Priya's glass is at the dining table during her weekday evening meal",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Priya's glass is on her nightstand by 22:00 on weekdays",
   "target": "glass_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Priya's plate is at the kitchen sink after dinner is over",
   "target": "plate_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 21,
   "to": 22
  }
 ],
 "targets": {
  "glass_priya": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ]
 }
}
```
