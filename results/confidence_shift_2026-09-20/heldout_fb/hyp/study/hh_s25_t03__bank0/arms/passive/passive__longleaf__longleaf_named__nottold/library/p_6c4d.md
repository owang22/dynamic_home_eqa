# p_6c4d — Contained household: nothing leaves the house

Over seven days there is zero evidence that any object leaves the house. Both sets of keys are at the entry table on all sighted days (Marco 7/7, Omar 6/7). Both jackets are at the entry hook (7/7 each). Marco's running shoes are at the shoe rack (7/7). Marco's water bottle is always in the house (desk, dish rack, sink, dining table). No OUT_OF_HOUSE sightings exist for any object in the entire log. The residents work from home, do their errands at midday on weekends (the shopping bag appears at the counter 16:00–18:00 on weekends), and their hobbies — reading, meditation, napping, houseplants — are all at-home activities. Omar's stated "seeing friends" hobby has produced no absence of his keys, jacket, or shoes.

This is a strong claim in itself: if any keys, jacket, or shoe is found OUT_OF_HOUSE, this document is refuted. It is distinguished from p_c3d4, p_d4e9, and p_b8c2 (which predict lunch outings) and from p_e5f6, p_a3f7, and p_e1a5 (which predict running outings). The running-shoes claim is particularly testable: if Marco runs, his shoes, water bottle, and jacket should be out simultaneously.

Refutation: if keys_marco or keys_omar are found OUT_OF_HOUSE at any time, or if jacket_marco or jacket_omar are OUT_OF_HOUSE, or if running_shoes_marco is OUT_OF_HOUSE.

```json
{
 "claims": [
  {
   "claim": "Marco's keys are at the entry table at all times and never leave the house",
   "target": "keys_marco",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Omar's keys are at the entry table at all times and never leave the house",
   "target": "keys_omar",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Marco's running shoes are at the shoe rack at all times and never leave the house",
   "target": "running_shoes_marco",
   "expect": "shoe_rack_e1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Marco's jacket is at the entry hook at all times and never leaves the house",
   "target": "jacket_marco",
   "expect": "entry_hook_e1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Omar's jacket is at the entry hook at all times and never leaves the house",
   "target": "jacket_omar",
   "expect": "entry_hook_e1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "keys_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "jacket_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "running_shoes_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "hat_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "scarf_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "sunglasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "umbrella_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "wallet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
   }
  ],
  "shoes_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "almost_always"
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
