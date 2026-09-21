# p_8f4b — Priya's glasses: three in-home spots, never out of the house

Priya's reading glasses are a tri-location object that never leaves the house. At night (roughly 22:00 to 07:00) they rest on the nightstand. During the waking day they rotate among three spots: the nightstand (when she's in the bedroom or just after waking), desk_b1 (when she's reading or doing paperwork at the desk), and bedroom_floor_b1 (when she's in the bedroom and sets them down). The per-hour sightings confirm all three locations appear on the same day at different passes. Critically, they are NOT taken out during her afternoon errands — even when her keys and wallet leave the entry table, the glasses stay in the house.

This document differs from p_a3f7 and p_d6a1 (which pin the glasses at desk_b1 all midday) and from p_7890 and p_1e82 (which claim they go OUT_OF_HOUSE during errands). The evidence against those: 12 weekday 9-17h looks at nightstand_b1 found the glasses 5 times (they were at desk or floor the other 7), and no sighting ever places them outside the house.

This would be refuted if the glasses are ever sighted at OUT_OF_HOUSE, or if they are found consistently at only one of the three spots for an entire week.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are at the nightstand overnight",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 22,
   "to": 24
  },
  {
   "claim": "Priya's glasses are at the nightstand in the early morning before she gets up",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Priya's glasses are back at the nightstand by evening after the day's rotation",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Priya's glasses are in the house (at the nightstand) during weekday afternoon errands, not out",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 13,
   "to": 16
  }
 ],
 "targets": {
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 12,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 12,
    "to": 16,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16,
    "to": 22,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
