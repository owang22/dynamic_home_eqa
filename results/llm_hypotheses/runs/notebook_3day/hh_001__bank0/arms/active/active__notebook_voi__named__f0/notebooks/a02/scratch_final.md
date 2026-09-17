# a02 — scratch memory, final (retired d01 Tue 23:59 (review: lowest at end of day); final weight 0.1979)

d01 Tue 06:06 Looked at counter_k1. Found: bowl_shared_1, mug_mara, plate_shared_2, water_bottle_mara. Residents: resident_1.
d01 Tue 06:06 Looked at cupboard_k1. Found: mug_shared_1, pot_shared_1. Residents: resident_1.

STATUS: Weight 0.178 (Rank 4/5). Score -8.38 (Panel avg -7.11). I underperformed the panel significantly on this look.

KEY LEARNINGS & CORRECTIONS:
1. **Cupboard is a Storage Zone, not a Dumping Ground:** My previous belief that 'high-traffic' zones (counter/coffee table) are the primary locations for misplaced items was too broad. The cupboard_k1 contains specific storage items: mug_shared_1 and pot_shared_1. These are not 'clutter' but stored cookware/drinkware. I assigned 0.02 to mug_shared_1 and pot_shared_1, which was a massive error (log(0.02) ≈ -3.9 each). I should have assigned higher probability (0.5-0.8) to items that fit the 'storage' class of the receptacle.
2. **Medication Bottle:** I assigned 0.15 to medication_bottle_mara in the cupboard. It was absent. This confirms that medication is likely kept in a more secure or specific spot (bathroom_shelf, nightstand, or ON_PERSON), not in the general kitchen cupboard. Lower this probability for kitchen receptacles.
3. **Resident Location:** Resident_1 is in the kitchen. This correlates with the presence of water_bottle_mara and mug_mara on the counter (active use) and mug_shared_1/pot_shared_1 in the cupboard (storage). The resident is likely preparing food or drinks.
4. **Absence Penalty:** The penalty for overestimating absent items is severe. However, the penalty for *underestimating* present items is also severe. My 'Zero-Noise' policy (0.01-0.02 for non-contextual) failed because I failed to identify the *correct* contextual items for the cupboard. Context for cupboard = stored pots, pans, mugs, maybe baking supplies. Context for counter = active dishes, drinks, food prep.

STRATEGY REVISION:
- **Receptacle-Specific Context:**
  - **Cupboard_k1:** High prob for pot_shared_1, pan_shared_1, mug_shared_1, bowl_shared_1/2 (if stored), maybe lunchbox_mara. Low prob for tech, personal items, active dishes.
  - **Counter_k1:** High prob for active dishes (plate/bowl), mugs (mug_mara), water_bottle_mara, food prep items. Low prob for stored pots/pans.
  - **Coffee_table_l1:** High prob for remote_shared_1, book_mara, notebook_mara, phone_mara (if not on person), glasses_mara. Low prob for kitchen items.
  - **Bedroom:** High prob for laptop, tablet, charger, blanket, pillow (if existed), clothes (jacket, towel).
  - **Entry:** High prob for keys, wallet, jacket, umbrella, backpack.
- **Probability Calibration:**
  - If an item fits the *class* of the receptacle (e.g., pot in cupboard), assign 0.5-0.8.
  - If an item is in its 'home spot' (e.g., keys in entry), assign 0.6-0.8.
  - If an item is in a 'high-traffic' zone but doesn't fit the class (e.g., laptop on counter), assign 0.1-0.2.
  - If an item is in a random other receptacle, assign 0.01-0.05.
- **Resident Tracking:** Resident_1 is in the kitchen. Monitor for movement. If they move to living, check if phone/keys move to ON_PERSON or coffee_table. If they move to bedroom, check if laptop/charger move to bed/desk.

NEXT STEPS:
- Update beliefs to distinguish between 'active use' zones (counter, coffee table) and 'storage' zones (cupboard, bedroom, entry).
- Be more precise about which items belong in which storage zone.
- Continue to track resident_1's location to predict movement of personal items (phone, keys, wallet).
