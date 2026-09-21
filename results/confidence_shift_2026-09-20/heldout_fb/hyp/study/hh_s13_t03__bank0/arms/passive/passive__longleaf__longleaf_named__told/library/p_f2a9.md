# p_f2a9 — Morning Bathroom: Both Residents, 7-to-10

This document models the weekday morning bathroom sequence for both residents. Hana takes a shower around 7: her phone appears on the bathroom shelf at 07:00 (1 sighting) alongside her towel (2 sightings on shelf at 07:00, 3 at 09:00, 1 at 10:00). By 08:00 the phone is back at the nightstand (3 sightings), but the towel remains on the shelf through 10:00, still drying. By 18:00 the towel is back on the rack, though one 19:00 sighting puts it on the shelf again (perhaps an evening shower). Priya shaves at 7: her razor is on the bathroom shelf at 07:00 on all six observed occasions, a very strong signal. Overnight the razor is mostly in the sink (2/3 at 03:00) and returns to the sink by 18:00.

What sets this document apart: it places Hana's phone on the bathroom shelf specifically during 7-to-8 (the shower window) and back at the nightstand by 8, rather than leaving it at the nightstand all morning as p_6f3c does for the 7-to-8 window (which gets 1 for, 14 against on that claim). It also extends the towel's shelf presence to 10:00 rather than cutting it off at 9, matching the 10:00 sighting. Priya's razor window of 6-to-9 matches the strong 07:00 evidence.

What would refute it: if Hana's phone is consistently at the nightstand at 07:00 (not the bathroom shelf), the shower-at-7 claim weakens. If the towel is back on the rack by 09:00, the drying window is shorter than stated.

```json
{
 "claims": [
  {
   "claim": "Hana's phone is on the bathroom shelf at 07:30 on a weekday because she is in the shower",
   "target": "phone_hana",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 7,
   "to": 8
  },
  {
   "claim": "Hana's towel is on the bathroom shelf at 09:00 on a weekday because it is still drying after the morning shower",
   "target": "towel_hana",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 8,
   "to": 10
  },
  {
   "claim": "Priya's razor is on the bathroom shelf at 07:00 on a weekday during her morning shave",
   "target": "razor_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Hana's phone is back at the nightstand at 08:30 on a weekday after the shower is over",
   "target": "phone_hana",
   "expect": "nightstand_b1",
   "days": "weekday",
   "from": 8,
   "to": 9
  }
 ],
 "targets": {
  "phone_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "nightstand_b1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 8,
    "to": 24,
    "at": "nightstand_b1",
    "chance": "usually"
   }
  ],
  "towel_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 7,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 10,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 10,
    "to": 18,
    "at": "towel_rack_ba1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 20,
    "at": "bathroom_shelf_ba1",
    "chance": "rarely"
   },
   {
    "days": "both",
    "from": 20,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   }
  ],
  "razor_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 6,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 6,
    "to": 9,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   },
   {
    "days": "both",
    "from": 9,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   }
  ]
 }
}
```
