# p_7e2b — Weekend Reset: No Commute Packing, Objects at Home Storage

On weekends, Elena does not stage her work items at the entry hook the night before because there is no commute. The laptop, which on weekday nights is found at the entry hook (packed in the bag), instead rests at the bedroom dresser on weekends — the sightings on day 5 (Sunday) confirm it three times at dresser_b1 where the mixture predicted entry_hook_e1. The notebook and pen, which get staged at the entry hook on weekday nights, stay at the bedroom desk on weekends. Priya's glasses remain on the nightstand all weekend; she has no weekday desk session, so they never migrate to desk_b1. The blanket shifts from the couch (its weekday resting spot) to the armchair, matching the more relaxed weekend seating pattern confirmed across all three weekend patrol passes. Elena's towel stays on the towel rack on weekends (used and replaced in the morning) rather than lingering on the bathroom shelf as it does on weekdays. Elena's phone stays at the nightstand (no entry-table staging for a commute). Her water bottle is at the dish rack (washed, not at the dining table for a work lunch). The shopping bag appears at the counter on weekend mornings (set down after a grocery run, not stored in the pantry).

This hypothesis sets itself apart by predicting the *absence* of the weekday overnight-packing pattern on weekends. Where the commuter documents (p_3a7c, p_b4e8, p_9e1f) predict laptop and notebook at the entry hook, this document predicts them in the bedroom. Where the weekday documents predict the blanket on the couch and the glasses at the desk, this predicts armchair and nightstand.

Refutation: if the laptop is found at the entry hook on a weekend morning (overnight packing still happening), if the blanket is on the couch on a weekend, or if Priya's glasses are at the bedroom desk on a weekend.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop rests at the bedroom dresser on a weekend (no overnight packing for a commute)",
   "target": "laptop_elena",
   "expect": "dresser_b1",
   "days": "weekend",
   "from": 0,
   "to": 8
  },
  {
   "claim": "Priya's glasses stay on the nightstand all weekend (no weekday desk session)",
   "target": "glasses_priya",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "The blanket is on the armchair on a weekend (relaxed weekend seating differs from weekday couch)",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Elena's towel is on the towel rack on a weekend (used and replaced, not left on the shelf)",
   "target": "towel_elena",
   "expect": "towel_rack_ba1",
   "days": "weekend",
   "from": 8,
   "to": 16
  },
  {
   "claim": "Elena's phone stays at the nightstand on a weekend (no commute, no entry table staging)",
   "target": "phone_elena",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dresser_b1",
    "chance": "sometimes"
   }
  ],
  "notebook_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "pen_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "sometimes"
   }
  ],
  "glasses_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "towel_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "phone_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "usually"
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
  "keys_elena": [
   {
    "days": "weekend",
    "from": 10,
    "to": 16,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
