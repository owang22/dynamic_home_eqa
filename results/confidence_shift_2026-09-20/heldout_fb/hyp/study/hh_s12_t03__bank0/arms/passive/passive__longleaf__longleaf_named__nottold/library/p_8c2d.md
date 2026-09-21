# p_8c2d — Dog evening feeding: food bag dragged to the kitchen floor by Elena

Elena comes home at about 17:30 and takes over the dog for the evening. Between 18:00 and 21:00 she opens the dog food bag and pours a portion into the bowl on the kitchen floor. The bag is dragged from the pantry shelf down to the kitchen floor for the pour and stays there until it is put back (often the next morning). The bowl itself is a permanent fixture on the kitchen floor—it is sighted there 12 times across 4 days and never moves. The leash stays on the entry hook because there is no evening walk; the dog's walk was in the morning.

What sets this apart: no existing document places the dog_food_bag on the kitchen floor in the evening. The per-object evidence shows the bag at floor_k_k1 at 19:00 (× 2), 20:00 (× 1), and 21:00 (× 2), yet the mixture's worst-object list flags "predicted pantry_shelf_k1, actually floor_k_k1 — 2×." The other documents (p_a1b2, p_e5f6, p_7890) only pin the bowl, not the bag, in the evening window.

Refutation: if the dog food bag is sighted at the pantry shelf during 19:00–21:00 on two or more evenings, or if the bowl is found off the kitchen floor during that window, the feeding-location claim is wrong.

```json
{
 "claims": [
  {
   "claim": "The dog food bag is on the kitchen floor at 20:00 during the evening pour",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 19,
   "to": 21
  },
  {
   "claim": "The dog bowl is on the kitchen floor at 19:30 just before the evening feed",
   "target": "dog_bowl_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 19,
   "to": 20
  },
  {
   "claim": "The dog leash stays on the entry hook at 16:00 on a weekday (no evening walk)",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 15,
   "to": 17
  }
 ],
 "targets": {
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 21,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "almost_always"
   }
  ],
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ]
 }
}
```
