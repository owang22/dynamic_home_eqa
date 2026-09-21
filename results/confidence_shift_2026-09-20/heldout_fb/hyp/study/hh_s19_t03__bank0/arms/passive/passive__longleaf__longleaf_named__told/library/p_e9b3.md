# p_e9b3 — Saturday: vacuum at ten, duster at the bookshelf, ironing afternoon, friends at eight

Saturday is the household's cleaning-and-social day. The residents' message confirms friends arrive in the evening. The morning is for errands (both are home, no commute), and the midday block is for chores. The vacuum cleaner is pulled from storage at 03:00 (1 sighting on floor_l_l1 vs 1 on storage) and is on the living room floor at 10:00 (2 sightings) and 12:00 (1 sighting) before going back to storage by 13:00 (3 sightings). The duster, normally in storage, is at the bookshelf at 11:00 (5 sightings!) — a dedicated dusting pass of the living-room shelves. The iron and ironing board leave storage around 13:00 and are at bed_b2 from 13:00 through 18:00 (iron: 1 at 15:00, 1 at 13:00; ironing board: 1 at 13:00, 1 at 15:00, 1 at 18:00), a long afternoon ironing session. By 19:00 the ironing board is back in storage. In the evening the living room fills: the guitar moves to the couch (Marco plays for guests), the laptop stays at the coffee table all day (no desk work on Saturday), and the keys stay at the entry table (no commute).

What sets this apart from p_9e4b and p_6d1f: the duster is specifically at the bookshelf (not just "out of storage"), the ironing window is 13:00–18:00 (not 14:50–19:00), and the vacuum is back in storage by 13:00 (not still out). A sighting of the vacuum on the floor after 13:00, the duster in storage at 11:00, or the iron in storage at 15:00 on a Saturday would refute this document.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 11:00 on Saturday (midday cleaning)",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 10,
   "to": 12
  },
  {
   "claim": "The duster is at the bookshelf at 11:00 on Saturday (dusting the shelves)",
   "target": "duster_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 10.5,
   "to": 12
  },
  {
   "claim": "The iron is at bed_b2 at 15:00 on Saturday (afternoon ironing session)",
   "target": "iron_shared",
   "expect": "bed_b2",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Omar's laptop is at the coffee table at 14:00 on Saturday (no desk work on weekends)",
   "target": "laptop_omar",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 12,
   "to": 16
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 12.5,
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
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 10.5,
    "to": 12,
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
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 18,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 18,
    "at": "bed_b2",
    "chance": "usually"
   }
  ],
  "guitar_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "laptop_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
