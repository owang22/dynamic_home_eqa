# p_6d2c — Priya's Saturday: Late Walk, Return to the Entry, Kitchen Table Unpacking

Priya's Saturday rhythm is: sleep in until around 9 or 10, take a late-morning walk (roughly 10:00 to 11:30), come home, and settle into the afternoon. The 16:00 Saturday pass found her in the entry, which is consistent with either having just returned from the walk or being in the process of going out again for a short errand. At the same 16:00 pass, plate_priya was on kitchen_table_k1 and the shopping bag was also on kitchen_table_k1, suggesting that a meal or snack has been set out, or that she has been to the shops and is unpacking.

During the walk window (10:00–11:30), Priya's jacket, keys, and phone are briefly OUT_OF_HOUSE or ON_PERSON. Her shoes are at the shoe rack. When she returns, her jacket goes back to entry_hook_e1, her keys to entry_table_e1, and her phone to nightstand_b2.

Hana, meanwhile, is in the living room at 16:00 on Saturday. She is not in the kitchen, not in the bedroom, not in the bathroom. The living room is where she spends her Saturday afternoon: reading, scrolling her phone, or just relaxing. The blanket is on the armchair, the remote is on the coffee table, and the board game is out on the coffee table (perhaps from a morning session or set out for later).

This document differs from p_f7a2 (Priya's weekday Tuesday/Thursday travel) by focusing on the weekend walk pattern, which is shorter and later in the day. It differs from p_2a6e (Priya's weekday walk) by placing the walk at 10:00–11:30 rather than 8:00–9:30, and by noting the kitchen-table activity at 16:00 that does not appear on weekdays.

What would refute this: finding Priya in the kitchen at 16:00 on a Saturday (she was in the entry), finding her plate in the cupboard at 16:00 on a Saturday (it was on the kitchen table), or finding the shopping bag in the pantry at 16:00 on a Saturday (it was on the kitchen table).

```json
{
 "claims": [
  {
   "claim": "Priya's plate is on the kitchen table at 16:00 on a Saturday, set out for a meal or snack",
   "target": "plate_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The shopping bag is on the kitchen table at 16:00 on a Saturday, unpacked from an errand",
   "target": "shopping_bag_shared",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Priya's jacket is at the entry hook at 16:00 on a Saturday, back from the walk",
   "target": "jacket_priya",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "Priya's keys are at the entry table at 16:00 on a Saturday, back from the walk",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 12,
   "to": 18
  }
 ],
 "targets": {
  "jacket_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "shoes_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ]
 }
}
```
