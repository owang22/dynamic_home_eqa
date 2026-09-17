# a14 — scratch memory, final (live at the end; final weight 0.0000)

d02 Wed 04:05: Looked at entry_hook_e1. Found: backpack_mara, charger_mara, jacket_mara. Residents: nobody.
- **Forecast Error**: Score -13.28. I assigned 0.45 to keys_mara and 0.15 to wallet_mara, but they were absent. I assigned 0.05 to jacket_mara, which was present. The massive penalty comes from the high probability assigned to keys/wallet being absent (log(1-0.45) + log(1-0.15) is very negative) and the low probability assigned to the actual items (backpack, charger) which I likely assigned near 0.
- **Key Insight**: Entry_hook_e1 is NOT just for keys/wallet. It is a 'catch-all' hook for items being brought in or taken out. Backpack, charger, and jacket were all here at 04:05.
- **Resident Status**: Resident_1 is NOT in the entry. Given the time (04:05) and the items on the hook (backpack, charger), the resident is likely in the bedroom (sleeping or waking up) or kitchen. The presence of the backpack and charger on the hook suggests the resident may have just returned or is about to leave, but since they are not in the entry, they are elsewhere.
- **Item Locations Update**:
  - backpack_mara: entry_hook_e1
  - charger_mara: entry_hook_e1
  - jacket_mara: entry_hook_e1
  - keys_mara: NOT on entry_hook_e1. Likely ON_PERSON (if resident is up) or in pocket of backpack? Or on entry_table_e1? My belief that keys are 'canonically' on the hook is too strong; they might be in the backpack or on the table.
  - wallet_mara: NOT on entry_hook_e1. Likely ON_PERSON or entry_table_e1.
  - umbrella_mara: NOT on entry_hook_e1.
- **Strategy Update**:
  1. **Resident Location**: Check bedroom (bed_b1 or nightstand_b1) to see if resident is there. If not, check kitchen.
  2. **Keys/Wallet**: Since they are not on the hook, check entry_table_e1 next. If not there, they are likely ON_PERSON.
  3. **Backpack/Charger/Jacket**: Now known to be on entry_hook_e1. Do not look for them elsewhere unless the hook is checked again and they are gone.
  4. **Time Context**: 04:05 is very early. Resident might be sleeping. If resident is in bedroom, phone/laptop/tablet are likely on nightstand/desk. If resident is in kitchen, they are up and about.
- **Belief Refinement**: Entry_hook_e1 is a high-variability receptacle. It holds outerwear, bags, and small electronics (chargers) that are 'in transit'. It is not a stable storage for keys/wallet exclusively. Keys/wallet are more likely ON_PERSON or on entry_table_e1 if not on the hook.
