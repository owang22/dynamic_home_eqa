# p_f3a1 — Hana Home Sick; the Entry Set Stays, Tablet in Bed

Hana is home sick today, Friday. The message from the residents confirms it: she will not leave for her afternoon-to-night shift. That means the whole cluster of objects that normally rides out with her at 1:40 pm — handbag, jacket, hat, scarf, shoes, wallet, keys, pen, water bottle — stays at the entry all day. On a normal weekday the robot's 9-to-17 looks at the entry find these items only 2 out of 8 times (the other 6 are empty because Hana has taken them out). Today every one of those looks should come back full.

Her tablet, which the evidence already shows is not reliably at desk_b1 (12 against, 0 for on that claim in p_b8c2), will sit in her bedroom: on the bed while she scrolls or watches something, and on the nightstand once she settles in for the night. Her phone, which on work days vanishes from the nightstand for the entire 9-to-17 window (0 found, 8 empty), should be back at nightstand_b1 or in her hand in bed. Her guitar stays on the bedroom floor; she is too unwell to play.

This document is refuted if any of Hana's entry items are sighted OUT_OF_HOUSE today, or if her tablet is found at desk_b1 (meaning she is working from the desk despite being sick), or if her phone is absent from the bedroom for the whole afternoon.

```json
{
 "claims": [
  {
   "claim": "Hana's handbag stays at the entry floor all day because she is home sick and not leaving",
   "target": "handbag_hana",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 8,
   "to": 20
  },
  {
   "claim": "Hana's tablet is in her bedroom, not at her desk, because she is too sick to work",
   "target": "tablet_hana",
   "expect": "bed_b1",
   "days": "weekday",
   "from": 8,
   "to": 18
  },
  {
   "claim": "Hana's keys are at the entry table in the afternoon, not out of the house, because she is not going to work",
   "target": "keys_hana",
   "expect": "entry_table_e1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Hana's phone is at her nightstand in the afternoon, not out of the house, because she is home sick",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
  "handbag_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "hat_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "scarf_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "wallet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "pen_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "entry_floor_e1",
    "chance": "usually"
   }
  ],
  "tablet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bed_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 21,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "sometimes"
   }
  ],
  "phone_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ]
 }
}
```
