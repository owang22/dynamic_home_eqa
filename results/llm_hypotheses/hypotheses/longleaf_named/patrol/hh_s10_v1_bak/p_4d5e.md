# p_4d5e — Yuki's medication is a nightly bathroom routine

Yuki takes her medication every night around 21:00. The medication_yuki lives in the medicine_cabinet_ba1 during the day but is taken to the bathroom (or held ON_PERSON) between 20:30 and 22:00. Her toiletry bag is at the bathroom shelf. Omar's toiletry bag is also at the bathroom shelf. What sets this hypothesis apart: medication_yuki is NOT in the medicine cabinet between 20:30 and 22:00. What would refute it: medication_yuki sighted in medicine_cabinet_ba1 between 21:00 and 22:00.

```json
{
 "claims": [
  {
   "claim": "Yuki's medication is not in the medicine cabinet at 21:00",
   "target": "medication_yuki",
   "expect": "ON_PERSON",
   "days": "both",
   "from": 20.5,
   "to": 22
  },
  {
   "claim": "Yuki's medication is in the medicine cabinet during the day",
   "target": "medication_yuki",
   "expect": "medicine_cabinet_ba1",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "Omar's toiletry bag is at the bathroom shelf at all times",
   "target": "toiletry_bag_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Yuki's toiletry bag is at the bathroom shelf at all times",
   "target": "toiletry_bag_yuki",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "medication_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "medicine_cabinet_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20.5,
    "to": 22,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "toiletry_bag_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "toiletry_bag_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
