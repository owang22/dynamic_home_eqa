# p_f2c1 — Weekend afternoon chores: duster at the bookshelf, vacuum in the living room

On weekend afternoons (roughly 13:00–15:00), after the midday errands are done, someone—likely Yuki—dusts the living room bookshelf. The duster, which lives in the kitchen cupboard on weekdays, is carried to the bookshelf and left there while the dusting happens (or set on top of the shelf between sessions). Earlier in the morning (around 10:00), the vacuum cleaner is out on the living room floor for a weekend clean, then goes back to the entry floor by 13:00.

This differs from p_5b8c and p_7b3c, which place the vacuum at the entry floor all day on weekdays with a brief 18:00–19:30 living-room session. Here the vacuum is out on the floor in the *morning* on weekends, not the evening. The duster at the bookshelf is a new resting spot not captured by any current document (p_b2c8 puts the duster at the entry floor, which has failed). It would be refuted if the duster is never seen at the bookshelf on any weekend, or if the vacuum is at the entry floor at 10:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "The duster is at the bookshelf on a weekend afternoon (dusting session)",
   "target": "duster_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 13,
   "to": 15
  },
  {
   "claim": "The vacuum cleaner is on the living room floor on a weekend morning (weekend clean)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 9.5,
   "to": 13
  },
  {
   "claim": "The duster is back in the kitchen cupboard by weekend evening (dusting done)",
   "target": "duster_shared",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 15,
   "to": 18
  }
 ],
 "targets": {
  "duster_shared": [
   {
    "days": "weekend",
    "from": 13,
    "to": 15,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 9.5,
    "to": 13,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
