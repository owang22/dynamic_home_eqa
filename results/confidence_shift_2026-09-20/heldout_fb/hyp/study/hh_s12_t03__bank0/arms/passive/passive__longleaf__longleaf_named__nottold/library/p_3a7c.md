# p_3a7c — Priya's yoga morning and guitar afternoon

Priya is retired and home most of the day. This hypothesis centres on her two physical hobbies: yoga in the morning and guitar in the afternoon. The critical evidence is the yoga mat: it is seen in the wardrobe at 03:00 on both sighted days, yet three separate looks during the 9–17 h window on a weekday found the wardrobe empty of the mat. That is not a one-off; the mat is consistently out of storage all day. The most natural explanation is that Priya unrolls it on the living-room floor in the early morning for a yoga session and leaves it there (or re-rolls it and sets it on the floor) until the evening, when she puts it back. The guitar shows a similar but weaker pattern: it rests on the bedroom floor at 03:00, and one weekday look during 9–17 h found the bedroom floor without it. Priya's afternoon is when she practises, and the living-room floor is the open space where she would sit and play.

This document sets itself apart from p_e5f6 (which makes the *office* Priya's creative space) by placing her practice in the *living room*. It also differs from p_a1b2, which says nothing about where the yoga mat or guitar go during the day. If the mat is ever found back in the wardrobe during a weekday 10–14 h look, or the guitar is found on the bedroom floor during a 15 h look, this document is in trouble.

```json
{
 "claims": [
  {
   "claim": "The yoga mat is on the living-room floor at midday on a weekday",
   "target": "yoga_mat_priya",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "The guitar is on the living-room floor during Priya's afternoon practice",
   "target": "guitar_priya",
   "expect": "floor_l_l1",
   "days": "weekday",
   "from": 15,
   "to": 16
  },
  {
   "claim": "The yoga mat is back in the wardrobe at bedtime",
   "target": "yoga_mat_priya",
   "expect": "wardrobe_b1",
   "days": "both",
   "from": 22,
   "to": 24
  },
  {
   "claim": "The guitar is on the bedroom floor in the early morning before Priya moves it",
   "target": "guitar_priya",
   "expect": "bedroom_floor_b1",
   "days": "both",
   "from": 5,
   "to": 7
  }
 ],
 "targets": {
  "yoga_mat_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "wardrobe_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 18,
    "at": "floor_l_l1",
    "chance": "usually"
   }
  ],
  "guitar_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 17,
    "at": "floor_l_l1",
    "chance": "sometimes"
   }
  ],
  "headphones_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   }
  ]
 }
}
```
