# p_e8b2 — Kitchen Table Breakfast at 08:00; Both Residents Present

The 08:00 patrol pass shows bowl_priya (×3), mug_priya (×2), and tablet_priya (×2) all at kitchen_table_k1, with the dog food bag on the kitchen floor. This is a shared breakfast at the kitchen table, not the dining table. Both residents are home at this hour: Hana before her 13:40 departure, Priya after her early-morning routine. Priya's tablet joins her at the table, suggesting she checks photos or reads while eating. The dog is fed at the kitchen floor (floor_k_k1) during this window. This differs from p_e5f6, which places the shared breakfast at the dining table, and from p_a1b2, which focuses on Priya cooking light dinners. Here the meal is at the kitchen table, casual, with both residents present.

What sets this apart: the kitchen table (not dining table) as the breakfast spot, Priya's tablet at the table during the meal, the dog food bag at floor_k_k1 (not counter) during the 08:00 window.

What would refute it: bowl_priya and mug_priya found at dining_table_d1 during 07:30–09:00 on a weekday; the dog food bag at counter_k1 at 08:00; tablet_priya at coffee_table_l1 during the breakfast window.

```json
{
 "claims": [
  {
   "claim": "Priya's bowl is at the kitchen table during the weekday breakfast",
   "target": "bowl_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9
  },
  {
   "claim": "Priya's mug is at the kitchen table during the weekday breakfast",
   "target": "mug_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9
  },
  {
   "claim": "Priya's tablet is at the kitchen table while she eats breakfast",
   "target": "tablet_priya",
   "expect": "kitchen_table_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9
  },
  {
   "claim": "The dog food bag is on the kitchen floor during the 8 AM feeding",
   "target": "dog_food_bag_shared",
   "expect": "floor_k_k1",
   "days": "weekday",
   "from": 7.5,
   "to": 9
  }
 ],
 "targets": {
  "bowl_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "cupboard_k1",
    "chance": "usually"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "mug_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "tablet_priya": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "coffee_table_l1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7.5,
    "to": 9,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ],
  "dog_food_bag_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "pantry_shelf_k1",
    "chance": "sometimes"
   },
   {
    "days": "weekday",
    "from": 7,
    "to": 9,
    "at": "floor_k_k1",
    "chance": "sometimes"
   }
  ],
  "fruit_bowl_shared": [
   {
    "days": "both",
    "from": 0,
    "to": 24,
    "at": "kitchen_table_k1",
    "chance": "usually"
   }
  ]
 }
}
```
