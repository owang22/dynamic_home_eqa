# p_ab2c — Yuki's Evening Run: 18 to 19 on Wednesday and Saturday

Yuki goes for a running session on Wednesday evenings (18:00–19:00) and Saturday mornings (8:00–9:00). The running shoes and gym bag go OUT_OF_HOUSE during those windows. On other days the running shoes are at the shoe rack and the gym bag at the wardrobe. This is different from p_e2f8 (6 a.m. gym Mon/Wed/Fri) — here it is an evening run on Wed and a Saturday morning run.

What sets this hypothesis apart: on Wednesday at 18:00 or 20:00, running_shoes_yuki is absent from shoe_rack_e1. On Saturday at 8:00, both running shoes and gym bag are gone. On Monday and Tuesday evenings, the running shoes are at the rack.

What would refute it: running_shoes_yuki sighted at shoe_rack_e1 at 18:00 on a Wednesday, or gym_bag_yuki at wardrobe_b1 at 8:00 on a Saturday.

```json
{
 "claims": [
  {
   "claim": "Yuki's running shoes are out of the house at 18:00 on Wednesday",
   "target": "running_shoes_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "Yuki's running shoes are out of the house at 8:00 on Saturday",
   "target": "running_shoes_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 8,
   "to": 9
  },
  {
   "claim": "Yuki's gym bag is out of the house at 8:00 on Saturday",
   "target": "gym_bag_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 8,
   "to": 9
  },
  {
   "claim": "Yuki's running shoes are at the shoe rack on Monday evening",
   "target": "running_shoes_yuki",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
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
    "from": 18,
    "to": 19,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "gym_bag_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
  ]
 }
}
```
