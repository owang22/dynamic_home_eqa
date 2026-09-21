# p_e7b4 — Yuki's journaling is a nightly bedroom ritual

Yuki journals every evening in bed or at the bedroom desk. Her journal_yuki is at the nightstand during the day but moves to desk_b1 (or is held ON_PERSON) between 20:00 and 23:00. Her pen_yuki is at desk_b1 during the day and moves to the nightstand at night for journaling. Omar's book and glasses are at the nightstand because he reads in bed in the morning before work. What sets this hypothesis apart: journal_yuki is at desk_b1 (or on Yuki) in the evening, not at the nightstand. What would refute it: journal_yuki sighted at nightstand_b1 between 20:00 and 23:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Yuki's journal is at the bedroom desk in the evening",
   "target": "journal_yuki",
   "expect": "desk_b1",
   "days": "both",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Yuki's pen is at the nightstand in the evening for journaling",
   "target": "pen_yuki",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Omar's book is at the nightstand in the morning",
   "target": "book_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 6,
   "to": 12
  },
  {
   "claim": "Yuki's journal is at the nightstand during the day",
   "target": "journal_yuki",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 8,
   "to": 19
  }
 ],
 "targets": {
  "journal_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "book_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "book_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
