# p_4e7a — Weekend Evening Guitar on the Couch

Hana's guitar does not stay in her bedroom all week. On weekdays it rests on bedroom_floor_b1 (confirmed by 3 sightings at 03:00 and 1 at 18:00), but on weekend evenings she drags it out to the living room and plays it on the couch. The weekend 21:00 pass caught it on couch_l1 twice (and once still on the bedroom floor, likely mid-move). The mixture's worst-objects list flags this: predicted bedroom_floor_b1, actually couch_l1, 2×. Every top-weighted document that claims "guitar stays in her bedroom all week" is bleeding weight on this exact miss.

This hypothesis predicts that on weekends from roughly 19:00 to 23:00 the guitar is on couch_l1, Hana is in the living room playing, and the blanket is draped over the couch beside her. On weekdays the guitar never leaves bedroom_floor_b1. What would refute it: a weekend evening pass (19–23 h) that finds the guitar still on bedroom_floor_b1, or finds it on the couch on a weekday evening.

```json
{
 "claims": [
  {
   "claim": "On weekend evenings Hana plays guitar on the couch in the living room",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 19,
   "to": 23
  },
  {
   "claim": "On weekdays the guitar stays in her bedroom all day",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 6,
   "to": 22
  },
  {
   "claim": "The blanket is on the couch beside her during weekend guitar playing",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
