# p_7c3e — Weekend resting positions: objects migrate to secondary spots

Yuki and Omar are both home all weekend, and the house settles into a different rhythm. The weekday "resting" spots give way to weekend ones: the journal moves from the nightstand to the bed (she reads in bed, sleeps in), Omar's glasses shift from the nightstand to the bedroom desk (he reads or works at the desk in the morning), the scarf goes from the entry hook into the wardrobe (neither is cycling out early), and the wallet drops from the entry table to the entry floor (casual weekend, less precise placement). In the kitchen, glasses that rest at the sink on weekdays end up in the dish rack on weekends (washed and put away properly over the longer morning), the pan shifts from the cupboard to the drawer, and the spatula moves to the pantry shelf. The snack bowl, which sits at the counter or armchair on weekdays, is washed and stored at the sink on weekends. Yuki's phone, which wanders the coffee table on weekdays, charges at the nightstand on weekends. Omar's razor is put away on the bathroom shelf rather than left at the sink.

This hypothesis is set apart by its systematic weekend-only repositioning blocks. It does not claim the objects are *in use* at these spots; they are simply resting there. The weekday positions remain as the library already models them. What would refute this: if weekend sightings repeatedly show these objects at their weekday spots (nightstand for the journal, sink for the glasses, entry hook for the scarf, sink for the pan), or if the objects are found at a third, unexpected location on weekends.

```json
{
 "claims": [
  {
   "claim": "Yuki's journal is on the bed on Saturday morning because she reads in bed before getting up",
   "target": "journal_yuki",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 6,
   "to": 10
  },
  {
   "claim": "Omar's glasses are at the bedroom desk on Saturday morning because he reads at the desk after sleeping in",
   "target": "glasses_omar",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 6,
   "to": 12
  },
  {
   "claim": "Omar's scarf is in the wardrobe on Saturday because neither is cycling out early on the weekend",
   "target": "scarf_omar",
   "expect": "wardrobe_b1",
   "days": "weekend",
   "from": 0,
   "to": 12
  },
  {
   "claim": "Yuki's phone is at the bedroom nightstand on Saturday morning charging overnight",
   "target": "phone_yuki",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 0,
   "to": 10
  },
  {
   "claim": "Omar's razor is on the bathroom shelf on Saturday morning, put away after his weekend shave",
   "target": "razor_omar",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 6,
   "to": 12
  }
 ],
 "targets": {
  "journal_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   }
  ],
  "glasses_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "scarf_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "sometimes"
   }
  ],
  "wallet_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "glass_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "glass_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "drawer_k_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "phone_yuki": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "razor_omar": [
   {
    "days": "weekend",
    "from": 0,
    "to": 16,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ]
 }
}
```
