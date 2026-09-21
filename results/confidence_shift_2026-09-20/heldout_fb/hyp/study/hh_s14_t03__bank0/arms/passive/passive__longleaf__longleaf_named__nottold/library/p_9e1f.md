# p_9e1f — Marco's Corrected Work Kit: Lunchbox and Vitamins Out, Journal at Desk

This document combines the best-supported claims from p_b7c2 (lunchbox and vitamins leave with Marco at 13:40) and p_e4c8 (journal at the desk during midday). The evidence is strong: 11 empty looks at the cupboard during 9–17 h for the lunchbox (weak-for for OUT_OF_HOUSE), 15 empty looks at the counter for vitamins, and 2 positive sightings of the journal at desk_b1 during 9–17 h with zero empty looks. The journal transitions to the nightstand by 18:00 (seen there at the 18:00 pass). This is distinct from p_b7c2 (which wrongly sends the journal out of the house), p_8e2f (which puts the journal at the nightstand during the day, contradicting the desk sightings), and p_a3f1 (which keeps the lunchbox in the cupboard, contradicted by 11 empty looks). It would be refuted if the lunchbox is found in the cupboard at 15:00, or the journal is found at the nightstand at 12:00.

```json
{
 "claims": [
  {
   "claim": "Marco's lunchbox is out of the house during his work shift",
   "target": "lunchbox_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 21
  },
  {
   "claim": "Marco's vitamins are out of the house during his work shift",
   "target": "vitamins_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 21
  },
  {
   "claim": "Marco's journal is at the bedroom desk during his midday writing session",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Marco's journal is at the nightstand after he returns home in the evening",
   "target": "journal_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 18,
   "to": 23
  }
 ],
 "targets": {
  "lunchbox_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "vitamins_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "journal_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 14,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
