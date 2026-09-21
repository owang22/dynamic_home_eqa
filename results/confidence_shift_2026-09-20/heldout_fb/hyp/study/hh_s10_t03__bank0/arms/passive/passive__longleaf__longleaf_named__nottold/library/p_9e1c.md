# p_9e1c — Weekend afternoon dusting: the duster visits the living room bookshelf

The duster lives in the kitchen cupboard almost all the time (6/6 sighted days, 15 sightings). But on a weekend afternoon, it makes a trip to the living room bookshelf. On day 5 (Sunday) at 14:00, the duster was seen at bookshelf_l1 (twice in one pass), and the residents were home (Omar is off work, Yuki is home after her midday errands). This is a weekend chore: someone dusts the bookshelf around mid-afternoon, then the duster returns to the cupboard. The weekday pattern shows no such trip — the duster stays in the cupboard all day on weekdays.

This document is distinct from the "entry chaos" and "kitchen" documents in that it predicts a specific weekend afternoon location (bookshelf_l1) for an object that otherwise never leaves the kitchen. If the duster is found in the cupboard at 14:00 on a weekend, or at the bookshelf on a weekday, this is refuted.

```json
{
 "claims": [
  {
   "claim": "The duster is at the living room bookshelf at 14:00 on a weekend (being used for dusting)",
   "target": "duster_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "The duster is in the kitchen cupboard at 10:00 on a weekend (not yet needed for the afternoon dusting)",
   "target": "duster_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  },
  {
   "claim": "The duster is in the kitchen cupboard at 20:00 on a weekend (dusting done, back in storage)",
   "target": "duster_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 18,
   "to": 22
  }
 ],
 "targets": {
  "duster_shared": [
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
