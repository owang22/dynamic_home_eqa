# p_6e3b — Monday-morning carryover: weekend sorting persists into the next weekday

The weekend sorting captured by p_3d9e does not reset at midnight. On Sunday evening Yuki and Omar settle in with the laptop, notebooks, and pens at the bedroom desk, and the journal on the bed. They fall asleep in that configuration. On Monday 03:00—the robot's first pass of the new weekday—those items are still where they were left on Sunday night. Yuki does not get up at 05:00 to move her journal back to the nightstand or her laptop back to the entry hook; she wakes at 06:15, journals at the desk, and only then moves things. The Monday 03:00 pass catches the pre-morning state: the desk is loaded, the journal is on the bed, the entry hook is bare of the items that would normally be there on a weekday.

This document is distinguished from p_3d9e (which covers only weekend 0–7h) by extending the same targets into Monday 0–7h. It is distinguished from p_b2c8 and p_7d4a (which predict the entry hook as the Monday 03:00 resting spot for laptop, notebooks, and pens) by saying the entry is empty of those items on Monday morning because they were sorted to the desk on Sunday and have not been moved back. It would be refuted if the Monday 03:00 pass finds the laptop, notebooks, or pens at the entry hook, or the journal at the nightstand.

```json
{
 "claims": [
  {
   "claim": "Yuki's journal is on the bed on Monday at 03:00 (carried over from Sunday night, not yet moved to nightstand)",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Yuki's laptop is at the bedroom desk on Monday at 03:00 (sorted on Sunday, not yet moved to entry)",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Omar's notebook is at the bedroom desk on Monday at 03:00 (sorted on Sunday, not yet moved to entry)",
   "target": "notebook_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Yuki's notebook is at the bedroom desk on Monday at 03:00 (sorted on Sunday, not yet moved to entry)",
   "target": "notebook_yuki",
   "expect": "desk_b1",
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
    "to": 6,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "laptop_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pen_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
