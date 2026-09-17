# a04 — scratch memory, final (retired d00 Mon 05:49 (population cap); final weight 0.0339)

d00 Mon 04:42: Looked at nightstand_b1. Found: phone_mara. Residents: resident_1.
d00 Mon 04:42: Looked at desk_b1. Found: (nothing). Residents: resident_1.
d00 Mon 04:42: Looked at bathroom_shelf_ba1. Found: hairbrush_mara, makeup_kit_mara, medication_bottle_mara. Residents: nobody.
d00 Mon 05:27: Looked at towel_rack_ba1. Found: towel_mara. Residents: resident_1.
d00 Mon 05:49: Looked at counter_k1. Found: lunchbox_mara, mug_mara, water_bottle_mara. Residents: resident_1.

Analysis:
- My uniform model (1/35) is failing badly. Score -11.49 vs panel avg -9.69.
- The counter_k1 look revealed 3 items: lunchbox, mug, water_bottle. These are 'kitchen/food/drink' items.
- I assigned 0.03 to each. The log penalty for missing these high-probability items was severe.
- Resident_1 is in the kitchen. This correlates with the presence of personal food/drink items (lunchbox, water_bottle) and a personal mug.
- Pattern emerging: Receptacles hold class-appropriate items. Kitchen counter holds food/drink. Bathroom shelf holds hygiene/meds. Bathroom rack holds towels. Bedroom nightstand holds phone.
- The 'Uniform' belief is contradicted by the strong class-location correlation.
- I am ranked 5th (weight 0.068). I must fork to a Class-Conditional model to survive.
- Fork Rationale: The uniform model assumes independence between object class and location. The data shows strong dependency. A model that boosts probability for class-matched locations (e.g., P(mug|kitchen) >> P(mug|bedroom)) will score much better on hits and misses.
- New Beliefs will assign higher base probabilities to 'home' spots based on object class and lower probabilities elsewhere. It will also account for resident presence: if resident is in a room, personal items are more likely to be in that room's receptacles or ON_PERSON.
