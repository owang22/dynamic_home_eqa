# p_5a1c — Saturday: friends at the house, the living room fills up

Saturday breaks the weekday split. Both residents are home all day: they sleep in, do errands around midday, and are home for the rest of the day. Friends arrive in the evening, so the living room becomes the social hub — the couch and armchair are occupied, the coffee table is in active use (laptop, magazines, snacks, glasses), and the kitchen sees heavier traffic (multiple glasses, plates, the fruit bowl out). Omar does not go to his desk; his laptop stays at the coffee table all day. Marco does not commute; his keys, backpack, and notebook stay at the entry. The guitar is likely out on the couch or coffee table for casual evening play. The blanket is on the couch.

This document differs from the weekday hypotheses by keeping Omar's laptop at the coffee table all day (no desk work), keeping Marco's entry items in the house (no commute), and activating the living room and kitchen for social use in the evening.

What would refute this document: finding Omar at his desk working on Saturday morning, or finding Marco's keys out of the house on Saturday.

```json
{
 "claims": [
  {
   "claim": "Omar's laptop is at the coffee table all day on Saturday (no desk work)",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 10,
   "to": 18
  },
  {
   "claim": "Marco's keys stay at the entry table on Saturday (no commute)",
   "target": "keys_marco",
   "expect": "entry_table_e1",
   "days": "weekend",
   "from": 10,
   "to": 18
  },
  {
   "claim": "The guitar is on the couch during Saturday evening social time",
   "target": "guitar_marco",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The blanket is on the couch during Saturday evening",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "laptop_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "class:towel": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
