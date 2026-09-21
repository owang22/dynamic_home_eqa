# p_7c4e — Weekend Dusting; Duster Leaves Storage for the Coffee Table at 17:00

On weekends Priya's cleaning routine extends well into the late afternoon and early evening. After her mid-morning walk she vacuums the living room: the vacuum appears on floor_l_l1 at 11:00 and again at 15:00, then is set down on coffee_table_l1 by 17:00. The duster, which stays on storage_shelf_s1 throughout every weekday, is brought out on weekend afternoons. It appears at bookshelf_l1 at 15:00 (one sighting, presumably being used to dust the shelves) and then at coffee_table_l1 from 17:00 onward (one sighting at 17:00, two at 19:00). This is the pattern the mixture has missed three times: on day 5 (Sunday) at 17:00 the robot looked at storage_shelf_s1 and found the duster at the coffee table instead.

The duster's weekend path: storage_shelf_s1 until 15:00, bookshelf_l1 at 15:00–16:00 (active dusting of the shelves), then coffee_table_l1 from 16:00 to about 21:00 (set down between dusting tasks in the living room). On weekdays it never leaves storage_shelf_s1.

The vacuum's weekend path: storage_floor_s1 until 11:00, floor_l_l1 from 11:00 to 16:00 (active vacuuming, seen at both 11:00 and 15:00), then coffee_table_l1 from 16:00 to 18:00 (set down while Priya transitions to dusting). On weekdays it stays in storage all day.

What would refute this document: if the duster is found at storage_shelf_s1 on a weekend afternoon after 16:00, or if the vacuum is never seen at coffee_table_l1 on a weekend, the cleaning-transition narrative collapses.

```json
{
 "claims": [
  {
   "claim": "The duster is on the coffee table during the weekend evening dusting",
   "target": "duster_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 17,
   "to": 20
  },
  {
   "claim": "The vacuum is on the living room floor during the weekend afternoon vacuuming",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 11,
   "to": 16
  },
  {
   "claim": "The vacuum is set down on the coffee table after the weekend vacuuming",
   "target": "vacuum_cleaner_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 16,
   "to": 18
  },
  {
   "claim": "The duster stays on the storage shelf during weekday working hours",
   "target": "duster_shared",
   "expect": "storage_shelf_s1",
   "days": "weekday",
   "from": 9,
   "to": 17
  }
 ],
 "targets": {
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
    "from": 15,
    "to": 16,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
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
    "from": 11,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
