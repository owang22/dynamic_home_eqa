# p_e4c9 — Sick Day Revised; Hana Drifts to the Living Room, Water Bottle at the Entry (fork of p_7f2a)

The parent document p_7f2a correctly places Hana in bed at 03:00 and keeps her tablet at the nightstand, but two blocks failed on day 3. First, water_bottle_hana was predicted at nightstand_b1 all day but was actually sighted at entry_table_e1 at 03:00 (and the block scored 0.16 on 2 sightings). Second, mug_hana was predicted at cupboard_k1 but was found at coffee_table_l1 at 10:00 on the sick day. The evidence suggests that even while sick, Hana drifts out of the bedroom into the living room by mid-morning, takes a mug of tea to the coffee table, and leaves her water bottle by the entry where she grabbed it the night before.

What changed from the parent: water_bottle_hana moves from nightstand_b1 to entry_table_e1 (its confirmed 03:00 location on the sick day). mug_hana gains a daytime block at coffee_table_l1 (10:00–17:00) before returning to the cupboard. book_hana gains a daytime block at coffee_table_l1 (12:00–17:00), matching the 12:00 and 13:00 sightings. The tablet stays at nightstand_b1 because the 03:00 and 12:00 sightings confirm it there on the sick day; the 09:00 kitchen-table sightings in the aggregate are from working days, not this one.

This document is refuted if tablet_hana is sighted at kitchen_table_k1 or coffee_table_l1 between 08:00 and 13:00 on the sick day, or if water_bottle_hana reappears at nightstand_b1.

```json
{
 "claims": [
  {
   "claim": "Hana's water bottle is at the entry table on the sick day, not the nightstand",
   "target": "water_bottle_hana",
   "expect": "entry_table_e1",
   "days": "both",
   "from": 0,
   "to": 24
  },
  {
   "claim": "Hana's mug is at the coffee table during the sick-day afternoon, not the cupboard",
   "target": "mug_hana",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 10,
   "to": 17
  },
  {
   "claim": "Hana's tablet stays at her nightstand on the sick day",
   "target": "tablet_hana",
   "expect": "nightstand_b1",
   "days": "both",
   "from": 8,
   "to": 13
  },
  {
   "claim": "Hana's book is in the living room during the sick-day afternoon",
   "target": "book_hana",
   "expect": "coffee_table_l1",
   "days": "both",
   "from": 12,
   "to": 17
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
    "at": "entry_table_e1",
    "chance": "usually"
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
    "days": "both",
    "from": 10,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "usually"
   }
  ],
  "book_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 17,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ]
 }
}
```
