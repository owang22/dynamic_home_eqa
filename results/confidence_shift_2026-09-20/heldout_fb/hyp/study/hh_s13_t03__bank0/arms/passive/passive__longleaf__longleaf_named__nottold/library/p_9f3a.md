# p_9f3a — Weekend: All-Day Vacuum, Midday Shower, Armchair Evening

On weekends the house runs on a completely different rhythm from weekdays. The vacuum cleaner is out on the living room floor from early morning through the late afternoon (sighted at 03:00, 10:00, 12:00, and 15:00 on weekend passes), suggesting an all-day cleaning project rather than a brief 30-minute session. Hana takes a midday shower around 11:00–13:00 (towel_hana at bathroom_shelf_ba1 with 7 sightings at the 12:00 pass). The evening settles into the armchair: the blanket is there from 18:00 through 23:00, the remote is at the coffee table from 20:00, and the guitar rests on the couch (not played).

This is distinguished from p_2d9c (which also captures the weekend vacuum and couch guitar) by adding the midday shower signal and by placing the blanket specifically on the armchair (not the couch) for the 18:00–23:00 window. It differs from p_9e2b by removing the ON_PERSON guitar claim (contradicted by evidence) and by extending the vacuum window to cover the 03:00 pass.

What would refute this: the vacuum in storage at 12:00 on a Saturday, towel_hana on the towel_rack at 12:00 on a weekend, or the blanket on the couch (not armchair) at 20:00 on a weekend.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 11:00 on a Saturday",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Hana's towel is on the bathroom shelf at 12:00 on a Saturday (midday shower)",
   "target": "towel_hana",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 11,
   "to": 13
  },
  {
   "claim": "The blanket is on the armchair at 21:00 on a Saturday",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The remote is on the coffee table at 20:30 on a Saturday",
   "target": "remote_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20,
   "to": 21.5
  },
  {
   "claim": "The guitar is on the couch at 16:00 on a Saturday (not being played)",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 15,
   "to": 17
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 18,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ],
  "towel_hana": [
   {
    "days": "weekend",
    "from": 11,
    "to": 13,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "sometimes"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 18,
    "to": 23.5,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
