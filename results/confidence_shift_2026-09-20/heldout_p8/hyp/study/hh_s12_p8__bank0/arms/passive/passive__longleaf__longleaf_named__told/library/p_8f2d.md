# p_8f2d — Priya's glasses: nightstand until nine, then the desk

Priya's day begins in the bedroom: she reads in bed or on the floor, and her glasses stay on the nightstand through the early morning. The 08:00 passes show the glasses split across nightstand, desk, and bedroom floor, meaning the move to the desk happens around 9 rather than 7. Once at the desk (roughly 9–17 h) she reads, writes, and works on her music; her pen and headphones join her there. By 18:00 the glasses are back on the nightstand for the evening. This document corrects the timing in p_c5d9 (which placed the glasses at the desk from 7 h and was contradicted twice) and refines p_b4e8's midday-only window to a full 9–17 h span. The pen and headphones at desk_b1 during those hours are the supporting cast.

What would refute it: if the glasses are consistently at the desk before 9 on multiple mornings (meaning she moves them earlier than this model says), or if they are found on the nightstand during the 10–15 h window on more than half of looks (meaning the desk session is shorter or interrupted).

```json
{
 "claims": [
  {
   "claim": "Priya's glasses are on the nightstand in the early morning before her desk session",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Priya's glasses are at the bedroom desk during her midday reading",
   "target": "glasses_priya",
   "expect": "desk_b1",
   "days": "both",
   "from": 10,
   "to": 15
  },
  {
   "claim": "Priya's glasses are back on the nightstand in the evening",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "Priya's pen is at the bedroom desk on a weekday afternoon",
   "target": "pen_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 15
  }
 ],
 "targets": {
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "pen_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 9,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 9,
    "to": 17,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
