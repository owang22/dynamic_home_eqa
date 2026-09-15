# p_6b3f — Evening reorganization: object_10 stays at receptacle_17, object_26 at entryway pre-dawn (fork of p_e9a4)

This fork corrects two errors in p_e9a4. First, the claim that object_10 moves to receptacle_8 in the evening has accumulated 2 for and 15 against; object_10 remains at receptacle_17 (its primary location, 8/18 sighted days) through the evening, with its absence during weekday work hours (3 found, 11 empty at receptacle_17) explained by a midday errand or use at another location rather than an evening bedroom relocation. Second, the claim that object_1 is at receptacle_8 during weekday 14-18h (3 for, 4 against) is weak and inconsistent with the stronger p_5f2b/p_9c4e evidence placing it at receptacle_15 or receptacle_17.

What changed from p_e9a4: the object_10 evening block now keeps it at receptacle_17 instead of moving it to receptacle_8; the object_1 afternoon block is removed in favour of the receptacle_15 hypothesis in p_9c4e; the object_26 pre-dawn entryway claim is retained (6 for, 5 against — the strongest claim in the parent).

What would refute this document: object_26 sighted at receptacle_10 during 03:00-05:00 on two or more occasions; object_10 sighted at receptacle_8 during 19:00-22:00 on two or more occasions.

_(targets the fork left unstated are inherited from p_e9a4)_

```json
{
 "claims": [
  {
   "claim": "object_26 (living room item) is at the entryway (receptacle_11) during the pre-dawn hours 3-6, not at the living room",
   "target": "object_26",
   "expect": "receptacle_11",
   "days": "both",
   "from": 3,
   "to": 6
  },
  {
   "claim": "object_10 (personal item) is at receptacle_17 during the evening 18-22h, not at the bedroom shelf",
   "target": "object_10",
   "expect": "receptacle_17",
   "days": "both",
   "from": 18,
   "to": 22
  },
  {
   "claim": "object_26 (living room item) is at the living room (receptacle_10) during weekday afternoon 14-20h",
   "target": "object_26",
   "expect": "receptacle_10",
   "days": "weekday",
   "from": 14,
   "to": 20
  }
 ],
 "targets": {
  "object_10": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_17",
    "chance": "sometimes"
   }
  ],
  "object_26": [
   {
    "days": "both",
    "from": 3,
    "to": 6,
    "at": "receptacle_11",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 9,
    "to": 21,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ],
  "object_1": [
   {
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "receptacle_8",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_17",
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
  "object_13": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_6",
    "chance": "almost_always"
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
    "from": 14,
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
  "object_28": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_10",
    "chance": "usually"
   }
  ],
  "object_34": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "receptacle_21",
    "chance": "almost_always"
   }
  ]
 }
}
```
