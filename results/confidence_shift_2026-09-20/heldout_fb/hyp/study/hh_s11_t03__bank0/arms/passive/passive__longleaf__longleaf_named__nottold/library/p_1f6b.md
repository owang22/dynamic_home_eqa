# p_1f6b — Weekend Evening Living Room; Guitar on the Couch, Blanket on the Table, Mat on the Floor

On weekend evenings the living room becomes a shared activity space. The robot sees the guitar on couch_l1 at 21:00 (two sightings) while Hana plays. The blanket is on coffee_table_l1 at 20:00 (three sightings) — pulled over for the evening. Priya's yoga mat is on floor_l_l1 at 20:00 (one sighting), unrolled for her evening session. The snack bowl appears on coffee_table_l1 at 21:00 (one sighting) for shared snacking. By 23:00 the guitar returns to bedroom_floor_b1 (one sighting at 21:00 on the same pass shows the transition).

This document captures the weekend-evening cluster that no single existing document covers in full. p_5e2a and p_8c3f cover the weekend-morning sleep-in; p_4e7a covers the guitar on the couch but not the blanket and mat simultaneously. The distinguishing prediction is the co-occurrence: guitar on couch AND blanket on coffee table AND yoga mat on floor, all in the 20:00–22:00 weekend window.

What would refute it: a weekend evening sighting (19:00–23:00) that finds the guitar in bedroom_floor_b1 while the blanket is also on the coffee table, or a weekend evening pass that finds the yoga mat in wardrobe_b2 while the guitar is on the couch.

```json
{
 "claims": [
  {
   "claim": "On weekend evenings Hana's guitar is on the couch in the living room",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 19,
   "to": 23
  },
  {
   "claim": "On weekend evenings the blanket is on the coffee table",
   "target": "blanket_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 19,
   "to": 22
  },
  {
   "claim": "On weekend evenings Priya's yoga mat is on the living room floor",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "On weekend evenings the snack bowl is on the coffee table",
   "target": "snack_bowl_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 19,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 23,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 5,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 5,
    "to": 14,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 19,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 9,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 9,
    "to": 19,
    "at": "couch_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 22,
    "to": 24,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 14,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 19,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 21,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 18,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
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
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
