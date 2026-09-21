# p_7d1c — Omar's tablet lives on the nightstand; gaming at the TV stand

Omar's tablet is not a kitchen-chair object. The per-object evidence shows nightstand_b1 as its dominant resting spot (9 of 12 weekday 9–17 h looks found it there; the hourly sightings confirm nightstand_b1 x3 at 12:00, 14:00, 16:00, and 18:00). It briefly appears at kitchen_table_k1 around 10:00 (one pass shows kitchen_table_k1 x2, chair_k1 x1), likely while Omar has his morning coffee and scrolls before his gaming block. By 12:00 it is back on the nightstand and stays there through the evening. The controller, by contrast, is firmly at tv_stand_l1 (12/12 weekday looks, 36 sightings, single receptacle).

This hypothesis is set apart from p_e5f6, p_7a3f, p_4e91, and p_5b7e, all of which place the tablet at chair_k1 for extended windows and have accumulated 14–21 "against" tallies on that claim. It is set apart from p_b2c8, which also puts the tablet at chair_k1. The tablet's home is the nightstand; the kitchen chair is where Omar sits, not where the tablet rests.

Refutation: tablet_omar sighted at chair_k1 on three or more consecutive weekday passes between 12:00 and 22:00; controller_omar absent from tv_stand_l1 during the 10:00–13:00 gaming window.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the nightstand at 14:00 on a weekday while he is at work",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 13,
   "to": 15
  },
  {
   "claim": "Omar's controller is at the TV stand at 11:00 on a weekday during his gaming block",
   "target": "controller_omar",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Omar's tablet is at the nightstand at 22:00 on a weekday",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "controller_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "almost_always"
   }
  ]
 }
}
```
