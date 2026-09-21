# p_a7e3 — Hana's Tablet Stays at the Nightstand; Midnight Kitchen Cook

Hana's tablet is not a work tool and does not leave the house. It rests at nightstand_b1 through the entire day — the robot has found it there on both sighted days, and a weekday 9–17 h look at the nightstand found it present. When Hana leaves for her 13:40–23:00 shift she takes her notebook (seen at desk_b1) but not the tablet. After coming home at 23:00 she cooks in the kitchen; the resident log places her in the kitchen at 00:00, 02:00, 04:00, and 06:00 on day 1. During that midnight cook the pan, pot, and knife are on the counter. This document differs from p_b8c2 and p_a1b2 (which put the tablet at desk_b1 in the morning) and from p_c3d4 (which puts the tablet out of the house during the shift). If the tablet is ever sighted at desk_b1 or OUT_OF_HOUSE during 14–22 h weekdays, this document is refuted.

```json
{
 "claims": [
  {
   "claim": "Hana's tablet stays at the nightstand while she is at work",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "The pan is on the counter during Hana's midnight cook",
   "target": "pan_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 0,
   "to": 5
  },
  {
   "claim": "Hana's notebook is at her desk in the morning before she leaves",
   "target": "notebook_hana",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 7,
   "to": 13
  }
 ],
 "targets": {
  "tablet_hana": [
   {
    "days": "both",
    "from": 0,
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
   },
   {
    "days": "weekday",
    "from": 14,
    "to": 23,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "pan_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "pot_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "counter_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "counter_k1",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 0,
    "to": 6,
    "at": "counter_k1",
    "chance": "almost_always"
   }
  ],
  "class:towel": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "almost_always"
   }
  ],
  "class:skincare": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
