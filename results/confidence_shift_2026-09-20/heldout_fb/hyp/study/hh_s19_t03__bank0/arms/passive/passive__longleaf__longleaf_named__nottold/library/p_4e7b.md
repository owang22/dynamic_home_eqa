# p_4e7b — The full evening arc: 18:30 cook, counter snacks, 21:00 wind-down

This document captures the complete evening sequence as a single routine, which no other document in the library does in one place. The evidence is unambiguous: the pan sits in the cupboard at the 18:00 pass and is on the counter at 19:00 (weekday ×2, weekend ×4); the snack bowl is on the counter at both 18:00 and 20:00 on weekdays; the remote has never been seen off the tv_stand (5/5 days, one receptacle); the guitar is on the bedroom floor at 18:00 but on the couch at 21:00; the iron and ironing board are in storage all day and on Omar's bed at 21:00 (×3 weekdays, ×1 weekend). Omar's laptop leaves the desk at 18:00 and lands on the coffee table.

What sets this apart from p_b4d8 and p_b8c2 (which cover the 18:30 cook) is the 21:00 wind-down: the guitar moves to the couch and the iron goes to Omar's bed in the same window. What sets it apart from p_c9f2, p_6c1a, and p_d4e9 (which cover the 21:00 iron) is the cooking block. A document that gets both the 18:30 cooking and the 21:00 chores right should outperform either alone.

Refutation: if the pan is on the counter at 18:00 (cooking started earlier), if the snack bowl is on the coffee table at 20:00, if the remote is off the tv_stand during the evening, if the guitar is still on the bedroom floor at 21:30, or if the iron is still in storage at 21:30.

```json
{
 "claims": [
  {
   "claim": "The pan is still in the cupboard at 18:00 before cooking begins",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 18,
   "to": 18.5
  },
  {
   "claim": "The pan is on the counter during the cooking window",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The snack bowl is on the kitchen counter during the TV block",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The guitar is on the couch during the late-evening wind-down",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "both",
   "from": 21,
   "to": 22.5
  },
  {
   "claim": "The iron is on Omar's bed during the late-evening ironing session",
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
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
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
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
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21.5,
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
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
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
  ]
 }
}
```
