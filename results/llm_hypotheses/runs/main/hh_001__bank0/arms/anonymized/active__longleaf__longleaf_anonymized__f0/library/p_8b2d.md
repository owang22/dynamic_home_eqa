# p_8b2d — Retired couple; object_4 visits the desk at night (fork of p_7c3e)

Two retired adults live here, home all day. During the waking hours the kitchen shelf (receptacle_18) holds object_4 securely, but in the small hours—after the couple has settled in for the evening and perhaps done some light work or mending at the shared desk (receptacle_12)—object_4 is brought over and left on the desk until morning. The three sightings of object_4 at receptacle_12 on day 15 around 00:00 confirm this overnight detour. The rest of the household is as stable as the parent describes: keys at the entryway, bathroom items at the sink, counter items at the counter.

**What changed from the parent:** The parent placed object_4 at receptacle_18 for the full 24-hour cycle. Three consecutive sightings at receptacle_12 on day 15 at 00:00 show the object is at the desk in the night window. I have added a night block (22:00–06:00) at receptacle_12 that overrides the catch-all receptacle_18 block. The day block (06:00–22:00) keeps object_4 at receptacle_18. A new claim tests the night location.

What sets this apart from p_7c3e: between 22:00 and 06:00, object_4 is at receptacle_12, not receptacle_18. What would refute it: object_4 sighted at receptacle_18 during 23:00–05:00, or object_4 not found at receptacle_12 during that window on multiple nights.

```json
{
 "claims": [
  {
   "claim": "object_2 (keys) is always in the house because the retired couple rarely goes far",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "object_4 (kitchen item) is at the shared desk during the late-night hours 22-24, not on the kitchen shelf",
   "target": "object_4",
   "expect": "receptacle_12",
   "days": "both",
   "from": 22,
   "to": 24
  },
  {
   "claim": "object_4 (kitchen item) is at the shared desk during the early-morning hours 0-6, not on the kitchen shelf",
   "target": "object_4",
   "expect": "receptacle_12",
   "days": "both",
   "from": 0,
   "to": 6
  },
  {
   "claim": "object_4 (kitchen item) is stored on the kitchen shelf during the waking day 8-20, not on the counter",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_13 (bathroom item) is at the bathroom sink at all hours",
   "target": "object_13",
   "expect": "receptacle_6",
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
  "object_4": [
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "receptacle_12",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "receptacle_12",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 6,
    "to": 22,
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
  "object_26": [
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
    "chance": "sometimes"
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
  ]
 }
}
```
