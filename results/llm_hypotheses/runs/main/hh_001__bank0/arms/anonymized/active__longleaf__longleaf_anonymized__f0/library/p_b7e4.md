# p_b7e4 — Retired couple; object_4 makes a brief early-morning desk visit only (fork of p_8b2d)

Two retired adults live here, home all day. The parent (p_8b2d) placed object_4 at the shared desk (receptacle_12) for the full 22:00–06:00 night window. The evidence has narrowed the picture considerably: the 22:00–24:00 claim has 0 for and 4 against (the object is never at the desk in that window), while the 00:00–06:00 claim has 4 for and 17 against (it is there rarely, roughly one look in five). The mixture's worst-objects report confirms two sightings at receptacle_12 on day 16 at 05:00, but nothing in the 22:00–00:00 stretch.

**What changed from the parent:** The 22:00–24:00 block at receptacle_12 is removed entirely. The 00:00–06:00 block is kept but its chance is lowered to "rarely" to reflect the 4/21 hit rate. The day block (06:00–22:00 at receptacle_18) is unchanged. A new claim tests the 00:00–05:00 window specifically, where the day-16 sightings fell.

What sets this apart from p_8b2d: between 22:00 and 00:00, object_4 is at receptacle_18 (the kitchen shelf), NOT at the desk. The desk visit is confined to the 00:00–06:00 window and is infrequent. What would refute it: object_4 sighted at receptacle_12 during 22:00–00:00, or object_4 at receptacle_12 on more than one in three looks during 00:00–06:00.

```json
{
 "claims": [
  {
   "claim": "object_4 (kitchen item) is at the shared desk during the early-morning hours 0-5, not on the kitchen shelf",
   "target": "object_4",
   "expect": "receptacle_12",
   "days": "both",
   "from": 0,
   "to": 5
  },
  {
   "claim": "object_4 (kitchen item) is stored on the kitchen shelf during the waking day 8-20, not at the desk",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_2 (keys) is always in the house because the retired couple rarely goes far",
   "target": "object_2",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
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
    "from": 0,
    "to": 5,
    "at": "receptacle_12",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 5,
    "to": 24,
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
