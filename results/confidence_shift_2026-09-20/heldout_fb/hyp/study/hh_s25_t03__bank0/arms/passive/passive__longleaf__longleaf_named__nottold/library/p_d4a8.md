# p_d4a8 — Kitchen knife: drawer on weekdays, counter on weekend evenings; the cutting board is a permanent counter fixture

The kitchen knife sits in the drawer throughout the weekday (three 03:00 sightings, one 18:00 sighting all in the drawer). On weekends, however, it appears on the counter at 18:00 and 19:00, indicating that weekend cooking or prep happens in that window and the knife is laid out on the counter. The cutting board, by contrast, is a permanent fixture on the counter: six out of six sighted days show it there, with no sightings in any other receptacle. It is always in its resting place because it is used so frequently (every meal prep) that it is never put away.

What sets this apart from the cooking-sequence documents (p_b7e3, p_c9f1): those track the pan and spatula; this document isolates the knife and the cutting board and draws the weekday/weekend contrast for the knife. What would refute it: the knife on the counter at 18:00 on a weekday, or the cutting board in the drawer or pantry on any day.

```json
{
 "claims": [
  {
   "claim": "The kitchen knife is in the drawer at 18:00 on weekdays",
   "target": "kitchen_knife_shared",
   "expect": "drawer_k_k1",
   "days": "weekday",
   "from": 17.5,
   "to": 19
  },
  {
   "claim": "The kitchen knife is on the counter at 18:00 on weekends",
   "target": "kitchen_knife_shared",
   "expect": "counter_k1",
   "days": "weekend",
   "from": 17.5,
   "to": 19.5
  },
  {
   "claim": "The cutting board is on the counter at all times as a permanent fixture",
   "target": "cutting_board_shared",
   "expect": "counter_k1",
   "days": "both",
   "from": 0,
   "to": 24
  }
 ],
 "targets": {
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 17.5,
    "to": 19.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "cutting_board_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ]
 }
}
```
