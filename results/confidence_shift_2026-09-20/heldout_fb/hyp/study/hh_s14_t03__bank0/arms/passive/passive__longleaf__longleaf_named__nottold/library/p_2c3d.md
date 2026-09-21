# p_2c3d — Marco's Glasses: Mobile, Not Pinned to the Nightstand

Marco's glasses are among the most mobile objects in the house. The statistical model and several existing documents pin them to the nightstand, but the per-object evidence shows "weekday 9-17h looks at nightstand_b1 found it 1, found nothing 2" — they are rarely there during waking hours. Instead, the glasses travel with Marco from room to room: at the coffee table when he's in the living room (10:00, 13:00 weekday; 22:00, 23:00 weekend), at the armchair when he's seated (13:00 weekday), on the bathroom shelf during his morning shower (09:00 weekday) and evening shower (23:00 weekday), and on the bookshelf in the evening (18:00, 23:00 weekday). Overnight they settle at the nightstand (03:00, both day types) or the bed. On weekends the pattern is simpler: nightstand at 03:00, coffee table in the evening (22:00, 23:00).

This document sets itself apart by predicting the coffee table during Marco's waking hours rather than the nightstand, and by acknowledging the bathroom-shelf windows during showers. The mixture's worst-objects list flags "glasses_marco: predicted nightstand_b1, actually coffee_table_l1 — 2×, e.g. day 5 22:00."

What would refute: if the glasses are found at the nightstand during the 10:00–16:00 window on multiple consecutive days, the mobile pattern breaks down.

```json
{
 "claims": [
  {
   "claim": "Marco's glasses are on the bathroom shelf during his weekday morning shower",
   "target": "glasses_marco",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Marco's glasses are at the coffee table at 13:00 on a weekday",
   "target": "glasses_marco",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Marco's glasses are at the nightstand at 03:00 on a weekday",
   "target": "glasses_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 2,
    "to": 6,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 9.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "bathroom_shelf_ba1",
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
