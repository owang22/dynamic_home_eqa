# p_4f8e — The Medicine Cabinet and the Bedroom Floor

Two objects have been mis-located by the mixture on every recent pass. medication_priya is predicted at coffee_table_l1 but the robot keeps finding it in medicine_cabinet_ba1 (seven misses since the last call). The per-object evidence shows it at the coffee table x2 and the medicine cabinet x1–2 at each hour, meaning it is *stored* in the cabinet and only occasionally brought to the coffee table when Priya takes a dose. This document pins it to the medicine cabinet as the default and allows a brief coffee-table window around the likely dosing times (early morning, early evening).

Similarly, tablet_priya is predicted at nightstand_b2 but the robot finds it on bedroom_floor_b2 five times in the recent window. The hourly sightings show it at the nightstand x2 and the bedroom floor x1 from 10:00 through 18:00, with the floor share growing in the afternoon. Priya is retired and spends her afternoons in her bedroom reading, photographing, or using the tablet on the bed or floor. This document places the tablet on bedroom_floor_b2 from 08:00 to 18:00 and back on the nightstand for the evening and overnight.

The document also re-asserts the two rock-solid anchors that every other hypothesis shares: guitar_hana on bedroom_floor_b1 (39/39 sightings, four of four days) and camera_priya on bookshelf_l1 (39/39, four of four days). These are included so the document is self-contained.

What would refute this: medication_priya found at the coffee table in the mid-afternoon (14:00–18:00) when no dosing is expected; tablet_priya at the nightstand during the 10:00–16:00 window; either anchor object found elsewhere.

```json
{
 "claims": [
  {
   "claim": "Priya's medication is in the medicine cabinet, not on the coffee table, during the mid-morning",
   "target": "medication_priya",
   "expect": "medicine_cabinet_ba1",
   "days": "both",
   "from": 9,
   "to": 13
  },
  {
   "claim": "Priya's tablet is on her bedroom floor while she uses it in the afternoon",
   "target": "tablet_priya",
   "expect": "bedroom_floor_b2",
   "days": "both",
   "from": 10,
   "to": 16
  },
  {
   "claim": "Priya's medication is in the medicine cabinet in the late afternoon",
   "target": "medication_priya",
   "expect": "medicine_cabinet_ba1",
   "days": "both",
   "from": 14,
   "to": 18
  },
  {
   "claim": "Priya's tablet is back on her nightstand by the evening",
   "target": "tablet_priya",
   "expect": "nightstand_b2",
   "days": "both",
   "from": 20,
   "to": 23
  }
 ],
 "targets": {
  "medication_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "medicine_cabinet_ba1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 7,
    "to": 8,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 20,
    "to": 21,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   }
  ],
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 8,
    "at": "nightstand_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 8,
    "to": 18,
    "at": "bedroom_floor_b2",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 18,
    "to": 24,
    "at": "nightstand_b2",
    "chance": "usually"
   }
  ],
  "camera_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bookshelf_l1",
    "chance": "almost_always"
   }
  ],
  "guitar_hana": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "bedroom_floor_b1",
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
   }
  ]
 }
}
```
