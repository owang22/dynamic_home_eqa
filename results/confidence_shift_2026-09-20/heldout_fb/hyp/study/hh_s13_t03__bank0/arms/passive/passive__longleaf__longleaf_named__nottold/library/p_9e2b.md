# p_9e2b — Weekend: Armchair Day, Coffee Table Night

On weekends the house runs on a completely different clock. Hana sleeps in until 9 or 10, and the blanket stays on the armchair all day—seen at 03:00 and 18:00 on Saturday, never on the couch. Breakfast or brunch is at the kitchen table around 9:00 (mugs and bowls seen there at the 09:00 pass). Hana goes out for errands midday, roughly 11:00 to 14:00, taking her keys, jacket, and handbag. In the afternoon she plays guitar, 14:00 to 17:00. Dinner is later than on weekdays, around 19:00 to 20:00, with Priya's plates at the kitchen table. At 20:00 the TV session begins, but unlike weekdays the remote is on the coffee table (seen 4 times at the 20:00 pass) and the blanket is on the coffee table by 20:00–21:00. The vacuum comes out during the day—seen on the living room floor at 12:00 and 15:00 on Saturday—rather than the 15:00 and 18:00 weekday slots. Hana's laptop stays home all weekend, resting at the entry hook or at the desk in the afternoon.

This document differs from p_e5f0 (which places Hana's keys at the entry table at 8:00 on Saturday and the puzzle box on the coffee table at 14:00) and from all weekday documents (which put the blanket on the couch and the remote at the TV stand). The armchair blanket is the single strongest weekend signal: 3 sightings on the armchair across 2 weekend days, zero on the couch. The coffee-table remote is equally clear: 5 sightings on the coffee table at 20:00–21:00, zero at the TV stand during the same window.

This document is refuted if the blanket is found on the couch on a weekend day, if the remote is at the TV stand during a weekend evening, if Hana's keys are in the house at noon on a Saturday, or if the guitar is on the bedroom floor at 15:00 on a Saturday.

```json
{
 "claims": [
  {
   "claim": "The blanket is on the armchair at 15:00 on a Saturday",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The remote is on the coffee table at 20:30 on a Saturday",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 19.5,
   "to": 21.5
  },
  {
   "claim": "The guitar is being played at 15:30 on a Saturday",
   "target": "guitar_hana",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Hana's keys are out of the house at 12:00 on a Saturday (errands)",
   "target": "keys_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The vacuum is on the living room floor at 13:00 on a Saturday (daytime cleaning)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 11,
   "to": 16
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "sometimes"
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
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "from": 11,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "plate_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
