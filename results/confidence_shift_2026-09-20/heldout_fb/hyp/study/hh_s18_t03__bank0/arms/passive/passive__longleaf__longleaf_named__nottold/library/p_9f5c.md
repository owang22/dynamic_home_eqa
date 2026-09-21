# p_9f5c — Morning ritual: bathroom, breakfast, and departure (06:00–09:00)

This document covers the 06:00–09:00 window on both weekdays and weekends, when the household transitions from sleep to activity. Elena's morning is the more structured one: she showers around 06:30–07:00 (her towel is on the bathroom shelf at 07:00, confirmed by three sightings at bathroom_shelf_ba1 at that hour, while at 03:00 and 08:00 it is back on the towel rack). Her razor is scattered across the bathroom at 07:00 (bathroom_shelf, medicine_cabinet, and sink all show one sighting each), suggesting she is mid-grooming. Her water bottle is at the armchair at 07:00 (two sightings), where she grabs it before heading out.

Ines's morning is quieter. Her razor is on the bathroom shelf at 07:00 (three sightings) and her towel is on the rack (she showers later or not at all in the morning). At 07:00 her mug is at the kitchen table (one sighting) and at 08:00 her bowl is at the kitchen table (three sightings), indicating breakfast. Her vitamins are at the kitchen table at 08:00 (one sighting) and at 03:00 (two sightings), suggesting she takes them with a morning drink.

By 08:00 Elena is out the door on weekdays: her keys, backpack, jacket, laptop, water bottle, and headphones are all OUT_OF_HOUSE. Ines settles at the office desk: her water bottle is at desk_o1 at 08:00 (one sighting), and her laptop is at desk_o1 at 03:00 (two sightings) and 10:00 (one sighting). The yoga mat, which is scattered across the living room area (coffee table, bed, floor) at 03:00 and 07:00, is Elena's pre-departure or post-arrival exercise mat; by 18:00 it is stored in the wardrobe.

On weekends the pattern is similar but later: both sleep in until about 09:00. Elena's towel appears on the bathroom shelf at 11:00–12:00 on a weekend (two sightings), and Ines's towel is on the bathroom shelf at 14:00–15:00 on a weekend (three sightings), suggesting a later, more relaxed bathroom routine.

What sets this apart from p_2e9f (which places Elena's water bottle at the armchair and her towel on the bathroom shelf at 07:00, and Ines's water bottle at the desk by 08:00): this document adds the full 06:00–09:00 timeline including Ines's breakfast objects, the vitamins, the bowl, and the weekend bathroom shift. It also tracks the yoga mat's morning scatter.

Refutation: if Elena's towel is on the towel rack at 07:00 on a weekday (not the bathroom shelf), or if Ines's bowl is in the cupboard at 08:00 on a weekday, or if Elena's water bottle is at the dish rack at 07:00 (not the armchair), this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Elena's towel is on the bathroom shelf at 07:00 on weekdays",
   "target": "towel_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 6.5,
   "to": 7.5
  },
  {
   "claim": "Elena's water bottle is at the armchair at 07:00",
   "target": "water_bottle_elena",
   "expect": "armchair_l1",
   "days": "both",
   "from": 6.5,
   "to": 7.5
  },
  {
   "claim": "Ines's bowl is at the kitchen table at 08:00 on weekdays",
   "target": "bowl_ines",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  },
  {
   "claim": "Ines's water bottle is at the office desk by 08:00 on weekdays",
   "target": "water_bottle_ines",
   "expect": "desk_o1",
   "days": "weekday",
   "from": 8,
   "to": 9
  },
  {
   "claim": "Elena's razor is in the bathroom at 07:00 on weekdays",
   "target": "razor_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 6.5,
   "to": 7.5
  }
 ],
 "targets": {
  "towel_elena": [
   {
    "days": "weekday",
    "from": 6.5,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ],
  "towel_ines": [
   {
    "days": "weekend",
    "from": 13,
    "to": 16,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ],
  "razor_elena": [
   {
    "days": "weekday",
    "from": 6.5,
    "to": 7.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ],
  "razor_ines": [
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "both",
    "from": 6.5,
    "to": 7.5,
    "at": "armchair_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "bowl_ines": [
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "mug_ines": [
   {
    "days": "both",
    "from": 6.5,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 18,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "vitamins_ines": [
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ],
  "water_bottle_ines": [
   {
    "days": "weekday",
    "from": 8,
    "to": 17,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "laptop_ines": [
   {
    "days": "weekday",
    "from": 8,
    "to": 10.5,
    "at": "desk_o1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_o1",
    "chance": "usually"
   }
  ],
  "yoga_mat_elena": [
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "keys_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "backpack_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
