# p_4c2a — Hybrid three days; Priya's mid-morning desk (fork of p_c5d9)

Elena works from the bedroom desk three weekdays a week (Monday, Wednesday, Friday) and commutes the other two (Tuesday, Thursday). She drives both ways, so the helmet and bike lock never leave the entry. On WFH days her laptop, notebook, and pen are at desk_b1 from 9 to 17; on commute days they leave with her in the backpack. The charger is permanently at desk_b1. Priya uses desk_b1 for her morning-to-afternoon routine—glasses, pen, and book from 9 to 16 on weekdays—then moves to the living room or kitchen for the rest of the day. On Elena's commute days (Tue/Thu) Priya extends her desk time to 9–16 since the desk is unoccupied by Elena. On weekends, after her late-morning walk, she settles at the desk from about 10 to 14. The laptop rests on the coffee table in the evenings. The dog is fed by Priya at 7 and walked by Elena after 17:30.

What changed from the parent (p_c5d9): Priya's glasses window was 7–11, but two looks in that window found the glasses at the nightstand, not the desk. The sightings show the glasses at desk_b1 at 08:00 on only one of two days, and solidly at desk_b1 by 16:00. The transition from nightstand to desk happens between 08:00 and 12:00, not before 09:00. On weekends she sleeps in and walks late, so the desk window starts at 10. I widened the window to 9–16 (weekday) and 10–14 (weekend) to match where the evidence actually places them. The claim is updated accordingly.

What sets this apart: three WFH days means the laptop and notebook_elena are at desk_b1 on 60% of weekdays. Priya's desk time is 9–16 on weekdays (not 7–11 as in the parent) and 10–14 on weekends. The backpack is at the entry hook on WFH days but OUT_OF_HOUSE on commute days.

Refuted if: the laptop is at desk_b1 on a Tuesday or Thursday; Priya's glasses are at the nightstand during 10–14 on a weekday; the helmet is out of the house; the backpack is at the entry hook during a weekday 9–17h look on a commute day.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is at the bedroom desk on a weekday afternoon (WFH day)",
   "target": "laptop_elena",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's glasses are at the bedroom desk during her mid-morning to afternoon desk session",
   "target": "glasses_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Elena's helmet is at the entry hook on a weekday midday (drives, never cycles to work)",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 11,
   "to": 15
  },
  {
   "claim": "Elena's notebook is out of the house on a weekday morning (commute day)",
   "target": "notebook_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 17
  },
  {
   "claim": "Priya's pen is at the bedroom desk on a weekday afternoon",
   "target": "pen_priya",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 10,
   "to": 15
  }
 ],
 "targets": {
  "helmet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "almost_always"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
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
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
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
  "charger_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
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
    "chance": "sometimes"
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
    "chance": "sometimes"
   }
  ],
  "glasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 16,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 14,
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
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 16,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 14,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "phone_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "entry_table_e1",
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
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "ON_PERSON",
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
  "wallet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
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
  "shoes_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "class:bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
