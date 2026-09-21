# p_9d2a — Priya's Saturday Rhythm; Late Walk, Yoga, Armchair Afternoon

Priya's Saturday follows her stated weekend rhythm: a late-morning walk with the dog (10:00–11:00, later than her weekday 7:00 walk), then a yoga session in the living room (11:30–12:30) where the mat unrolls on floor_l_l1, then settling into the armchair for reading (14:00–17:00). Her water bottle travels to the armchair with her. The camera stays on the bookshelf all day (she is "around the house," not going out for a photography trip). The magazine and book migrate to the armchair for the afternoon reading block. The yoga mat returns to wardrobe_b2 by 13:00.

What sets this apart: p_c9d4 places Priya's yoga at 06:00 (early morning), but the weekend message says "around the house more" and her stated weekend routine is a *late-morning* walk, pushing yoga to mid-morning. The dog leash is out at 10:00–11:00 (not 7:00–8:00 as on weekdays). The water bottle is at the armchair during the reading block (supported by p_d5e8's weekday 8:50–11:00 armchair claim which scored 2-for). The camera is NOT out for photography (unlike a weekday where she might take it on her walk).

What would refute it: if the yoga mat is in wardrobe_b2 at 12:00, the mid-morning yoga block fails. If the dog leash is on the entry hook at 10:30, the walk timing is wrong. If the magazine is on the coffee table or bookshelf at 15:00, the armchair reading claim weakens. If the camera is sighted out of the house or on person, the "stays home" claim is contradicted.

```json
{
 "claims": [
  {
   "claim": "The yoga mat is on the living room floor during Priya's Saturday mid-morning yoga session",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 11.5,
   "to": 12.5
  },
  {
   "claim": "Priya's magazine is in the armchair during the Saturday afternoon reading block",
   "target": "magazine_priya",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Priya's water bottle is at the armchair during the Saturday afternoon",
   "target": "water_bottle_priya",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "The dog leash is out with Priya during the late-morning Saturday walk",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 11
  },
  {
   "claim": "Priya's camera stays on the bookshelf all Saturday and does not go out",
   "target": "camera_priya",
   "expect": "bookshelf_l1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "yoga_mat_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b2",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 11.5,
    "to": 12.5,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "weekend",
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
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
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
    "days": "weekend",
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
    "chance": "usually"
   }
  ],
  "magazine_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "book_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dining_table_d1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 14,
    "to": 17,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "camera_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "shoes_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "usually"
   }
  ]
 }
}
```
