# p_6eb5 — Nora's Weekend Nap: Afternoon rest 14 to 16 on weekends

On weekends, after errands, Nora naps from about 14:00 to 16:00. During the nap, book_nora is on the couch or in bedroom_b2 (not at the nightstand). The blanket may be on the couch. On weekdays Nora is at work so this pattern does not apply. Yuki continues working from the desk on weekends (lighter schedule, maybe 10:00–15:00).

What sets this hypothesis apart: on weekend afternoons (14:00–16:00), book_nora is NOT at nightstand_b2 — it is on the couch or in the bedroom. This is a weekend-specific pattern. p_a3f1 and p_3be9 keep book_nora at the nightstand.

What would refute it: book_nora sighted at nightstand_b2 at 15:00 on a Saturday.

```json
{
 "claims": [
  {
   "claim": "Nora's book is on the couch during the weekend nap",
   "target": "book_nora",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Nora's book is at the nightstand on weekday evenings",
   "target": "book_nora",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 19,
   "to": 23
  },
  {
   "claim": "The blanket is on the couch during Nora's weekend nap",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Nora's book is at the nightstand on weekday mornings",
   "target": "book_nora",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 6,
   "to": 10
  }
 ],
 "targets": {
  "book_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "couch_l1",
    "chance": "sometimes"
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
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ],
  "sketchbook_nora": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "usually"
   }
  ],
  "laptop_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 15,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
