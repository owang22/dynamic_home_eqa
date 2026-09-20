# p_e2f8 — The 6 a.m. Gym Rat: Yuki trains Monday, Wednesday, Friday

Yuki goes to the gym at 6:00 on Monday, Wednesday, and Friday, returning by 7:30. The gym bag and running shoes are OUT_OF_HOUSE during that window. On other days the gym bag stays at wardrobe_b1 and the running shoes at shoe_rack_e1. Nora's commute is standard (out 8:00–17:30 all weekdays). Yuki works from the desk 9:00–17:30 on all weekdays.

What sets this hypothesis apart: on Mon/Wed/Fri at the 4:00 or 8:00 patrol, gym_bag_yuki is absent from wardrobe_b1 and running_shoes_yuki is absent from shoe_rack_e1. On Tue/Thu they are in place.

What would refute it: gym_bag_yuki sighted at wardrobe_b1 at 6:00 or 7:00 on a Monday.

```json
{
 "claims": [
  {
   "claim": "Yuki's gym bag is out of the house at 6 a.m. on Monday",
   "target": "gym_bag_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 6,
   "to": 7.5
  },
  {
   "claim": "Yuki's running shoes are out of the house at 6 a.m. on Wednesday",
   "target": "running_shoes_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 6,
   "to": 7.5
  },
  {
   "claim": "Yuki's gym bag is at the wardrobe on Tuesday midday",
   "target": "gym_bag_yuki",
   "expect": "wardrobe_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Yuki's running shoes are at the shoe rack on Thursday midday",
   "target": "running_shoes_yuki",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "gym_bag_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 7.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "running_shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 7.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
