# p_7f2a — Marco's desk items are ON_PERSON during active work hours

Marco works from home at desk_b1 from 9 to roughly 5:30 on weekdays. During this window his laptop, charger, and notebook are open, plugged in, and in active use — physically in his hands or on his lap — rather than resting flat on the desk surface. The robot's two looks at desk_b1 during the 9–17 h window found all three items absent, which is exactly what you would expect if they are ON_PERSON. Outside work hours (early morning, evening, weekends) they return to desk_b1 to rest, which is why the per-object statistics still show desk_b1 as the "usual" place. This hypothesis directly contrasts with p_a1b2 and p_a3f7, which place these items at desk_b1 during work hours and have each taken two "against" hits on that very claim.

What would refute this document: a look at resident_2 during 9–17 h that shows none of the three items being carried, or a sighting of any of the three at a third receptacle (not desk_b1, not ON_PERSON) during the work window.

```json
{
 "claims": [
  {
   "claim": "Marco's laptop is in his hands during weekday work hours",
   "target": "laptop_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's charger is in his hands during weekday work hours",
   "target": "charger_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's notebook is in his hands during weekday work hours",
   "target": "notebook_marco",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "charger_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "notebook_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ]
 }
}
```
