# p_2a6e — Priya's Wednesday: Walk, Puzzle, Friends

Priya's Wednesday follows her regular rhythm with the addition of the guest evening. She takes her morning walk from about 8:00 to 9:30 — keys out of the house, jacket on her or in hand. She is home by 10:00. The afternoon is for her jigsaw puzzle at desk_b2, with her book on the nightstand and her phone at the nightstand. At 18:00 friends arrive and the living room becomes the social space; she moves to the living room and her puzzle stays at the desk.

On a typical weekday Priya's keys are out of the house from 8:00 to 9:30 for the walk, then back at the entry table. Her jacket is out with her during the walk. Her phone is at the nightstand during the day and may be ON_PERSON in the evening when she is in the living room with friends. The puzzle box moves from the bookshelf to desk_b2 in the afternoon for her puzzle time.

What sets this apart: Priya's keys are out of the house in the morning (not at the entry table at 8:30), her jacket is out during the walk, and the puzzle box is at desk_b2 in the afternoon (not on the bookshelf or the coffee table). This contrasts with p_a3f1 (which puts Priya's keys out only 14-16 for afternoon errands) and p_d5e7 (Priya's Bedroom Fortress, which keeps everything in bedroom-b2 and does not model the morning walk or the evening social move).

What would refute it: if Priya's keys are at the entry table at 8:30, or if the puzzle box is on the bookshelf at 15:00, or if her phone is at the nightstand at 20:00 on Wednesday evening (she should be in the living room).

```json
{
 "claims": [
  {
   "claim": "Priya's keys are out of the house during her morning walk at 8:30 on a weekday",
   "target": "keys_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Priya's jacket is out of the house during her morning walk at 8:30 on a weekday",
   "target": "jacket_priya",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "Priya's phone is at the nightstand at 15:00 on a weekday",
   "target": "phone_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The puzzle box is at desk_b2 during Priya's afternoon puzzle time",
   "target": "puzzle_box_shared",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 14,
   "to": 17
  }
 ],
 "targets": {
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
    "from": 8,
    "to": 9.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
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
    "from": 8,
    "to": 9.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "puzzle_box_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 17,
    "at": "desk_b2",
    "chance": "sometimes"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ]
 }
}
```
