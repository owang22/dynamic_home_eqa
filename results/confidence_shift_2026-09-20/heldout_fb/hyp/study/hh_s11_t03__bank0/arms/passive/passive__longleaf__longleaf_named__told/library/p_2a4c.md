# p_2a4c — Hana's 13:40 Departure; Entry Objects Leave the House Together

Hana leaves for her afternoon shift at approximately 13:40 on weekdays and does not return until 23:00. When she goes, she takes her jacket, keys, handbag, wallet, shoes, hat, and scarf with her. These objects are reliably on the entry hook, entry table, or shoe rack during the morning (the 03:00 pass shows them there on most sighted days) and are absent from the house between 13:40 and 23:00. They reappear at the entry when she comes home.

On weekends Hana stays home; the entry objects remain in the entry area all day. The 03:00 weekend pass confirms jacket_hana, keys_hana, handbag_hana, wallet_hana, shoes_hana, hat_hana, and scarf_hana at their entry spots.

This document differs from p_7b2e, which only tracks jacket_hana as OUT_OF_HOUSE during the work shift and tablet_hana at the nightstand. Here all seven entry objects are tracked together as a single departure event. It also differs from p_a3f7, which tracks keys_priya as OUT_OF_HOUSE during Priya's morning walk (07:00–09:00) but does not address Hana's departure.

The document would be refuted if any of the seven entry objects is sighted inside the house between 14:00 and 22:00 on a weekday (meaning Hana did not take it with her or is home during the work window), or if the objects are missing from the entry at the 03:00 weekday pass on multiple days (meaning they are stored elsewhere overnight).

```json
{
 "claims": [
  {
   "claim": "Hana's jacket is out of the house during the 15:00 weekday pass",
   "target": "jacket_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Hana's keys are out of the house during the 16:00 weekday pass",
   "target": "keys_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 22
  },
  {
   "claim": "Hana's handbag is on the entry hook at the 03:00 weekday pass",
   "target": "handbag_hana",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 0,
   "to": 3
  },
  {
   "claim": "Hana's shoes are on the shoe rack at the 03:00 weekend pass",
   "target": "shoes_hana",
   "expect": "shoe_rack_e1",
   "days": "weekend",
   "from": 0,
   "to": 3
  }
 ],
 "targets": {
  "jacket_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "keys_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "handbag_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "wallet_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "shoes_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "hat_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "scarf_hana": [
   {
    "days": "weekday",
    "from": 0,
    "to": 13.67,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13.67,
    "to": 23,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   },
   {
    "days": "weekday",
    "from": 23,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ]
 }
}
```
