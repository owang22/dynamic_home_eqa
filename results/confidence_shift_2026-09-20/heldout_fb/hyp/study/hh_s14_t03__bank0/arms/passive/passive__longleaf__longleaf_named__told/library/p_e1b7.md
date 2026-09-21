# p_e1b7 — Weekend vacuum: midday clean at 11:00 AND evening clean at 21:00 (fork of p_5e28)

This fork of p_5e28 adds a midday cleaning window on weekends. The parent document placed the vacuum on storage_shelf_s1 from 00:00 to 20:00, then on the living room floor from 20:00 to 23:00. But the weekend patrol data shows the vacuum on floor_l_l1 at 11:00 (two sightings) and again at 21:00 (two sightings), with it back on storage_shelf_s1 or storage_floor_s1 at 03:00, 14:00, and 23:00. The 11:00 floor sightings are unambiguous: the vacuum was pulled down from the shelf and used in the living room around midday, then put back up by 14:00.

The revised weekend pattern: vacuum on storage_shelf_s1 overnight and early morning (00:00–10:00), pulled to the living room floor for a midday clean (10:00–13:00), back on the shelf (13:00–20:00), pulled again for an evening clean (20:00–23:00), then to storage_floor_s1 for the night (23:00–24:00). The midday clean likely follows the late-morning dog walk and breakfast, while the evening clean comes after dinner and the kitchen is cleared.

The blanket and guitar blocks from p_5e28 are retained: blanket on the coffee table early, bathroom shelf midday, bed by evening; guitar on the bedroom floor overnight, couch during the day.

What sets this apart from p_5e28: at 11:00 on a weekend, the vacuum is on the living room floor (not the storage shelf). If the robot finds the vacuum on storage_shelf_s1 at 11:00 on a Saturday or Sunday, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 11:00 on a weekend during the midday clean",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 10,
   "to": 13
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 21:00 on a weekend during the evening clean",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "The vacuum cleaner is back on the storage shelf at 14:00 on a weekend, between the two cleaning sessions",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_shelf_s1",
   "days": "weekend",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Yuki's guitar is on the couch at 14:00 on a weekend during her afternoon practice",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 13,
   "to": 16
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 13,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 20,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 23,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 16,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "guitar_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   }
  ]
 }
}
```
