# p_e9a4 — The Afternoon Tidy; Duster and Vacuum at the Coffee Table, Then Left Overnight

The duster and vacuum cleaner are stored in the utility area (storage_shelf_s1 and storage_floor_s1) most of the time, but the sightings show them at coffee_table_l1 at 16:00 (1× each) and at 00:00 (1× each) on weekdays. This pattern suggests Priya pulls them out for a living-room tidy in the mid-afternoon (roughly 14:00–17:00), uses them, and sometimes leaves them at the coffee table overnight before putting them back by 08:00. The 00:00 sighting at the coffee table means the items are still out at midnight; the 08:00 sighting back in storage means they are put away before the morning walk. This is a general weekday pattern, not limited to social evenings, though a friends-coming-over day makes it more likely.

What sets this document apart: it places the duster and vacuum at coffee_table_l1 in the 14:00–18:00 window AND at 23:00–24:00 (left out overnight), with a return to storage by 08:00. It also predicts Priya's mug and tablet at the coffee table during the 18:00–23:00 wind-down (both were sighted there at 18:00 on weekdays). A look at the coffee table at 16:00 that finds neither the duster nor the vacuum, or a look at storage that finds them at 00:00, would weaken this document.

```json
{
 "claims": [
  {
   "claim": "The duster is left at the coffee table overnight after the afternoon tidy",
   "target": "duster_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "The vacuum cleaner is left at the coffee table overnight after the afternoon tidy",
   "target": "vacuum_cleaner_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Priya's mug is at the coffee table during the evening wind-down",
   "target": "mug_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 23
  },
  {
   "claim": "Priya's tablet is at the coffee table during the evening wind-down",
   "target": "tablet_priya",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 18,
   "to": 23
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
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
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
    "days": "weekday",
    "from": 14,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
