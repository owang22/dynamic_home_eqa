# p_c9f2 — Project-based home; receptacle_19 is the afternoon parking shelf

Two adults live here and both do flexible, project-based work from home. Their rhythm is not clock-based but task-based: in the morning (08:00–12:00) they are at the desk (receptacle_12) working through a to-do list, and in the afternoon (12:00–18:00) they shelve their materials on a large storage unit at receptacle_19 while they take a break, do errands around the house, or relax in the living room. This means several desk-adjacent items—object_14 (laptop/notebook), object_24 (tablet/reference books), object_5 (a second accessory), object_20 (another work item), and object_7 (a small tool or charger)—cycle between receptacle_12 in the morning and receptacle_19 in the afternoon on weekdays. On weekends the items stay at receptacle_12 or go to the living room.

The kitchen routine is the same as the dominant model: object_4 is parked on the kitchen shelf (receptacle_18) all day; object_15 and object_16 are on the active counter (receptacle_4). Nothing leaves the house. The bathroom (receptacle_6) and bedroom (receptacle_8, receptacle_13) items are static.

What sets this apart from p_b2d9 and p_a7e3: it extends the afternoon-shelf pattern to multiple objects (object_5, object_20, object_7) in addition to object_14 and object_24, and it frames the movement as task-completion rather than a fixed clock. What would refute it: object_14 or object_24 found at receptacle_12 during 13:00–17:00 on a weekday, or object_5 found at receptacle_19 during 08:00–11:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "object_14 (desk item) is at the desk (receptacle_12) in the morning but parked at the storage shelf (receptacle_19) in the afternoon on weekdays",
   "target": "object_14",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 13,
   "to": 17
  },
  {
   "claim": "object_24 (desk item) is at the storage shelf (receptacle_19) in the afternoon on weekdays after work wraps up",
   "target": "object_24",
   "expect": "receptacle_19",
   "days": "weekday",
   "from": 13,
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
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "receptacle_12",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 12,
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
  "object_24": [
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "receptacle_12",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
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
  "object_5": [
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "receptacle_21",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "receptacle_19",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "usually"
   }
  ],
  "object_20": [
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "receptacle_12",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "receptacle_19",
    "chance": "sometimes"
   },
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
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "receptacle_19",
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
