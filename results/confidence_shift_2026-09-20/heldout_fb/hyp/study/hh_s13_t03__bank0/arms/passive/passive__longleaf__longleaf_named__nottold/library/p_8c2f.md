# p_8c2f — Priya Cooks Lunch, Dinner Is a Pot

The household cooking rhythm is **asymmetric and front-loaded**. Priya, home all day, does the real cooking at lunch (11:00–13:00): pan on the counter, knife out, cutting board in use. Hana is at work and misses it. Dinner at 18:00 is **not a cooking event**—it is a serving event. A pot (pot_shared) has been on the stove or counter since the afternoon (Priya started a soup or stew around 15:00), and by 18:00 the food goes onto plates at the kitchen table. The pan, knife, and cutting board are already back in the cupboard and drawer by 13:30.

What sets this apart: p_c1d6 says the pan is on the counter at BOTH 11–13 h AND 18–20 h. This document says the pan is on the counter only at 11–13 h. p_b9c4 says the pan is on the counter at 17.5–19 h. This document says it is not. The pot, not the pan, is the dinner vessel.

Refutation: if the robot finds pan_shared on counter_k1 during 17.5–20 h on a weekday, or finds pot_shared in cupboard_k1 during 17–19 h (meaning it was never on the stove), this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (not on the counter)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19.5
  },
  {
   "claim": "The pot is on the kitchen counter at 18:00 on a weekday (dinner simmering)",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 17,
   "to": 20
  },
  {
   "claim": "The cutting board is in the cupboard at 18:00 on a weekday",
   "target": "cutting_board_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19.5
  },
  {
   "claim": "The pan is on the counter at noon on a weekday (Priya cooking lunch)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 11,
   "to": 13
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
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "plate_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
