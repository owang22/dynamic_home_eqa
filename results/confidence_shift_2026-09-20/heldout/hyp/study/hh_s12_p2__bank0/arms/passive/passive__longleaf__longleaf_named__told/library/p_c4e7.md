# p_c4e7 — Weekend domestic: Elena's items shift to bathroom and entry floor; vacuum and iron in afternoon

Elena and Priya are both home all day on the weekend, and the house runs on a slower, more domestic rhythm. Elena's keys, which sit on the entry table on weekdays, drop to the entry floor on weekends — she's not reaching for them to leave for work, so they slide off the table. Her skincare and toiletry bag, which rest at the nightstand and dresser on weekdays, migrate to the bathroom shelf from the morning routine onward; she's in the bathroom at 08:00 (confirmed by the resident look) and her items stay on the shelf for the rest of the day. The blanket, which sits on the couch on weekdays, is on the armchair all weekend — perhaps pulled over for a nap or reading session in the afternoon.

The afternoon is a chore block: the vacuum cleaner moves from its entry-floor resting spot into the living room between roughly 12:00 and 18:00 (it is seen on floor_l_l1 at 12, 14, 16, and 18). The ironing board is set up on the bed at 14:00 and stowed in the wardrobe by 16:00, with the iron briefly at the bed at the same hour — a focused ironing session in the bedroom. Elena's hair dryer, normally on the bathroom shelf, ends up at the bedroom desk from 14:00 onward, consistent with a post-shower hair routine done at the desk.

Priya's weekend is calmer: her glasses stay at the nightstand all day (no midday rotation to desk_b1 or bedroom_floor as on weekdays), her guitar stays on the bedroom floor, and she is seen in the kitchen at 10:00 and 12:00, then the bedroom at 14:00 and 16:00, and the kitchen again at 20:00. Her water bottle is at the sink overnight and moves to the dish rack from 10:00; her mug is at the dish rack overnight and in the cupboard from 10:00.

This hypothesis is set apart from the weekday documents by the weekend-specific resting spots for Elena's personal items (keys on floor, toiletries on bathroom shelf) and by the afternoon chore objects (vacuum in living room, ironing board on bed then wardrobe). It is refuted if Elena's keys are found at the entry table on a weekend, or if the vacuum is never seen off the entry floor on a weekend afternoon, or if the blanket is on the couch rather than the armchair on a weekend.

```json
{
 "claims": [
  {
   "claim": "Elena's keys are on the entry floor on a weekend morning, not the entry table",
   "target": "keys_elena",
   "expect": "entry_floor_e1",
   "days": "weekend",
   "from": 8,
   "to": 18
  },
  {
   "claim": "Elena's toiletry bag is on the bathroom shelf on a weekend morning after her routine",
   "target": "toiletry_bag_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekend",
   "from": 8,
   "to": 14
  },
  {
   "claim": "The vacuum cleaner is in the living room during the weekend afternoon chore block",
   "target": "vacuum_cleaner_shared",
   "expect": "floor_l_l1",
   "days": "weekend",
   "from": 12,
   "to": 18
  },
  {
   "claim": "The blanket is on the armchair on a weekend afternoon",
   "target": "blanket_shared",
   "expect": "armchair_l1",
   "days": "weekend",
   "from": 10,
   "to": 16
  }
 ],
 "targets": {
  "keys_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "skincare_elena": [
   {
    "days": "weekend",
    "from": 8,
    "to": 22,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "toiletry_bag_elena": [
   {
    "days": "weekend",
    "from": 8,
    "to": 22,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   }
  ],
  "blanket_shared": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "armchair_l1",
    "chance": "almost_always"
   }
  ],
  "vacuum_cleaner_shared": [
   {
    "days": "weekend",
    "from": 12,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "ironing_board_shared": [
   {
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 16,
    "to": 22,
    "at": "wardrobe_b1",
    "chance": "usually"
   }
  ],
  "iron_shared": [
   {
    "days": "weekend",
    "from": 14,
    "to": 16,
    "at": "bed_b1",
    "chance": "sometimes"
   }
  ],
  "hair_dryer_elena": [
   {
    "days": "weekend",
    "from": 14,
    "to": 22,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "water_bottle_elena": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "dish_rack_k1",
    "chance": "almost_always"
   }
  ],
  "glasses_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_priya": [
   {
    "days": "weekend",
    "from": 10,
    "to": 22,
    "at": "dish_rack_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "weekend",
    "from": 10,
    "to": 22,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
