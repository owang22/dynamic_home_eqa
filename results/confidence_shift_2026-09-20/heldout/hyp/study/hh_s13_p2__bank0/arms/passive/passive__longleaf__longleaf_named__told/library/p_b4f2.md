# p_b4f2 — Weekend Hana at Rest: Laptop and Pen at the Entry Hook, Guitar Never Played

On weekends Hana does not go to the office, so her work kit (laptop, pen) is not carried out. But she also does not sit at her desk to browse or work from home. Instead, the laptop and pen are dumped at the entry hook and stay there all day — every single weekend sighting from 00:00 to 22:00 puts both objects at entry_hook_e1. The charger, by contrast, stays at desk_b1 all day on weekends (it is plugged in overnight and she does not unplug it). The guitar is on the bedroom floor all day, every hour, both weekend days — it is never picked up, never played. The book stays on the bookshelf. The headphones stay at desk_b2.

This document is set apart from p_8a3c (which claims the guitar is played at 16:00 on Saturday), p_e3f8 (which also claims Saturday guitar play), p_b1c6 (same), and p_e5f0 (same). The data is unambiguous: guitar_hana is at bedroom_floor_b1 for all twelve weekend hours on both Saturday and Sunday. It is not played on weekends in this log. It is also set apart from p_c2e9 and p_9b6e, which place the laptop at desk_b1 on Saturday — the data shows entry_hook_e1 instead.

This document is refuted if a weekend look at 10:00–18:00 finds the laptop at desk_b1, the pen at desk_b1, or the guitar at ON_PERSON or coffee_table_l1.

```json
{
 "claims": [
  {
   "claim": "Hana's laptop is at the entry hook at noon on a Saturday because she does not use the desk on weekends",
   "target": "laptop_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 11,
   "to": 14
  },
  {
   "claim": "The guitar is on the bedroom floor at 4 PM on a Saturday because Hana does not play it on weekends",
   "target": "guitar_hana",
   "expect": "bedroom_floor_b1",
   "days": "weekend",
   "from": 14,
   "to": 17
  },
  {
   "claim": "Hana's pen is at the entry hook at 2 PM on a Saturday, not at the desk",
   "target": "pen_hana",
   "expect": "entry_hook_e1",
   "days": "weekend",
   "from": 13,
   "to": 16
  },
  {
   "claim": "Hana's charger is at the desk at 10 AM on a Saturday because it stays plugged in overnight",
   "target": "charger_hana",
   "expect": "desk_b1",
   "days": "weekend",
   "from": 9,
   "to": 12
  }
 ],
 "targets": {
  "laptop_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "pen_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "entry_hook_e1",
    "chance": "almost_always"
   }
  ],
  "charger_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
    "chance": "almost_always"
   }
  ],
  "book_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "headphones_priya": [
   {
    "days": "weekend",
    "from": 0,
    "to": 24,
    "at": "desk_b2",
    "chance": "almost_always"
   }
  ]
 }
}
```
