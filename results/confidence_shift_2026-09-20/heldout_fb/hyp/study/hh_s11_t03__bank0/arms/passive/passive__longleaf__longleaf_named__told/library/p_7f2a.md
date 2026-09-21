# p_7f2a — Sick Day; Hana Rests, Tablet at the Nightstand

Hana is home sick on this Friday. She will not leave for her afternoon shift at 13:40 as she does on normal weekdays. Instead, she remains in the house, most likely in bed_b1 or on the couch, resting for the majority of the day. Her tablet, which the evidence places at the kitchen table at 09:00 and 10:00 on normal weekday mornings (her work block, sighted there 5 times versus 9 empty looks), will instead stay at nightstand_b1 or in bed_b1. Her notebook remains at desk_b1, untouched. Her guitar stays in the bedroom; she may bring it to bed for quiet entertainment but it will not travel to the living room. Her phone stays at nightstand_b1. Her water bottle stays in the bedroom.

This hypothesis is set apart from the standard documents (p_a3f7, p_b8c2, p_f3a7) by the complete absence of the morning kitchen-table work block. Where those documents predict tablet_hana at kitchen_table_k1 from 09:00 to 12:00, this document predicts it at nightstand_b1. Where p_a3f7 predicts Hana out of the house from 13:40 to 23:00, this document keeps all her personal objects inside. No Hana object leaves the house today.

This document is refuted if tablet_hana is sighted at kitchen_table_k1 between 08:00 and 12:00, or if Hana's phone or water bottle appears at the entry table or entry floor suggesting she is preparing to leave the house.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet stays at her nightstand all day because she is too sick to work at the kitchen table",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 8,
   "to": 13
  },
  {
   "claim": "Hana's notebook is untouched at her desk all day on the sick day",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "both",
   "from": 8,
   "to": 18
  },
  {
   "claim": "Hana's guitar remains in her bedroom and does not come to the living room",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "both",
   "from": 8,
   "to": 20
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "notebook_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "usually"
   }
  ],
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   }
  ]
 }
}
```
