# p_c9d2 — Omar's work: laptop shuttles between desk and coffee table; glasses trace a morning path

Omar works from home at desk_o1 but is not as anchored to the desk as Marco. His laptop (and charger) migrate to the coffee table during midday — sightings show laptop_omar at both desk_o1 and coffee_table_l1 at 11:00 and 16:00, and at coffee_table alone at 16:00. The charger follows the same pattern. His headphones stay at the desk or on the couch. His glasses follow a clear daily path: nightstand overnight, bathroom shelf during the 7:00 morning routine, desk during morning work, back to nightstand mid-afternoon, desk again in the late afternoon, then armchair or TV stand in the evening.

This document is distinct from p_5c1f (which put Omar's laptop at coffee_table 11-16h) in that it acknowledges the laptop is at BOTH locations during that window — he moves between them. It is distinct from p_5e1c (glasses path) in that it adds the work-hour laptop/charger blocks and the evening glasses location.

What would refute it: if Omar's laptop is found at a third location (not desk_o1 or coffee_table_l1) during 9–17 h, or if his glasses are consistently at the desk all day without visiting the bathroom, the path model breaks.

```json
{
 "claims": [
  {
   "claim": "Omar's glasses are on the bathroom shelf during his weekday morning routine",
   "target": "glasses_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Omar's laptop is at the coffee table during midday work on weekdays",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Omar's charger follows the laptop to the coffee table during midday",
   "target": "charger_omar",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Omar's glasses are at the nightstand overnight",
   "target": "glasses_omar",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Omar's headphones are at the desk during weekday work hours",
   "target": "headphones_omar",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "charger_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 16,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "headphones_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 16,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 16,
    "to": 18,
    "at": "desk_o1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "mouse_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "notebook_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ]
 }
}
```
