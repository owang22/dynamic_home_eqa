# p_5e6f — Yuki's pen migrates between bedroom desk and office desk

Yuki uses her pen at the bedroom desk (desk_b1) for journaling and planning in the evening, but takes it to the office desk (desk_o1) during the day for work-related writing. The pen is at desk_b1 from 20:00 to 07:00, and at desk_o1 from 08:00 to 19:00 on weekdays. On weekends it stays at desk_b1. What sets this hypothesis apart: pen_yuki is at desk_o1 during weekday daytime hours, not at desk_b1. What would refute it: pen_yuki sighted at desk_b1 between 10:00 and 16:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Yuki's pen is at the office desk during weekday work hours",
   "target": "pen_yuki",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  },
  {
   "claim": "Yuki's pen is at the bedroom desk in the evening",
   "target": "pen_yuki",
   "expect": "desk_b1",
   "days": "both",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Yuki's pen is at the bedroom desk on weekends",
   "target": "pen_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
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
  "pen_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 19,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "journal_yuki": [
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
  "wallet_yuki": [
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
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
