# p_e9a4 — Evening wind-down: objects relocate to bedroom shelf and entryway after 18:00

The household follows a clear evening routine after 18:00. As the work day ends and dinner is prepared, several objects are moved from their daytime locations to secondary storage:

- object_10 (a personal item, daytime home at receptacle_17) is moved to receptacle_8 (a bedroom shelf or closet) in the evening. The robot sighted it at receptacle_8 on day 8 at 19:00, twice, when the mixture expected receptacle_17.
- object_26 (a living room item, daytime home at receptacle_10) was sighted at receptacle_11 (the entryway) on day 10 at 04:00, twice. This is very early morning, suggesting it is carried to the entryway overnight or in the pre-dawn hours, perhaps by a resident who wakes early.
- object_1 (a class_1 item, daytime home at receptacle_17) was sighted at receptacle_8 on day 9 at 15:00. Combined with 0/5 found at receptacle_17 during weekday 9-17h, object_1 may also cycle to receptacle_8 in the afternoon.

This document is distinct from the commuter-focused documents (p_d6c3, p_a3f7) and the desk-cycle documents (p_b8e2) in that it focuses on the post-work and pre-dawn relocation pattern. It does not claim any object is out of the house; all objects remain in the home. The keys (object_2) and the entryway items (object_35) are at receptacle_11 24/7 as in other documents.

What would refute this document: object_10 sighted at receptacle_17 during 19:00–23:00 on two or more occasions; object_26 sighted at receptacle_10 during 03:00–05:00 on two or more occasions.

```json
{
 "claims": [
  {
   "claim": "object_10 (personal item) is at the bedroom shelf (receptacle_8) during the evening after 18:00",
   "target": "object_10",
   "expect": "receptacle_8",
   "days": "both",
   "from": 18,
   "to": 23
  },
  {
   "claim": "object_26 (living room item) is at the entryway (receptacle_11) during the pre-dawn hours 3-6",
   "target": "object_26",
   "expect": "receptacle_11",
   "days": "both",
   "from": 3,
   "to": 6
  },
  {
   "claim": "object_1 (class_1 item) is at the bedroom shelf (receptacle_8) during weekday afternoon 14-18h",
   "target": "object_1",
   "expect": "receptacle_8",
   "days": "weekday",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "object_10": [
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "receptacle_8",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "receptacle_17",
    "chance": "sometimes"
   }
  ],
  "object_26": [
   {
    "days": "both",
    "from": 3,
    "to": 6,
    "at": "receptacle_11",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ],
  "object_1": [
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "receptacle_8",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_17",
    "chance": "usually"
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
  "object_35": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
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
  "object_15": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_4",
    "chance": "usually"
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
  ],
  "object_14": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_24": [
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "receptacle_19",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_28": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ]
 }
}
```
