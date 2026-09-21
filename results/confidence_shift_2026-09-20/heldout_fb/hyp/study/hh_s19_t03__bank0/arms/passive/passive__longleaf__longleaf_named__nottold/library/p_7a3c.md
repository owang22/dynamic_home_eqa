# p_7a3c — The split cook: weekend kitchen starts an hour early, remote never moves

Marco commutes to his office 8:00–17:30 on weekdays; Omar works from his desk 9:00–17:30. The key distinction this document makes is that the evening cooking routine shifts by day type. On **weekdays**, the cutting board and knife come out at 18:00 for prep, but the pan itself stays in the cupboard until roughly 18:45 and only appears on the counter for the 19:00–20:00 cooking window. On **weekends**, both residents are home earlier and the whole kitchen sequence moves forward: the knife is on the counter by 17:45, the pan is already out and on the counter by 18:00, and the spatula follows at 18:30. The remote stays on the tv_stand_l1 at all times — the residents reach for it without moving it. The snack bowl migrates from the cupboard to the counter around 18:00 and stays there through the TV block. At 21:00 Omar sets up the iron and ironing board on his bed (bed_b2) for a late-evening pressing session, while Marco's guitar migrates from the bedroom floor to the couch for the wind-down.

What would refute this document: finding the pan on the counter at 18:00 on a weekday (it should still be in the cupboard), or finding it in the cupboard at 18:00 on a weekend (it should already be out). Finding the remote on the coffee table during TV would also weaken this hypothesis.

```json
{
 "claims": [
  {
   "claim": "The pan is still in the cupboard at 18:00 on a weekday",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "The pan is on the counter at 18:00 on a weekend",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "The kitchen knife is on the counter at 18:00 on a weekend",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17.75,
   "to": 18.25
  },
  {
   "claim": "The remote is on the tv stand during evening TV on both day types",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "both",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The iron is on Omar's bed during the 21:00 pressing session",
   "target": "iron_shared",
   "expect": "bed_b2",
   "days": "both",
   "from": 21,
   "to": 22.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18.75,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.75,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 17.5,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 18,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 17.5,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17.5,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 19,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "drawer_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
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
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 22.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23.5,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23.5,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 20.5,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 23.5,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "laptop_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 9,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ]
 }
}
```
