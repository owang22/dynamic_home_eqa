# p_5d9f — The 19:00 Couch; Priya's Solo Dinner and TV

On a normal weekday evening, Hana is still at work (she returns at 23:00), so the 19:00 hour belongs to Priya alone. She plates a light dinner — a bowl or plate at the dining table with a glass of water or tea — and eats around 19:00. By 20:00 the plates go to the sink and she pulls the blanket off the coffee table, drapes it over the couch, and drops the remote on the floor. She watches TV until about 21:30 or 22:00, then heads to her bedroom. Her tablet, which she had on the coffee table during the evening, goes to nightstand_b2. Her book and phone join it on the nightstand or bed.

This document differs from p_9e1f, which places glass_priya at the kitchen counter during 19:00–21:00 (a claim that has been against 8 times). The evidence shows glass_priya at dining_table_d1 at 19:00 (twice) and at counter_k1 only at 19:00 (once) and 21:00 (once), with the 21:00 counter sighting likely being the glass being washed or set down after dinner. The primary evening location is the dining table, not the counter.

This document also differs from p_4e8c (the guest evening) in that there are no guests; it is Priya alone on the couch. The blanket is on the couch, not the coffee table, but the snack bowl stays at the counter (Hana's late-night snack, not a guest spread).

This document is refuted if the robot finds the blanket on the coffee table during 19:00–21:00 on weekdays, or if glass_priya is consistently at the counter rather than the dining table during 19:00–20:00.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch during Priya's weekday evening TV, not the coffee table",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The remote is on the living room floor during the evening TV session",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Priya's glass is at the dining table during her 19:00 dinner",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Priya's plate is at the dining table during her evening meal",
   "target": "plate_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The snack bowl is on the kitchen counter in the evening for Hana's late snack",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 23
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 4,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 4,
    "to": 18.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 22,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 4,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 4,
    "to": 18.5,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "tablet_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7.5,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 19,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "class:dog_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
