# p_d7a1 — Weekend sorting extends through Monday morning (fork of p_3d9e)

Fork of p_3d9e. The parent covers weekend 0–7h only. The Monday 03:00 evidence (day 6) shows the same items at the same places: journal on the bed, laptop and notebooks at the desk, pen at the desk. The sorting done on Sunday does not get undone overnight; the items stay put until the residents wake up and start moving things in the morning. This fork adds Monday 0–6h targets for the same objects, and adds a claim for pen_omar at the desk on Monday morning (the parent did not include pen_omar in its claims).

What changed: added Monday (weekday) 0–6h blocks for laptop_yuki, notebook_yuki, notebook_omar, pen_omar, and journal_yuki; added a claim for pen_omar at desk_b1 on Monday 0–6h. The weekend 0–7h blocks are unchanged from the parent.

```json
{
 "claims": [
  {
   "claim": "Yuki's journal is on the bed on a weekend overnight (she reads in bed, not at the nightstand)",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Omar's glass is in the dish rack on a weekend overnight (washed before bed)",
   "target": "glass_omar",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Yuki's laptop is at the bedroom desk on Monday at 03:00 (carried over from Sunday sorting)",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Omar's pen is at the bedroom desk on Monday at 03:00 (carried over from Sunday sorting)",
   "target": "pen_omar",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 0,
   "to": 6
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
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
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
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
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
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
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "journal_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "glass_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
