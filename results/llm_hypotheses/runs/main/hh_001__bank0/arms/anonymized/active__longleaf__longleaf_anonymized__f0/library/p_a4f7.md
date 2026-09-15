# p_a4f7 — Daily desk cycle with mobile object_17 (fork of p_b8e2)

This fork corrects the object_17 prediction. The parent p_b8e2 placed object_17 at receptacle_19 during weekday 05:00–08:00, but that claim has now accumulated 23-against / 9-for over the full log, and two more against-tallies came in since the last call (day 12, 07:00 looks found object_17 at receptacle_12, not receptacle_19). The per-object data confirms: object_17 is mostly at receptacle_12 (7/14 sighted days) but is extremely mobile (8 distinct receptacles, 55 sightings). During weekday 09:00–17:00 looks at receptacle_12, it was found only 3 times out of 12, meaning it is at the desk roughly a quarter of the time during the work stretch.

The revised model keeps the core desk-cycle structure (object_20, object_21, object_16 pulled to the desk in the morning) but treats object_17 as a mobile desk-adjacent item: it is at receptacle_12 "sometimes" during the waking day (08:00–20:00) and is not reliably parked at receptacle_19 in the early morning. The early-morning receptacle_19 block is removed entirely; object_17 simply falls through to the robot's sighting statistics before 08:00.

What changed from p_b8e2: object_17 no longer has a 05:00–08:00 receptacle_19 block; its daytime block is now "sometimes" at receptacle_12 instead of "usually." The claim about object_17 is updated to reflect its mobile nature. What would refute this fork: object_17 found at receptacle_19 during weekday 05:00–08:00 on two or more occasions (reviving the parent's claim), or object_17 found at receptacle_12 on more than 80% of weekday 09:00–17:00 looks (indicating a stronger "usually" block is warranted).

```json
{
 "claims": [
  {
   "claim": "object_20 (storage item) is at the shared desk (receptacle_12) during weekday morning setup 7-9h",
   "target": "object_20",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "object_17 (desk item) is at the shared desk (receptacle_12) during weekday work hours, not at the storage shelf",
   "target": "object_17",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_16 (kitchen item) is at the shared desk (receptacle_12) during weekday early morning 7-9h",
   "target": "object_16",
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
  }
 ],
 "targets": {
  "object_17": [
   {
    "days": "both",
    "from": 8,
    "to": 20,
    "at": "receptacle_12",
    "chance": "sometimes"
   }
  ],
  "object_20": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
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
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "receptacle_12",
    "chance": "sometimes"
   },
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
