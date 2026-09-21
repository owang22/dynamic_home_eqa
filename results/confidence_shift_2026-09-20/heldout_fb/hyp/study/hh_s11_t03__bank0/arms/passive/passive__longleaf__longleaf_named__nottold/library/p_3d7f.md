# p_3d7f — Hana's Kitchen Table Morning; Notebook Anchors the Desk

Hana works afternoon-to-night shifts. On weekday mornings she is home from roughly 07:00 until she leaves for work at 13:40. The evidence over five days shows her tablet is **not** at the desk: it sits on the nightstand overnight, moves to the kitchen table for breakfast and early work (09:00, four sightings), drifts to the coffee table for a mid-morning break (10:00, two sightings), and is returned to the nightstand by 12:00 where it stays while she is at work. Her notebook, by contrast, has been seen at desk_b1 on all five days with no other receptacle — it is her permanent reference and does not travel. Her mug follows her to the coffee table around 10:00 and stays there through the afternoon (sightings at 10, 13, 17) before Priya puts it back in the cupboard by 18:00. Her guitar remains in the bedroom all day on weekdays. When Hana leaves at 13:40 her phone, keys, wallet, and handbag go with her and do not reappear until 23:00.

This document differs from p_b8c2 (which places the tablet at desk_b1, a claim that has accumulated eight "against" sightings) and from p_7e2a (which puts the mug at the coffee table but the tablet at the kitchen table only 8–10). Here the tablet has a two-stage morning migration (kitchen table → coffee table) and the mug is a separate, later object. The notebook's permanence at the desk is the anchor claim.

Refutation: finding tablet_hana at desk_b1 during 09:00–12:00 on a weekday, or finding notebook_hana anywhere other than desk_b1, would strongly contradict this document. Finding the mug in the cupboard during 10:00–17:00 on a weekday would also weaken it.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet is at the kitchen table during her weekday breakfast and early work",
   "target": "tablet_hana",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 9,
   "to": 10
  },
  {
   "claim": "Hana's tablet is at the coffee table during her weekday mid-morning break",
   "target": "tablet_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 10,
   "to": 12
  },
  {
   "claim": "Hana's notebook stays at her desk all day",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Hana's mug is at the coffee table during the weekday afternoon after she has left for work",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "weekday",
   "from": 13,
   "to": 17
  },
  {
   "claim": "Hana's guitar stays in her bedroom on weekdays",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekday",
   "from": 6,
   "to": 22
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
   },
   {
    "days": "weekday",
    "from": 9,
    "to": 10,
    "at": "kitchen_table_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 12,
    "at": "coffee_table_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 12,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "almost_always"
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
  "mug_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10,
    "to": 18,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "handbag_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "water_bottle_hana": [
   {
    "days": "weekday",
    "from": 9,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
