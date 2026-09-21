# p_8a4b — Weekend dinner cooking: knife, spatula, and pot all on the counter

Weekend cooking is a fuller affair than the weekday pan-and-board routine. On Saturday and Sunday evenings (around 18:30–20:00), both residents are home and there is time for a proper meal. The kitchen knife comes out of the drawer and sits on the counter for chopping. The spatula joins it for flipping. The pot goes on the counter (or the stove beside it) for a soup or stew alongside the pan. The cutting board is on the counter throughout. By 20:00 the pot is still out (it's simmering), and the knife may be washed and put in the sink.

This differs from p_c007 and p_e1a5, which describe weekday cooking as pan-and-board only, with the knife staying in the drawer and the pot in the cupboard. It differs from p_8d2c, which says the pan stays in the cupboard. Here the whole utensil set is deployed. It would be refuted if, on a weekend 19:00 pass, the knife is still in the drawer AND the spatula is in the drawer AND the pot is in the cupboard—meaning no full cooking happened.

```json
{
 "claims": [
  {
   "claim": "The kitchen knife is on the counter during weekend dinner cooking (full prep, not just pan)",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 18.5,
   "to": 20
  },
  {
   "claim": "The pot is on the counter during weekend dinner cooking (simmering alongside the pan)",
   "target": "pot_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 18.5,
   "to": 20.5
  },
  {
   "claim": "The spatula is on the counter during weekend dinner cooking (flipping, not just the pan)",
   "target": "spatula_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 18.5,
   "to": 20
  }
 ],
 "targets": {
  "kitchen_knife_shared": [
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "pot_shared": [
   {
    "days": "weekend",
    "from": 18,
    "to": 20.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 18,
    "to": 20,
    "at": "counter_k1",
    "chance": "usually"
   }
  ]
 }
}
```
