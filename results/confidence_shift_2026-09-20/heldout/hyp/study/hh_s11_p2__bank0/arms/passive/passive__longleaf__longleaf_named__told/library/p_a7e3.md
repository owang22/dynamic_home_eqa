# p_a7e3 — Weekend "Around the House": Blanket in Bed, Remote on Stand, Tablet at Desk

On weekends the household shifts into a "resting" layout that is almost the inverse of the weekday pattern. The shared blanket, which on weekdays migrates between the armchair, couch, and coffee table, stays on Hana's bed (bed_b1) for the entire Saturday and will do the same on Sunday. The remote, which on weekdays sits on the living-room floor through the morning and afternoon, stays on the TV stand all day on weekends—no one is moving it around for a TV session. Priya's tablet, scattered across the coffee table, dresser, and bedroom floor on weekdays, goes to her desk (desk_b2) for the full waking day on weekends: she photographs, reads, and plans board games there. Hana's tablet stays on her nightstand all day (she's not working). Hana's book moves from the nightstand to the bookshelf; Priya's book shifts from the nightstand to the bookshelf in the afternoon. The medication, which on weekdays is split between the coffee table and the medicine cabinet, stays in the cabinet all weekend. The laundry basket and Hana's towel end up on Hana's bedroom floor (she's been up and about, not following the weekday bathroom routine). The guitar remains on Hana's bedroom floor, as it does every day.

This document is distinguished from p_5c6a (remote on floor by day), p_9c2f (remote and blanket on coffee table for TV), p_c3d4 (blanket on coffee table evening), and p_4f8e (tablet_priya on bedroom floor / nightstand) by placing all these objects in their weekend resting spots. It would be refuted if the blanket is found in the living room, the remote off the TV stand, or Priya's tablet off the desk during weekend hours.

```json
{
 "claims": [
  {
   "claim": "The shared blanket is on Hana's bed all day on the weekend, not in the living room",
   "target": "blanket_shared",
   "expect": "bed_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The remote stays on the TV stand the entire weekend day",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Priya's tablet is at her desk during her weekend waking hours",
   "target": "tablet_priya",
   "expect": "desk_b2",
   "days": "weekend",
   "from": 10,
   "to": 22
  },
  {
   "claim": "Hana's book is on the bookshelf, not the nightstand, on the weekend",
   "target": "book_hana",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "The laundry basket is on Hana's bedroom floor on the weekend, not in the bathroom",
   "target": "laundry_basket_shared",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "almost_always"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ],
  "tablet_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "book_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 14,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ],
  "medication_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "medicine_cabinet_ba1",
    "chance": "almost_always"
   }
  ],
  "laundry_basket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "towel_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
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
  "magazine_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ]
 }
}
```
