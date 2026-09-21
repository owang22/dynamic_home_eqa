# p_3d7e — Omar's tablet lives at the nightstand; kitchen table only at 10:00 breakfast

Omar works afternoon-to-night shifts and is home in the morning. The robot's passes show his tablet sitting at the bedroom nightstand from 00:00 through 22:00 on every weekday, with a single exception: at 10:00 it appears at the kitchen table (2 of 3 passes) alongside his mug, bowl, and vitamins — a ten-minute breakfast. After that it returns to the nightstand by 12:00 and stays there. The "kitchen chair all morning" model (p_e5f6) has been contradicted 8 times since the last call; the nightstand is where the tablet actually rests.

This document sets itself apart by placing the tablet at nightstand_b1 for the entire 12:00–22:00 window (when Omar is at work or gaming) and limiting the kitchen-table appearance to a narrow 9:50–10:30 breakfast slot. It refutes if the tablet is found at chair_k1 or kitchen_table_k1 outside that 30-minute window on a weekday, or if it is absent from the nightstand during 12:00–16:00.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand during his midday window on weekdays",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand during his evening gaming on weekdays",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Omar's tablet is at the kitchen table during his 10:00 breakfast on weekdays",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.8,
   "to": 10.5
  },
  {
   "claim": "Omar's tablet is NOT at the kitchen chair during his 14:00 window on weekdays (he is at work)",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 16
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 9.8,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
