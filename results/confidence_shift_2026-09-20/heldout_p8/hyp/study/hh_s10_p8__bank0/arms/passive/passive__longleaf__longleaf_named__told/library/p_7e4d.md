# p_7e4d — Yuki's journal lives on the bed all weekend, at the nightstand on weekdays

The journal's resting place flips completely between weekdays and weekends. On weekdays the 00:00 and 08:00 patrols find it at the bedroom nightstand 3 out of 4 times (with 1 out of 4 at the bed, likely from reading before sleep). But on weekends the pattern is uniform: the 00:00, 08:00, and 16:00 patrols ALL find the journal at bed_b1, 2 out of 2 times each. Yuki sleeps in on weekends, reads and journals in bed, and leaves the journal there for the entire day. The mixture's worst-objects list flags this: the journal was predicted at nightstand_b1 but actually at bed_b1 three times (e.g. day 5 00:00, a Sunday midnight patrol).

What sets this apart: p_7c3e captures the Saturday-morning bed position (6–10h) but only for that window and has a low weight (0.011). This document extends the bed position to the full weekend (0–24h) and adds the weekday nightstand baseline. It makes no claim about the bedroom desk (p_c79a's dawn journaling hypothesis), treating the journal as a bed/nightstand object rather than a desk object.

Refutation: if the journal is found at the bedroom desk during a weekend morning patrol, or at the nightstand on a weekend afternoon, the all-weekend bed claim is wrong.

```json
{
 "claims": [
  {
   "claim": "Yuki's journal is on the bed on a weekend morning because she reads in bed before getting up",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 8,
   "to": 12
  },
  {
   "claim": "Yuki's journal is still on the bed on a weekend afternoon, left there from the morning",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Yuki's journal is at the bedroom nightstand overnight on a weekday, put away after her evening reading",
   "target": "journal_yuki",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  }
 ],
 "targets": {
  "journal_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
