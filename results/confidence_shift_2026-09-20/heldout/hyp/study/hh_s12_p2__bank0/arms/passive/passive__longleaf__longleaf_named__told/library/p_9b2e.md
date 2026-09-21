# p_9b2e — desk_b1 is the active workspace for both residents

The bedroom desk (desk_b1) is where both residents keep their working items. Priya's headphones, pen, and reading glasses live there during the day; Elena's charger, notebook, and pen rest there overnight and in the morning before she leaves. The office room (desk_o1) is essentially a storage corner with a single plant pot—no one works there. This explains why p_e5f6's "Priya's music studio in the office" model keeps failing: her creative tools are at desk_b1, not desk_o1.

Elena's work items (charger, notebook, pen) are at desk_b1 from the evening through the morning. She grabs them and leaves around 8; they come back around 17:30. On the rare WFH day the charger might stay, but the pattern is overwhelmingly "out during work." Priya's items stay at desk_b1 all day because she is home.

This document is distinguished from p_e5f6 (office desk workspace) and p_c3d4 (WFH at office desk) by placing all active desk items at desk_b1. It is distinguished from the plain statistical model by specifying the time-of-day movement of Elena's items.

Refutation: if headphones_priya or pen_priya are found at desk_o1 on multiple weekday afternoons, or if the plant pot at desk_o1 is missing, this document is wrong. If Elena's charger is consistently at desk_b1 during 9–17h on multiple weekdays (not just once), the "out during work" block needs revision.

```json
{
 "claims": [
  {
   "claim": "Priya's headphones are at desk_b1 on a weekday afternoon",
   "target": "headphones_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Priya's pen is at desk_b1 on a weekday afternoon",
   "target": "pen_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 14
  },
  {
   "claim": "Elena's charger is at desk_b1 in the morning before she leaves",
   "target": "charger_elena",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "The plant pot is at the office desk at all times",
   "target": "plant_pot_3_shared",
   "expect": "desk_o1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "notebook_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "pen_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ],
  "plant_pot_3_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "almost_always"
   }
  ]
 }
}
```
