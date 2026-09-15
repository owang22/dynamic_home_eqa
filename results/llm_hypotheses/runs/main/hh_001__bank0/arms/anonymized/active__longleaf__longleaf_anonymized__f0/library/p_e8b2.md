# p_e8b2 — Stable anchors; seven objects have fixed homes and never stray

This house contains a set of objects that are effectively immobile: they occupy the same receptacle on nearly every sighted day and have been seen at one or two locations at most. The document makes no claims about the household's daily rhythm beyond the fact that these objects are undisturbed. The three bathroom-sink items (object_13, object_27, object_31) are always at receptacle_6. object_30 is always at receptacle_16 (17/17 days, single receptacle). object_34 is at receptacle_21 on 17/17 days. object_35 is at receptacle_11 on 17/17 days. object_29 is at receptacle_22 on 15/17 days.

This document is a claim in itself: nothing in this house moves these seven objects. They are not taken to work, not shuffled to the desk, not relocated during evening reorganization. They are fixtures. What sets this apart from the other documents (which focus on the mobile objects like object_4, object_21, object_26): here the prediction is stasis. What would refute it: any of object_29, object_30, object_34, object_35, object_13, object_27, or object_31 sighted at a receptacle other than its assigned home during 08:00–20:00.

```json
{
 "claims": [
  {
   "claim": "object_30 is at receptacle_16 at all hours and never moves",
   "target": "object_30",
   "expect": "receptacle_16",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "object_34 is at receptacle_21 at all hours and never moves",
   "target": "object_34",
   "expect": "receptacle_21",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "object_29 is at receptacle_22 during the waking day and never moves",
   "target": "object_29",
   "expect": "receptacle_22",
   "days": "both",
   "from": 6,
   "to": 22
  },
  {
   "claim": "object_35 is at the entryway (receptacle_11) at all hours and never leaves the house",
   "target": "object_35",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "object_29": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_22",
    "chance": "almost_always"
   }
  ],
  "object_30": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_16",
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
  "object_35": [
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
  ],
  "object_27": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
    "chance": "almost_always"
   }
  ],
  "object_31": [
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
