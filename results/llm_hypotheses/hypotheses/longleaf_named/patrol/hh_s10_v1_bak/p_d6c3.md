# p_d6c3 — Omar's tablet goes to work; it is his job tool

Omar's job requires a tablet, so he takes tablet_omar out with him every weekday from about 13:30 until 23:00. In the morning, it sits at the kitchen chair where he uses it for personal tasks (music, gaming) before his shift. On weekends it stays at the kitchen chair all day. Yuki's items follow the standard commute pattern. What sets this hypothesis apart: tablet_omar is OUT_OF_HOUSE during weekday evening hours (14:00–22:00), whereas in p_a3f7 it is sometimes out and in p_b4e2 it is always home. What would refute it: tablet_omar sighted at chair_k1 between 14:00 and 22:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is out of the house during his work shift on weekdays",
   "target": "tablet_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Omar's tablet is at the kitchen chair in the morning on weekdays",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 6,
   "to": 13
  },
  {
   "claim": "Omar's tablet is at the kitchen chair all day on weekends",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's keys are out of the house on weekday mornings",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "controller_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ]
 }
}
```
