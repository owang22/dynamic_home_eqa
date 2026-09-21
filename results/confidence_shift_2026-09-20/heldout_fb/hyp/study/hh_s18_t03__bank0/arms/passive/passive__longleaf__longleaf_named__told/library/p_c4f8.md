# p_c4f8 — The 21:00 TV migration: remote, blanket, speaker, and snacks shift to the living-room centre

Both residents wind down after dinner. At roughly 21:00 the remote (remote_shared) moves from the TV stand (tv_stand_l1) to the coffee table (coffee_table_l1), the shared blanket (blanket_shared) shifts from the couch (couch_l1) to the coffee table, and the speaker (speaker_shared) is placed on the couch. By 22:00–23:00 the snack bowl (snack_bowl_shared) has been brought from the cupboard (cupboard_k1) to the coffee table, and Ines's mug (mug_ines) is at the coffee table. The tissue box (tissue_box_shared) and candle (candle_shared) are already at the coffee table and stay.

Before 21:00 the remote is on the TV stand (confirmed at 03:00 and 18:00), the blanket is on the couch (03:00, 18:00, 19:00), and the speaker is on the bookshelf (bookshelf_l1) at 18:00. The snack bowl is in the cupboard or at the sink/counter in the morning.

This document is about the evening entertainment cluster only. It does not make claims about work objects or the commute.

What sets it apart: p_a3f7 puts the remote on the TV stand and the snack bowl on the couch during evening TV; p_6d3b and p_8a3e also predict the coffee table but at lower weights and with different snack-bowl timing. Here the snack bowl reaches the coffee table at 22:00 (not 21:00), and the speaker is on the couch (not the bookshelf) from 21:00.

Refutation: if the remote is on the TV stand at 22:00 on multiple days, the migration is wrong. If the snack bowl is on the kitchen table at 22:00–23:00, the coffee-table prediction fails. If the speaker stays on the bookshelf at 21:00, the couch prediction fails.

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
   "claim": "The speaker is on the couch at 21:00",
   "target": "speaker_shared",
   "expect": "couch_l1",
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
  }
 ],
 "targets": {
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
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
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "tissue_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ],
  "candle_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
