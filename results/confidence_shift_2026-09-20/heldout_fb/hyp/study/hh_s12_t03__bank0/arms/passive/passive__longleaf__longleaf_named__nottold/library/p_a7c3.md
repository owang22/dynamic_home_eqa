# p_a7c3 — Priya's afternoon guitar: on the couch, 12 to 16

Elena is at her office job during the day; Priya is home and settles into her afternoon routine. The key pattern this document captures is where Priya plays guitar. The robot has seen the guitar on the couch three times at 13:00 on weekdays (and once on the bedroom floor at the same hour), which is a strong signal that the couch is her playing spot in the afternoon. Overnight and in the evening the guitar returns to the bedroom floor, where it rests against the bed. This sets the document apart from p_7ef3 (which places the guitar on the bedroom floor at midday) and p_e5f6 (which also keeps it in the bedroom). If the guitar is found on the bedroom floor repeatedly during 12–16h on weekdays, this document is refuted.

The guitar's resting place is the bedroom floor from roughly 17:00 onward (after playing ends) and through the night. In the morning before 10:00 it is still on the bedroom floor. The transition to the couch happens around 11:30–12:00 when Priya starts her afternoon music session, and back to the bedroom around 16:00–17:00.

```json
{
 "claims": [
  {
   "claim": "Priya's guitar is on the couch at 13:00 on a weekday afternoon",
   "target": "guitar_priya",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 12,
   "to": 15
  },
  {
   "claim": "Priya's guitar is back on the bedroom floor at 18:00 on a weekday",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "Priya's glasses are on the coffee table at 15:00 on a weekday",
   "target": "glasses_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 14,
   "to": 16
  }
 ],
 "targets": {
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 11.5,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 11.5,
    "to": 16.5,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11.5,
    "to": 16.5,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 16.5,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 6.5,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 14,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
