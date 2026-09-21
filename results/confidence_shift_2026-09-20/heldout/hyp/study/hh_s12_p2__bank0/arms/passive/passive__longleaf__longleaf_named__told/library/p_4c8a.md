# p_4c8a — Priya's glasses: bedroom rotation, never leave the house

Priya's reading glasses follow a tight daily rotation confined to the bedroom. Overnight and in the early morning (0–6 h) they rest on the nightstand, occasionally on the bed itself. Through the daytime (roughly 8–18 h) they drift to the bedroom floor or the small desk as Priya reads, works on guitar tabs, or does yoga; the nightstand still holds them half the time, but the floor and desk pick up the rest. By the evening (20 h onward) they are back on the nightstand and stay there through the night. The critical claim that separates this document from p_7890 and p_1e82 is that the glasses **never** go out of the house: they are not on Priya's person during her morning walk, and they are not in her bag during afternoon errands. The per-object evidence confirms this—there is no single sighting of glasses_priya at OUT_OF_HOUSE across all 69 recorded sightings.

What sets this apart: p_a3f7 places the glasses at desk_b1 during weekday midday (for 3, against 14); p_e7b3 moves them to nightstand_b1 (for 4, against 12) but still misses the daytime drift to the bedroom floor; p_7890 sends them OUT_OF_HOUSE during errands (against 3). This document says the glasses are in the bedroom, mostly on the nightstand, with a daytime wobble to the floor, and they never leave.

What would refute: a single sighting of glasses_priya at OUT_OF_HOUSE, or a sustained (3+ consecutive passes) presence at a non-bedroom receptacle such as the kitchen table or the coffee table.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are on the nightstand in the evening after the day's rotation",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Priya's glasses are on the nightstand overnight",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Priya's glasses are in the house at the nightstand during weekday afternoon errands, not out with her",
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
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 18,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
