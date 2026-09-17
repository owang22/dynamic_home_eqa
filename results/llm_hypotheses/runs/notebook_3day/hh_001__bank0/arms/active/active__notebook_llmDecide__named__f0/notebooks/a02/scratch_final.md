# a02 — scratch memory, final (retired d01 Tue 23:59 (review: lowest at end of day); final weight 0.1205)

d01 Tue 06:15: Looked at bed_b1. Found: nothing. Residents: nobody.

**Forecast Error Analysis**:
- **Success**: Correctly identified bed_b1 as empty. High confidence (0.99+) on absence of bulky items (laundry, suitcase, vacuum) and soft goods (blanket, yoga mat) was rewarded.
- **Failure**: Assigned non-negligible probability (0.01-0.15) to ~30 small items (electronics, personal care, dishes) that were absent. The cumulative log penalty for these 'just in case' guesses (~-6.0) dragged the score down to -0.80. The top performers (a05, a08) likely assigned near-zero probability to items that don't belong on a bed.
- **Lesson**: Bed_b1 is a 'dormant' receptacle. It is not a high-traffic zone for active items. Unless an item is specifically a 'bed item' (blanket, pillow - not in list, maybe book/notebook if reading in bed), its probability here should be extremely low (0.001-0.005). I over-weighted the 'bedroom as storage' belief for small electronics. Laptops/phones are rarely left on the bed surface; they are more likely on the desk or floor.

**Resident Location**:
- Resident_1 is NOT in bedroom (bed or floor).
- Last seen in kitchen (06:10).
- Likely still in kitchen or bathroom.

**Object Status Updates**:
- **Confirmed at bedroom_floor_b1**: laundry_basket_mara, suitcase_mara, vacuum_cleaner_shared_1. Stable 'dormant' bulky items.
- **Confirmed at entry_hook_e1**: backpack_mara, charger_mara, keys_mara. Staging area.
- **Confirmed at couch_l1**: blanket_mara, yoga_mat_mara. Soft goods repository.
- **Confirmed at bed_b1**: EMPTY. No electronics, no personal care, no dishes.
- **Absent from bedroom (bed+floor)**: All electronics (laptop, phone, tablet), personal care (glasses, makeup, hairbrush), small daily items (pen, notebook, book), and all kitchenware.

**Strategy Update**:
1. **Probability Calibration**: Refine 'Bedroom' belief. Bed_b1 and bedroom_floor_b1 are 'low-entropy' storage zones. Only items with a history of being there get >0.05 probability. Everything else gets 0.001-0.005. This avoids the log-penalty for false positives on small items.
2. **Resident Tracking**: Resident is isolated to kitchen/bathroom. Next look should target counter_k1 or sink_k1 to locate resident and check for dishes/mugs/phone.
3. **Next Targets**:
   - counter_k1 (resident, dishes, mugs, phone, laptop?)
   - coffee_table_l1 (remote, tablet, water bottle, charger?)
   - nightstand_b1 (phone, glasses, medication, charger backup) - *Note: If resident is not in bedroom, nightstand is less likely to have active items, but still a candidate for forgotten items.*
4. **Belief Refinement**: My 'High-Traffic Zones' belief needs nuance. High-traffic zones (coffee table, counter) hold *active* items. Bedroom floor/bed hold *dormant/bulky* items. Couch holds *soft/bulky* items. Entry hook holds *staging* items. I must distinguish between 'active' and 'storage' receptacles in my probability model. Specifically, 'storage' receptacles have a much lower entropy of contents. I will apply a 'sparse prior' to bed_b1 and bedroom_floor_b1 for all items not explicitly known to be stored there.
