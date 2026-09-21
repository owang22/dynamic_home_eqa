# p_9a1f — The Couch is the Blanket's Home; It Rests There, Not the Coffee Table

Seven distinct weekday sighting hours for blanket_shared: 03:00 (armchair x2, couch x1), 07:00 (couch x1), 14:00 (coffee_table x1), 16:00 (couch x1), 17:00 (couch x1, coffee_table x1), 18:00 (coffee_table x1, couch x1), 19:00 (couch x1). The couch appears in 5 of 7 hours and 7 of 11 total sightings. The coffee table appears in only 2 hours and 3 sightings. The armchair appears once at 03:00 (early-morning post-shift TV). The blanket's home is the couch, not the coffee table.

This directly contradicts p_c3d4, which places the blanket at coffee_table_l1 all day (0–24 h) and claims it "stays on the coffee table all evening" (21:00–23:00). That claim has gone against 2 times since the last call. It also contradicts the default blocks in p_a3f7 and p_a1b2, which put the blanket at coffee_table_l1.

The blanket's pattern: it is on the couch from roughly 06:00 through 19:00+ (the main waking hours). At 03:00 it may be on the armchair (Hana's post-shift TV session) or the couch. The brief coffee-table appearances at 14:00 and 18:00 are transitions—someone is moving it or adjusting the living room. The 19:00 couch sighting confirms it is back on the couch for the evening.

This document is refuted if the blanket is sighted at coffee_table_l1 during 16:00–19:00 on a weekday, or if it is at the couch during 21:00–23:00 (the window p_c3d4 claims is coffee-table-only).

```json
{
 "claims": [
  {
   "claim": "The blanket is on the couch during the weekday afternoon, not the coffee table",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 15,
   "to": 19
  },
  {
   "claim": "The blanket is on the couch at 07:00 in the morning, not the coffee table",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 6,
   "to": 8
  },
  {
   "claim": "The blanket is on the couch during the weekday evening, not the coffee table",
   "target": "blanket_shared",
   "expect": "couch_l1",
   "days": "weekday",
   "from": 19,
   "to": 22
  }
 ],
 "targets": {
  "blanket_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "couch_l1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 2,
    "to": 5,
    "at": "armchair_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 14,
    "to": 15,
    "at": "coffee_table_l1",
    "chance": "rarely"
   }
  ]
 }
}
```
