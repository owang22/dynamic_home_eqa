# p_3b7e — Weekend At Home: Hana's Objects at the Entry, Guitar Stays Put (fork of p_7f3a)

This fork corrects three errors in the parent that the Saturday (day 4) sightings expose. First, Hana's laptop and pen are NOT at desk_b1 on weekends; all three Saturday passes (00:00, 08:00, 16:00) found them at entry_hook_e1, the same spot they occupy on weekday evenings after the 18:00 homecoming dump. The charger, by contrast, does sit at desk_b1 on weekends (3/3 passes), so it stays as in the parent. Second, Hana's water bottle is at dish_rack_k1 on weekends, not sink_k1 as the parent claimed; the Saturday passes confirm dish_rack_k1 at all three times. Third, and most importantly, the guitar is NOT played on Saturday afternoon. The parent claimed ON_PERSON from 14:00 to 18:00, but the guitar's 5/5 sighting record shows bedroom_floor_b1 as its only receptacle across all days including Saturday. The 16:00 Saturday pass found it on the bedroom floor, and Hana was in the living room, not holding it. The guitar simply rests on the bedroom floor all weekend.

Everything else from the parent is retained: Hana's keys, wallet, handbag, jacket, phone, and sunglasses at the entry; the midday errand window (12:00–14:00) when her going-out objects are briefly OUT_OF_HOUSE; Priya's late-morning walk (10:00–11:30); and the puzzle box at bookshelf_l1.

What would refute this document: finding Hana's laptop at desk_b1 on a Saturday morning, finding the guitar ON_PERSON on a Saturday afternoon, or finding Hana's water bottle at sink_k1 on a weekend.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the entry hook on a Saturday morning because she is home and not at work",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Hana's pen is at the entry hook on a Saturday morning",
   "target": "pen_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 7,
   "to": 12
  },
  {
   "claim": "The guitar stays on the bedroom floor on a Saturday afternoon and is not played",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Hana's water bottle is at the dish rack on a Saturday afternoon",
   "target": "water_bottle_hana",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The puzzle box rests on the bookshelf on a Saturday afternoon",
   "target": "puzzle_box_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 13,
   "to": 17
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "charger_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "wallet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "sunglasses_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
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
    "chance": "sometimes"
   }
  ],
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
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "plate_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
