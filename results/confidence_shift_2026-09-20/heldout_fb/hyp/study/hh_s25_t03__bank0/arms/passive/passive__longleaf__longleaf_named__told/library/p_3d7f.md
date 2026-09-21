# p_3d7f — Omar's glasses: a full-day migration across six receptacles

Omar's glasses are the most mobile object in the house. They start the night on the nightstand, move to the bathroom shelf in the early morning (he puts them on while getting ready), go to his office desk for the work day, return to the nightstand in the mid-afternoon (a break or nap), go back to the desk for late-afternoon work, then migrate to the armchair for evening TV, and end up on the TV stand or coffee table in the late evening. This is a six-receptacle journey that no other object in the house follows.

What sets this apart: p_2a7c claims the glasses are at the desk 10–17 (a single long window) and p_6d1a claims them on the armchair 20.5–22.5. The data shows a break at 16:00 (nightstand) that interrupts the desk window, and the glasses are at the desk again at 18:00. My document captures the nightstand interlude at 15–17 and the return to the desk at 18, which the other documents miss.

What would refute it: finding the glasses at the desk at 16:00 (no nightstand break), finding them at the bathroom shelf after 9:00, or finding them at the armchair before 20:00.

```json
{
 "claims": [
  {
   "claim": "Omar's glasses are on the bathroom shelf in the early morning",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Omar's glasses are at his office desk during the main work window",
   "target": "glasses_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Omar's glasses are on the nightstand during the mid-afternoon break",
   "target": "glasses_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 15,
   "to": 17
  },
  {
   "claim": "Omar's glasses are on the armchair during evening TV",
   "target": "glasses_omar",
   "expect": "armchair_l1",
   "days": "both",
   "from": 21,
   "to": 22
  }
 ],
 "targets": {
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 6.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8.5,
    "to": 10,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 10,
    "to": 15,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 15,
    "to": 17,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 21,
    "to": 22,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
