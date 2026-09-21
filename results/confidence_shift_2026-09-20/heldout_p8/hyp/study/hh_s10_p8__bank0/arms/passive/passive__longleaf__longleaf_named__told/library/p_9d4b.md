# p_9d4b — Weekend afternoon desk work at the bedroom desk

On weekend afternoons (roughly 14:00 to 18:00), both residents gravitate to the bedroom desk. Yuki's laptop, which rests at the entry hook overnight and in the morning, is brought to the desk for a work or study session. Her notebook and pen follow. Omar's notebook and pen, also left at the entry hook in the morning, are moved to the desk for his own work or planning. This is a shared quiet-work period before the evening errands or social activities. The desk is the one in the bedroom (desk_b1), not the office desk (desk_o1), because the office is a weekday-only space.

This hypothesis is set apart by its specific weekend-afternoon window and its prediction that multiple work objects converge on desk_b1 simultaneously. The weekday evidence shows these objects at the entry hook in the morning (the "chaos zone" pattern) and at the desk only in the afternoon. What would refute it: if weekend-afternoon sightings show the laptop still at the entry hook, or the notebook and pen still at the entry, or if the objects are found at the office desk instead. It is also weakened if the residents are seen in the kitchen or living room at 16:00 on a weekend with the desk empty.

```json
{
 "claims": [
  {
   "claim": "Yuki's laptop is at the bedroom desk on Saturday afternoon during her work session",
   "target": "laptop_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Yuki's notebook is at the bedroom desk on Saturday afternoon, kept with the laptop",
   "target": "notebook_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Omar's notebook is at the bedroom desk on Saturday afternoon during his quiet work period",
   "target": "notebook_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Yuki's pen is at the bedroom desk on Saturday afternoon, in use for her work",
   "target": "pen_yuki",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "laptop_yuki": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "notebook_yuki": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "notebook_omar": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pen_omar": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pen_yuki": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
