# p_3a7f — Evening Migration Confirmed: Coffee Table by 21 (fork of p_c6d9)

The Thursday evening patrol confirms the migration choreography predicted by p_c6d9. mug_hana is at coffee_table_l1 at both 20:00 and 21:00 (two consecutive sightings). snack_bowl_shared is at counter_k1 at 18:00 and 19:00 (four sightings total in that window), then appears at coffee_table_l1 at 21:00 (two sightings). mug_priya is at sink_k1 at 18:00, then splits between cupboard_k1 and coffee_table_l1 at 21:00. The 23:00 sighting of glass_priya at coffee_table_l1 extends the migration window later than p_c6d9 originally placed it.

What changed from p_c6d9: (1) glass_priya now has an explicit 22–23h block at coffee_table_l1, confirmed by the 23:00 sighting; (2) mug_priya's 21–23h block is downgraded to "sometimes" at coffee_table_l1 because the 21:00 pass found it in two places (cupboard and coffee table); (3) the snack_bowl counter block is extended to 19–21h (the 19:00 pass found it three times at counter, and the first coffee_table sighting is at 21:00, not 20:00). The core 21:00 arrival time is unchanged.

If the snack bowl or mugs appear on the coffee table at 19:00, or if the kitchen table still has plates at 22:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's mug is on the coffee table at 20:00 on a weekday (evening TV session underway)",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 19:00 on a weekday (dinner just finished, not yet moved)",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18,
   "to": 20
  },
  {
   "claim": "Priya's glass is on the coffee table at 23:00 on a weekday (late-night drink during TV)",
   "target": "glass_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 22,
   "to": 23
  },
  {
   "claim": "The blanket is on the couch at 21:00 on a weekday (TV time)",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 20,
   "to": 23
  }
 ],
 "targets": {
  "mug_hana": [
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
    "to": 19,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
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
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
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
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
