# p_2e9d — Overnight parking at receptacle_21: a cluster of objects shifts there between 19:00 and 06:00

Several objects show up at receptacle_21 in the evening and early morning when the mixture expected them elsewhere: object_6 (2x at 19:00, day 23), object_25 (1x at 05:00, day 22), object_24 (1x at 06:00, day 22), object_23 (1x at 05:00, day 22). Receptacle_21 is already the fixed home of object_34 (25/25 days) and the primary location of object_25 (13/25 days). This suggests receptacle_21 is a secondary storage shelf or closet where residents park items at the end of the day before bed, and from which they retrieve them in the early morning.

This document is distinct from the desk-cycle documents (p_b8e2, p_3d7a) which focus on morning setup at receptacle_12, and from the storage-shelf documents (p_5c1b, p_7f3a) which anchor objects at receptacle_19. Here, receptacle_21 is the evening/overnight parking spot for a rotating set of objects, while their daytime locations (receptacle_19, receptacle_12, receptacle_20) remain as in other documents.

No objects leave the house in this document; the keys (object_2) and entryway items (object_35) stay at receptacle_11 24/7.

What would refute this document: object_6 sighted at receptacle_19 during 20:00-23:00 on two or more occasions; object_25 sighted at receptacle_21 during weekday 10:00-15:00 (which would mean it is there all day, not just overnight).

```json
{
 "claims": [
  {
   "claim": "object_6 (storage item) is at receptacle_21 during the evening 19-23h, not at the storage shelf",
   "target": "object_6",
   "expect": "receptacle_21",
   "days": "both",
   "from": 19,
   "to": 23
  },
  {
   "claim": "object_25 (personal item) is at receptacle_21 during the pre-dawn hours 4-7h, not at the storage shelf",
   "target": "object_25",
   "expect": "receptacle_21",
   "days": "both",
   "from": 4,
   "to": 7
  },
  {
   "claim": "object_24 (desk item) is at receptacle_21 during the pre-dawn hours 5-8h, not at the desk",
   "target": "object_24",
   "expect": "receptacle_21",
   "days": "both",
   "from": 5,
   "to": 8
  }
 ],
 "targets": {
  "object_6": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 24,
    "at": "receptacle_21",
    "chance": "sometimes"
   }
  ],
  "object_25": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "usually"
   }
  ],
  "object_24": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 5,
    "to": 8,
    "at": "receptacle_21",
    "chance": "sometimes"
   }
  ],
  "object_23": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 4,
    "to": 7,
    "at": "receptacle_21",
    "chance": "sometimes"
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
  "object_34": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "almost_always"
   }
  ],
  "object_4": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_18",
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
