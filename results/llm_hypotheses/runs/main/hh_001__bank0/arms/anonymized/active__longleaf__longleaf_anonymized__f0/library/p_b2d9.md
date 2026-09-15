# p_b2d9 — Home-based couple; kitchen shelf holds stored items, counter holds active ones

Two adults live here and both work from home (or one is retired and the other is a remote worker). The house is occupied from about 07:00 to 22:00 every day. The kitchen has a clear functional split: receptacle_18 is a storage shelf where object_4 (a cutting board or serving tray) and object_11 (a small appliance) are parked when not in active use; receptacle_4 is the active counter where object_15 and object_16 (small prep items, a kettle, a toaster) sit throughout the day. The desk at receptacle_12 is the shared workspace: object_14, object_19, object_21, and object_24 (laptop, notebooks, a second monitor, reference books) are there from 08:00 to 18:00 on weekdays. The living room (receptacle_10, receptacle_20) is the relaxation zone in the evening. The bedroom (receptacle_8, receptacle_13) holds personal items (object_17, object_18, object_22, object_23, object_25) that never move. The bathroom (receptacle_6, receptacle_22) holds toiletries (object_13, object_27, object_29, object_31) permanently.

What sets this apart from the other documents: (1) object_4 is at receptacle_18, NOT receptacle_4, for the entire waking day—this distinguishes it from p_f2a8 and p_c4d9 which put it on the counter. (2) object_15 and object_16 ARE at receptacle_4 (the counter), which p_f2a8 does not specify. (3) The desk is receptacle_12, not receptacle_21, distinguishing it from p_d8e3 and p_c9d4. (4) Nothing ever leaves the house: both residents work from home, so object_2, object_35, and object_3 are always present. What would refute it: object_4 found at receptacle_4 during 10:00–17:00, object_15 or object_16 NOT at receptacle_4 during 9:00–16:00, or object_2 found receptacle_2 on a weekday.

```json
{
 "claims": [
  {
   "claim": "object_4 (kitchen item) is stored on the kitchen shelf (receptacle_18), not the counter, all day",
   "target": "object_4",
   "expect": "receptacle_18",
   "days": "both",
   "from": 8,
   "to": 20
  },
  {
   "claim": "object_15 (kitchen item) is on the active counter (receptacle_4) during weekday work hours",
   "target": "object_15",
   "expect": "receptacle_4",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "object_14 (desk item) is at the shared desk (receptacle_12) during weekday work hours",
   "target": "object_14",
   "expect": "receptacle_12",
   "days": "weekday",
   "from": 8,
   "to": 18
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
  "object_11": [
   {
    "days": "both",
    "from": 7,
    "to": 21,
    "at": "receptacle_18",
    "chance": "usually"
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
    "to": 18,
    "at": "receptacle_12",
    "chance": "almost_always"
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
    "to": 18,
    "at": "receptacle_12",
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
