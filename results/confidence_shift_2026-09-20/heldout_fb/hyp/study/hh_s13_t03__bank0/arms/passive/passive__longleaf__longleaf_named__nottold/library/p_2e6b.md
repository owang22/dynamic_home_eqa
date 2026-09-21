# p_2e6b — The 20:00 Dinner to 21:00 Coffee Table Pivot

The weekday evening has a sharp pivot around 20:30. Dinner is at the kitchen table from roughly 19:50 to 21:00 (plates, glasses, and the water bottle are there at the 20:00 pass). At 20:30–21:00 the residents move to the living room: mugs migrate to the coffee table, the snack bowl comes from the counter, the blanket shifts from the couch to the coffee table, and the TV session begins. The remote stays at the tv_stand throughout (it is never carried to the couch). The laptop appears at desk_b1 by 22:00 for a brief evening work or reading session.

This is distinguished from p_8c2d (which also captures the dinner-to-TV transition) by including the remote-at-tv_stand claim (p_8c2d does not address the remote) and by placing the snack bowl's counter-to-coffee-table migration specifically at 20:30–21:00. It differs from p_c9d4 ("Late Night") by not predicting the guitar at the coffee table and by keeping the blanket at the coffee table (not the couch) during the TV window.

What would refute this: plates at the kitchen table after 21:00 on a weekday, the remote at the coffee table during a weekday TV session, or the snack bowl still on the counter at 21:30.

```json
{
 "claims": [
  {
   "claim": "Hana's plate is on the kitchen table at 20:15 on a weekday (dinner in progress)",
   "target": "plate_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 20,
   "to": 21
  },
  {
   "claim": "Hana's mug is on the coffee table at 21:15 on a weekday (TV session)",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22
  },
  {
   "claim": "The snack bowl is on the coffee table at 21:30 on a weekday (moved from counter)",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The remote is at the TV stand at 21:30 on a weekday (never moved to the couch)",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The blanket is on the coffee table at 22:00 on a weekday (not the couch)",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21.5,
   "to": 23
  }
 ],
 "targets": {
  "plate_hana": [
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "weekday",
    "from": 20.5,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 18.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23.5,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekday",
    "from": 22,
    "to": 23.5,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
