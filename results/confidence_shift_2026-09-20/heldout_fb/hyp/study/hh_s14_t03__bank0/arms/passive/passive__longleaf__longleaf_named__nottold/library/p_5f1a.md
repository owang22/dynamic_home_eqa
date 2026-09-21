# p_5f1a — Night Resting: Guitar on Couch, Leash on Hook, Knife in Cupboard

Overnight (roughly 22:00–07:00) the household settles into its resting configuration, and several objects sit in places the library has been mis-predicting. Yuki's guitar rests on the living-room couch, not in the bedroom and not on anyone's person; she only picks it up for afternoon practice. The dog leash hangs on the entry hook overnight and is moved to the entry table in the evening when it is ready for the next walk. The kitchen knife sleeps in the cupboard (not the drawer) overnight and is returned to the drawer after evening use. The pan rests in the pantry shelf overnight, not the cupboard.

This document is distinguished by its overnight blocks. The evidence: guitar_yuki was at couch_l1 at 03:00 (the mixture predicted ON_PERSON); dog_leash_shared was at entry_hook_e1 at 03:00 (the mixture predicted entry_table_e1); kitchen_knife_shared was at cupboard_k1 at 03:00 (the mixture predicted drawer_k_k1); pan_shared was at pantry_shelf_k1 at 03:00 (the mixture predicted ON_PERSON). All four were wrong because the resting spots differ from the in-use spots.

Refutation: if the guitar is found in the bedroom at 03:00, the leash at the entry table at 03:00, the knife in the drawer at 03:00, or the pan in the cupboard at 03:00, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "Yuki's guitar is on the living room couch at 03:00",
   "target": "guitar_yuki",
   "expect": "couch_l1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The dog leash is on the entry hook at 03:00",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The kitchen knife is in the cupboard at 03:00",
   "target": "kitchen_knife_shared",
   "expect": "cupboard_k1",
   "days": "both",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The pan is on the pantry shelf at 03:00",
   "target": "pan_shared",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 2,
   "to": 5
  }
 ],
 "targets": {
  "guitar_yuki": [
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 15,
    "to": 20,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 19,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 22,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 22,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 22,
    "at": "drawer_k_k1",
    "chance": "usually"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
