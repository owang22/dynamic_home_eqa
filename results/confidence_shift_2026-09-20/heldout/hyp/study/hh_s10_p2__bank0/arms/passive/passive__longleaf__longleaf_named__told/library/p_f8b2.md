# p_f8b2 — Yuki's full work bag: ten items leave the house 8:00–17:30

Yuki is a thorough packer. Every weekday morning she takes her entire work kit out the door: laptop, jacket, shoes, backpack, notebook, sunglasses, wallet, keys, phone, and water bottle. The robot's looks at their usual spots (entry hook, entry table, shoe rack, nightstand, sink) consistently find nothing between 9:00 and 17:00 on weekdays — five empty looks each for the laptop, jacket, shoes, backpack, notebook, sunglasses, wallet, keys, and water bottle; five empty looks for the phone at the nightstand. She arrives home around 17:30 and the items reappear at their entry-area spots.

This is the key distinction from p_7a3f and p_a1b2, which model Yuki as cycling to work and therefore predict her helmet and bike lock out of the house. The evidence contradicts this: helmet_yuki is at entry_hook_e1 five for five during 9:00–17:00, and bike_lock_yuki is at entry_table_e1 five for five. She does not cycle to work. Her cycling gear stays home; cycling is a weekend or social hobby.

Omar, by contrast, takes only a subset to his shift (handbag, lunchbox, notebook, pen, scarf, shoes, wallet — each found 2 times and absent 3 during 9:00–17:00) and leaves his cycling gear (helmet, bike lock) at home as well.

What would refute this document: finding any of the ten listed items inside the house during 9:00–17:00 on a weekday, or finding the helmet or bike lock out of the house during that window.

```json
{
 "claims": [
  {
   "claim": "Yuki's keys are out of the house during her work hours on weekdays",
   "target": "keys_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Yuki's laptop is out of the house during her work hours on weekdays",
   "target": "laptop_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Yuki's water bottle is out of the house during her work hours on weekdays",
   "target": "water_bottle_yuki",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Yuki's helmet stays at the entry hook during work hours (she does not cycle to work)",
   "target": "helmet_yuki",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 9,
   "to": 16
  }
 ],
 "targets": {
  "laptop_yuki": [
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
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_yuki": [
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
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "sunglasses_yuki": [
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
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_yuki": [
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
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "helmet_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
