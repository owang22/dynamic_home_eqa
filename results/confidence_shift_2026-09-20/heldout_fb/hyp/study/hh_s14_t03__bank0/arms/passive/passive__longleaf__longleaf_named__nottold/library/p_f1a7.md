# p_f1a7 — Midday Baking and Journal Writing (10:30–13:00)

The weekday midday in this house is a two-activity window: Yuki bakes around 11:00 (baking tray and mixing bowl on the counter, spatula out of the drawer), and Marco writes in his journal at the bedroom desk from about 11:30 to 13:00. Yuki's tablet is at the counter during the baking (she may be following a recipe or reading while she works). This corrects the timing in p_d1e6, which places Marco's baking at 07:00–08:30; the sightings show the baking tray and mixing bowl on the counter at 11:00, not in the morning. The journal at the desk (seen twice at 12:00) overlaps with the baking, suggesting the two residents work in parallel in different rooms.

What sets this apart: the baking is at 10:30–12:30 (not 07:00–08:30 as p_d1e6 claims), and the journal is at the desk during 11:00–13:30 (matching p_e4c8's window but combined with the baking context). The tablet at the counter at 11:00 is a Yuki-specific prediction that no other document makes.

What would refute it: if the baking tray is in the pantry at 11:00; if the mixing bowl is in the pantry at 11:00; if the journal is at the nightstand at 12:00; if the tablet is at the nightstand at 11:00.

```json
{
 "claims": [
  {
   "claim": "The baking tray is on the kitchen counter during the weekday midday baking",
   "target": "baking_tray_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 10.5,
   "to": 12.5
  },
  {
   "claim": "The mixing bowl is on the kitchen counter during the weekday midday baking",
   "target": "mixing_bowl_shared",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 10.5,
   "to": 12.5
  },
  {
   "claim": "Marco's journal is at the bedroom desk during his weekday midday writing",
   "target": "journal_marco",
   "expect": "desk_b1",
   "days": "weekday",
   "from": 11.5,
   "to": 13
  },
  {
   "claim": "Yuki's tablet is at the kitchen counter during the weekday midday baking",
   "target": "tablet_yuki",
   "expect": "counter_k1",
   "days": "weekday",
   "from": 10.5,
   "to": 12
  }
 ],
 "targets": {
  "baking_tray_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "mixing_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "usually"
   }
  ],
  "spatula_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "tablet_yuki": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ],
  "journal_marco": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 13.5,
    "at": "desk_b1",
    "chance": "usually"
   }
  ],
  "kitchen_knife_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "drawer_k_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 10.5,
    "to": 12.5,
    "at": "counter_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
