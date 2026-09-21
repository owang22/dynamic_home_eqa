# p_3e9f — Staggered dinner refined: Priya 19, Elena 20, clear by 21:30 (fork of p_8b3c)

Forked from p_8b3c to tighten the dinner windows to match the hourly passes exactly. The 19:00 pass shows glass_priya (×2) and water_bottle_priya (×2) at the dining table while plate_elena is still in the cupboard. The 20:00 pass shows plate_elena (×3), glass_elena (×3), and water_bottle_elena (×3) at the table. The 21:00 pass shows plate_priya (×1) and water_bottle_priya (×1) still at the table but glass_priya already back in the sink. Weekend shifts one hour later: Priya's items at 20:00 (×2), Elena's at 21:00 (×1).

What changed from the parent: (1) Priya's window is now 19–21 on weekdays (was 19–21, same) but the claim window is tightened to 19–20 to avoid the 21:00 pass where her glass is already in the sink; (2) Elena's window is 20–21.5 on weekdays (was 20–21) to capture the 21:00 pass where her items may still be at the table; (3) added explicit "clear" blocks at 21.5–23 putting items in the sink/dish rack; (4) weekend windows shifted to 20–22 for Priya and 21–22.5 for Elena.

Refutation: if plate_elena is at the dining table at 19:00 on a weekday (she arrived early, negating the stagger), or if glass_priya is not at the table at 19:00 (she sat down later than expected).

```json
{
 "claims": [
  {
   "claim": "Priya's glass is at the dining table at 19:00 on a weekday",
   "target": "glass_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Elena's plate is at the dining table at 20:00 on a weekday",
   "target": "plate_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21
  },
  {
   "claim": "Priya's water bottle is at the dining table at 19:00 on a weekday",
   "target": "water_bottle_priya",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 19,
   "to": 20
  },
  {
   "claim": "Elena's glass is at the dining table at 20:00 on a weekday",
   "target": "glass_elena",
   "expect": "dining_table_d1",
   "days": "weekday",
   "from": 20,
   "to": 21
  }
 ],
 "targets": {
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 23.5,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "plate_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 22,
    "at": "dining_table_d1",
    "chance": "usually"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23,
    "at": "dish_rack_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "plate_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21.5,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 23,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 22.5,
    "at": "dining_table_d1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 20,
    "to": 21.5,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 21.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
