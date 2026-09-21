# p_3d9e — Sunday-night sorting: entry dump moves to bedroom desk, journal to bed

Yuki and Omar are home all day on weekends, and by the time they settle in for the second weekend night (Sunday), the items that were dumped at the entry on Saturday have been carried in and set at the bedroom desk. On Saturday night the entry still holds the laptop, notebooks, and pens (they cycled in, dropped everything, went to bed). But Sunday they've been around the house, working and reading at the desk, and the items stay there overnight. Yuki's journal, which sits on the nightstand on weekday nights, ends up on the bed on weekends—she reads in bed rather than at the desk. Omar's glass, washed before bed on the weekend, dries in the dish rack rather than sleeping in the sink. His lunchbox, emptied and put away during the day, goes back in the cupboard.

This document sets itself apart by predicting the *second* weekend night differently from the first. Where p_b2c8 and p_7d4a say the entry is a permanent chaos zone, this says the chaos resolves by Sunday morning. Where p_7a3f and p_4e91 focus on weekday commuting, this captures the weekend overnight state. It would be refuted if, on a weekend 03:00 pass, the laptop and notebooks are still at the entry hook AND the journal is at the nightstand—meaning no sorting happened at all.

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
   "claim": "Yuki's laptop is at the bedroom desk on a weekend overnight (sorted from the entry during the day)",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 0,
   "to": 7
  },
  {
   "claim": "Omar's notebook is at the bedroom desk on a weekend overnight (sorted from the entry)",
   "target": "notebook_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 0,
   "to": 7
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
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
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
   }
  ],
  "pen_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 7,
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
