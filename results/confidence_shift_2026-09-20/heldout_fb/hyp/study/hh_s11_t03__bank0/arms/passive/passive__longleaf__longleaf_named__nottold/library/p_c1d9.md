# p_c1d9 — Hana's Post-Shift Wind-Down; Kitchen Snack Then Living Room TV

After Hana comes home from her night shift at 23:00, she goes straight to the kitchen for a snack: her glass and the shared snack bowl appear on the counter (two sightings each at 23:00). The snack bowl had been on the counter since dinner prep at 19:00 (three sightings), moved to the coffee table for Priya's TV at 21:00 (one sighting), and returns to the counter for Hana's late snack. After eating, Hana moves to the living room for TV: the remote ends up on the living room floor (two sightings at 03:00) and the blanket drapes over the armchair (two sightings at 03:00). By 02:00–03:00 she is in her bedroom, phone on the nightstand, tablet on the nightstand. Her handbag is left at the entry on the floor or hook. The mug goes back in the cupboard. This 23:00–05:00 window is when the robot is most likely to be asked about kitchen and living-room items, because Hana is the only resident awake and the objects are in their post-shift positions.

This document differs from p_c5d1 (which also covers the post-shift kitchen but has been getting "against" votes on the glass claim) by narrowing the glass window to 23:00–24:00 only and adding the living-room TV phase as a distinct block. The remote on the floor and blanket on the armchair at 03:00 are the key markers that separate this from the daytime documents.

Refutation: finding the remote on the TV stand at 03:00 on a weekday, or the blanket on the couch (rather than the armchair) during 02:00–05:00 on a weekday, would contradict this document. Finding the snack bowl in the cupboard at 23:00 would also weaken it.

```json
{
 "claims": [
  {
   "claim": "The remote is on the living room floor during Hana's post-shift TV in the early morning",
   "target": "remote_shared",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The blanket is on the armchair during Hana's post-shift TV in the early morning",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekday",
   "from": 2,
   "to": 5
  },
  {
   "claim": "The snack bowl is on the kitchen counter during Hana's post-shift snack",
   "target": "snack_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Hana's phone is on her nightstand after she has come home from her shift",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Hana's handbag is on the entry floor in the early morning after her shift",
   "target": "handbag_hana",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 0,
   "to": 4
  }
 ],
 "targets": {
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
    "from": 2,
    "to": 5,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 2,
    "to": 5,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 4,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
