# p_d6c3 — One resident commutes to an office; tools and appliance leave the house weekdays

Two adults live here. One works from home; the other commutes to an office Monday through Friday, roughly 08:30–17:30. The commuter takes a small cluster of items with them each morning: object_6 (a storage bin or project box), object_7 (a small tool or instrument), and object_11 (a compact appliance or device used at the office). These objects are at receptacle_2 (out of the house) during the weekday work stretch. On weekends and weekday evenings, they return to their home receptacles: object_6 and object_7 go back to the storage shelf (receptacle_19), and object_11 goes back to the kitchen shelf (receptacle_18).

The evidence for this: object_6 is at receptacle_19 on 7/7 sighted days overall, but weekday 9-17h looks at receptacle_19 found it only 1 time versus 6 empty. Object_7 is at receptacle_19 on 6/7 days overall, but weekday 9-17h looks found it 0 times versus 7 empty. Object_11 is at receptacle_18 on 5/7 days overall, but weekday 9-17h looks found it 0 times versus 5 empty. On weekends, object_6 at receptacle_19 held at 0.96 (p_5c1b's claim scored 6-for / 0-against). The pattern is clean: home on weekends, absent during weekday work hours.

The keys (object_2) remain at the entryway (receptacle_11) 9/9 days—this is likely a spare set or the resident uses a key fob/phone unlock and leaves the physical keys at home. The house is otherwise occupied by the work-from-home resident from 07:00 to 22:00. The kitchen, bathroom, and living-room routines are standard.

What sets this apart: it is the only live document that places object_6, object_7, and object_11 at receptacle_2 during weekday 09:00–17:00. What would refute it: object_6, object_7, or object_11 sighted anywhere in the house during weekday 10:00–16:00 on two or more occasions.

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
    "chance": "usually"
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
    "chance": "usually"
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
