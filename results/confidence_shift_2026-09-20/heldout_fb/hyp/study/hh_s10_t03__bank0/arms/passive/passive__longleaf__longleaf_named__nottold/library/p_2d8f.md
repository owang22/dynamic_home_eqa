# p_2d8f — Weekend overnight: work and study items settle at the bedroom desk

On weekdays, Yuki's laptop, her notebook, and Omar's notebook and pen all end the night at the entry hook — dumped when they come in, not sorted before bed. But on weekends the pattern shifts. Both residents are in the bedroom at 03:00 (confirmed by looks on day 4 Saturday and day 5 Sunday), and their work and study items are at the bedroom desk rather than the entry. Yuki journals and reads in bed (journal_yuki at bed_b1 on weekend 03:00), while Omar's notebook and pen sit at desk_b1, suggesting he does evening study or writing at the desk before turning in. Yuki's laptop also migrates to desk_b1 on at least one weekend night, implying a weekend work or planning session at the desk that runs late.

This hypothesis is distinct from the weekday "entry chaos" documents (p_b2c8, p_7d4a) in that it predicts the desk, not the hook, as the overnight resting place on weekends. It is also distinct from p_4b7e (weekend thorough cleanup) in that it focuses on the bedroom, not the kitchen. If the robot finds these items at the entry hook on a weekend 03:00 pass, or at the desk on a weekday 03:00 pass, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the bedroom desk at 03:00 on a weekend (left there after a late evening session)",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Omar's pen is at the bedroom desk at 03:00 on a weekend (left there after evening writing)",
   "target": "pen_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Yuki's journal is at the bed at 03:00 on a weekend (she reads in bed before sleeping)",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 2,
   "to": 6
  },
  {
   "claim": "Omar's notebook is at the bedroom desk at 03:00 on a weekend (left there after evening study)",
   "target": "notebook_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 2,
   "to": 6
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "weekend",
    "from": 2,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekend",
    "from": 2,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekend",
    "from": 2,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pen_omar": [
   {
    "days": "weekend",
    "from": 2,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "journal_yuki": [
   {
    "days": "weekend",
    "from": 2,
    "to": 6,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
