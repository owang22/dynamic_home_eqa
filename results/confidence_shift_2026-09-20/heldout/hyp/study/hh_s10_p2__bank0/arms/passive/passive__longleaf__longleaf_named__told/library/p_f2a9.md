# p_f2a9 — Omar's tablet: dresser_b1 on weekend afternoons, nightstand on weekdays

Omar's tablet rests at the bedroom nightstand during the early hours (00:00–08:00) on both weekdays and weekends. On weekday mornings around 10:00 it briefly appears at the kitchen table (coffee and breakfast). From midday through the evening on weekdays it returns to the nightstand, where it stays while Omar is at work and during his evening gaming.

On weekends the pattern shifts: after the 10:00 kitchen-table appearance, the tablet moves to the bedroom dresser from about 12:00 through 22:00. This is a distinct weekend resting spot that does not occur on weekdays. The robot's sightings confirm the split: on weekend passes from 12:00 onward, the tablet is found at either the nightstand or the dresser, with the dresser gaining prominence as the afternoon progresses.

This document differs from p_5f4b and p_3d7e, which place the tablet at the nightstand for the entire day on all days. It differs from p_a3d7, which predicts the kitchen chair on weekend mornings (the evidence shows the kitchen table at 10:00, not the chair). The key distinguishing prediction is the dresser_b1 location on weekend afternoons.

Refutation: if the tablet is sighted at the kitchen chair or desk_b1 on weekend afternoons (12:00–22:00), or if it is at the dresser during weekday afternoons.

```json
{
 "claims": [
  {
   "claim": "Omar's tablet is at the bedroom dresser during weekend afternoons",
   "target": "tablet_omar",
   "expect": "dresser_b1",
   "days": "weekend",
   "from": 12,
   "to": 22
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand during his midday window on weekdays",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Omar's tablet is at the kitchen table during his 10:00 morning coffee on weekdays",
   "target": "tablet_omar",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9.5,
   "to": 10.5
  },
  {
   "claim": "Omar's tablet is at the bedroom nightstand during weekend early morning",
   "target": "tablet_omar",
   "expect": "nightstand_b1",
   "days": "weekend",
   "from": 0,
   "to": 8
  }
 ],
 "targets": {
  "tablet_omar": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 9.5,
    "to": 10.5,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 10,
    "to": 11,
    "at": "kitchen_table_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekend",
    "from": 12,
    "to": 22,
    "at": "dresser_b1",
    "chance": "usually"
   }
  ]
 }
}
```
