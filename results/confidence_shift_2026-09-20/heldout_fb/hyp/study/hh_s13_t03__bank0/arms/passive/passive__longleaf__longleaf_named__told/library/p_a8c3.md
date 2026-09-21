# p_a8c3 — Priya's Drink Migration: Table at 12, Coffee Table at 22, Nightstand by 23

This document tracks Priya's glass and mug through a full weekday, capturing the distinctive pattern that separates her drinkware from Hana's. The glass is at the nightstand overnight (2/3 sightings at 03:00), moves to the kitchen table at 12:00 (4 sightings—her midday drink after returning from errands), returns to the nightstand by 13:00, passes through the sink at 18:00 (washed), sits in the cupboard at 19-to-20 (put away after washing), and is back at the nightstand by 22:00 (3 sightings—bedtime drink). The mug follows a parallel but distinct arc: kitchen table at 7-to-9 (8 sightings—morning tea, the single strongest morning signal in the house), sink at 18:00 (washed after afternoon use), and coffee table at 21-to-22 (4 sightings—she moves to the living room for TV and takes her mug with her).

What sets this document apart: p_4e1b places Priya's glass at the nightstand at 13:00 (1 for, 4 against) and misses the 12:00 kitchen table peak. p_2d8f puts the glass at the nightstand at 22:30 (3 for, 0 against) which agrees, but this document adds the 19-to-20 cupboard transit and the 12:00 table peak. For the mug, p_6f3c nails the 7-to-9 kitchen table window (8 for, 7 against) but does not model the 21-to-22 coffee table migration. This document unifies both objects into a single daily arc.

What would refute it: if the glass is reliably on the kitchen table at 14:00 or later (not back at the nightstand by 13), the midday window is longer than stated. If the mug is at the nightstand rather than the coffee table at 22:00, the evening migration is wrong.

```json
{
 "claims": [
  {
   "claim": "Priya's glass is on the kitchen table at 12:00 on a weekday for her midday drink after errands",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 11,
   "to": 13
  },
  {
   "claim": "Priya's glass is back at the nightstand at 22:00 on a weekday for her bedtime drink",
   "target": "glass_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Priya's mug is on the kitchen table at 08:00 on a weekday for morning tea",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Priya's mug is on the coffee table at 22:00 on a weekday during the evening TV session",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 11,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 13,
    "to": 18,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 19,
    "at": "sink_k1",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 9,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "sink_k1",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
