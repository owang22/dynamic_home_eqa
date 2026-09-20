# p_3be9 — Nora's Sketching Hour: Evening art at desk_b2

After dinner, Nora sits at desk_b2 to sketch for an hour or two (19:30–21:30 on weekdays, 20:00–22:00 on weekends). The sketchbook and pencil case are at desk_b2 during that window. Before and after, they may be on the desk or moved to the nightstand. Yuki reads or watches TV in the living room during this time.

What sets this hypothesis apart: sketchbook_nora and pencil_case_nora are specifically at desk_b2 in the evening window, not just "usually there." On p_a3f1 they are at desk_b2 all day with no specific evening emphasis. Here the evening is the active use window.

What would refute it: sketchbook_nora sighted on the couch or at the kitchen table at 20:00 on a weekday (Nora is not at the desk).

```json
{
 "claims": [
  {
   "claim": "Nora's sketchbook is at desk_b2 in the evening on weekdays",
   "target": "sketchbook_nora",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Nora's pencil case is at desk_b2 in the evening on weekdays",
   "target": "pencil_case_nora",
   "expect": "desk_b2",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Nora's sketchbook is at desk_b2 on weekend evenings",
   "target": "sketchbook_nora",
   "expect": "desk_b2",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Nora's book is at the nightstand in the evening (she is at the desk, not in bed)",
   "target": "book_nora",
   "expect": "nightstand_b2",
   "days": "both",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "sketchbook_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ],
  "pencil_case_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": "22",
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ],
  "book_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
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
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
