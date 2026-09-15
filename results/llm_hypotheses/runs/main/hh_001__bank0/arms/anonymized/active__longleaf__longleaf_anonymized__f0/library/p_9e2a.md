# p_9e2a — object_11 commutes out of the house during weekday work hours

One resident commutes to an office or workshop on weekdays, taking object_11 (a small appliance, possibly a portable mixer, blender, or heated tool) with them. The object lives at the kitchen shelf (receptacle_18) on weekends and weekday mornings before 9 and evenings after 17, but during the 9–17 window it is out of the house (receptacle_2). The per-object evidence is striking: during weekday 9–17h, looks at receptacle_18 found object_11 only 1 of 14 times, while 13 looks found nothing. The p_d6c3 and p_f2b6 documents already predict this out-of-house pattern and each accumulated 13 weak-for scores (empty looks at receptacle_18 during the window), with only 1 against (a single in-house sighting). No other in-house location has been confirmed: receptacle_13 (p_e4b7, 1 for / 42 against), receptacle_8 (p_4d8a, 0 for / 15 against), and receptacle_4 (p_3a7d, 0 for / 18 against) all failed.

What sets this apart: unlike p_b2d9 and its forks which keep object_11 at receptacle_18 all day, this document predicts the object is absent from the house entirely during weekday work hours. Unlike p_d6c3, it does not also claim object_6 or object_7 leave the house (their out-of-house claims have 0 for and only modest weak-for counts). The object returns by 17:00 and sits on the kitchen shelf through the evening. What would refute it: object_11 sighted at any in-house receptacle during weekday 10:00–16:00 on 3+ separate days, or object_11 consistently found at a specific in-house receptacle (other than receptacle_18) during the 9–17 window.

```json
{
 "claims": [
  {
   "claim": "object_11 (appliance) is out of the house with the commuting resident during weekday work hours",
   "target": "object_11",
   "expect": "receptacle_2",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_11 (appliance) is at the kitchen shelf (receptacle_18) on weekends during the day",
   "target": "object_11",
   "expect": "receptacle_18",
   "days": "weekend",
   "from": 8,
   "to": 18
  },
  {
   "claim": "object_4 (kitchen item) is on the kitchen shelf (receptacle_18) all day, not the counter",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "object_11": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_18",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_2",
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
  ]
 }
}
```
