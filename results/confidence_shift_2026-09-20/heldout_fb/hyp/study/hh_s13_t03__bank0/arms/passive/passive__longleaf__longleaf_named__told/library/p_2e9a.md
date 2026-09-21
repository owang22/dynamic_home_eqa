# p_2e9a — Weekend Vacuum All Day on the Floor

On weekends the vacuum cleaner stays out on the living room floor from the 03:00 pass through the 18:00 pass (floor_l_l1 at 03:00 ×2, 10:00 ×5, 12:00 ×1, 15:00 ×1, 18:00 ×1) and only goes back to storage_floor_s1 in the evening (18:00 ×2, 23:00 ×1). This is the opposite of the weekday pattern where the vacuum is mostly in storage with brief excursions at 10:00, 15:00, and 18:00. On weekends someone (likely Priya, who is home all day) is doing a full cleaning pass in the morning and the vacuum just stays out on the floor as a reference point for the rest of the day.

What sets this apart: p_7a3c models the weekday three-pass pattern (10, 15, 18) but says nothing about weekends. p_e5f0 mentions the weekend is "a completely different rhythm" but does not place the vacuum. This document's central claim is that the vacuum is on the floor at 10:00 AND 15:00 on a weekend, not in storage.

What would refute it: if the vacuum is at storage_floor_s1 at 10:00 or 15:00 on multiple weekend days, the all-day-out pattern is wrong.

```json
{
 "claims": [
  {
   "claim": "The vacuum cleaner is on the living room floor at 10:00 on a weekend",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 10,
   "to": 12
  },
  {
   "claim": "The vacuum cleaner is on the living room floor at 15:00 on a weekend",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 14,
   "to": 16
  },
  {
   "claim": "The vacuum cleaner is back in storage at 23:00 on a weekend",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekend",
   "from": 22,
   "to": 24
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
    "days": "weekday",
    "from": 9.5,
    "to": 11,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 14.5,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 3,
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
   }
  ]
 }
}
```
