# p_a9d3 — Weekend Morning: Bathroom Shelf Routine, Dish Rack Rest, Slow Start

On weekends both residents sleep in and their morning routines are slower and more spread out. Elena's skincare moves from the nightstand (its weekday resting spot between uses) to the bathroom shelf in the morning, where she uses it at her leisure; the weekend sightings show it at the bathroom shelf at both 08:00 and 16:00. Priya's razor is on the bathroom shelf rather than the sink on weekend mornings — the day-5 08:00 sighting found it at bathroom_shelf_ba1 three times where the mixture predicted sink_ba_ba1. Elena's toiletry bag is at the bathroom shelf from the morning onward (in active use for the day, not stowed at the dresser as on weekdays). Priya's skincare appears at the bathroom sink on weekends (in the middle of her routine, not yet back on the shelf). In the kitchen, the slower morning means items are in their "clean and stored" positions: Elena's glass is in the cupboard (washed and put away after a weekend breakfast, not left at the sink as on weekdays), the kitchen knife is in the dish rack (washed, drying from breakfast prep), and the shopping bag is at the counter (set down after a weekend grocery run). Priya's water bottle is at the sink in the early morning (washed and filled before her late-morning walk). The hair dryer appears at the bedroom desk in the afternoon (Elena styling her hair for the social evening, using the desk as a vanity). The ironing board goes into the wardrobe in the afternoon (stored away, not in active use on weekends).

This hypothesis predicts a slower weekend morning where personal-care items are at the bathroom (in use or just used) rather than at their weekday resting spots, and kitchen items are in their "clean and stored" positions (cupboard, dish rack) rather than their "in use" positions (sink, counter). It differs from the weekday documents by placing skincare, razor, and toiletry bag at the bathroom shelf, and glass and knife at cupboard and dish rack respectively.

Refutation: if the skincare is at the nightstand on a weekend morning (weekday pattern persists), if the razor is at the sink (not shelf), or if the glass is at the sink (not cupboard).

```json
{
 "claims": [
  {
   "claim": "Elena's skincare is on the bathroom shelf during her weekend morning routine",
   "target": "skincare_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Priya's razor is on the bathroom shelf on a weekend morning (used and set aside)",
   "target": "razor_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 7,
   "to": 12
  },
  {
   "claim": "Elena's glass is in the cupboard on a weekend morning (washed and stored, not at the sink)",
   "target": "glass_elena",
   "expect": "cupboard_k1",
   "days": "weekend",
   "from": 0,
   "to": 10
  },
  {
   "claim": "The kitchen knife is in the dish rack on a weekend morning (washed from breakfast prep)",
   "target": "kitchen_knife_shared",
   "expect": "dish_rack_k1",
   "days": "weekend",
   "from": 0,
   "to": 10
  },
  {
   "claim": "Priya's water bottle is at the sink on a weekend morning (washed and filled before her walk)",
   "target": "water_bottle_priya",
   "expect": "sink_k1",
   "days": "weekend",
   "from": 6,
   "to": 10
  }
 ],
 "targets": {
  "skincare_elena": [
   {
    "days": "weekend",
    "from": 7,
    "to": 16,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "razor_priya": [
   {
    "days": "weekend",
    "from": 7,
    "to": 16,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "toiletry_bag_elena": [
   {
    "days": "weekend",
    "from": 7,
    "to": 16,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "skincare_priya": [
   {
    "days": "weekend",
    "from": 7,
    "to": 16,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "weekend",
    "from": 10,
    "to": 18,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "glass_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "dish_rack_k1",
    "chance": "sometimes"
   }
  ],
  "shopping_bag_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekend",
    "from": 6,
    "to": 10,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "wardrobe_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
