# a06 — scratch memory, final (live at the end; final weight 0.0004)

d00 Mon 06:14 Look 1: cupboard_k1. Found: mug_shared_1, plate_shared_1, pot_shared_1. Resident_1 in kitchen.

d00 Mon 06:14 Look 2: sink_k1. Found: pan_shared_1, watering_can_mara. Resident_1 in kitchen.

**CRITICAL LEARNINGS:**
1. **Sink is a Storage/Prep Spot:** I assumed sink was only for washing. It holds `pan_shared_1` and `watering_can_mara`. This contradicts my 'Kitchen Zone' belief that pans are in cupboard and watering can is on counter. The sink is a valid receptacle for items being cleaned, prepped, or temporarily stored.
2. **Cupboard is Selective:** Cupboard has `mug_shared_1`, `plate_shared_1`, `pot_shared_1`. It does NOT have `bowl_shared_1/2`, `plate_shared_2`, or `pan_shared_1`. This suggests not all shared dishware is in the cupboard. Some are in use (counter/sink) or elsewhere (dish_rack).
3. **Resident Location:** Resident_1 is consistently in the kitchen. This is the active zone. Portable items (keys, phone, wallet) are likely ON_PERSON or in the kitchen (counter/sink) rather than their 'home' zones (entry/bedroom).
4. **Forecast Failure:** I gave near-zero probability to `pan_shared_1` and `watering_can_mara` being in the sink. I need to assign non-negligible probability to 'active' receptacles (sink, counter) for kitchenware, especially when the resident is present.
5. **Strategy:**
   - **Kitchenware:** If resident is in kitchen, prioritize `counter_k1`, `sink_k1`, `dish_rack_k1` over `cupboard_k1` for items like pans, bowls, plates. Cupboard is for 'stored' items, but the line is blurry.
   - **Portable Items:** If resident is in kitchen, `ON_PERSON` is a strong candidate for keys/phone/wallet/glasses. If not ON_PERSON, look in kitchen receptacles (counter, sink) before entry/bedroom.
   - **Watering Can:** Can be in kitchen (sink/counter) or entry. Not just kitchen.
   - **Look Budget:** 6 remaining. Next look should target `counter_k1` or `dish_rack_k1` to map the rest of the kitchenware. Or `resident_1` to check for carried items if asked.

**BELIEF UPDATE NEEDED:** My current beliefs are too rigid about 'home' zones. I need a 'State-Dependent' model where the resident's location shifts probabilities for portable items and active kitchenware. I will propose a FORK to rewrite beliefs to reflect this dynamic.
