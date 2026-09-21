# p_b3a8 — Priya's afternoon vacuum: living room 15:30–17:30

The vacuum cleaner is at the entry floor as its resting spot, but the 16:00 and 17:00 passes both find it on the living-room floor (floor_l_l1). This is a mid-afternoon cleaning session, almost certainly by Priya, who is home while Elena is at work (8:00–17:30). The sequence fits Priya's routine: she returns from her afternoon errands (glasses and water bottle out 13:00–16:00 per p_7890), unpacks the shopping bag at the kitchen counter (seen 14:00–15:00), and then vacuums the living room 15:30–17:30. By 18:00 the vacuum is back at the entry floor.

What sets this hypothesis apart: the vacuum is on the living-room floor at 16:00 and 17:00 on weekdays, not at the entry. No other document places the vacuum there in that window. What would refute it: the vacuum at the entry floor at 16:00 or 17:00 on a weekday (no cleaning), or the vacuum on the living-room floor on a weekend (Priya does not vacuum on weekends in this model).

```json
{
 "claims": [
  {
   "claim": "The vacuum is on the living-room floor during Priya's afternoon cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 16,
   "to": 17
  },
  {
   "claim": "The vacuum is back at the entry after cleaning is done",
   "target": "vacuum_cleaner_shared",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 18,
   "to": 19
  },
  {
   "claim": "The dog toy is on the living-room floor during the vacuum session",
   "target": "dog_toy_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 15.5,
   "to": 17.5
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
    "days": "weekday",
    "from": 15.5,
    "to": 17.5,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 15.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
