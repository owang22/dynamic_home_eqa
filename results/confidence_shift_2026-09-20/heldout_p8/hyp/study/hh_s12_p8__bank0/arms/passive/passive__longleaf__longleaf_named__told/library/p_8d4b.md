# p_8d4b — Priya's weekend social: guitar at rest, glasses at nightstand, armchair blanket

Priya is retired and home all weekend. On a social evening (friends arriving around 18:00), her routine is: a late-morning walk (she is briefly out of the house 10–12 h with her water bottle), then she settles in. Her guitar stays on the bedroom floor all day — she does not play during the social, and it is not moved to the living room. Her glasses rest on the nightstand (she is not at the bedroom desk reading; the social keeps her in the living room and dining area). Her headphones stay at the bedroom desk. The blanket, which on weekdays sits on the couch, shifts to the armchair on weekends (a different resting spot when she is lounging rather than watching TV at a fixed spot). Her mug is in the dish rack in the morning (washed from the previous night) and in the cupboard by mid-afternoon. Her plate is in the pantry shelf in the morning (a weekend storage quirk) and at the sink by mid-afternoon (being washed before the social).

What sets this apart: p_5e6d (weight 0.000) puts Priya's glasses at the bedroom desk on Saturday midday and her water bottle out of the house 10–12 h. This document says the glasses stay at the nightstand (the data confirms nightstand at 00:00, 08:00, and 16:00 on the weekend) and the water bottle is at the sink, not out. The blanket-on-armchair prediction is unique: no other live document places the blanket on the armchair on weekends. The plate-in-pantry-shelf morning spot is also a weekend-only pattern.

What would refute it: if the robot finds glasses_priya at the bedroom desk on a weekend afternoon, the nightstand prediction fails. If the blanket is on the couch (not the armchair) on a weekend, the armchair shift is wrong. If the guitar is in the living room during the social (being played for guests), the bedroom-floor prediction is refuted.

```json
{
 "claims": [
  {
   "claim": "Priya's guitar rests on the bedroom floor all weekend (not moved for the social)",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 14,
   "to": 20
  },
  {
   "claim": "Priya's glasses are on the nightstand during the weekend afternoon (not at the desk)",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The blanket is on the armchair on a weekend afternoon (weekend resting spot differs from weekday couch)",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "Priya's water bottle is at the sink during her weekend morning (washed, ready for the walk)",
   "target": "water_bottle_priya",
   "expect": "sink_k1",
   "days": "weekend",
   "from": 7,
   "to": 10
  }
 ],
 "targets": {
  "guitar_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "glasses_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
