# p_a4c7 — Thursday Social: Drinks and TV, Not a Board Game Night (fork of p_7e4a)

The parent document (p_7e4a) modelled a Wednesday social evening with Hana playing guitar for friends and the board game as the centrepiece. Two days of evidence have reshaped that picture. First, the guitar has been sighted on the bedroom floor in all 15 passes — never on a person, never on the coffee table. The 22:00 passes on both Tuesday and Wednesday show both residents in the living room with no guitar displacement. Second, the board game, blanket, and remote all show a 1×/1× split at 22:00 (one sighting at the resting spot, one at the coffee table), which is inconsistent with a deliberate "everything on the coffee table" setup. What IS consistent across both evenings: the snack bowl (2×/2× on the coffee table), both glasses (on the coffee table), and both mugs (on the coffee table). The social is a drinks-and-snacks-and-TV evening, not a performance or game night.

This fork is triggered by the Thursday message ("friends coming over this evening"), making it the second consecutive social night. The pattern should repeat: kitchen dinner around 19:00–20:30, then a gradual shift to the living room where glasses, mugs, and the snack bowl are set on the coffee table. The board game may come out (it did partially on Wednesday) but it is not the focus. The guitar stays on the bedroom floor. The blanket and remote are partially moved — some at the old spot, some at the coffee table — reflecting a casual, low-effort setup rather than a deliberate staging.

What changed from the parent: (1) removed the guitar ON_PERSON and coffee_table blocks entirely — 15/15 bedroom-floor sightings make playing very unlikely; (2) lowered the board game coffee_table block from "usually" to "sometimes" to match the 1×/1× split; (3) added a blanket coffee_table block at "sometimes" (the parent had no evening blanket move, but the split evidence shows it does move partially); (4) lowered the remote coffee_table block from "usually" to "sometimes"; (5) added a class:mug target showing mugs on the coffee table at 22:00 (confirmed 2× Wednesday); (6) the context is now Thursday, the second social night in a row.

What would refute it: if on Thursday at 22:00 the snack bowl is NOT on the coffee table (still at the sink or counter), if the guitar is sighted off the bedroom floor, or if the residents are still in the kitchen at 22:00 rather than the living room.

Travelling objects: Hana's laptop, jacket, keys, handbag, wallet, pen, and water bottle are out with her at work 8:00–17:30. Priya's keys and jacket are out on the afternoon errand 14:00–16:00. Nothing else leaves the house.

```json
{
 "claims": [
  {
   "claim": "The snack bowl is on the coffee table at 22:00 on a weekday social evening",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "The guitar stays on the bedroom floor at 22:00 on a weekday (not played, not moved)",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Hana's glass is on the coffee table at 22:00 on a weekday social evening",
   "target": "glass_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Hana's laptop is out of the house during weekday work hours",
   "target": "laptop_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 8,
   "to": 17.5
  }
 ],
 "targets": {
  "board_game_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 21,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
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
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
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
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "class:plate": [
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
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 22.5,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "laptop_hana": [
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
    "chance": "almost_always"
   }
  ],
  "jacket_hana": [
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
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
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
  "keys_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 16,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "class:mug": [
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
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 23,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
