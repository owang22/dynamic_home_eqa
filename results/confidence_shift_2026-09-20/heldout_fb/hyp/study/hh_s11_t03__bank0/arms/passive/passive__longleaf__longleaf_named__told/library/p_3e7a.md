# p_3e7a — The Kitchen Table Morning; Hana Works Where She Eats

Hana and Priya share the kitchen table in the morning, but for different reasons. Priya sits down at 08:00 for a proper breakfast — bowl, mug, and her tablet for the news. Hana arrives at the table around 08:30, still in her pyjamas, and pulls her tablet onto the surface. She does not go to desk_b1. The desk is where her notebook and pen live between uses, and where plant_pot_3 sits, but her active morning workspace is the kitchen table. She eats a quick breakfast (bowl_hana appears at the table at 09:00) and works through the morning, tablet in front of her, until she packs up around 13:00 and heads out the door at 13:40 for her afternoon-to-night shift.

What sets this document apart from p_b8c2 and p_a1b2 is the location of tablet_hana during the weekday morning. Those documents place it at desk_b1, but the robot has found it at kitchen_table_k1 five times in the 9–17 h window and has never found it at the desk. The notebook, by contrast, is consistently at desk_b1 (3/3 sighted days, one receptacle), so it stays there. The mug_hana also migrates to the kitchen table during the work block rather than staying in the cupboard.

This document is refuted if the robot repeatedly finds tablet_hana at desk_b1 during 09:00–12:00 on weekdays, or if notebook_hana is sighted at the kitchen table during that window. It is also weakened if Hana's mug is consistently in the cupboard during 09:00–11:00 rather than at the table.

Hana's phone, keys, wallet, handbag, and water bottle travel with her: they are at their entry-area resting spots in the morning and OUT_OF_HOUSE from 13:40 to 23:00 on weekdays. Priya's keys go out during her morning walk (07:00–09:00) and afternoon errands (13:00–15:00). The dog leash goes out with Priya for the morning walk.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table during her weekday morning work block, not at the desk",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Hana's notebook stays at her desk all day and does not migrate to the kitchen table",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 7,
   "to": 13
  },
  {
   "claim": "Hana's mug is at the kitchen table during her morning work and breakfast block",
   "target": "mug_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 11
  },
  {
   "claim": "Hana's phone is out of the house during her weekday shift",
   "target": "phone_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "The yoga mat is back in wardrobe_b2 after the 6 AM session",
   "target": "yoga_mat_priya",
   "expect": "wardrobe_b2",
   "days": "both",
   "from": 7,
   "to": 23
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 8.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8.5,
    "to": 12.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12.5,
    "to": 13.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 23,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "phone_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
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
  "wallet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
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
  "handbag_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
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
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.5,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.5,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
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
  "keys_priya": [
   {
    "days": "weekday",
    "from": 0,
    "to": 7,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 15,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
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
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 10,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "class:dog_bowl": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 7,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "almost_always"
   }
  ]
 }
}
```
