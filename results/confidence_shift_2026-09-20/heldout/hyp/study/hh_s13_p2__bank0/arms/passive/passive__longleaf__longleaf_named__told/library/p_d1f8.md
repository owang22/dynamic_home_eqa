# p_d1f8 — Priya's Afternoon Arc: Kitchen to Armchair to Living Room

Priya's day has a clear spatial arc that the existing documents only partially capture. In the morning (08:00–14:00) she is in the kitchen: her glass is at the kitchen table at 14:00 (a cup of tea or coffee), her mug was at the kitchen table at 08:00 (breakfast), and the robot finds her in the kitchen at 08:00, 10:00, and 14:00 on Wednesday. In the mid-afternoon (15:00–17:00) she moves to the living room: at 16:00 on Wednesday her book is at the armchair and she is in the living room. This is her reading time. By 18:00 Hana is home and they are both in the living room. At 20:00 they are back in the kitchen for dinner. At 22:00 they are in the living room for the evening, and Priya's mug and glass are on the coffee table.

Her headphones follow a different arc: they rest at desk_b2 from 00:00 through 16:00 (all seven daytime passes confirm this). At 18:00 they are at bed_b2 (she is resting in the bedroom before dinner). At 20:00 they are split (1× bed, 1× desk — she is moving them). By 22:00 they are back at desk_b2 (2×/2×). The 18:00–20:00 bed_b2 window is a brief "resting" phase before the evening.

Her glass has the most complex path: nightstand at night (00:00–12:00), kitchen table at 14:00 (tea), sink at 16:00 (washed after tea), sink+cupboard at 18:00, kitchen table at 20:00 (dinner drink, 2×/2×), then cupboard+coffee_table at 22:00 (evening drink in the living room). The 22:00 split mirrors the general transit pattern.

What sets this apart: p_d5e7 (Priya's Bedroom Fortress) claims her objects never leave bedroom-b2, but the evidence shows her book at the armchair, her glass at the kitchen table, and her mug at the coffee table. p_a3f1 and p_2f9b have generic "Priya is home" blocks but do not model her specific afternoon reading arc. This document is the only one that places book_priya at armchair_l1 in the 15–17 h window and tracks her glass through the full day.

What would refute it: if on a weekday at 16:00 Priya's book is at the nightstand (not the armchair) and she is in the kitchen (not the living room), the afternoon reading arc is wrong. If her mug is at the sink (not the coffee table) at 22:00, the evening transition is wrong. If her headphones are at the bed at 22:00 (not the desk), the 18:00–20:00 rest window is wrong.

Travelling objects: Priya's keys and jacket are out with her on the afternoon errand 14:00–16:00. Her phone, wallet, and sunglasses stay at the entry table. Nothing else of hers leaves the house.

```json
{
 "claims": [
  {
   "claim": "Priya's book is at the armchair at 16:00 on a weekday (afternoon reading)",
   "target": "book_priya",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Priya's glass is at the kitchen table at 14:00 on a weekday (afternoon tea)",
   "target": "glass_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Priya's mug is on the coffee table at 22:00 on a weekday (evening drink in the living room)",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Priya's headphones are at her desk at 10:00 on a weekday (not the bed, not the nightstand)",
   "target": "headphones_priya",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 9,
   "to": 16
  }
 ],
 "targets": {
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 18,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 20,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "notebook_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   }
  ]
 }
}
```
