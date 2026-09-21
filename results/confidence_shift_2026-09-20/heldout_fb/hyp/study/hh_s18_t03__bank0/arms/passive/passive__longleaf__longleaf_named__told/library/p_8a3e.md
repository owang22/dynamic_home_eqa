# p_8a3e — The 21:00 migration: TV objects shift to the living room

At roughly 21:00 the household settles into evening TV and the small objects in the living room migrate in a coordinated way. The remote leaves the TV stand and lands on the coffee table (seen there at 21:00 ×1 and 22:00 ×3). The speaker leaves the bookshelf and moves to the couch (seen there at 21:00 ×3). The blanket slides from the couch to the coffee table (seen there at 21:00 ×1, 22:00 ×1, 23:00 ×3). The snack bowl, which has been in the kitchen or cupboard through the day, appears on the coffee table by 23:00 (×2).

Before 21:00 the remote rests on the TV stand (03:00 ×2, 18:00 ×1), the speaker is on the bookshelf (03:00 ×1, 18:00 ×1), the blanket is on the couch (03:00 ×2, 18:00 ×1, 19:00 ×1), and the snack bowl is in the kitchen area (03:00 sink/counter, 18:00 cupboard).

This document differs from p_a3f7, which pins the snack bowl on the couch and the remote on the TV stand during 20–22:30 h — both contradicted by the 21:00 and 22:00 passes. It also differs from p_f7b3, which places the snack bowl on the kitchen table rather than the coffee table.

Refutation: finding the remote on the TV stand at 22:00, the speaker on the bookshelf at 21:00, the blanket on the couch at 23:00, or the snack bowl in the cupboard at 23:00.

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
   "claim": "The speaker is on the couch at 21:00",
   "target": "speaker_shared",
   "expect": "couch_l1",
   "days": "both",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The blanket is on the coffee table at 23:00",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23.5
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
    "to": 20,
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
  "speaker_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 20,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23.5,
    "at": "couch_l1",
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
    "to": 23.5,
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
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
