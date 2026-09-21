# p_9c0d — Omar's morning routine: he is in the bedroom until 09:00, then kitchen

Omar wakes up, reads in bed (book, glasses at nightstand) from 06:00 to 09:00. Then he moves to the kitchen for breakfast (mug, bowl on table) from 09:00 to 11:00. Then he does a quick gaming session (controller at TV stand) from 11:00 to 13:00 before leaving at 13:40. In the evening, he comes home at 23:00, eats a quick snack (mug at kitchen table 23:00–00:30), then games until 02:00. What sets this hypothesis apart: the controller is at the TV stand 11:00–13:00 in the morning (gaming before work), and the book/glasses are at the nightstand 06:00–09:00 but may be moved by 10:00. What would refute it: controller_omar sighted at the TV stand at 07:00 on a weekday (it should not be in use yet).

```json
{
 "claims": [
  {
   "claim": "Omar's book is at the nightstand at 7am on a weekday",
   "target": "book_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Omar's controller is at the TV stand at 11am on a weekday (gaming)",
   "target": "controller_omar",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 11,
   "to": 13
  },
  {
   "claim": "Omar's mug is on the kitchen table at 10am on a weekday",
   "target": "mug_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 12
  },
  {
   "claim": "Omar's controller is at the TV stand at 7am on a weekday (not yet in use)",
   "target": "controller_omar",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 6,
   "to": 10
  }
 ],
 "targets": {
  "book_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 13.5,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "glasses_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "controller_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13,
    "at": "ON_PERSON",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "ON_PERSON",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 2,
    "at": "ON_PERSON",
    "chance": "usually"
   }
  ],
  "mug_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 1,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   }
  ],
  "keys_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ]
 }
}
```
