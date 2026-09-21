# p_4f2a — Midday drift: Priya's afternoon moves objects between resting spots

This document captures a pattern the existing library underweights: during the weekday 12:00–17:00 window, several objects are in a state of transition because Priya is moving through the house doing small tasks (tidying, preparing for an errand, tending to the dog). The objects do not have a single stable midday location; they are found at their "resting" spot and at a "working" spot in roughly equal measure.

**Sunglasses (sunglasses_priya):** Rest at entry_table_e1 overnight and in the morning (00:00–10:00: entry_table x2, entry_floor x1). But during 14:00–16:00 the sightings shift: at 14:00 entry_table x1 and entry_floor x1; at 16:00 entry_floor x1 only. The sunglasses are being set down on the entry floor, perhaps while Priya puts on her coat for an errand or takes them off after returning. The mixture has been wrong 10 times predicting entry_table when the actual was entry_floor.

**Toiletry bag (toiletry_bag_elena):** Rests at dresser_b1 overnight and in the morning (00:00–10:00: dresser x2, bathroom_shelf x1). During 12:00–16:00 the split is 1-to-1 between dresser_b1 and bathroom_shelf_ba1. The bag is being moved to the bathroom shelf, likely because Priya (who is home all day) uses the bathroom and reaches for it there. The mixture has been wrong 8 times.

**Razor (razor_priya):** Rests at sink_ba_ba1 overnight (00:00–10:00: sink x2, medicine_cabinet x1). During 12:00–16:00 the split is 1-to-1 between sink_ba_ba1 and medicine_cabinet_ba1. The razor is being stored in the medicine cabinet during the day, perhaps after a midday shave or as part of tidying. The mixture has been wrong 8 times.

**Dog food bag (dog_food_bag_shared):** Rests at pantry_shelf_k1 during the day (12:00–16:00: pantry x2). But in the evening (20:00–22:00) it appears at pantry x1, kitchen_table x1, and floor_k_k1 x1 — the bag is opened for the evening feeding and left on the kitchen floor. The mixture has been wrong 8 times predicting pantry when the actual was floor_k.

What sets this hypothesis apart: it explicitly models the 12:00–17:00 "drift" window where four objects are in a 50/50 split between two receptacles, rather than assigning them to a single resting spot. It also captures the evening dog-feeding shift of the food bag to the kitchen floor.

Refutation: if sunglasses are found at entry_table_e1 on 8+ of 10 looks during 14–16h on weekdays; if the toiletry bag is at the dresser on 8+ of 10 looks during 12–16h; if the razor is at the sink on 8+ of 10 looks during 12–16h; if the dog food bag is at the pantry on 8+ of 10 looks during 20–22h.

```json
{
 "claims": [
  {
   "claim": "Priya's sunglasses are on the entry floor during weekday afternoon",
   "target": "sunglasses_priya",
   "expect": "entry_floor_e1",
   "days": "weekday",
   "from": 14,
   "to": 16
  },
  {
   "claim": "Elena's toiletry bag is on the bathroom shelf during weekday midday",
   "target": "toiletry_bag_elena",
   "expect": "bathroom_shelf_ba1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "Priya's razor is in the medicine cabinet during weekday midday",
   "target": "razor_priya",
   "expect": "medicine_cabinet_ba1",
   "days": "weekday",
   "from": 12,
   "to": 16
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the evening feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "both",
   "from": 20,
   "to": 22
  }
 ],
 "targets": {
  "sunglasses_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "entry_table_e1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 13,
    "to": 17,
    "at": "entry_floor_e1",
    "chance": "sometimes"
   }
  ],
  "toiletry_bag_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "dresser_b1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 17,
    "at": "bathroom_shelf_ba1",
    "chance": "sometimes"
   }
  ],
  "razor_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_ba_ba1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 11,
    "to": 17,
    "at": "medicine_cabinet_ba1",
    "chance": "sometimes"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "floor_k_k1",
    "chance": "sometimes"
   },
   {
    "days": "both",
    "from": 19,
    "to": 22,
    "at": "kitchen_table_k1",
    "chance": "rarely"
   }
  ],
  "glass_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 21,
    "to": 23,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ],
  "glass_elena": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "sink_k1",
    "chance": "usually"
   },
   {
    "days": "both",
    "from": 12,
    "to": 18,
    "at": "cupboard_k1",
    "chance": "sometimes"
   }
  ]
 }
}
```
