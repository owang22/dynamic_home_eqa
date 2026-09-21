# p_7b2c — Saturday: Both Home, Midday Errands, Guitar and Board Games in the Afternoon

Saturday breaks the weekday split. Hana is off work and Priya is retired, so both are in the house for the full day. Priya takes a late-morning walk with the dog (around 10:00–11:00), taking the leash, her jacket, and her keys out. Hana runs errands around midday (12:00–14:00), taking her handbag, keys, water bottle, and wallet. The rest of the day they are home together: Hana plays guitar in the living room (the guitar comes out of the bedroom and goes to the armchair), Priya reads or does photography at her desk, and in the evening they pull the puzzle box from the bookshelf for board games at the dining table. The tablet stays at the nightstand (Hana is not working). The remote and blanket follow the evening-migration pattern. What sets this document apart: the guitar is in the living room in the afternoon (not the bedroom), the puzzle box is on the dining table in the evening, and both residents' personal items are in the house for most of the day. A look at the bedroom floor at 16:00 that finds the guitar, or a look at the bookshelf at 20:00 that finds the puzzle box, would refute this document.

```json
{
 "claims": [
  {
   "claim": "Hana's guitar is at the armchair in the living room on Saturday afternoon",
   "target": "guitar_hana",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 14,
   "to": 20
  },
  {
   "claim": "The puzzle box is on the dining table for Saturday evening board games",
   "target": "puzzle_box_shared",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The dog leash is out of the house during Priya's Saturday morning walk",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Hana's handbag is out of the house during her Saturday midday errands",
   "target": "handbag_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Hana's tablet is at her nightstand on Saturday morning",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 8,
   "to": 12
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 21,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "jacket_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ]
 }
}
```
