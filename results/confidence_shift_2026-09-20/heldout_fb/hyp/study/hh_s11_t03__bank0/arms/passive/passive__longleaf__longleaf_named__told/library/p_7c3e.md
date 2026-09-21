# p_7c3e — Saturday Home Day; Both In, Leisure Afternoon, Errands at Midday

Hana and Priya are both home all day Saturday. The Friday message confirmed Hana was sick, and the Saturday message says they are "off our usual routine and around the house more." This means Hana does NOT leave for her afternoon-to-night work shift; her notebook stays at desk_b1 and her tablet stays at nightstand_b1 (no work session). Instead, Hana takes her usual weekend errands around midday (roughly 12:00–14:00), carrying her keys, handbag, jacket, and wallet out the door. Priya takes the dog on a late-morning walk (10:00–11:00) with the leash and toy. After their outings, both settle into the living and dining areas: they play board games (puzzle box on the dining table), Hana plays guitar in her bedroom, and the afternoon drifts into shared TV with the blanket on the couch.

What sets this apart: unlike the weekday documents (p_a3f7, p_b8c2) where Hana vanishes at 13:40, here she is home all day. The puzzle box leaves the bookshelf for the dining table (no other live document places it there on a weekend). Hana's work objects do NOT migrate to the kitchen table or coffee table because there is no work session. The blanket rests on the couch (supported by 11 sightings across 4 days) rather than the coffee table.

What would refute it: if Hana's keys, handbag, or jacket are sighted inside the house between 12:00 and 14:00, the errand block fails. If the puzzle box is still on the bookshelf at 15:00, the board-game block fails. If the tablet appears at the kitchen table or desk during the day, the "no work" claim is wrong. If the blanket is found on the coffee table rather than the couch during the afternoon, the resting-spot claim weakens.

```json
{
 "claims": [
  {
   "claim": "Hana's keys are out of the house during her Saturday midday errands",
   "target": "keys_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 12,
   "to": 14
  },
  {
   "claim": "The puzzle box is on the dining table for the Saturday afternoon board-game session",
   "target": "puzzle_box_shared",
   "expect": "dining_table_d1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "The blanket is on the couch all Saturday, not the coffee table",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Hana's tablet stays at her nightstand all Saturday because she is not working",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The dog leash is out with Priya during the late-morning Saturday walk",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 11
  }
 ],
 "targets": {
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
  "handbag_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
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
  "dog_leash_shared": [
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
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
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
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "coffee_table_l1",
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
  "notebook_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
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
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
