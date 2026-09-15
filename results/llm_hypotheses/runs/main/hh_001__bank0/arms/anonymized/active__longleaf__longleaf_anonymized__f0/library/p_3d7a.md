# p_3d7a — Desk-resident items; object_17 stays at the desk, no early-morning shelf park (fork of p_b8e2)

The parent (p_b8e2) proposed a tight daily cycle in which storage-shelf items are pulled to the desk at 07:00 and parked back at 15:00. The core cycle idea survives for object_21 (for 11, against 15 on its early-morning desk claim) and partially for object_20 (for 8, against 15). However, the parent's most distinctive claim — object_17 parked at receptacle_19 in the early morning (05:00–08:00) — has collapsed: 9 for, 40 against in total, and 10 against with 0 for since the last call. Object_17 is at receptacle_12 on 13 of 22 sighted days and has 9 distinct receptacles, indicating it is a desk-resident with occasional excursions, not a shelf-parked item.

**What changed from the parent:** I have removed the weekday 05:00–08:00 block placing object_17 at receptacle_19 and replaced it with a continuous "at the desk" block. I have also downgraded object_16's morning desk visit from "sometimes" to "rarely" (its claim has 4 for, 16 against total, and 3 against since the last call), and object_20's morning desk visit from "usually" to "sometimes" (8 for, 15 against). The afternoon parking of object_24 at receptacle_19 (14:00–18:00) is retained from the parent.

What sets this apart from p_f4a9: here object_17 is at the desk all day with no overnight shelf park, and object_16 is almost always at the counter (receptacle_4) rather than the desk. What would refute it: object_17 sighted at receptacle_19 during weekday 05:00–09:00 on two or more occasions; object_21 sighted at receptacle_19 during weekday 06:00–08:00.

```json
{
 "claims": [
  {
   "claim": "object_17 (desk item) is at the shared desk (receptacle_12) during weekday early morning 5-9h, not at the storage shelf",
   "target": "object_17",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 5,
   "to": 9
  },
  {
   "claim": "object_20 (storage item) is at the shared desk (receptacle_12) during weekday morning setup 7-9h",
   "target": "object_20",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "object_21 (desk item) is at the shared desk (receptacle_12) during weekday early morning 6-8h",
   "target": "object_21",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 6,
   "to": 8
  },
  {
   "claim": "object_16 (kitchen item) is at the active counter (receptacle_4) during weekday early morning 7-9h, not at the desk",
   "target": "object_16",
   "expect": "receptacle_4",
   "days": "weekday",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "object_17": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_20": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "receptacle_12",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_21": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_16": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_4",
    "chance": "usually"
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
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
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
  ],
  "object_26": [
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ]
 }
}
```
