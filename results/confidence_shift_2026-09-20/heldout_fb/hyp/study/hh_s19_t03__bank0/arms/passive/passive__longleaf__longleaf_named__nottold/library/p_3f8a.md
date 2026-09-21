# p_3f8a — The 18-to-20 cook: pan out at six, counter snacks, remote stays put

Marco comes home around 17:30 and Omar wraps up his desk work at the same time. They start cooking together at 18:00: the pan, pot, and knife come out of storage then, are actively on the counter by 19:00, and go back by 20:00. Dinner is eaten at the kitchen table around 19:00–20:00. After dinner the snack bowl stays on the kitchen counter (not the coffee table) for the evening TV block. The remote never leaves the tv stand — it is seen there every single patrol, every day. Marco's guitar is in the bedroom at 18:00 but migrates to the couch by 21:00 for his evening practice. The iron and ironing board stay in storage until 21:00, when Omar sets up in his bedroom for a pressing session.

What sets this apart: the cooking window is 18:00–20:00 (not 17:50–19:00 as p_789a claims, and not 18:30–19:30 as p_b4d8 suggested). The pan is still in the cupboard at the 18:00 pass and on the counter at 19:00. The snack bowl is on the counter, not the coffee table. The remote is immovable. On weekends the pan is already on the counter at 18:00, so the weekend cook starts an hour earlier.

Refutation: if the pan is seen on the counter at 18:00 on a weekday, or the remote is seen off the tv stand at any hour, or the snack bowl is on the coffee table at 20:00 on a weekday, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter at 19:00 on a weekday",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.75,
   "to": 19.25
  },
  {
   "claim": "The remote is on the tv stand at 20:00 on a weekday",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 19.75,
   "to": 20.25
  },
  {
   "claim": "The snack bowl is on the kitchen counter at 20:00 on a weekday",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19.75,
   "to": 20.25
  },
  {
   "claim": "The pan is still in the cupboard at 18:00 on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "The guitar is on the couch at 21:30 on a weekday",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 21.25,
   "to": 21.75
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 17,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 23.5,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 21,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ]
 }
}
```
