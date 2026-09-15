# p_c9d3 — object_30 visits the bedroom shelf (receptacle_8) in the evening; object_34 is a fixed anchor

The mixture's worst-objects report caught object_30 predicted at receptacle_16 but actually at receptacle_8 four times (e.g. day 19, 16:00). The stable-anchor document p_e8b2 places object_30 at receptacle_16 all hours (for 33, against 12), and the per-object data confirms it is at receptacle_16 on 20/22 sighted days with weekday 9-17h looks finding it there 11 of 12 times. So the daytime anchor is solid. But the four evening sightings at receptacle_8 suggest a nightly or late-afternoon visit to the bedroom shelf. Object_30 has 2 distinct receptacles (receptacle_16 and receptacle_8) and 40 sightings, consistent with a two-location pattern.

Object_34 is a perfect anchor: 22/22 sighted days at receptacle_21, weekday 9-17h found 10 of 11. It never moves.

This document is distinct from p_e8b2 in that it allows object_30 to leave receptacle_16 in the evening. What would refute it: object_30 sighted at receptacle_16 during 18:00–22:00 on two or more occasions; object_34 sighted anywhere other than receptacle_21.

```json
{
 "claims": [
  {
   "claim": "object_30 is at receptacle_16 during the daytime 8-17h, not at the bedroom shelf",
   "target": "object_30",
   "expect": "receptacle_16",
   "days": "both",
   "from": 8,
   "to": 17
  },
  {
   "claim": "object_30 is at the bedroom shelf (receptacle_8) during the evening 17-22h, not at receptacle_16",
   "target": "object_30",
   "expect": "receptacle_8",
   "days": "both",
   "from": 17,
   "to": 22
  },
  {
   "claim": "object_34 is at receptacle_21 at all hours and never moves",
   "target": "object_34",
   "expect": "receptacle_21",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "object_30": [
   {
    "days": "both",
    "from": 0,
    "to": 17,
    "at": "receptacle_16",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 22,
    "at": "receptacle_8",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "receptacle_16",
    "chance": "usually"
   }
  ],
  "object_34": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "almost_always"
   }
  ],
  "object_29": [
   {
    "days": "both",
    "from": 6,
    "to": 22,
    "at": "receptacle_22",
    "chance": "almost_always"
   }
  ],
  "object_35": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_2": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
    "chance": "almost_always"
   }
  ]
 }
}
```
