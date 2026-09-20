# p_2ad7 — The Balcony Gardener: Watering at dawn and dusk

The residents tend plants on the balcony. The watering can is brought out to balcony_floor_y1 in the early morning (7:00–8:30) and again in the late afternoon (17:00–19:00) on all days. At other times it is stored on the balcony floor or brought inside. On weekends the morning watering is later (8:00–9:30).

What sets this hypothesis apart: watering_can_shared is on balcony_floor_y1 at 7:00–8:30 and 17:00–19:00 on weekdays. If the robot patrols at 4:00, the can is not yet out; at 8:00 it is. This is a fixed daily ritual distinct from a one-time observation.

What would refute it: watering_can_shared sighted on the balcony at 12:00 on a weekday (outside the watering windows) or never seen on the balcony.

```json
{
 "claims": [
  {
   "claim": "The watering can is on the balcony floor in the early morning on weekdays",
   "target": "watering_can_shared",
   "expect": "balcony_floor_y1",
   "days": "weekday",
   "from": 7,
   "to": 8.5
  },
  {
   "claim": "The watering can is on the balcony floor in the late afternoon on weekdays",
   "target": "watering_can_shared",
   "expect": "balcony_floor_y1",
   "days": "weekday",
   "from": 17,
   "to": 19
  },
  {
   "claim": "The watering can is on the balcony on weekend mornings",
   "target": "watering_can_shared",
   "expect": "balcony_floor_y1",
   "days": "weekend",
   "from": 8,
   "to": 9.5
  },
  {
   "claim": "The watering can is not on the balcony at midday on weekdays",
   "target": "watering_can_shared",
   "expect": "balcony_floor_y1",
   "days": "weekday",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "watering_can_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "balcony_floor_y1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 8.5,
    "at": "balcony_floor_y1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 17,
    "to": 19,
    "at": "balcony_floor_y1",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 8,
    "to": 9.5,
    "at": "balcony_floor_y1",
    "chance": "almost_always"
   }
  ],
  "vase_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "usually"
   }
  ]
 }
}
```
