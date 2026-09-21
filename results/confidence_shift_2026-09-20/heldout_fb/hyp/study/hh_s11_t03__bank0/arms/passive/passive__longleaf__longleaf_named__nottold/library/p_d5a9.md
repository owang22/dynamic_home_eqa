# p_d5a9 — Weekend Afternoon Vacuum and Evening Yoga

Priya's weekend routine includes two living-room activities that the library has not captured as a pair. On Saturday (and likely Sunday) around 15:00 she vacuums the living room: the weekend pass at 15:00 found the vacuum on floor_l_l1 twice (and once still in storage). The mixture's worst-objects list confirms: predicted storage_floor_s1, actually floor_l_l1, 2×, day 4 15:00. Later, around 20:00, she unrolls her yoga mat on the living room floor for an evening session (one weekend sighting at 20:00 on floor_l_l1). On weekdays the vacuum stays in storage_floor_s1 and the mat stays in wardrobe_b2.

This hypothesis predicts that on weekend afternoons the vacuum is out on the living room floor, and on weekend evenings the yoga mat is unrolled on the living room floor. What would refute it: a weekend 14–16 h pass that finds the vacuum still in storage, or a weekend 19–21 h pass that finds the mat still in the wardrobe.

```json
{
 "claims": [
  {
   "claim": "On weekend afternoons Priya vacuums the living room and the vacuum is on the floor",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 14,
   "to": 16
  },
  {
   "claim": "On weekend evenings Priya unrolls her yoga mat on the living room floor",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "On weekdays the vacuum stays in storage all day",
   "target": "vacuum_cleaner_shared",
   "expect": "storage_floor_s1",
   "days": "weekday",
   "from": 9,
   "to": 17
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
    "from": 14,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
