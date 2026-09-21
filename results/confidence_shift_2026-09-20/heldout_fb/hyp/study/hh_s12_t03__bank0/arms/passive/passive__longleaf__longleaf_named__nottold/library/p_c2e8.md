# p_c2e8 — Ironing board: wardrobe by day, floor during morning and evening ironing

The ironing board follows a clear two-phase pattern. In the morning (roughly 6:00–10:00) and again in the evening (17:00–20:00), it is set up on the bedroom floor for ironing. During the middle of the day (10:00–17:00) and after the evening session (20:00 onward), it is folded and stored in the wardrobe. The robot has seen it in the wardrobe at 11:00 and 20:00 on weekdays, and on the bedroom floor at 07:00, 18:00, and 19:00. Overnight it appears to remain on the floor (not put away), consistent with the 03:00 sightings. The iron itself stays in the wardrobe 7/7 days, so both items are stored together when not in active use. This differs from the statistical model, which predicts bedroom_floor_b1 at 11:00 (where the board is actually in the wardrobe). If the board is found on the bedroom floor at 12:00 or 14:00 on a weekday, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "The ironing board is in the wardrobe at 12:00 on a weekday",
   "target": "ironing_board_shared",
   "expect": "wardrobe_b1",
   "days": "weekday",
   "from": 10,
   "to": 16
  },
  {
   "claim": "The ironing board is on the bedroom floor at 07:00 on a weekday morning",
   "target": "ironing_board_shared",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 6.5,
   "to": 8
  },
  {
   "claim": "The ironing board is in the wardrobe at 21:00 on a weekday evening",
   "target": "ironing_board_shared",
   "expect": "wardrobe_b1",
   "days": "weekday",
   "from": 20,
   "to": 23
  }
 ],
 "targets": {
  "ironing_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 6,
    "to": 10,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 17,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 17,
    "to": 20,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "almost_always"
   }
  ],
  "iron_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "almost_always"
   }
  ],
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
