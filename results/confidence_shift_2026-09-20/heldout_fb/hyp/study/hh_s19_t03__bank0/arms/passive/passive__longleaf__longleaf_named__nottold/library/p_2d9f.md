# p_2d9f — The 18:15 cook: pan, pot, and knife emerge from storage together

The sightings fix the cooking window tightly. At 18:00 the pan is in the cupboard, the pot is in the cupboard (one sighting) and on the counter (one sighting, mid-move), and the kitchen knife is in the drawer (one sighting) and on the counter (one sighting). By 19:00 the pan is on the counter, the knife is on the counter, and Marco's glass is at the kitchen table. This means the cooking *starts* around 18:15–18:30, not at 17:30. The pan, pot, and knife all leave their storage spots in a narrow 18:00–18:30 window and are on the counter by 19:00. Dinner is at the kitchen table around 19:00 (Marco's glass is there at 19:00; Omar's plate was at the kitchen table at 12 for lunch but is back in the cupboard by 18, so dinner plates go out fresh). Cleanup returns everything to the cupboard/drawer by 20:00–22:00.

This document differs from p_789a (pan on counter 17.5–19, contradicted by the 18:00 cupboard sighting) and from p_b2e9 (pan in cupboard until 19:00, too late given the 19:00 counter sighting). It also differs from p_9c3a in that the pot is already being moved at 18:00, not still in the cupboard until 18:30.

What would refute this: a sighting of the pan on the counter before 18:00 on a weekday, or the knife still in the drawer at 19:30.

```json
{
 "claims": [
  {
   "claim": "The pan is still in the cupboard at 18:00 before cooking starts",
   "target": "pan_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 17.5,
   "to": 18.25
  },
  {
   "claim": "The pan is on the counter during the cooking window",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "The kitchen knife is on the counter during cooking",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18.5,
   "to": 19.5
  },
  {
   "claim": "Marco's glass is at the kitchen table during dinner",
   "target": "glass_marco",
   "expect": "kitchen_table_k1",
   "days": "both",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "The pot is on the counter during the cooking window",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 18.25,
   "to": 19.5
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
    "days": "both",
    "from": 18.25,
    "to": 20,
    "at": "counter_k1",
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
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
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
    "days": "both",
    "from": 18.25,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "glass_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "plate_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18.5,
    "to": 20,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "bowl_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17.5,
    "to": 19.5,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
