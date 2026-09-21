# p_d5e9 — Saturday: vacuum at ten, dust at eleven, iron at three, friends at eight

Saturday is the cleaning day. The vacuum cleaner is on the living room floor from 10:00 to 13:00 (sightings: 10:00 floor_l_l1 x2, 12:00 floor_l_l1 x1, back in storage by 13:00 x3). The duster is at the bookshelf at 11:00 (5 sightings at bookshelf_l1, 1 at storage_shelf_s1) for a shelf-dusting session. The iron and ironing board are at bed_b2 from roughly 14:30 to 18:00 (weekend sightings: iron at bed_b2 at 15:00, ironing board at bed_b2 at 13:00, 15:00, 18:00). On weekday evenings the ironing session shifts to 21:00 (iron at bed_b2 x3, board at bed_b2 x2).

In the evening, friends come over (Saturday message) and the living room fills up. Omar's laptop is at the bookshelf overnight on weekends (03:00: bookshelf x2) and its daytime location is uncertain — no weekend daytime sightings exist. Marco's keys stay at the entry table (no commute). The watering can is on the balcony (7/7 days).

This document is refuted if the vacuum is in storage at 11:00 on Saturday, if the duster is in storage at 11:00 on Saturday, or if the iron is in storage at 15:00 on Saturday.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 11:00 on Saturday during midday cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 10.75,
   "to": 11.25
  },
  {
   "claim": "The duster is at the bookshelf at 11:00 on Saturday during the dusting session",
   "target": "duster_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 10.75,
   "to": 11.25
  },
  {
   "claim": "The iron is at bed_b2 at 15:00 on Saturday during the afternoon ironing session",
   "target": "iron_shared",
   "expect": "bed_b2",
   "days": "weekend",
   "from": 14.75,
   "to": 15.25
  },
  {
   "claim": "The vacuum cleaner is back in storage at 14:00 on Saturday after cleaning is done",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekend",
   "from": 13.75,
   "to": 14.25
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "duster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10.5,
    "to": 12.5,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14.5,
    "to": 18,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14.5,
    "to": 18,
    "at": "bed_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20.5,
    "to": 23,
    "at": "bed_b2",
    "chance": "sometimes"
   }
  ],
  "keys_marco": [
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
  "watering_can_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "almost_always"
   }
  ]
 }
}
```
