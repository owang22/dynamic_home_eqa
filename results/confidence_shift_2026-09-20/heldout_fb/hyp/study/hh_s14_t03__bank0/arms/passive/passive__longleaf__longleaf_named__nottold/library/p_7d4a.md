# p_7d4a — Journal at the Desk: Extended Window (fork of p_e4c8)

This fork corrects p_e4c8 in two ways the evidence demands. First, the 6:00–12:00 nightstand claim has now gone against twice (on p_b7c2 and p_8e2f), and the 12:00 sightings place the journal at desk_b1 on both observed days. The journal is at the desk from early morning through midday, not just from 11:00. Second, the 03:00 sighting split (one day nightstand, one day desk) shows the journal sometimes stays at the desk overnight after a late writing session, so the overnight block is no longer a clean "usually nightstand."

What changed from p_e4c8: the desk window is extended from 11–14 h to 6–14 h on weekdays; the overnight block (0–6 h) is split between nightstand (usually) and desk (sometimes); the 17–22 h evening block is downgraded to "sometimes" at nightstand because the claim went against three times (the journal was found elsewhere in that window). The 11.5–13.5 h desk claim is retained because it has scored 2-for, 0-against.

Refutation: if the journal is found at the nightstand at 08:00 or 10:00 on a weekday, or at the desk at 03:00 on three or more consecutive days, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Marco's journal is at the bedroom desk during his weekday midday writing session",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 11.5,
   "to": 13.5
  },
  {
   "claim": "Marco's journal is at the bedroom desk in the early morning before he leaves",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 7,
   "to": 11
  },
  {
   "claim": "Marco's journal is at the nightstand in the evening after he gets home",
   "target": "journal_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 17,
   "to": 22
  }
 ],
 "targets": {
  "journal_marco": [
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "desk_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 6,
    "to": 14,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ]
 }
}
```
