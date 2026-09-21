# p_d5a2 — Weekend Morning: Yuki's Dog Walk and Marco's Midday Errands

On weekends the rhythm shifts. Yuki, retired and home all day, takes the dog for a late-morning walk between 10:00 and 11:00, carrying the leash on her person. Marco, off work, bakes in the morning (baking tray and mixing bowl at the counter around 9:00–11:00) and then heads out for errands around midday (12:00–14:00), taking his keys, jacket, sunglasses, and water bottle with him. The dog food bag is at the kitchen floor in the morning for feeding, and the dog bowl stays on the kitchen floor throughout.

This document fills a gap: the existing library is almost entirely weekday-focused. p_f3a9 has one weekend claim (leash ON_PERSON 10–11 h) but no weekend targets for Marco's errand items. p_d1e6 covers weekday baking but not the weekend afternoon session. This document predicts that on a Saturday or Sunday, Marco's keys and jacket are OUT between 12:00 and 14:00, and the baking tray is at the counter in the morning.

Refutation: if Marco's keys or jacket are found at the entry on a weekend between 12:00 and 14:00, the errand block is wrong. If the dog leash is on the entry table (not on Yuki) during 10:00–11:00 on a weekend, the walk block fails. If the baking tray is in the pantry at 10:00 on a weekend, the baking block is wrong.

```json
{
 "claims": [
  {
   "claim": "The dog leash is on Yuki's person during her weekend late-morning walk",
   "target": "dog_leash_shared",
   "expect": "ON_PERSON",
   "days": "weekend",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Marco's keys are out of the house during his weekend midday errands",
   "target": "keys_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The baking tray is on the kitchen counter during Marco's weekend morning baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Marco's jacket is out of the house during his weekend midday errands",
   "target": "jacket_marco",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 14
  }
 ],
 "targets": {
  "dog_leash_shared": [
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
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
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
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "jacket_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 14,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "sunglasses_marco": [
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
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   }
  ]
 }
}
```
