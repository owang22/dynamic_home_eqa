# p_e91d — Weekend morning clean: vacuum in the living room, duster at the bookshelf

On weekends both residents sleep in until about 09:00, then tackle a cleaning session before midday errands. The vacuum cleaner is pulled from storage_floor_s1 and set on the living room floor (floor_l_l1) from roughly 08:00 to 13:00, where it sits while they go room to room. The duster is taken from storage_shelf_s1 and used at the bookshelf (bookshelf_l1) around 10:00–12:00, then returned to storage by 13:00. On weekdays neither item leaves storage during the day — the vacuum stays in storage_floor_s1 and the duster in storage_shelf_s1 from 03:00 through 20:00. This document does not make strong claims about the kitchen or office routines; it is specifically about the weekend chore objects that the robot is asked about after the residents finish their cleaning.

What would refute this: finding the vacuum in storage at 10:00 on a Saturday or Sunday, or finding the duster in storage at 11:00 on a weekend. Finding the vacuum on the living room floor on a weekday would also contradict the model.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 10:00 on a weekend",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 9.5,
   "to": 10.5
  },
  {
   "claim": "The duster is at the bookshelf at 11:00 on a weekend",
   "target": "duster_shared",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 10.5,
   "to": 11.5
  },
  {
   "claim": "The vacuum cleaner is in storage at 10:00 on a weekday",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 9.5,
   "to": 10.5
  },
  {
   "claim": "The duster is in storage at 11:00 on a weekday",
   "target": "duster_shared",
   "expect": "storage_shelf_s1",
   "days": "weekday",
   "from": 10.5,
   "to": 11.5
  }
 ],
 "targets": {
  "vacuum_cleaner_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 13,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 13,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   }
  ],
  "duster_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "almost_always"
   },
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
    "to": 12.5,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12.5,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
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
