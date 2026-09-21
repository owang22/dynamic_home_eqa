# p_7d4e — Marco home sick (recurring): kit stays home (fork of p_c4f8)

Marco and Yuki live together. Marco has been home sick on two consecutive weekdays — Friday (day 3) and Monday (day 6). On a sick day he does not go to work; his entire going-out kit remains in the house. In the afternoon the jacket is at the shoe rack, not the entry hook: the 16:00 weekday passes consistently show shoe_rack_e1, suggesting Marco takes the jacket off and drapes it over the shoe rack when he decides to stay in. The backpack is at the entry hook. Keys and wallet are at the entry table. The phone is at the nightstand, where he charges it by the bed. The journal is at the desk, where he may write to pass the time. Vitamins are at the kitchen counter. His lunchbox is in the cupboard, unpacked.

Marco is in the living room for most of the sick day (confirmed by resident sightings on day 3: living room at 00:00, 08:00, and 16:00), with his book and glasses nearby. Yuki is home looking after the dog and possibly Marco; the guitar is on the couch in the morning and may move to the bedroom floor for her afternoon practice.

This document differs from p_c4f8 in two ways. First, the jacket's afternoon resting spot is shoe_rack_e1 instead of entry_hook_e1, based on the 16:00 weekday pass showing shoe_rack_e1 on every weekday including the sick day. The parent's jacket claim (entry_hook_e1) scored 0 for and 4 against, while the shoe-rack location matches the actual sightings. Second, the prose is generalized from "Friday sick" to "recurring sick days" since Marco is sick on both Friday and Monday. The OUT_OF_HOUSE override blocks remain with "sometimes" chance: on a normal weekday the items leave, but on a sick day they stay, and the sightings in the 14–22 h window will adjust the chance accordingly.

What would refute it: If on a weekday 14–18 h Marco's jacket is found at the entry hook (not the shoe rack), or if the backpack, keys, and phone are all confirmed out of the house, the sick-day prediction fails for that day. If the journal is not at the desk, the document is weakened.

```json
{
 "claims": [
  {
   "claim": "Marco's jacket is at the shoe rack during the afternoon when he is home sick",
   "target": "jacket_marco",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Marco's backpack is at the entry hook during the afternoon when he is home sick",
   "target": "backpack_marco",
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
    "to": 14,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
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
