# p_3b7e — Marco's Work Commute: Personal Kit Leaves at 13:40, Returns at 23:00

Marco works afternoon-to-night shifts, leaving the house around 1:40 PM and returning around 11 PM on weekdays. When he leaves, he takes his entire personal kit with him: phone, keys, wallet, sunglasses, jacket, scarf, shoes, notebook, and backpack. In the early morning (03:00 sightings) all of these sit at the entry — hook, table, shoe rack — while he sleeps. By midday they are gone. The phone is the clearest signal: eight empty looks at the coffee table during 9–17 h versus one find, and the phone reappears at the entry table at 22:00 when he is home. The keys, wallet, sunglasses, jacket, scarf, shoes, notebook, and backpack are each seen only at 03:00 (entry-area receptacles) and never during the working day, consistent with being carried out at 13:40 and not returning until 23:00.

This document is distinguished from p_b7c2 and p_8e2f, which model only the lunchbox, vitamins, and journal as the "work kit." Here the full personal kit travels. It also differs from p_4b6a, which places the phone at the bed at 12–14 h and the entry table at 22–23 h but never says it is OUT during the shift. This document explicitly removes nine objects from the house for the work window.

Refutation: if the robot sights Marco's keys, wallet, jacket, sunglasses, or backpack anywhere in the house between 14:00 and 22:00 on a weekday, this document is wrong for that object. If the phone is found at the coffee table or nightstand during 15:00–21:00, the phone block fails.

```json
{
 "claims": [
  {
   "claim": "Marco's phone is out of the house during his work shift",
   "target": "phone_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 15,
   "to": 22
  },
  {
   "claim": "Marco's keys are out of the house during his work shift",
   "target": "keys_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 15,
   "to": 22
  },
  {
   "claim": "Marco's jacket is out of the house during his work shift",
   "target": "jacket_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 15,
   "to": 22
  },
  {
   "claim": "Marco's sunglasses are out of the house during his work shift",
   "target": "sunglasses_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 15,
   "to": 22
  }
 ],
 "targets": {
  "phone_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_marco": [
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_marco": [
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "sunglasses_marco": [
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "jacket_marco": [
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "scarf_marco": [
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "shoes_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 14,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "notebook_marco": [
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_marco": [
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
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
