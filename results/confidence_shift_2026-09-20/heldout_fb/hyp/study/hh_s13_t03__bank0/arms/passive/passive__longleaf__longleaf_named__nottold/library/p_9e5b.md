# p_9e5b — The 18:00 Drop: Entry Hook as a Brief Stop

When Hana walks through the door at 17:30, she sets her charger and water bottle on the entry hook. The robot catches both there at 18:00. But this is a 30-to-60-minute holding spot, not the overnight home. By 20:00 the charger has moved to desk_b1 (where it was also at 03:00, presumably plugged into the laptop for overnight charging), and by 23:00 it is at the nightstand (three sightings) where Hana charges her phone while she sleeps. The water bottle goes from the entry hook to the kitchen sink, where it rests overnight.

This document is distinct from p_d3e8 (Entry Mess), which predicts these items STAY at the hook through 22:00 and was refuted by seven against-votes, and from p_1d9b (Brief Entry, Then the Desk), which places items at the desk at 20:00 but does not specify the 18:00 hook stop or the water bottle. The key prediction: at 18:00 the charger and water bottle are at the entry hook, but at 20:00 they are NOT. If the robot finds the charger at the entry hook at 21:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Hana's charger is at the entry hook at 18:00 on a weekday",
   "target": "charger_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's water bottle is at the entry hook at 18:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "Hana's charger is at desk_b1 at 03:00 on a weekday",
   "target": "charger_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "Hana's water bottle is in the sink at 03:00 on a weekday",
   "target": "water_bottle_hana",
   "expect": "sink_k1",
   "days": "weekday",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "charger_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 19,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
