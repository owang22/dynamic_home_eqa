# p_8e1c — object_21 and object_20 are desk-residents; no overnight storage-shelf park (fork of p_f4a9)

The parent (p_f4a9) placed object_21 at the storage shelf (receptacle_19) overnight (00:00–08:00) and object_20 at the storage shelf all day. Both placements are now badly contradicted. Object_21's overnight claim has 15 for, 66 against (19% hit rate), and the mixture's worst-objects report caught it predicted at receptacle_19 but actually at receptacle_12 three times (e.g. day 21, 07:00). Object_20's all-day receptacle_19 claim has 34 for, 80 against (30% hit rate), and the mixture caught it predicted at receptacle_19 but actually at receptacle_12 (day 18, 19:00). Object_21 is at receptacle_12 on 14/23 sighted days; object_20 is at receptacle_12 on 7/22 days but with 90 sightings and weekday 9-17h looks finding it there 8 of 17 times.

**What changed from the parent:** I have removed the 00:00–08:00 receptacle_19 block for object_21 and replaced it with a continuous receptacle_12 block. I have removed the all-day receptacle_19 block for object_20 and replaced it with a receptacle_12 block (the desk is its primary home, with occasional visits to the storage shelf). The storage-shelf cluster for object_5 (0.86 on 76 sightings — excellent) is retained. object_28 at the desk during work hours (0.85 on 71 sightings) is retained. The other storage-shelf objects (object_6, object_7, object_9, object_12, object_23) are kept at receptacle_19 as a default, but their weekday work-hour absence is acknowledged by the low hit rates.

What sets this apart from p_3d7a: here object_20 is at the desk as its primary home (not the storage shelf), and the storage-shelf cluster is explicitly maintained for object_5. What would refute it: object_21 sighted at receptacle_19 during 01:00–07:00 on two or more occasions; object_20 sighted at receptacle_19 during weekday 09:00–14:00 on two or more occasions.

_(targets the fork left unstated are inherited from p_f4a9)_

```json
{
 "claims": [
  {
   "claim": "object_21 (desk item) is at the shared desk (receptacle_12) during the early morning 5-9h, not at the storage shelf",
   "target": "object_21",
   "expect": "receptacle_12",
   "days": "both",
   "from": 5,
   "to": 9
  },
  {
   "claim": "object_20 (storage item) is at the shared desk (receptacle_12) during weekday work hours 9-17h",
   "target": "object_20",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_28 (living room item) is at the shared desk (receptacle_12) during weekday work hours",
   "target": "object_28",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_5 (storage item) is at the storage shelf (receptacle_19) during weekday work hours 9-17h",
   "target": "object_5",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
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
    "from": 8,
    "to": 20,
    "at": "receptacle_18",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_18",
    "chance": "usually"
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_17": [
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ],
  "object_28": [
   {
    "days": "weekday",
    "from": 8,
    "to": 20,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "sometimes"
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
  "object_5": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_6": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_7": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_9": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_12": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_23": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
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
  "object_26": [
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ],
  "object_20": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_12",
    "chance": "usually"
   }
  ]
 }
}
```
