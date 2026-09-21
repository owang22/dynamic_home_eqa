# p_4b6a — Marco's Phone: Nightstand by Morning, Bed at Noon, Entry at Night

Marco's phone is one of the most mobile objects in the house, sighted at four different receptacles across the day. The pattern from the patrol passes: at 07:00 and 08:00 it is at the nightstand (or coffee table), at 13:00 it is at the bed (Marco is in the bedroom getting ready to leave for work), and at 22:00 it is at the entry table (he has just arrived home from his night shift). During 9–17 h the nightstand is empty of the phone (three empty looks). No other document in the library tracks phone_marco's movement, so this hypothesis fills a gap. It would be refuted if the phone is found at the nightstand at 13:00 or at the bed at 07:00 on a weekday.

```json
{
 "claims": [
  {
   "claim": "Marco's phone is at the nightstand in the early morning",
   "target": "phone_marco",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 7,
   "to": 9
  },
  {
   "claim": "Marco's phone is at the bed during his pre-work preparation",
   "target": "phone_marco",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 12,
   "to": 14
  },
  {
   "claim": "Marco's phone is at the entry table in the evening after his shift",
   "target": "phone_marco",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 22,
   "to": 23
  }
 ],
 "targets": {
  "phone_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 14,
    "at": "bed_b1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 22,
    "to": 23,
    "at": "entry_table_e1",
    "chance": "sometimes"
   }
  ]
 }
}
```
