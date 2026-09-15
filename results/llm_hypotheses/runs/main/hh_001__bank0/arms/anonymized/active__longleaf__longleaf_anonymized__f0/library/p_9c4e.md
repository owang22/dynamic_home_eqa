# p_9c4e — object_1 at receptacle_15 during work hours, not the desk (fork of p_5f2b)

This fork corrects the central error of p_5f2b: object_1 is NOT at the shared desk (receptacle_12) during weekday work hours. The desk claim has accumulated 0 for and 20 against over the full log, and the per-object evidence confirms that weekday 9-17h looks at receptacle_17 found object_1 zero times while 14 looks found nothing. The mixture's worst-objects report since the last call caught object_1 at receptacle_15 three times (day 22, 22:00) and at receptacle_8 once (day 22, 06:00). With only 3 distinct receptacles across 47 sightings, the most parsimonious reading is a two-location shuttle between receptacle_17 (morning/evening anchor) and receptacle_15 (weekday work-hours parking), with occasional early-morning appearances at receptacle_8.

What changed from p_5f2b: the weekday 7-17h block now points to receptacle_15 instead of receptacle_12; the evening block splits between receptacle_17 and receptacle_15; a new early-morning block allows receptacle_8. The claims are rewritten to target receptacle_15 during work hours.

What would refute this document: object_1 sighted at receptacle_12 during weekday 10:00-15:00 on two or more occasions; object_1 sighted at receptacle_17 during weekday 10:00-14:00 on two or more occasions.

```json
{
 "claims": [
  {
   "claim": "object_1 (class_1 item) is at receptacle_15 during weekday work hours 9-16h, not at receptacle_17 or the desk",
   "target": "object_1",
   "expect": "receptacle_15",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "object_1 (class_1 item) is at receptacle_17 during the evening 18-22h, not at receptacle_15",
   "target": "object_1",
   "expect": "receptacle_17",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "object_1 (class_1 item) is at receptacle_17 during weekday early morning 4-7h, not at receptacle_15",
   "target": "object_1",
   "expect": "receptacle_17",
   "days": "weekday",
   "from": 4,
   "to": 7
  }
 ],
 "targets": {
  "object_1": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "receptacle_17",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 17,
    "at": "receptacle_15",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 24,
    "at": "receptacle_17",
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
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
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
  "object_29": [
   {
    "days": "both",
    "from": 6,
    "to": 22,
    "at": "receptacle_22",
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
  ]
 }
}
```
