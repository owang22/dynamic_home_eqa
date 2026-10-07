# p_a7b8 — The entry is Priya's permanent shelf; both work from home

Priya's keys, wallet, sunglasses, jacket, and shoes are ALWAYS at the entry. This is not a transitional state—this is her permanent storage system. She keeps her keys on the entry table, her wallet next to them, her sunglasses on the table, her jacket on the floor by the door, and her shoes on the rack. She does not move them when she goes to the kitchen or the bedroom. Both Hana and Priya work from home (remote jobs). The 18:00 walkthrough simply shows the normal state of the house. Nothing is in transition. Hana's umbrella at the entry is also permanent storage (she keeps it by the door in case of rain). The dog is home all day. On a typical day, the only things that move are mugs (cupboard to counter for coffee/tea) and plates (cupboard to table for meals). What sets this apart: Priya's keys, wallet, sunglasses, jacket, and shoes are IN the house at ALL times, including 9:00–17:00 on weekdays. No OUT_OF_HOUSE blocks for these items. What would refute it: finding Priya's keys out of the house for more than 30 minutes on any day, or finding her jacket anywhere other than the entry floor or entry hook.

```json
{
 "claims": [
  {
   "claim": "Priya's keys are at the entry table on weekday midday (permanent storage)",
   "target": "keys_priya",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's jacket is at the entry floor on weekday midday (permanent storage)",
   "target": "jacket_priya",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Hana's tablet is at her desk on weekday midday (work from home)",
   "target": "tablet_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's sunglasses are at the entry table on weekend midday",
   "target": "sunglasses_priya",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "desk_b2",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "umbrella_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 10,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 16,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
