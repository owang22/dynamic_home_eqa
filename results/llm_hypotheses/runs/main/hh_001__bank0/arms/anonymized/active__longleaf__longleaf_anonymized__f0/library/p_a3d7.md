# p_a3d7 — Retired couple; object_26 lives at the entryway, not the living room (fork of p_7c3e)

Two retired adults live here, home all day, slow pace. The parent document (p_7c3e) placed object_26 in the living room (receptacle_10) during 09:00–21:00, but the claim has accumulated 10 for and 19 against over the full log. Forks that tried receptacle_20 (p_c1f4: 0 for, 24 against; p_3a9f: 0 for, 13 against) fared even worse. The per-object evidence is unambiguous: object_26 is sighted at receptacle_11 (the entryway) on 9 of 17 days, making it the object's modal location. It is a class_23 item—perhaps a scarf, a pair of gloves, or a small bag that the couple sets by the door after their short walks and leaves there for the rest of the day.

**What changed from the parent:** object_26's primary block is moved from receptacle_10 to receptacle_11, covering all hours. The claim is updated to test receptacle_11. All other blocks (object_2 at receptacle_11, object_4 at receptacle_18, object_13 at receptacle_6, object_15 and object_16 at receptacle_4) remain as in the parent.

What sets this apart: on all days, object_26 is at the entryway (receptacle_11), not in the living room. What would refute it: object_26 sighted at receptacle_10 or receptacle_20 during 10:00–18:00 on multiple consecutive days.

```json
{
 "claims": [
  {
   "claim": "object_26 (living room item) is at the entryway (receptacle_11) all day, not in the living room",
   "target": "object_26",
   "expect": "receptacle_11",
   "days": "both",
   "from": 0,
   "to": 24
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
   "claim": "object_4 (kitchen item) is stored on the kitchen shelf all day, not on the counter",
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
  "object_26": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_11",
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
