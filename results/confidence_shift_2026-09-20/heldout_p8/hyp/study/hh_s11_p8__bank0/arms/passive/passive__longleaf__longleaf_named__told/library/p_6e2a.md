# p_6e2a — Glasses at the Sink and Pantry, Never in the Cupboard

Every document in the library that assigns `class:glass` to `cupboard_k1` has failed badly (0.14–0.15 hold rate on 12–14 sightings). The evidence shows that glasses are **never** stored in the cupboard. Instead, glass_hana rests at the **pantry_shelf_k1** overnight and in the evening (00:00, 18:00 weekday) and at the **sink_k1** on weekends. Glass_priya rests at the **sink_k1** during the day (16:00 weekday, 3 sightings) and is scattered across the **dining_table_d1**, **desk_b2**, and **nightstand_b2** in the morning, reflecting where she left it after the previous evening's use. On weekends, glass_priya is at the **nightstand_b2** in the morning and the **pantry_shelf_k1** in the afternoon.

The pattern is: glasses are used at meals, then either rinsed at the sink and left there, or put away on the pantry shelf. They are not cupboard items. The sink is the "drying" spot; the pantry shelf is the "stored" spot. In the morning, a glass may still be at the table or desk where it was used the night before, before someone washes it.

What sets this document apart: it explicitly places `class:glass` at **sink_k1** and **pantry_shelf_k1**, never at `cupboard_k1`. It also captures the weekday-morning scatter (dining_table, desk_b2) as a transient "left from last night" state that resolves to the sink or pantry by midday.

This document is refuted if a glass is consistently found in the cupboard across multiple passes, or if the pantry shelf never holds a glass.

```json
{
 "claims": [
  {
   "claim": "Hana's glass is on the pantry shelf at 18:00 on a weekday, not in the cupboard",
   "target": "glass_hana",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Priya's glass is at the kitchen sink at 16:00 on a weekday, not in the cupboard",
   "target": "glass_priya",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 15.5,
   "to": 17
  },
  {
   "claim": "Hana's glass is at the kitchen sink on weekend mornings, not in the cupboard",
   "target": "glass_hana",
   "expect": "sink_k1",
   "days": "weekend",
   "from": 7.5,
   "to": 9
  },
  {
   "claim": "Priya's glass is at the nightstand on weekend mornings, not in the cupboard",
   "target": "glass_priya",
   "expect": "nightstand_b2",
   "days": "weekend",
   "from": 7.5,
   "to": 9
  }
 ],
 "targets": {
  "glass_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 17,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 12,
    "at": "dining_table_d1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
