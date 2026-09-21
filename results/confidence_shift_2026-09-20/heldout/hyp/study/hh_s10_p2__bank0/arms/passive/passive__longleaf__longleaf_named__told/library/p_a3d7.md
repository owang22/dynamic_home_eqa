# p_a3d7 — Omar's tablet: kitchen chair mornings, nightstand midday, chair evenings

Omar's tablet follows a tight daily rhythm locked to his work schedule. In the early morning (before 10:00) he is home and the tablet rests at the kitchen chair (chair_k1), where he games or reads. Around 10:00–12:00 he may shift it to the kitchen table for a quick session, but by 12:00 he sets it on the bedroom nightstand (nightstand_b1) before heading out for his 1:40 pm shift. It stays on the nightstand while he is at work (roughly 12:00–23:00). When he returns home around 23:00 he picks it back up, and it goes back to the kitchen chair for evening gaming. On weekends he is home all day and the tablet stays at the kitchen chair for most of the day.

This document sets itself apart from p_e5f6, which places the tablet at chair_k1 for the entire 7:00–13:00 morning window. The sightings are unambiguous: at 12:00, 14:00, and 16:00 the tablet is at nightstand_b1, not chair_k1. The claim in p_e5f6 has now gone against six times. This document corrects the midday placement.

It also differs from p_4e91, which likewise puts the tablet at chair_k1 during 14:00–22:00 on weekday evenings. The evidence shows the tablet at nightstand_b1 through 16:00 and only returning to chair_k1 from 18:00 onward.

What would refute this document: finding the tablet at chair_k1 during 12:00–17:00 on a weekday, or at nightstand_b1 during 19:00–22:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom nightstand during his midday window on weekdays",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Omar's tablet is back at the kitchen chair during his evening gaming on weekdays",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekday",
   "from": 19,
   "to": 22
  },
  {
   "claim": "Omar's tablet is at the kitchen chair during his weekend morning",
   "target": "tablet_omar",
   "expect": "chair_k1",
   "days": "weekend",
   "from": 10,
   "to": 14
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "weekday",
    "from": 0,
    "to": 10,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 18,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 18,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "chair_k1",
    "chance": "usually"
   }
  ]
 }
}
```
