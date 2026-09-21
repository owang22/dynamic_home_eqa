# p_9b4e — Entry Objects: Umbrellas on the Floor, Keys and Wallet on the Table, Coats on the Hook

The entryway has three distinct zones, and the evidence is unambiguous: the *floor* holds the doormat and both umbrellas (5/5 sighted days each at entry_floor_e1); the *hook* holds jackets, scarves, Marco's backpack, and his notebook; the *table* holds both residents' keys, wallets, and sunglasses; the *shoe rack* holds both residents' shoes. The p_d1e6 document incorrectly placed class:umbrella at entry_hook_e1 (a block that failed at 0.20 confidence). This document corrects that: umbrellas live on the entry floor, leaning against the wall or in a stand, not hung on the hook.

Marco's keys, wallet, sunglasses, and notebook are at the entry table or hook when he is home (mornings before 13:40, evenings after 23:00) and OUT_OF_HOUSE during his work shift. Yuki's keys, wallet, and sunglasses stay at the entry table throughout the day (she is home most of the time; even on her errands she may leave them if the walk is short). If an umbrella is found on the entry hook, or if Marco's keys are at the entry table during his 14–22 h work shift on a normal weekday, this document is contradicted.

```json
{
 "claims": [
  {
   "claim": "Marco's umbrella is on the entry floor, not on the hook, at 03:00",
   "target": "umbrella_marco",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Yuki's umbrella is on the entry floor at 03:00",
   "target": "umbrella_yuki",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Marco's keys are out of the house during his work shift on a normal weekday",
   "target": "keys_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Yuki's sunglasses remain at the entry table at 03:00 on a weekday",
   "target": "sunglasses_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "class:umbrella": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "class:keys": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "class:wallet": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "class:sunglasses": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "class:shoes": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "class:jacket": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:scarf": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "doormat_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
