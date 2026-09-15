# p_f8d2 — Evening kitchen-table routine: dishes, makeup removal, and planning at the kitchen table after 18:00

Mara lives alone and follows a consistent evening routine in the kitchen after 18:00. After dinner (around 18:30–19:00), she sits at the kitchen table to do her evening routine: removing makeup (makeup kit is at the kitchen table, not the bathroom shelf, during this window), journaling or planning the next day (notebook and pen at the chair next to the kitchen table), and packing her lunchbox for the next day (lunchbox ends up at the dish rack while she cleans it). She then does the dishes: plates, pots, and mugs go to the sink and dish rack. By 22:00 the kitchen is cleared and the objects return to their resting places.

This document is specifically about the 18:00–23:00 window and overrides the "resting place" predictions that other documents make for the evening. The mixture's worst-objects list since the last call shows a cluster of 22:00 sightings that no current document models: makeup_kit at kitchen_table (predicted bathroom_shelf), notebook at chair_k1 (predicted counter), pen at chair_k1 (predicted dish_rack), lunchbox at dish_rack (predicted sink), mug_mara at dish_rack (predicted kitchen_table), plate_shared_1 at sink (predicted ON_PERSON), pot_shared_1 at sink (predicted ON_PERSON). This document explains that cluster as a single evening routine.

What sets this apart from the other documents: (1) The makeup kit is at the kitchen table (not the bathroom shelf) during 18–23h — she does her evening skincare at the kitchen table. (2) The notebook and pen are at chair_k1 (not the counter or dish rack) during 18–23h — she journals at the kitchen table. (3) The lunchbox is at dish_rack_k1 during 19–23h (not the counter) — she's cleaning it for the next day. (4) Plates and pots are at sink_k1 during 19–22h (dishes being washed), not ON_PERSON or in the cupboard. (5) The mug is at dish_rack_k1 during 19–22h (just washed, drying). What would refute it: the makeup kit found at the bathroom shelf at 21:00, the notebook found at the counter at 22:00, or the lunchbox found at the counter at 21:00.

```json
{
 "claims": [
  {
   "claim": "The makeup kit is at the kitchen table at 22:00 (evening routine, not the bathroom shelf)",
   "target": "makeup_kit_mara",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 20,
   "to": 23
  },
  {
   "claim": "The notebook is at the kitchen chair at 22:00 (journaling, not the counter)",
   "target": "notebook_mara",
   "expect": "chair_k1",
   "days": "both",
   "from": 20,
   "to": 23
  },
  {
   "claim": "The plate shared 1 is at the sink at 21:00 (dishes being washed)",
   "target": "plate_shared_1",
   "expect": "sink_k1",
   "days": "both",
   "from": 19,
   "to": 22
  },
  {
   "claim": "The lunchbox is at the dish rack at 22:00 (cleaned and drying, not the counter)",
   "target": "lunchbox_mara",
   "expect": "dish_rack_k1",
   "days": "both",
   "from": 20,
   "to": 23
  }
 ],
 "targets": {
  "makeup_kit_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 23,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "notebook_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 23,
    "at": "chair_k1",
    "chance": "usually"
   }
  ],
  "pen_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 23,
    "at": "chair_k1",
    "chance": "usually"
   }
  ],
  "lunchbox_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 23,
    "at": "dish_rack_k1",
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
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "class:pot": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "sink_k1",
    "chance": "usually"
   }
  ],
  "mug_mara": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "class:mug": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "class:pan": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 8,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 17,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
