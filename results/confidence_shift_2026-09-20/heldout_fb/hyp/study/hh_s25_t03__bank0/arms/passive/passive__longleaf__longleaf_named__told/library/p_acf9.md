# p_acf9 — p_7k2m — Marco's glasses: desk during work, coffee table late evening

Marco's glasses follow a clear four-stop weekday path that no current document captures. They start the night on the nightstand (seen at 03:00 every day), move to his bedroom desk for the work day (seen at desk_b1 at 09:00, 11:00, and 11:00 again), return to the nightstand in the early evening (seen at 18:00 and 21:00), and end the night on the coffee table (seen at 22:00 and 23:00) where he reads or watches TV. On weekends the pattern shifts: he sleeps in, so the glasses stay on the nightstand until about 7, then go to the bathroom shelf for his later morning routine (seen at 07:00 and 08:00 on a weekend). In the evening he works or reads at his desk (seen at desk_b1 at 21:00 twice on a weekend) before returning them to the nightstand at 23:00.

What sets this apart: the class:glasses block in most documents (p_a1b2, p_c3d4, etc.) puts all glasses at nightstand_b1 for the full 0–24 window, which is wrong for Marco during work hours. p_9d4c has a partial weekend block for Marco's glasses at the bathroom shelf 7–9 but does not capture the weekday desk window or the late-evening coffee table stop. This document gives Marco's glasses their own full-day schedule.

What would refute it: finding Marco's glasses at the desk at 22:00 on a weekday (they should be at the coffee table), finding them at the bathroom shelf after 9:00 on a weekday, or finding them at the coffee table before 21:00.

```json
{
 "claims": [
  {
   "claim": "Marco's glasses are at his bedroom desk during weekday work hours",
   "target": "glasses_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Marco's glasses are on the coffee table during late evening on both day types",
   "target": "glasses_marco",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 22,
   "to": 23.5
  },
  {
   "claim": "Marco's glasses are on the bathroom shelf during the weekend morning routine",
   "target": "glasses_marco",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Marco's glasses are on the nightstand during the early evening after work",
   "target": "glasses_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 18,
   "to": 21
  }
 ],
 "targets": {
  "glasses_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 6.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 6.5,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 21,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 6.5,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 21,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 23,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
