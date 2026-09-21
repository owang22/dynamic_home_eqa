# p_9e3f — Weekend domestic: Elena's items shift to bathroom and desk

On weekdays Elena is out from roughly 8 to 17:30, and her personal items sit at their weekday anchors: skincare on the nightstand, toiletry bag on the dresser, hair dryer on the bathroom shelf, laptop and notebook at the entry hook or out with her. On weekends the picture changes. Elena is home all day, takes a longer morning routine in the bathroom, and her skincare and toiletry bag migrate to the bathroom shelf where she actually uses them (the per-object data shows skincare_elena at bathroom_shelf_ba1 2-for-2 at every weekend pass from 08:00 onward, versus nightstand_b1 on weekdays). In the weekend afternoon the hair dryer moves to the bedroom desk. In the weekend evening she organises her work kit for the coming week: the laptop slides from the entry hook to the dresser, and the notebook and pen move from the entry hook to the bedroom desk. Her keys, which rest on the entry table on weekdays, shift to the entry floor during weekend daylight hours.

What sets this apart: p_c4e7 captures some of the weekend bathroom shift but also predicts the vacuum in the living room and the blanket on the armchair (both getting against votes). p_f9a3 captures the laptop-to-dresser evening move but bundles it with a board-game claim that is not yet supported. This document focuses narrowly on the bathroom/desk shift of Elena's personal items and the work-kit reorganisation.

What would refute: finding Elena's skincare on the nightstand during a weekend morning (08–14 h), or her toiletry bag on the dresser on a weekend, or the laptop still at the entry hook at 21:00 on a Saturday or Sunday.

```json
{
 "claims": [
  {
   "claim": "Elena's skincare is on the bathroom shelf on a weekend morning after her routine",
   "target": "skincare_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 8,
   "to": 14
  },
  {
   "claim": "Elena's toiletry bag is on the bathroom shelf on a weekend morning",
   "target": "toiletry_bag_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 8,
   "to": 14
  },
  {
   "claim": "Elena's laptop is on the bedroom dresser on a weekend evening after she organises her kit",
   "target": "laptop_elena",
   "expect": "dresser_b1",
   "days": "weekend",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Elena's notebook is on the bedroom desk on a weekend evening",
   "target": "notebook_elena",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "skincare_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 22,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "toiletry_bag_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dresser_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 22,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dresser_b1",
    "chance": "usually"
   }
  ],
  "notebook_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "pen_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 18,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 18,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
