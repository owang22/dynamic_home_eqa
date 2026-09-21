# p_6e2b — Priya's home anchor: nightstand glasses, dish rack bottle, bedroom guitar

Priya is retired and home most of the day, with a morning walk and afternoon errands on weekdays. Her glasses rest on the nightstand as their primary anchor—confirmed 6/7 days as the most common location. They are not at the bedroom desk as p_b4e8, p_c5d9, and p_4c2a claim; the desk gets an occasional appearance but the nightstand is where they live. Her water bottle stays at the dish rack (or briefly at the sink when washed) even during her weekday afternoon errands—she does not carry it out. Her guitar rests on the bedroom floor 7/7 days, never moved to the living room during the day. Her pen and headphones stay at the bedroom desk. Her book is at the nightstand. During her afternoon errands (13–16h weekdays) she leaves the house, but her personal items remain in their resting spots.

This document is refuted if: Priya's glasses are found at desk_b1 on a majority of midday passes; the water bottle is sighted out of the house during her errand window; the guitar is found in the living room or on the couch during the day; or the pen is found away from the desk.

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are on the nightstand during midday, not at the bedroom desk",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's water bottle is at the dish rack during her weekday afternoon errands (she does not take it out)",
   "target": "water_bottle_priya",
   "expect": "dish_rack_k1",
   "days": "weekday",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Priya's guitar rests on the bedroom floor during midday",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "both",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's pen is at the bedroom desk during the afternoon",
   "target": "pen_priya",
   "expect": "desk_b1",
   "days": "both",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's book is on the nightstand overnight",
   "target": "book_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 0,
   "to": 7
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
    "from": 7,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 10,
    "to": 16,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 16,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "pen_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
