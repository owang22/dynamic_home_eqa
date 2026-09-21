# p_2d8e — Yuki's two-hour afternoon errand

Yuki is home most of the day with a morning walk (7:00–8:30) and a shorter afternoon errand. Her keys, jacket, and sunglasses are each found at the entry 3 out of 4 times during the 9–17h window, meaning she is out for roughly two of those eight hours — not the four-and-a-half hours posited by p_c9d4, whose claims have all resolved against. I place her errand at 14:00–16:00, after lunch and before the evening settle. Her water bottle stays at the dish rack (4/4 found at 9–17h) because she refills it and leaves it. On weekends she stays home more (the residents' own message confirms this), so her keys and jacket remain at the entry all day. A look that finds her keys at the entry table at 15:00 on a weekday would refute this; a look that finds the entry table empty of her keys at 15:00 would support it.

```json
{
 "claims": [
  {
   "claim": "Yuki's keys are out of the house during her afternoon errand",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Yuki's jacket is out of the house during her afternoon errand",
   "target": "jacket_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Yuki's keys are at the entry table in the mid-morning",
   "target": "keys_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 9,
   "to": 13
  }
 ],
 "targets": {
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
