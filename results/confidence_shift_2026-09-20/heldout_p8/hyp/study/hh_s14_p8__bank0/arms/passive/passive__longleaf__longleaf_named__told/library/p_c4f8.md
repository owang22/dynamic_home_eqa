# p_c4f8 — Friday sick: Marco's whole kit stays home

Marco and Yuki live together. On Friday Marco is home sick and does not go to work. His entire going-out kit—backpack, jacket, keys, phone, wallet, shoes, sunglasses, notebook, water bottle—remains in the house. He is likely in bed or on the couch for much of the day, with his book, glasses, and phone nearby. His journal sits at the desk (he may journal to pass the time, or it simply stays at its usual desk spot). His vitamins are at the kitchen counter, where he takes them at home as usual. His lunchbox is in the cupboard, not packed. Yuki is home looking after the dog and possibly after Marco. The guitar is on the couch in the morning and may move to the bedroom floor for Yuki's afternoon practice.

This document differs from the work-shift documents (p_b2c9, p_f3a7) in that the going-out items are NOT out of the house during the 14–22 h window. The "sometimes" chance on the OUT_OF_HOUSE override blocks reflects that on most weekdays the items do leave, but on a sick day they stay. On a normal weekday the empty look at the entry hook supports the OUT_OF_HOUSE block; on a sick day the look finds the item there and weakens it.

What would refute it: If on a weekday 14–18 h Marco's backpack, jacket, keys, and phone are all confirmed out of the house (not found in any room), the sick-day prediction is wrong for that day. If the journal is not at the desk (e.g., at the nightstand or in Marco's hand), the document is weakened.

```json
{
 "claims": [
  {
   "claim": "Marco's backpack is at the entry hook during the afternoon when he is home sick",
   "target": "backpack_marco",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Marco's jacket is at the entry hook during the afternoon when he is home sick",
   "target": "jacket_marco",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Marco's keys are at the entry table during the afternoon when he is home sick",
   "target": "keys_marco",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Marco's journal is at the desk during the afternoon when he is home sick",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "backpack_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "phone_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "wallet_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "shoes_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "sunglasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 22,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "journal_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "vitamins_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "guitar_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "bedroom_floor_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
