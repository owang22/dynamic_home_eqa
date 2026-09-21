# p_1a2b — Omar's gaming night: controller and tablet in use 23:00–02:00

Omar comes home at 23:00 and immediately starts gaming. The controller_omar is picked up from the TV stand and held ON_PERSON (or used at the couch) from 23:00 to 02:00. The tablet_omar is used as a secondary screen at the kitchen chair or couch. In the morning, both are back at their resting spots. Yuki is asleep by 23:00. What sets this hypothesis apart: controller_omar is ON_PERSON or at the couch between 23:00 and 02:00 on weekdays, not at the TV stand. What would refute it: controller_omar sighted at tv_stand_l1 between 23:30 and 01:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Omar's controller is not at the TV stand during his gaming hours",
   "target": "controller_omar",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Omar's controller is at the TV stand in the morning",
   "target": "controller_omar",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 6,
   "to": 12
  },
  {
   "claim": "Omar's tablet is at the kitchen chair in the morning",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 6,
   "to": 12
  },
  {
   "claim": "Omar's controller is at the TV stand during the day while he is at work",
   "target": "controller_omar",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "controller_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 2,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
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
    "from": 23,
    "to": 24,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 2,
    "at": "couch_l1",
    "chance": "sometimes"
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
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 1,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
