# p_d2b9 — Weekend morning: slow start, dog fed by 8, Saturday baking

On weekends both residents sleep in. At 3:00 the robot finds them in the bedroom (or Elena in the living room on Saturday, kitchen on Sunday). The first real activity is the morning dog feeding around 7:00–8:00, when the dog food bag is dragged from the pantry shelf to the kitchen floor. Priya's glasses appear on the bathroom shelf at 7:00 as part of her morning routine. On Saturday, Elena bakes in the morning and the baking tray is at the kitchen counter from about 9:00 to 12:00; on Sunday the tray stays in the pantry. Elena's laptop is at the dresser on weekend mornings (not the entry hook as on weekdays), consistent with no commute.

What would refute this: finding the dog food bag still in the pantry at 7:30 on a weekend, finding Priya's glasses on the nightstand at 7:00 on a weekend, or finding the baking tray in the pantry on a Saturday between 9 and 12.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the kitchen floor at 7:30 on a weekend morning",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekend",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Priya's glasses are on the bathroom shelf at 7:00 on a weekend",
   "target": "glasses_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 7,
   "to": 8
  },
  {
   "claim": "The baking tray is at the kitchen counter during Saturday morning baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 9,
   "to": 12
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "weekend",
    "from": 7,
    "to": 8,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "glasses_priya": [
   {
    "days": "weekend",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "baking_tray_shared": [
   {
    "days": "weekend",
    "from": 9,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 6,
    "to": 12,
    "at": "dresser_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
