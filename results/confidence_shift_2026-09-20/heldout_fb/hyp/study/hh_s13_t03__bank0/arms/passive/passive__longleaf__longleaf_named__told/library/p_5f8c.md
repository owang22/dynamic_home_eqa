# p_5f8c — Morning Shelf: Hana's Towel and Priya's Razor in Use 7–10

This is a fresh document addressing a pattern the library has been missing. The mixture's worst-objects list shows towel_hana was predicted at towel_rack_ba1 but actually found at bathroom_shelf_ba1 (2 times, day 2 07:00). Razor_priya was predicted at sink_ba_ba1 but actually at bathroom_shelf_ba1 (1 time, day 2 03:00).

The clock-hour sightings make the routine clear. Towel_hana is on bathroom_shelf_ba1 at 07:00 (2×), 09:00 (2×), and 10:00 (1×). It is on towel_rack_ba1 at 03:00 (2×) and 18:00 (1×). This means: the towel rests on the rack overnight, is moved to the shelf for Hana's morning shower (7:00–10:00), and is hung back on the rack by evening. Razor_priya is on bathroom_shelf_ba1 at 07:00 (3×) — Priya shaves in the morning. It is in the sink at 18:00 (1×) — evening rinse. At 03:00 it is split between sink and shelf.

What sets this apart: at 08:00 on any day, towel_hana is at bathroom_shelf_ba1 (not towel_rack_ba1), and razor_priya is at bathroom_shelf_ba1 (not sink_ba_ba1). The standard documents place the towel on the rack and the razor in the sink all day. What would refute it: towel_hana at towel_rack_ba1 at 08:00, or razor_priya at sink_ba_ba1 at 07:00.

```json
{
 "claims": [
  {
   "claim": "Hana's towel is on the bathroom shelf at 08:00 (morning shower in progress)",
   "target": "towel_hana",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 7,
   "to": 10
  },
  {
   "claim": "Priya's razor is on the bathroom shelf at 07:00 (morning shave)",
   "target": "razor_priya",
   "expect": "bathroom_shelf_ba1",
   "days": "both",
   "from": 6,
   "to": 9
  },
  {
   "claim": "Hana's towel is back on the towel rack at 18:00 (hung up after morning use)",
   "target": "towel_hana",
   "expect": "towel_rack_ba1",
   "days": "both",
   "from": 17,
   "to": 24
  }
 ],
 "targets": {
  "towel_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "towel_rack_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 10,
    "at": "bathroom_shelf_ba1",
    "chance": "almost_always"
   }
  ],
  "razor_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
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
    "from": 17,
    "to": 19,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   }
  ],
  "skincare_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bathroom_shelf_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 9,
    "at": "sink_ba_ba1",
    "chance": "sometimes"
   }
  ],
  "soap_dispenser_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "almost_always"
   }
  ],
  "toothbrush_holder_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "almost_always"
   }
  ]
 }
}
```
