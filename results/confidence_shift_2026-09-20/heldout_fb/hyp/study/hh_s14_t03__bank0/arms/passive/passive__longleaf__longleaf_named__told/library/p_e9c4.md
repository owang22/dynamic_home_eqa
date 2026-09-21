# p_e9c4 — Marco's 11 pm Return: Jacket on Hook, Cleanup Begins

Marco clocks off his night shift at roughly 11 pm and walks in. His jacket goes on the entry hook, his shoes on the shoe rack, his keys on the entry table, and his backpack hangs beside the jacket. He may head to the bathroom for a quick freshen-up, leaving his glasses on the bathroom shelf. By this hour the friends may be leaving or already gone; the board game is being put back on the bookshelf and the glasses are heading back to the cupboard. The coffee table is being cleared. The dog, having been in the living room all evening, settles on the kitchen floor near its bowl.

This document is distinct in the 22:30–24:00 window: it predicts Marco's personal items (jacket, keys, shoes, backpack) at the entry, which no other document places there on a weekday evening because Marco is normally still at work. It also predicts the board game returning to the bookshelf and glasses returning to the cupboard, marking the transition from the social gathering back to the resting state. If the robot finds Marco's jacket still in his bag or on his person at 23:00, or the board game still on the coffee table at 23:00, the timing of the cleanup is off.

```json
{
 "claims": [
  {
   "claim": "Marco's jacket is on the entry hook after he comes home at 11",
   "target": "jacket_marco",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "Marco's keys are on the entry table after he comes home at 11",
   "target": "keys_marco",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 23,
   "to": 24
  },
  {
   "claim": "The board game is back on the bookshelf after the gathering winds down",
   "target": "board_game_shared",
   "expect": "bookshelf_l1",
   "days": "weekday",
   "from": 22.5,
   "to": 24
  },
  {
   "claim": "Marco's shoes are on the shoe rack after he comes home at 11",
   "target": "shoes_marco",
   "expect": "shoe_rack_e1",
   "days": "weekday",
   "from": 23,
   "to": 24
  }
 ],
 "targets": {
  "jacket_marco": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_marco": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "keys_marco": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "backpack_marco": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "glasses_marco": [
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "board_game_shared": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "sometimes"
   }
  ],
  "class:glass": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "snack_bowl_shared": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "dog_bowl_shared": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "floor_k_k1",
    "chance": "usually"
   }
  ],
  "phone_marco": [
   {
    "days": "weekday",
    "from": 22.5,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
