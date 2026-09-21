# p_8b3c — Priya's Day Kitchen: Sink and Table, Not Counter

The per-object evidence is unambiguous: during weekday 9–17h, the pan, cutting board, knife block, kettle, Hana's glass, and the snack bowl are all absent from their usual counter or cupboard spots (five empty looks each at the counter for several items). Yet the robot has never sighted them on the counter either—the claims in p_c1d6 and p_b9c4 placing them there have accumulated 5–13 against-counts. The 18:00 clock data shows a mass wash-up: bowl_hana, bowl_priya, glass_priya, and mug_priya are all in the sink at 18h. The most coherent reading is that Priya, home from roughly 9:00 to 14:00 and again 16:00 to 18:00, uses the kitchen for a midday meal and general tidying, leaving used items in the sink to be washed or dried in the dish rack. The items are not on the counter (in use) because the robot's passes catch them after the brief cooking window, when they have already been moved to the sink.

This document predicts that weekday looks at sink_k1 during 10–14h and 16–18h will find the pan, cutting board, or kettle. If the robot finds these items on the counter during those hours, or in the cupboard (as p_c3d8 and the resting-spot blocks predict), this hypothesis is refuted.

```json
{
 "claims": [
  {
   "claim": "The pan is in the kitchen sink at noon on a weekday (Priya has finished lunch and set it to wash)",
   "target": "pan_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The cutting board is in the kitchen sink at 17:00 on a weekday (washed after afternoon use)",
   "target": "cutting_board_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 16,
   "to": 18
  },
  {
   "claim": "Hana's glass is in the kitchen sink at noon on a weekday (washed after morning use)",
   "target": "glass_hana",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 10,
   "to": 14
  },
  {
   "claim": "The kettle is in the kitchen sink at 13:00 on a weekday (used for tea, then washed)",
   "target": "kettle_shared",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 11,
   "to": 14
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 18,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 18,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "kettle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "knife_block_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 14,
    "at": "sink_k1",
    "chance": "rarely"
   }
  ]
 }
}
```
