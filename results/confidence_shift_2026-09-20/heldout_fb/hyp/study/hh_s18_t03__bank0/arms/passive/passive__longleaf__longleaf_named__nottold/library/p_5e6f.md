# p_5e6f — Ines's headphones on her person in the morning, at the desk by 14:00

Ines wears her headphones during the morning work session, so they are on her person from 9 to about 13 and not visible at the desk. By 14 she sets them on the office desk, where they remain through the late afternoon (matching the cluster of sightings at desk_o1 from 14 through 17). In the evening the headphones move to the bedroom. The laptop follows the three-session pattern: desk in the morning, on her person during the midday mobile period, back at the desk by 15. The charger stays at the desk all day. Elena commutes as usual.

What sets this apart: the headphones are ON_PERSON during 9–13, explaining why desk looks in that window do not find them, while the 14–17.5 window finds them at the desk. No other document in the library separates the headphones' morning and afternoon locations.

What would refute it: a sighting of headphones_ines at desk_o1 during 9–13 on a weekday; a look at Ines showing she is not wearing them in that window; the headphones found somewhere other than the desk during 14–17.5.

```json
{
 "claims": [
  {
   "claim": "Ines's headphones are on her person during the morning work session",
   "target": "headphones_ines",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Ines's headphones are at the office desk during the afternoon work session",
   "target": "headphones_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 14,
   "to": 17.5
  },
  {
   "claim": "Ines's laptop is on her person during the midday mobile session",
   "target": "laptop_ines",
   "expect": "ON_PERSON",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Ines's headphones are in the bedroom during the evening",
   "target": "headphones_ines",
   "expect": "bed_b1",
   "days": "both",
   "from": 20,
   "to": 23
  }
 ],
 "targets": {
  "headphones_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 23,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "laptop_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 15,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 20,
    "at": "floor_o_o1",
    "chance": "sometimes"
   }
  ],
  "charger_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
