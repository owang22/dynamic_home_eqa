# p_a3f1 — Full commuter: Elena out 8–17:30, laptop and wallet gone, entry kit anchored

Elena is a full commuter every weekday. She leaves the house around 8:00 and returns around 17:30. Her laptop, keys, wallet, and phone travel with her to the office and are not in the house during work hours. The per-object evidence is unambiguous: the laptop has accumulated eight weak-for sightings (the robot looked at its resting places during 9–17 h and found nothing), and it has never once been sighted at desk_o1, ruling out any home-office day. Her entry kit—backpack, helmet, bike lock, hat, jacket, shoes—stays at the entry all day because she leaves it there; she cycles to work and stores the bike (with helmet and lock) at the office, but the backpack, hat, and jacket remain on the hook and rack. On weekends the helmet and lock return to the entry because she does not commute.

This document differs from p_c3d4 (which places the laptop at desk_o1 on Mon/Wed) by asserting the laptop is never in the house during work hours, and from p_f8a6 (which puts it at desk_b1 two days a week) by the same token. It also differs from p_d2f8 in that it does not claim the helmet and lock leave the house; they are simply never observed during 9–17 h, so the document takes the conservative position that they stay at the entry.

What would refute this document: a sighting of laptop_elena at any in-house receptacle during weekday 9–17 h; a sighting of keys_elena or wallet_elena in the house during that window; or a sighting of the backpack at a non-entry location on a weekday.

```json
{
 "claims": [
  {
   "claim": "Elena's laptop is out of the house on a weekday at noon",
   "target": "laptop_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 11,
   "to": 14
  },
  {
   "claim": "Elena's keys are out of the house on a weekday during work hours",
   "target": "keys_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Elena's wallet is out of the house on a weekday during work hours",
   "target": "wallet_elena",
   "expect": "OUT_OF_HOUSE",
   "days": "weekday",
   "from": 9,
   "to": 16
  },
  {
   "claim": "Elena's backpack stays at the entry hook on a weekday during work hours",
   "target": "backpack_elena",
   "expect": "entry_hook_e1",
   "days": "weekday",
   "from": 10,
   "to": 15
  },
  {
   "claim": "Elena's helmet stays at the entry hook on a weekend midday",
   "target": "helmet_elena",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 10,
   "to": 15
  }
 ],
 "targets": {
  "laptop_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "keys_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "wallet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "phone_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "almost_always"
   }
  ],
  "backpack_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "helmet_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "bike_lock_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   }
  ],
  "hat_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "jacket_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "usually"
   }
  ],
  "shoes_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "shoe_rack_e1",
    "chance": "usually"
   }
  ],
  "notebook_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "pen_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 8,
    "to": 17.5,
    "at": "OUT_OF_HOUSE",
    "chance": "sometimes"
   }
  ],
  "charger_elena": [
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
