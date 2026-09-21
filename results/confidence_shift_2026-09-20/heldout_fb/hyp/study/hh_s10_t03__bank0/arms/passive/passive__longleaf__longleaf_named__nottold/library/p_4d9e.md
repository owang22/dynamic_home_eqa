# p_4d9e — Yuki's journal: nightstand by day, bedroom desk at 21:00, bed on weekends

Yuki's journal occupies three distinct resting spots depending on time and day. On weekdays, from the early morning through her 17:30 arrival home, the journal sits at the bedroom nightstand (03:00: nightstand 3×, bed 1×; 18:00: nightstand 1×). She does not touch it during the day—her work takes it nowhere, and it stays in the bedroom. The key event is at 21:00: the journal appears at the bedroom desk (21:00: desk_b1 2×, nightstand 2×), indicating she journals at the desk in the late evening, roughly 21:00–23:00. By the next morning it's back at the nightstand. On weekends the pattern shifts: the journal is at the bed (03:00: bed 2×), suggesting she reads in bed before falling asleep and leaves the journal there. Weekend daytime sightings are sparse, but the bed is the dominant resting spot.

This differs from p_c79a, which places the journal at the bedroom desk during a 06:15–07:00 dawn window (0 for, 0 against, 0 weak-for—untested but the 03:00 sightings show nightstand, not desk, on weekdays). The 21:00 desk appearance is the distinguishing feature.

```json
{
 "claims": [
  {
   "claim": "Yuki's journal is at the bedroom nightstand at 05:00 on a weekday (overnight, not in use)",
   "target": "journal_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 3,
   "to": 7
  },
  {
   "claim": "Yuki's journal is at the bedroom desk at 21:30 on a weekday (evening journaling session)",
   "target": "journal_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Yuki's journal is at the bed at 04:00 on a weekend (left there after reading in bed)",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 3,
   "to": 6
  }
 ],
 "targets": {
  "journal_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 21,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 21,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
