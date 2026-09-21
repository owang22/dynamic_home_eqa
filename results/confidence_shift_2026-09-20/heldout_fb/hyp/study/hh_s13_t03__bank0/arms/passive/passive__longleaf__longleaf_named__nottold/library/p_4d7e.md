# p_4d7e — The 19:00 Cook: a Narrow Counter Window

Hana comes home at roughly 17:30–18:00 and begins dinner prep. The evidence is unambiguous that the major cooking tools are in storage at the 18:00 patrol (pan in the cupboard ×2, spatula in the drawer ×2, recipe book in the pantry ×2) and appear on the kitchen counter at the 19:00 patrol (one sighting each). The window in which they are actually *on the counter* is therefore very short—perhaps 18:45 to 19:15—because the robot's next pass at 20:00 does not find them there. During the actual cooking (stovetop work, 19:00–19:45) the pan and spatula are at the stove or sink, not the counter, which is why broader "counter at 18.5–20" claims keep failing. This document places the tools on the counter only in the narrow 18:45–19:15 prep-and-plate window and in storage before and after.

What sets this apart from p_b9c4 (which puts the pan on the counter 17.5–19) and p_7a3f (which uses 18.5–20): the counter window is tighter, centred on 19:00, and the document explicitly expects the tools to be *absent* from the counter during the active stovetop phase. If the robot ever catches the pan on the counter at 17:30 or 18:15, this document is wrong.

What would refute it: pan or spatula sighted on the counter at 17:00–18:30 on multiple occasions, or the recipe book on the counter at 18:00 (it is in the pantry at that hour).

```json
{
 "claims": [
  {
   "claim": "The pan is on the kitchen counter at 19:00 on a weekday (prep or plating, not stovetop)",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 18.75,
   "to": 19.25
  },
  {
   "claim": "The spatula is in the drawer at 18:00 on a weekday (cooking has not started)",
   "target": "spatula_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "The recipe book is in the pantry at 18:00 on a weekday (not yet in use)",
   "target": "recipe_book_shared",
   "expect": "pantry_shelf_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  },
  {
   "claim": "The pan is in the cupboard at 18:00 on a weekday (not yet in use)",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 18.5
  }
 ],
 "targets": {
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.75,
    "to": 19.25,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.75,
    "to": 19.25,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "recipe_book_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18.75,
    "to": 19.25,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
