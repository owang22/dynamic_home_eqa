# p_e6a1 — object_20 at the desk weekday mornings; object_24 shuttles to receptacle_21 early (fork of p_8e2f)

This fork addresses two misprediction patterns in the parent p_8e2f. First, object_20 (class_18) was predicted at receptacle_21 or receptacle_19 but found at receptacle_12 (the desk) twice on day 5 at 08:00. The per-object data shows object_20 is at 3 distinct receptacles and was found at receptacle_19 only 1 of 5 times during weekday 9–17h looks. The pattern suggests object_20 is brought to the desk in the early morning (07:00–12:00) for reference or use, then returned to its storage location later in the day. Second, object_24 (class_21) was found at receptacle_21 on day 6 at 07:00 (twice), before the workday begins. The per-object data shows object_24 is at 3 distinct receptacles and is solidly at receptacle_12 during 09:00–17:00 (found 4 of 5 looks). The early-morning sightings at receptacle_21 suggest object_24 is stored there overnight and moved to the desk when work begins.

The parent's core prediction (object_14 and object_24 at the desk during work hours) is retained. The kitchen, bathroom, and entryway routines are unchanged. Nothing leaves the house.

What changed from p_8e2f: object_20 gains a weekday 07:00–12:00 block at receptacle_12 (desk) before falling back to receptacle_19; object_24 gains a weekday 00:00–08:00 block at receptacle_21 before moving to the desk. What would refute this fork: object_20 found at receptacle_19 during weekday 08:00–10:00, or object_24 found at receptacle_12 during weekday 05:00–07:00.

```json
{
 "claims": [
  {
   "claim": "object_20 (storage item) is at the shared desk (receptacle_12) during weekday early morning hours 7-12",
   "target": "object_20",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 7,
   "to": 12
  },
  {
   "claim": "object_24 (desk item) is at the secondary shelf (receptacle_21) during weekday early morning before work",
   "target": "object_24",
   "expect": "receptacle_21",
   "days": "weekday",
   "from": 0,
   "to": 8
  },
  {
   "claim": "object_14 (desk item) stays at the desk (receptacle_12) for the full weekday working stretch 9-17h",
   "target": "object_14",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
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
    "from": 0,
    "to": 8,
    "at": "receptacle_21",
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
  "object_5": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_19",
    "chance": "usually"
   }
  ],
  "object_20": [
   {
    "days": "weekday",
    "from": 7,
    "to": 12,
    "at": "receptacle_12",
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
