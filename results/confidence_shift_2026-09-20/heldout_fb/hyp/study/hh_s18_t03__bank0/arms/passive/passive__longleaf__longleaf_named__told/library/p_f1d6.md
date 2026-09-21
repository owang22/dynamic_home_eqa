# p_f1d6 — Morning ritual 07:00–08:30: bathroom, kitchen breakfast, settling in

Both women wake around 06:30–07:00. The bathroom ritual (07:00–08:00) puts both razors on the bathroom shelf (bathroom_shelf_ba1) and Elena's towel on the bathroom shelf before it goes back to the towel rack (towel_rack_ba1) by 08:00. Elena's water bottle (water_bottle_elena) is at the armchair (armchair_l1) at 07:00 while she gets ready.

Breakfast at the kitchen table (07:00–08:30): Ines's mug (mug_ines) is at the kitchen table (kitchen_table_k1) at 07:00. By 08:00, Ines's bowl (bowl_ines), glass (glass_ines), and vitamins (vitamins_ines) are at the kitchen table. Elena's water bottle moves from the armchair to the entry floor (entry_floor_e1) by 18:00 (she takes it with her to work).

After breakfast, Ines settles into the office room. Her water bottle is at the desk (desk_o1) by 08:00. Her laptop is at the desk by 09:00 (or on the floor if she's just sitting down).

What sets this apart: p_d1e5 and p_9c2f put the mugs at the kitchen table at 07:00 but also claim an early 05:45 wake-up and 07:15 departure. Here the wake-up is around 06:30–07:00 and Elena leaves at 08:00. The 07:00 razor and towel sightings at the bathroom shelf are the anchor.

Refutation: if the razors are at the sink (sink_ba_ba1) at 07:00 on multiple days, the bathroom-shelf prediction fails. If Elena's water bottle is not at the armchair at 07:00, the morning transition is wrong. If Ines's mug is in the cupboard at 07:00, the breakfast-at-the-table prediction fails.

```json
{
 "claims": [
  {
   "claim": "Ines's razor is on the bathroom shelf at 07:00",
   "target": "razor_ines",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Elena's towel is on the bathroom shelf at 07:00",
   "target": "towel_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Elena's water bottle is at the armchair at 07:00",
   "target": "water_bottle_elena",
   "expect": "armchair_l1",
   "days": "both",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Ines's mug is at the kitchen table at 07:00",
   "target": "mug_ines",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 7,
   "to": 8
  }
 ],
 "targets": {
  "razor_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "razor_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "towel_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "bowl_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "vitamins_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glass_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "desk_o1",
    "chance": "usually"
   }
  ]
 }
}
```
