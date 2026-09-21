# p_2d9c — Morning Kitchen: Dog Feeding, Yuki's Tablet, Marco's Glasses

The household's morning runs on a tight 6:30–9:30 sequence. Yuki feeds the dog first (6:30–7:15): the dog bowl comes out to the counter, the food bag is opened from its resting spot on the kitchen floor, and the bowl is filled. The bowl stays on the counter while the dog eats, then goes back to the floor. Yuki then settles at the kitchen table with her tablet for morning reading or scrolling (7:30–9:00). Marco gets up, goes to the bathroom, and leaves his glasses on the bathroom shelf while he showers (8:00–9:00). By 9:15 the kitchen is clear again: tablet back to the nightstand, glasses back to the nightstand, dog bowl back to the floor.

This document differs from the library in three specific ways: (1) it places the dog bowl at the counter during the 7–8 h feeding window rather than on the floor all day; (2) it puts Yuki's tablet at the kitchen table 7–9 h rather than at the nightstand; (3) it puts Marco's glasses at the bathroom shelf 8–9 h rather than at the nightstand. The sightings confirm all three: dog_bowl at counter_k1 at 08:00, tablet_yuki at kitchen_table_k1 at 08:00, glasses_marco at bathroom_shelf_ba1 at 09:00.

Refutation: if the dog bowl is found on the floor at 07:30 on a weekday, or the tablet is at the nightstand at 08:00, or the glasses are at the nightstand at 08:30 while Marco is in the bathroom, this document is wrong.

```json
{
 "claims": [
  {
   "claim": "The dog bowl is at the kitchen counter during weekday morning feeding",
   "target": "dog_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Yuki's tablet is at the kitchen table during her weekday morning reading",
   "target": "tablet_yuki",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 8.5
  },
  {
   "claim": "Marco's glasses are on the bathroom shelf during his weekday morning shower",
   "target": "glasses_marco",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 8.25,
   "to": 9
  },
  {
   "claim": "The dog food bag is on the kitchen floor at 07:00 on a weekday",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 6.75,
   "to": 7.25
  }
 ],
 "targets": {
  "dog_bowl_shared": [
   {
    "days": "weekday",
    "from": 6.75,
    "to": 8,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7,
    "to": 8.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "tablet_yuki": [
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 7.5,
    "to": 9.5,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "glasses_marco": [
   {
    "days": "weekday",
    "from": 8,
    "to": 9.25,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9.5,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ]
 }
}
```
