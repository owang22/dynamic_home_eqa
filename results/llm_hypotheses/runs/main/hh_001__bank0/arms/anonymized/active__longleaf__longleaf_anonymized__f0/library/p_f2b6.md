# p_f2b6 — Commuter with WFH days; object_6 and object_7 out most weekdays but not all (fork of p_d6c3)

This fork of p_d6c3 adjusts the out-of-house blocks for object_6 and object_7 from "usually" to "sometimes" to account for the recurring "against" sightings. Since the last call, object_7's out-of-house claim went against twice and object_6's went against twice. The per-object data shows 2/11 found at receptacle_19 during weekday 9-17h for each, meaning on roughly 2 of 11 workdays the objects are in the house at their home shelf. This is consistent with a commuter who works from home one or two days per week (perhaps a hybrid 3-office / 2-WFH schedule).

On WFH days, the objects remain at receptacle_19 all day. On office days, they are at receptacle_2 from 09:00 to 17:00. The "sometimes" chance reflects this 3/5 or 4/5 split rather than the near-certain absence implied by "usually."

What changed from p_d6c3: the chance for object_6 and object_7 weekday 9-17h receptacle_2 blocks changed from "usually" to "sometimes." The claims are retained as-is (they still expect receptacle_2); the scoring will now weight the "weak for" (empty look at the overridden location) more heavily relative to the "against" (sighting in house), since the block's starting chance is lower. Object_11's block remains "usually" since it has 0 against and 5 weak-for.

What would refute this fork: object_6 or object_7 sighted at receptacle_19 during weekday 10:00–16:00 on four or more occasions (indicating they are in the house more than 1-2 days per week).

```json
{
 "claims": [
  {
   "claim": "object_7 (small tool) is out of the house with the commuting resident during weekday work hours",
   "target": "object_7",
   "expect": "receptacle_2",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_6 (storage item) is out of the house with the commuting resident during weekday work hours",
   "target": "object_6",
   "expect": "receptacle_2",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_11 (appliance) is out of the house with the commuting resident during weekday work hours",
   "target": "object_11",
   "expect": "receptacle_2",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_6 (storage item) is back at the storage shelf (receptacle_19) on weekends during the day",
   "target": "object_6",
   "expect": "receptacle_19",
   "days": "weekend",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "object_6": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_2",
    "chance": "sometimes"
   },
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
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_2",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_11": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "receptacle_2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_18",
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
