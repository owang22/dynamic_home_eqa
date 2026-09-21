# p_c2e9 — Elena's weekend at-home: no commute, cleaning, bathroom shelf

On the weekend Elena does not go to her office. Her laptop, notebook, and pen all stay at the entry hook all day (staged from the previous night or simply not taken out). Her keys move to the entry floor during the day because she uses them for the midday errand run (driving), and she sets them on the floor by the door when she comes back. Her skincare and toiletry bag shift to the bathroom shelf in the morning because she does a full grooming routine at home (not the quick nightstand grab of a weekday). The vacuum cleaner appears on the living-room floor in the mid-afternoon: she is cleaning up the living room in preparation for the friends arriving that evening. Her mug rests in the cupboard on weekends (not at the sink as on weekdays, because there is no morning coffee routine at the kitchen sink). Her hair dryer is occasionally at the bedroom desk in the afternoon (she dries her hair after a weekend shower and sets it there).

What sets this apart: the weekday documents (p_3a7c, p_b4e8, p_a3f7, etc.) all predict Elena's work items are either out of the house or at the bedroom desk during 9–17 h. This document says they are at the entry hook all weekend. The bathroom-shelf shift for skincare and toiletry bag is also unique to weekends (weekday documents put them at the nightstand or dresser). The vacuum in the living room at 14–18 h is a hosting-prep signal no other document makes.

What would refute it: if the robot finds laptop_elena at the bedroom desk or at the office desk on a weekend, or finds Elena's keys at the entry table (not the floor) during the afternoon, the at-home pattern is wrong. If the vacuum stays at the entry floor all weekend, the cleaning-for-guests story fails.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop stays at the entry hook all day on the weekend (no commute)",
   "target": "laptop_elena",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "Elena's keys are on the entry floor during her midday errand window on the weekend",
   "target": "keys_elena",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 10,
   "to": 15
  },
  {
   "claim": "Elena's skincare is on the bathroom shelf during the weekend morning routine",
   "target": "skincare_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 9,
   "to": 15
  },
  {
   "claim": "The vacuum cleaner is on the living room floor during Elena's weekend afternoon cleaning",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "notebook_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "pen_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "keys_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 16,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "skincare_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 18,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "toiletry_bag_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 8,
    "at": "dresser_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 18,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "mug_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 20,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
