# p_5e2a — Weekend Rest; Hana Sleeps In, Guitar on the Couch, Yoga at Eight

On weekends the household rhythm shifts. Hana sleeps in: the blanket is on her bed from 03:00 through 08:00 (three sightings) and her phone stays on the nightstand (sightings at 03:00 and 08:00). Priya takes a late-morning walk around 10:00–11:00 with the dog leash, her jacket, and her keys, all of which leave the house. In the afternoon Priya vacuums the living room (15:00, two sightings of the vacuum on the floor). The evening belongs to their respective hobbies: Hana plays guitar on the couch (21:00, two sightings) and Priya unrolls her yoga mat on the living room floor (20:00, one sighting). The dog bowl remains on the kitchen floor throughout. The blanket is on the couch on weekday mornings (Hana's post-shift TV) but migrates to the bed on weekend mornings.

This document is the only one that unifies the full weekend picture: Hana's sleep-in, Priya's walk, the vacuum, and the two evening hobbies. The guitar on the couch at weekend 21:00 and the yoga mat on the floor at weekend 20:00 are the key differentiators from the weekday-focused documents.

Refutation: finding the guitar in the bedroom on a weekend evening (19:00–23:00), or the blanket on the couch (rather than the bed) on a weekend morning, would contradict this document. Finding the yoga mat in the wardrobe at weekend 20:00 would also weaken it.

```json
{
 "claims": [
  {
   "claim": "On weekend mornings the blanket is on Hana's bed because she is sleeping in",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 3,
   "to": 9
  },
  {
   "claim": "On weekend evenings Hana plays guitar on the couch in the living room",
   "target": "guitar_hana",
   "expect": "couch_l1",
   "days": "weekend",
   "from": 19,
   "to": 23
  },
  {
   "claim": "On weekend evenings Priya unrolls her yoga mat on the living room floor",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 20,
   "to": 21
  },
  {
   "claim": "On weekend mornings Hana's phone is on her nightstand while she sleeps in",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 3,
   "to": 9
  },
  {
   "claim": "On weekend afternoons Priya vacuums and the vacuum is on the living room floor",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 15,
   "to": 16
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 3,
    "to": 9,
    "at": "bed_b1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 19,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
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
    "from": 20,
    "to": 21,
    "at": "floor_l_l1",
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
  "vacuum_cleaner_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "storage_floor_s1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 15,
    "to": 16,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "jacket_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
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
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
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
  ]
 }
}
```
