# p_a3c7 — Omar's glasses: nightstand on weekdays, desk on weekends, bathroom shelf at 09:00

Omar's reading glasses follow a clear two-track pattern that differs sharply between weekdays and weekends. On weekdays, the glasses sleep at the bedroom nightstand (03:00 sightings: nightstand 3×, desk 1×). In the early morning they remain at the nightstand (08:00: nightstand 1×), but by 09:00 they split three ways: bathroom shelf (3×), nightstand (2×), and bedroom desk (2×). This 09:00 scatter reflects Omar's morning grooming (shaving, skincare) at the bathroom shelf, followed by a brief desk session before his 13:40 departure. Once he leaves for his afternoon-to-night shift, the glasses settle back at the nightstand (18:00: nightstand 1×; 23:00: nightstand 1×). On weekends the pattern inverts: the glasses sleep at the bedroom desk (03:00: desk 2×), reflecting an evening desk-work session the prior night. Weekend mornings show them at the bathroom shelf (09:00: 2×) or desk (1×), and by 23:00 they're back at the desk (2×).

This hypothesis is distinguished by the weekday/weekend inversion (nightstand vs. desk overnight) and the 09:00 bathroom-shelf peak. It would be refuted if the glasses were consistently at the desk on weekday mornings or at the nightstand on weekend overnight passes.

```json
{
 "claims": [
  {
   "claim": "Omar's glasses are at the bedroom nightstand at 04:00 on a weekday (overnight resting spot)",
   "target": "glasses_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 3,
   "to": 7
  },
  {
   "claim": "Omar's glasses are at the bathroom shelf at 09:30 on a weekday (morning grooming)",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 9,
   "to": 10
  },
  {
   "claim": "Omar's glasses are at the bedroom desk at 04:00 on a weekend (left after evening desk work)",
   "target": "glasses_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 3,
   "to": 6
  }
 ],
 "targets": {
  "glasses_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
