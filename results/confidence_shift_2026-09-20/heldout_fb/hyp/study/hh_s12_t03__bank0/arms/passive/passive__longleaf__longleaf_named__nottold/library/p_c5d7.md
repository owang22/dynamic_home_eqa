# p_c5d7 — Priya's glasses: nightstand by day, coffee table by evening, never worn

The ON_PERSON block for glasses_priya in p_a1b2 and p_4c7d has failed (0.13 on 3 sightings). The hourly passes show a clear pattern: the glasses rest on the nightstand overnight and through the morning (03:00 ×3), go to the bathroom shelf at 07:00 during her shower routine (×1 weekday, ×2 weekend), return to the nightstand by 08:00, then move to the coffee table in the afternoon (15:00 ×1, 16:00 ×1) and stay there through the evening (21:00 ×1, 22:00 ×1). At 18:00 they are briefly back on the nightstand (×1) before moving to the coffee table again at 20:00. At 23:00 they return to the nightstand for bed.

What sets this apart: Priya never wears her glasses during the day. She sets them on the coffee table when she sits down to read or watch TV in the afternoon and evening. A document that predicts ON_PERSON between 7 and 22 will be contradicted by every pass showing them on the nightstand or coffee table.

Refutation: if glasses_priya is sighted ON_PERSON at any hour on a weekday or weekend, or if they are on the coffee table at 07:00 (before the afternoon).

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are on the nightstand at 03:00 on a weekday",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Priya's glasses are on the coffee table at 16:00 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Priya's glasses are on the nightstand at 23:00 on a weekday",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
  },
  {
   "claim": "Priya's glasses are on the bathroom shelf at 07:00 on a weekend",
   "target": "glasses_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 6.5,
   "to": 7.5
  }
 ],
 "targets": {
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 15,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
