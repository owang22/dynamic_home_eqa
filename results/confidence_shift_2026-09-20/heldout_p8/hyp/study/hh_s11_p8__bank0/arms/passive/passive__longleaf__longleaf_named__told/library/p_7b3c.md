# p_7b3c — Hana's Phone Travels; Out of the House During Work Hours

Hana's phone is sighted at nightstand_b1 on 6 of 6 days, but the weekday 9:00–17:00 looks at the nightstand found the phone 0 times and found nothing 4 times. This means that during the working day the phone is not at the nightstand. The most natural explanation is that Hana takes her phone with her to work (OUT_OF_HOUSE from roughly 13:40 to 23:00 on weekdays). In the morning before she leaves, the phone is at the nightstand (or in her hand as she gets ready). When she returns home in the evening, it goes back to the nightstand. On weekends, when she is home all day, the phone stays at the nightstand or is briefly in her hand.

What sets this document apart: it is the only document that explicitly places Hana's phone OUT_OF_HOUSE during weekday work hours. The tablet (p_c3d4) and notebook (p_a1b2) documents make similar claims for those objects, but the phone is a different object with its own evidence. A sighting of the phone at the nightstand during 14:00–22:00 on a weekday would refute this; an empty look at the nightstand in that window would support it.

```json
{
 "claims": [
  {
   "claim": "Hana's phone is out of the house during her weekday work shift",
   "target": "phone_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 23
  },
  {
   "claim": "Hana's keys are out of the house during her weekday work shift",
   "target": "keys_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 23
  },
  {
   "claim": "Hana's handbag is out of the house during her weekday work shift",
   "target": "handbag_hana",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 14,
   "to": 23
  },
  {
   "claim": "Hana's tablet stays at the nightstand and does not travel to work",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 14,
   "to": 22
  }
 ],
 "targets": {
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
    "chance": "usually"
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
    "chance": "usually"
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
    "chance": "usually"
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
    "chance": "usually"
   }
  ],
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
    "chance": "usually"
   }
  ]
 }
}
```
