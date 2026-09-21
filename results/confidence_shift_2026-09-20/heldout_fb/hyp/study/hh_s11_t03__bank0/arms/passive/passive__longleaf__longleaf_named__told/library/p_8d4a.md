# p_8d4a — Weekend Evening Living Room; Duster on the Coffee Table, Guitar on the Couch, Yoga on the Floor

This document captures a weekend-evening routine that no other document in the library addresses as a coherent sequence. On Saturday and Sunday evenings, the living room becomes the centre of activity: someone dusts the coffee table and surrounding furniture (the duster appears on the coffee table at 17:00 and 19:00 on day 5, three sightings total), Priya unrolls her yoga mat on the living room floor for an evening session (mat on floor_l_l1 at 20:00 on the weekend), and Hana brings her guitar to the couch for a relaxed playing session (guitar on couch_l1 at 21:00, two sightings).

What sets this apart: the duster's weekend migration to the coffee table is the key distinguishing prediction. Every other document leaves the duster on the storage shelf, and the mixture's worst-objects list flags three misses where the duster was predicted at storage_shelf_s1 but actually found at coffee_table_l1. This document also bundles the guitar-on-couch and yoga-mat-on-floor weekend evening patterns that are scattered across p_5b9c, p_4b6f, and p_e7a3 but never combined with the cleaning activity.

A look at the storage shelf at 17:00 or 19:00 on a weekend that finds the duster there would refute the cleaning claim. A look at the bedroom floor at 21:00 on a weekend that finds the guitar there (rather than the couch) would weaken the guitar claim. A look at wardrobe_b2 at 20:00 on a weekend that finds the yoga mat there would refute the yoga claim.

No objects leave the house during this evening window. Both residents are home.

```json
{
 "claims": [
  {
   "claim": "The duster is on the coffee table during the weekend late-afternoon cleaning, not on the storage shelf",
   "target": "duster_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 17,
   "to": 20
  },
  {
   "claim": "Hana's guitar is on the couch during the weekend evening, not in the bedroom",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 20,
   "to": 23
  },
  {
   "claim": "Priya's yoga mat is on the living room floor during the weekend evening yoga session",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The duster is back on the storage shelf by 21:00 after the cleaning is done",
   "target": "duster_shared",
   "expect": "storage_shelf_s1",
   "days": "weekend",
   "from": 21,
   "to": 24
  }
 ],
 "targets": {
  "duster_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_shelf_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 20,
    "to": 23,
    "at": "couch_l1",
    "chance": "sometimes"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 21,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
