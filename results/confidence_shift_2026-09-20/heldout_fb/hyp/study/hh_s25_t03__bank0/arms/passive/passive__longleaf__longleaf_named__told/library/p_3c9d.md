# p_3c9d — Sick day evening: Omar on the couch, low-energy household

By evening Omar has moved from bed to the couch, wrapped in the blanket, watching TV or dozing (his two favourite pastimes). The remote is in use. Marco leaves his desk around 5:30, does a short evening meditation (cushion on the bedroom floor), then joins Omar on the couch for TV or settles into the armchair with a book. Dinner is simple—Marco makes something light while Omar rests. The snack bowl comes out to the coffee table for the couch. The household is more sedentary than a normal evening: no running, no errands, no energy for a second wind.

This differs from p_e1a5 in that Marco does not run in the evening (the household is low-energy on a sick day) and Omar is available for shared TV rather than watching alone. It differs from p_b8c2 (separate evenings) in that Omar is up and on the couch, making shared TV likely. It differs from p_a3f7 in that the evening is quieter and the blanket is in active use on the couch rather than just resting there.

This would be refuted if: the blanket is still in the bedroom at 20:00; the remote is not sighted in use (no TV happens); Omar is still in the bedroom at 21:00; or Marco's running shoes are out of the house in the evening.

```json
{
 "claims": [
  {
   "claim": "The blanket has moved to the couch by 8 PM as Omar settles in for the evening",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Marco's running shoes remain at the shoe rack in the evening (no run on a sick day)",
   "target": "running_shoes_marco",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 19.5,
   "to": 21
  },
  {
   "claim": "The remote is on the TV stand during the evening TV session",
   "target": "remote_shared",
   "expect": "tv_stand_l1",
   "days": "weekday",
   "from": 20,
   "to": 22
  },
  {
   "claim": "Marco's meditation cushion is on the bedroom floor during his short evening meditation",
   "target": "meditation_cushion_marco",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 18.5,
   "to": 19.25
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekday",
    "from": 18,
    "to": 23,
    "at": "couch_l1",
    "chance": "usually"
   }
  ],
  "remote_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "meditation_cushion_marco": [
   {
    "days": "weekday",
    "from": 18,
    "to": 19.25,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "running_shoes_marco": [
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "class:remote": [
   {
    "days": "weekday",
    "from": 19,
    "to": 22,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ]
 }
}
```
