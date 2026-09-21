# p_3b8d — Omar's work gear migrates from entry to bedroom during his morning at home

Omar is home from 23:00 to 13:40 on weekdays. Overnight and in the early morning (00:00–08:00) his work gear — handbag, jacket, lunchbox, notebook, pen, scarf, shoes, wallet — rests at the entry (hook, table, or floor), where it was dropped on arrival from his night shift. But the 9–17h window shows zero sightings of any of these items at the entry: the robot looked at entry_hook_e1 three times between 9:00 and 17:00 and never found handbag_omar, jacket_omar, lunchbox_omar, notebook_omar, pen_omar, scarf_omar, shoes_omar, or wallet_omar there.

This document hypothesises that Omar moves his work gear from the entry to his bedroom during the 08:00–13:00 window, before he leaves at 13:40. The jacket and scarf go to wardrobe_b1 (the scarf was seen there once at 00:00), the shoes go to shoe_rack_e1 (seen there once at 00:00), and the smaller items (handbag, lunchbox, notebook, pen, wallet) go to dresser_b1 or bedroom_floor_b1. At 13:40 he grabs everything and it is OUT_OF_HOUSE from 13:40 to 23:00. When he returns at 23:00, the gear goes back to the entry hook/table for the night.

This sets this document apart from p_f3a7 and p_e9c1, which do not model Omar's item migration, and from p_b2c8, which claims the entry is a permanent chaos zone where nothing gets sorted (p_b2c8's own claims about items at entry_hook_e1 in the evening have taken 6 "against" votes each). The key prediction: during weekday 9:00–13:00, Omar's jacket is at wardrobe_b1, not entry_hook_e1, and his handbag is at dresser_b1, not entry_hook_e1.

What would refute this document: finding any of Omar's work items (handbag, jacket, lunchbox, notebook, pen, scarf, shoes, wallet) at entry_hook_e1 or entry_table_e1 during weekday 9:00–13:00, or finding them in the bedroom during 14:00–22:00 (they should be out of the house by then).

```json
{
 "claims": [
  {
   "claim": "Omar's jacket is at the wardrobe during his weekday morning at home, moved from the entry before he leaves for work",
   "target": "jacket_omar",
   "expect": "wardrobe_b1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Omar's handbag is at the dresser during his weekday morning, packed and ready for his shift",
   "target": "handbag_omar",
   "expect": "dresser_b1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Omar's shoes are at the shoe rack during his weekday morning, ready to put on before his 13:40 departure",
   "target": "shoes_omar",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Omar's handbag is out of the house during his afternoon-to-night shift on weekdays",
   "target": "handbag_omar",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 23
  }
 ],
 "targets": {
  "handbag_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "dresser_b1",
    "chance": "sometimes"
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
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "wardrobe_b1",
    "chance": "sometimes"
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
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "lunchbox_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "dresser_b1",
    "chance": "sometimes"
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
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "notebook_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "desk_b1",
    "chance": "sometimes"
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
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "pen_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "desk_b1",
    "chance": "sometimes"
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
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "scarf_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "wardrobe_b1",
    "chance": "sometimes"
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
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "shoe_rack_e1",
    "chance": "sometimes"
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
   }
  ],
  "wallet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 13.5,
    "at": "dresser_b1",
    "chance": "sometimes"
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
   }
  ],
  "keys_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
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
   }
  ]
 }
}
```
