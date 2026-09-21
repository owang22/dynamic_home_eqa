# p_5b9d — Night Glass in the Cupboard: Put Away After Dinner, Not Left at the Sink

The mixture model places glass_priya at sink_k1 because that is where it is found during the day (drying after washing, or being filled for a drink). But the nighttime picture is different. At 22:00 on a weekday, glass_priya is in cupboard_k1 four out of five times, with one sighting at the coffee table (a last drink before bed). By 00:00 it has shifted to the nightstand (2/5) or back to the sink (2/5), suggesting a glass of water is fetched for the night.

This hypothesis distinguishes three phases for glass_priya: (1) daytime resting at the sink or in the cupboard, (2) dinner use at the kitchen table (19:00–21:00), (3) post-dinner storage in the cupboard (21:00–23:00), and (4) night use at the nightstand (00:00–07:00). The key differentiator from the statistical model is the 21:00–23:00 window, where the cupboard dominates over the sink.

What would refute this: if at 22:00 on a weekday the robot consistently finds glass_priya at the sink rather than the cupboard, the "put away in the cupboard" claim is wrong. If the nightstand pattern disappears (glass never at nightstand_b2 between 00:00 and 07:00), the night-drink hypothesis is weakened.

```json
{
 "claims": [
  {
   "claim": "Priya's glass is in the cupboard at 22:00 on a weekday, put away after dinner",
   "target": "glass_priya",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 21,
   "to": 23
  },
  {
   "claim": "Priya's glass is at her nightstand at 02:00 on a weekday for a night drink",
   "target": "glass_priya",
   "expect": "nightstand_b2",
   "days": "weekday",
   "from": 0,
   "to": 6
  },
  {
   "claim": "Hana's glass is in the cupboard at 22:00 on a weekday, put away after dinner",
   "target": "glass_hana",
   "expect": "cupboard_k1",
   "days": "weekday",
   "from": 21,
   "to": 23
  }
 ],
 "targets": {
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b2",
    "chance": "sometimes"
   }
  ],
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 21,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "cupboard_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ]
 }
}
```
