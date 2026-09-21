# p_9c2b — Omar's tablet is locked at the nightstand 9–17h; the early morning is a toss-up

The per-object evidence is unambiguous for the midday window: four looks at the bedroom nightstand during weekday 9–17h found the tablet every single time (4 found, 0 empty). But the early morning is not so clean. The 08:00 patrol finds the tablet at the nightstand 2 out of 3 times, at the kitchen chair 1 out of 3, and occasionally at the dresser. The 00:00 patrol shows the same three-way split. This means the "tablet at the nightstand all day" claim (p_a7f3, 7–9h window) is too strong: it has now accumulated 4 against in that window. On weekends the tablet is at the nightstand most of the day but the Sunday 16:00 patrol caught it at the dresser, so the afternoon confidence drops.

What sets this apart: p_a7f3 and p_f3a7 claim the nightstand for the full 7–9h or 14–18h window with high confidence. This document narrows the "almost_always" label to 9–17h (where the data is 4/4) and uses "sometimes" for 6–9h, acknowledging the chair_k1 and dresser_b1 alternatives. It also adds a weekend afternoon block at "sometimes" to account for the dresser sightings.

Refutation: if the tablet is found at the nightstand at 07:00 or 08:00 on 3+ consecutive weekday mornings, the "sometimes" label for 6–9h should be upgraded and this document's distinction from p_a7f3 collapses.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 12:00 on a weekday, in its reliable midday position",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand at 16:00 on a weekday, still in its daytime resting spot",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand on a weekend morning before he leaves for errands",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 6,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
