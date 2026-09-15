# p_e6c1 — Retiree with a brief midday errand; objects shift once a day

One adult is retired but maintains a daily routine that includes a short errand (grocery run, post office, or a quick walk to the shops) between roughly 11:00 and 13:00 on weekdays. The rest of the day they are home. The walkthrough at 15:08 caught them back in the house, settling into the afternoon. The keys (object_2) and bag (object_35) go out during the errand window and return by 13:00. The kitchen item object_4 is at receptacle_18 (the storage shelf) all day—it is not used for the errand and is not on the counter. The counter (receptacle_4) holds object_15 and object_16. The desk at receptacle_12 holds object_14 and object_24 (a laptop and a tablet used for email and reading). The living room (receptacle_10) is the main afternoon space. The bedroom and bathroom items never move.

What sets this apart: unlike the "nothing ever leaves" documents (p_f2a8, p_d8e3, p_c9d4), this document predicts that object_2 and object_35 are receptacle_2 during a narrow weekday window (11:00–13:00). This explains the single empty look at receptacle_11 for object_2 during 9–17h without requiring a full work commute. The kitchen shelf (receptacle_18) holds object_4, distinguishing it from counter-based documents. What would refute it: object_2 found receptacle_2 outside the 11:00–13:00 weekday window, or object_4 found at receptacle_4 during 10:00–16:00.

```json
{
 "claims": [
  {
   "claim": "object_2 (keys) is out of the house during the midday errand on weekdays",
   "target": "object_2",
   "expect": "receptacle_2",
   "days": "weekday",
   "from": 11,
   "to": 13
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18), not the counter, all day",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_14 (desk item) is at the desk (receptacle_12) in the afternoon after the errand",
   "target": "object_14",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 13,
   "to": 18
  },
  {
   "claim": "object_26 (living room item) is in the living room during the afternoon",
   "target": "object_26",
   "expect": "receptacle_10",
   "days": "both",
   "from": 13,
   "to": 21
  }
 ],
 "targets": {
  "object_2": [
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "receptacle_2",
    "chance": "usually"
   },
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
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "receptacle_2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
    "chance": "almost_always"
   }
  ],
  "object_3": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_7",
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
  "object_16": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_4",
    "chance": "usually"
   }
  ],
  "object_14": [
   {
    "days": "weekday",
    "from": 8,
    "to": 18,
    "at": "receptacle_12",
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
  "object_26": [
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
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
  "object_17": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_8",
    "chance": "almost_always"
   }
  ]
 }
}
```
