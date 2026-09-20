# p_ef4f — The Vacuum Ritual: Deep clean Saturday morning

The vacuum cleaner is stored at entry_floor_e1 on all days except Saturday morning, when the household does a deep clean from 9:00 to 11:00. During that window the vacuum is in use (ON_PERSON or in the room being cleaned). By 11:00 it is back at the entry. On other days it is untouched. The doormat stays at the entry floor always.

What sets this hypothesis apart: on Saturday at the 8:00 or 12:00 patrol, the vacuum_cleaner_shared may be absent from entry_floor_e1 (in use or in another room). On all other days it is at the entry. This is a once-a-week event.

What would refute it: vacuum_cleaner_shared sighted at entry_floor_e1 at 9:00 on a Saturday (it should be in use), or sighted OUT_OF_HOUSE on a Tuesday.

```json
{
 "claims": [
  {
   "claim": "The vacuum is at the entry floor on Tuesday midday",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The vacuum is at the entry floor on Wednesday midday",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The vacuum is not at the entry floor on Saturday morning (in use)",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 9,
   "to": 11
  },
  {
   "claim": "The doormat is at the entry floor on all days",
   "target": "doormat_shared",
   "expect": "entry_floor_e1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 11,
    "at": "ON_PERSON",
    "chance": "sometimes"
   }
  ],
  "doormat_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "almost_always"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ]
 }
}
```
