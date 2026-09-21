# p_c4f8 — Weekend Social Evening: Armchair Hub, Coffee Table Games, Kitchen Prep

The residents' messages confirm friends are coming over both Saturday and Sunday evenings. This shifts the living room from its weekday TV-only use to a social gathering space: the blanket is on the armchair for guests to settle in, the board game comes down from the bookshelf to the coffee table for group play, and the remote stays at the TV stand (individual TV watching gives way to group activity, so the remote is not migrated to the coffee table as on weekday evenings). In the kitchen, the late afternoon becomes an active prep window: Priya's phone is at the kitchen table (checking recipes, coordinating timing with Elena), and the cutting board is at the counter for food preparation. The vacuum cleaner appears on the living room floor in the mid-afternoon (Elena tidying up before guests arrive at 6 or 7). Elena's keys are on the entry floor in the midday window (she has been out on errands and set them down, or is about to head out again). Elena's shoes are on the entry floor at 16:00 (getting ready for the evening, or just back from an errand run). The dog toy is on the living room floor as the dog roams freely during the social gathering.

This hypothesis predicts a distinct evening social mode that differs from the weekday pattern: the living room furniture is in a "guest-ready" configuration, the kitchen is in active prep, and the entry area shows the traffic of someone who has been out and about during the day. The dog toy on the living room floor is supported by the weekend sightings (2/3 days) and the p_7d4a claim that already scored 2 for.

Refutation: if the board game stays on the bookshelf on a weekend evening (no group play), if the blanket is on the couch (not armchair), or if the vacuum stays at the entry floor (no cleaning before guests).

```json
{
 "claims": [
  {
   "claim": "The board game is at the coffee table on a weekend evening when friends play",
   "target": "board_game_shared",
   "expect": "coffee_table_l1",
   "days": "weekend",
   "from": 18,
   "to": 22
  },
  {
   "claim": "The blanket is on the armchair on a weekend evening as guests settle in",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 17,
   "to": 22
  },
  {
   "claim": "The vacuum cleaner is on the living room floor during Elena's weekend afternoon cleaning before guests arrive",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Priya's phone is at the kitchen table on a weekend afternoon (coordinating dinner prep)",
   "target": "phone_priya",
   "expect": "kitchen_table_k1",
   "days": "weekend",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Elena's keys are on the entry floor during her weekend midday errand window",
   "target": "keys_elena",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 10,
   "to": 15
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 16,
    "to": 22,
    "at": "armchair_l1",
    "chance": "usually"
   }
  ],
  "board_game_shared": [
   {
    "days": "weekend",
    "from": 16,
    "to": 22,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "remote_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "tv_stand_l1",
    "chance": "usually"
   }
  ],
  "phone_priya": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "weekend",
    "from": 16,
    "to": 19,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "floor_l_l1",
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
  ],
  "shoes_elena": [
   {
    "days": "weekend",
    "from": 14,
    "to": 18,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "dog_toy_shared": [
   {
    "days": "weekend",
    "from": 14,
    "to": 20,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ]
 }
}
```
