# a03 — scratch memory, final (live at the end; final weight 0.0001)

d02 Wed 04:05: Looked at entry_hook_e1. Found: backpack_mara. Residents: nobody.
d02 Wed 04:05: Looked at entry_table_e1. Found: bowl_shared_1. Residents: nobody.

ANALYSIS:
1. **Surprise**: bowl_shared_1 on entry_table_e1 at 04:05 is a significant deviation. Shared kitchenware should be in the kitchen (counter/sink/cupboard). Its presence in the entry suggests it was moved there recently (perhaps for a snack or to be washed later) or is being used as a temporary drop spot. This contradicts the strict 'kitchen items in kitchen' rule for non-personal items.
2. **Forecast Error**: Score -5.08. I assigned 0.05 to keys/wallet/jacket (likely in bedroom or on hook) and 0.02 to umbrella. I missed bowl_shared_1 entirely (p=0). The penalty came from the log(0) for the bowl and the accumulated log(1-p) for the ~30 other absent items. I over-weighted the 'entry = keys/jacket' heuristic and ignored the possibility of shared items migrating to the entryway.
3. **Refined Entry Model (Night/Early Morning)**:
   - **Entry Hook**: Backpack, Jacket, Umbrella, Keys (if resident is out or just in).
   - **Entry Table**: Keys, Wallet, Phone (if charging), **Shared Items** (bowl, mug, plate) if resident is eating/drinking in entry or moving them to kitchen. At 04:05, a bowl here is unusual but possible if resident is awake and eating.
   - **Resident**: Not in entry. Likely bedroom (0.8) or OUT_OF_HOUSE (0.2). If resident is in bedroom, entry items are static. If resident is out, entry items are static. If resident is awake in bedroom, they might have moved items to entry.
4. **Probability Adjustment**: 
   - For entry_table_e1: Assign 0.05-0.10 to keys, wallet, phone, jacket. Assign 0.02-0.05 to shared items (bowl, mug, plate) because they *can* be there, even if unlikely. Do not assign 0 to shared items in entry.
   - For entry_hook_e1: Assign 0.10 to backpack, jacket, umbrella. Assign 0.05 to keys.
   - Keep base probability for absent items <0.005 to minimize cumulative penalty.
5. **Current State (04:05)**:
   - entry_hook_e1: backpack_mara (confirmed).
   - entry_table_e1: bowl_shared_1 (confirmed).
   - resident_1: Not in entry. Likely bedroom (0.8) or OUT_OF_HOUSE (0.2).
   - Other objects: Assume standard night locations (bedroom) for personal items. Shared items in kitchen unless observed elsewhere.
6. **Strategy**: When looking at entry receptacles, include a small probability mass (0.02-0.05) for shared kitchen items (bowl, mug, plate) in case they are being moved or used. Do not assume entry is exclusively for personal carry items. This prevents the log(0) penalty for unexpected shared items.
