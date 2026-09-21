# p_9d3e — Glasses in the Pantry and Sink, Not the Cupboard

The shared class block `class:glass at cupboard_k1` that appears in nearly every document in this library is wrong. The evidence is unambiguous: glass_hana is found at the pantry shelf (where spare glasses are stored) on 2 of 4 sighted days, and at her nightstand or the kitchen sink on the remaining days. Glass_priya is found at the kitchen sink (drying after a wash) on 1 of 4 days and at her desk or the dining table on others. Neither glass is consistently in the cupboard. The 16:00 pass shows glass_priya at sink_k1 three times (all three weekdays), confirming the sink as her drying/resting spot. Glass_hana at the pantry shelf makes sense: she keeps a personal glass in the pantry with the other glassware, not in the main cupboard where bowls and mugs are stored. What sets this document apart: it explicitly rejects the cupboard as the resting spot for either glass. A look at cupboard_k1 that finds either glass during the 7–10h window would refute this document; a look at pantry_shelf_k1 that finds glass_hana, or at sink_k1 that finds glass_priya, would support it.

```json
{
 "claims": [
  {
   "claim": "Hana's glass is on the pantry shelf in the morning, not in the cupboard",
   "target": "glass_hana",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Priya's glass is at the kitchen sink in the morning, not in the cupboard",
   "target": "glass_priya",
   "expect": "sink_k1",
   "days": "both",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Hana's glass is on the pantry shelf in the late afternoon",
   "target": "glass_hana",
   "expect": "pantry_shelf_k1",
   "days": "both",
   "from": 16,
   "to": 18
  },
  {
   "claim": "Priya's glass is at the kitchen sink in the late afternoon",
   "target": "glass_priya",
   "expect": "sink_k1",
   "days": "both",
   "from": 16,
   "to": 18
  }
 ],
 "targets": {
  "glass_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
