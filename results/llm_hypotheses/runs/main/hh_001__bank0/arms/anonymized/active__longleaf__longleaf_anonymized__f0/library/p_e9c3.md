# p_e9c3 — Project-based home; object_17 at the desk, not the bedroom shelf (fork of p_8e2f)

This fork corrects the object_17 placement. The parent p_8e2f (and its ancestor p_c9f2) placed object_17 at receptacle_8 (the bedroom shelf) for the full 24-hour cycle with "almost_always" confidence. That block has now failed across ten documents (0.15 on 29 sightings), and the per-object data shows object_17 is mostly at receptacle_12 (7/14 sighted days), not receptacle_8. The object is highly mobile (8 distinct receptacles, 55 sightings), but its modal location is the shared desk, not the bedroom.

The revised model keeps the project-based framing: two adults work from home, desk items stay at receptacle_12 for the full weekday stretch. object_17 is now placed at receptacle_12 "sometimes" during the waking day (08:00–20:00), reflecting that it is at the desk on about half of sighted days but is frequently moved to other locations. The 09:00–17:00 weekday looks at receptacle_12 found it 3 times out of 12, supporting "sometimes" rather than "usually."

What changed from p_8e2f: object_17 moved from receptacle_8 (all day, almost_always) to receptacle_12 (08:00–20:00, sometimes). All other blocks and claims are unchanged. What would refute this fork: object_17 found at receptacle_8 on more than 60% of sighted days over the next week, or object_17 found at receptacle_12 on more than 80% of weekday 09:00–17:00 looks (warranting "usually").

```json
{
 "claims": [
  {
   "claim": "object_14 (desk item) stays at the desk (receptacle_12) for the full weekday working stretch 8-18h",
   "target": "object_14",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_17 (desk item) is at the shared desk (receptacle_12) during weekday work hours, not the bedroom shelf",
   "target": "object_17",
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
  },
  {
   "claim": "object_2 (keys) is always in the house because both residents work from home",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
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
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
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
    "from": 8,
    "to": 20,
    "at": "receptacle_12",
    "chance": "sometimes"
   }
  ]
 }
}
```
