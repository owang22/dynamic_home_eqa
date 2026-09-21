# p_e4c8 — Journal at the Desk: Marco's Midday Prep

Marco's journal is not a nightstand object all day. He keeps it at the nightstand overnight and in the early morning, but between roughly 11:00 and 14:00 on weekdays he moves it to the bedroom desk for his pre-work journaling and planning session. He is home from about 07:00 to 13:40 on weekdays, and the midday block is when he sits down to write before heading out. The journal returns to the nightstand by 17:00 (he is at work until 22:00, so it simply stays put overnight).

This document directly corrects p_b7c2's claim that the journal is at the nightstand from 6:00 to 12:00, which has gone against twice. The sightings show journal_marco at desk_b1 at 12:00 (twice on the same day) and at nightstand_b1 at 03:00 and 18:00. The 12:00 sighting at the desk is the critical data point: the journal is at the desk during the midday window, not the nightstand.

Refutation: if the journal is found at the nightstand at 12:00 or 13:00 on a weekday, or at the desk at 03:00, this document is wrong.

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
   "claim": "Marco's journal is at the nightstand at 03:00 on a weekday",
   "target": "journal_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 2,
   "to": 5
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
    "to": 11,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 14,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
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
