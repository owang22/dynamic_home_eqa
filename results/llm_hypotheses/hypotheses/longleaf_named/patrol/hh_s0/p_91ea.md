# p_91ea — The Shared Dog Walk: Both residents walk the dog together in the evening

Unlike p_f4a0 (Yuki walks alone at 7) or p_a3f1 (Nora walks at 19:30), here both residents walk the dog together around 19:30–20:30 on all days. The leash is OUT_OF_HOUSE during that window. In the morning, no one walks the dog (the dog stays in the house). On weekends the walk is at 10:00–11:00.

What sets this hypothesis apart: the dog leash is at the entry hook in the morning (7:00–8:00) on weekdays — unlike p_f4a0 where it is gone. It goes out at 19:30. On weekends it goes out at 10:00.

What would refute it: dog_leash_shared sighted OUT_OF_HOUSE at 7:00 on a weekday, or at the entry hook at 20:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "The dog leash is at the entry hook at 7 a.m. on weekdays (no morning walk)",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 6,
   "to": 9
  },
  {
   "claim": "The dog leash is out of the house at 19:30 on weekdays",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 19,
   "to": 20.5
  },
  {
   "claim": "The dog leash is out of the house at 10 a.m. on weekends",
   "target": "dog_leash_shared",
   "expect": "OUT_OF_HOUSE",
   "days": "weekend",
   "from": 10,
   "to": 11
  },
  {
   "claim": "The dog leash is at the entry hook at 8 a.m. on weekends",
   "target": "dog_leash_shared",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 7,
   "to": 9
  }
 ],
 "targets": {
  "dog_leash_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 19,
    "to": 20.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "floor_k_k1",
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
