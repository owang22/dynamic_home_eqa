# p_7a8b — Yuki's shoes go out with her on weekdays; they are at the rack only when she is home

Yuki takes her shoes with her (she changes at the office or walks to a transit stop in them and the shoes are her work shoes). The shoe_rack_e1 is empty of her shoes between 08:00 and 17:30 on weekdays. On weekends, the shoes are at the rack (she wears indoor slippers at home). What sets this hypothesis apart: shoes_yuki are OUT_OF_HOUSE on weekday work hours. What would refute it: shoes_yuki sighted at shoe_rack_e1 between 09:00 and 17:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Yuki's shoes are out of the house on weekday work hours",
   "target": "shoes_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Yuki's shoes are at the shoe rack in the morning before she leaves",
   "target": "shoes_yuki",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 6,
   "to": 8
  },
  {
   "claim": "Yuki's shoes are at the shoe rack on weekends",
   "target": "shoes_yuki",
   "expect": "shoe_rack_e1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's keys are out of the house on weekday work hours",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "shoes_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
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
  "jacket_yuki": [
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
    "chance": "sometimes"
   }
  ]
 }
}
```
