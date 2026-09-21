# p_2e8a — Yuki's keys and wallet rest on the entry table; phone travels to the dining table at dinner

Yuki's keys and wallet are set on the small entry table (entry_table_e1) when she comes home, not on the floor. The hourly sightings at 20:00 and 22:00 show entry_table_e1 x2 versus entry_floor_e1 x1 for the keys, and the wallet is at entry_table_e1 on all four sighted days with 12/12 empty looks during work hours (confirming it goes out with her). The wallet's resting spot is exclusively entry_table_e1 (single receptacle, 23 sightings). Yuki's phone rests at coffee_table_l1 during the day (2/3 sighted days, 13 sightings) but moves to dining_table_d1 at 20:00 (sighting confirms dining_table_d1 x1 at that hour).

This document is set apart from p_3f8a (which puts keys at entry_floor_e1, now 9 against) and from p_b2c8 (which puts keys at entry_floor_e1 as the base block). It adds the phone's dinner migration, which no other document tracks. The keys and wallet are table objects, not floor objects.

Refutation: keys_yuki or wallet_yuki sighted at entry_floor_e1 on three or more consecutive weekday evening passes; phone_yuki at coffee_table_l1 at 20:00 on a weekday (it should be at the dining table).

```json
{
 "claims": [
  {
   "claim": "Yuki's keys are at the entry table at 20:00 on a weekday after she returns home",
   "target": "keys_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 19,
   "to": 21
  },
  {
   "claim": "Yuki's phone is at the dining table at 20:00 on a weekday during dinner",
   "target": "phone_yuki",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "Yuki's wallet is at the entry table at 22:00 on a weekday",
   "target": "wallet_yuki",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "keys_yuki": [
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
    "chance": "almost_always"
   }
  ],
  "wallet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 19.5,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ]
 }
}
```
