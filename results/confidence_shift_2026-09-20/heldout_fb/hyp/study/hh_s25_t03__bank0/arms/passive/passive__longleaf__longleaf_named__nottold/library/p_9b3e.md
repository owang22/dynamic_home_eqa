# p_9b3e — Evening triptych: cook at 19, eat at 20, watch at 21

The evening follows a three-act structure that the sightings confirm. Cooking begins around 19:00 on weekdays: the pan moves from the cupboard to the counter (sighted at 19:00 and 23:00), and the spatula moves from the drawer to the counter (sighted at 19:00 ×3, 20:00, 21:00). On weekends the 19:00 cooking does not happen (pan stays in the cupboard at 19:00; the spatula appears on the counter at 20:00 instead). Dinner is served at the dining table around 20:00: both plates and the serving dish are at the table (serving dish at 20:00 and 22:00 on weekdays, 20:00–22:00 on weekends). TV begins around 21:00: the remote moves from the TV stand to the coffee table (sighted at 21:00), the blanket migrates from the couch to the coffee table (sighted at 22:00 weekdays, 21:00 and 23:00 weekends), and the snack bowl appears on the coffee table (sighted at 21:00 and 22:00 ×3). By 22:00–23:00 the remote drops to the floor, the snack bowl goes to the sink, and the blanket ends up on the bed or coffee table.

This is distinguished from p_a1b2 (which has no evening sequence) and from p_c6a1 (which places the pan on the counter at 19:00 on both weekdays and weekends, but the weekend evidence shows the pan stays in the cupboard).

Refutation: if the pan is found in the cupboard at 19:30 on a weekday, or if the serving dish is not at the dining table at 20:30 on either a weekday or weekend.

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter during the weekday 19:00 cooking window",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The serving dish is at the dining table during the evening meal",
   "target": "serving_dish_shared",
   "expect": "dining_table_d1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The remote is on the coffee table during active TV watching",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table during evening TV",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The blanket is on the coffee table during the late-evening TV wind-down",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21.5,
   "to": 23
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "almost_always"
   }
  ],
  "plate_omar": [
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "plate_marco": [
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "serving_dish_shared": [
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
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
    "days": "both",
    "from": 21,
    "to": 22.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 21.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
