# p_7f3a — Weekend Guitar Rests on the Couch, Not Played

Hana and Priya live together. Hana works weekdays 8-to-5:30; Priya is retired and home most of the day. On weekends both are "around the house more" per their own message. This document focuses on the guitar: the three documents that claimed Hana plays it ON_PERSON at 16:00 Saturday were all refuted three times since the last call. The Saturday 16:00 pass found the guitar at couch_l1 (twice) and bedroom_floor_b1 (once). Hana does not pick up the guitar on Saturday afternoons; it leans against the couch where she sits reading or snacking, or it stays on its bedroom floor. The weekday pattern is unchanged: the guitar rests on bedroom_floor_b1 all day and is found there at the 03:00 and 18:00 passes.

What sets this document apart: it denies the ON_PERSON guitar claim on weekends entirely. If the robot ever sees Hana holding the guitar in the living room on a Saturday between 14:00 and 18:00, this document is wrong. If the guitar is consistently on the couch or bedroom floor during that window, this document is right.

```json
{
 "claims": [
  {
   "claim": "The guitar is on the couch on a Saturday afternoon, not being played",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 15,
   "to": 17
  },
  {
   "claim": "The guitar is on the bedroom floor on a Saturday morning before Hana gets up",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 0,
   "to": 10
  },
  {
   "claim": "The guitar is on the bedroom floor on a weekday evening after Hana gets home",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 17,
   "to": 19
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
