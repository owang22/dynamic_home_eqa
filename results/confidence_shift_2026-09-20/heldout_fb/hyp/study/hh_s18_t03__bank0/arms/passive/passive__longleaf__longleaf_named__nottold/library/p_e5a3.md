# p_e5a3 — The 21:00 convergence: remote, blanket, and snacks migrate to the coffee table

After dinner and the kitchen is cleared (around 20h), the evening TV ritual begins and objects migrate from their resting spots to the coffee table and couch. The remote leaves the TV stand and lands on the coffee table. The blanket moves from the couch to drape over the coffee table. The snack bowl comes out of the cupboard, sits briefly at the kitchen table (20–21h) while they grab a drink, then moves to the coffee table for the 22h+ window. The speaker is placed on the couch for music during the 20–22:30 window. Ines's headphones, which have been at the office desk all day, are carried to the bedroom around 21h.

This document focuses exclusively on the 20–23h window and the objects that move during it. It sets itself apart from p_a3f7 (which puts the snack bowl on the couch and the remote on the TV stand all evening) by placing the remote and blanket on the coffee table after 21h and the snack bowl on the coffee table after 22h. It differs from p_6d3b and p_9e2c by adding the speaker-on-couch block and the headphones-to-bedroom transition.

What would refute it: the remote staying on the TV stand at 22h; the blanket remaining on the couch at 22h; the snack bowl never appearing at the coffee table; the speaker staying on the bookshelf during the evening.

```json
{
 "claims": [
  {
   "claim": "The remote is on the coffee table at 22:00",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table at 22:00",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The snack bowl is on the coffee table at 23:00",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "The speaker is on the couch during the 20-to-22:30h entertainment window",
   "target": "speaker_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 20,
   "to": 22.5
  },
  {
   "claim": "Ines's headphones are in the bedroom at 21:00",
   "target": "headphones_ines",
   "expect": "bed_b1",
   "days": "both",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22.5,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "glass_ines": [
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "candle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "tissue_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
