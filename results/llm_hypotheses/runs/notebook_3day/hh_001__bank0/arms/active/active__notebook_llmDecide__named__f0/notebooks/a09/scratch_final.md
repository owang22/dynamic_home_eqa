# a09 — scratch memory, final (retired d01 Tue 23:59 (population cap); final weight 0.0010)

d01 Tue 05:40 Look at resident_1 in bathroom: wallet_mara ONLY.
- Score -5.14. Weight 0.053 (Rank 4).
- Analysis:
1. **Correction to Drift Model**: The 'Dynamic Drift' hypothesis that high-mobility items (phone, keys, glasses) follow the resident ON_PERSON was partially wrong. Only the wallet was carried. Phone, keys, and glasses were NOT on person.
2. **Location Inference**: Since resident_1 is in the bathroom and the shelf (looked at 05:40) contained only care items, the missing high-mobility items (phone, keys, glasses) are likely:
   - ON_PERSON (but look says no, so this is ruled out for this moment).
   - In the bathroom but not on the shelf: towel_rack_ba1 or bathroom_floor_ba1? Unlikely for phone/keys.
   - Left in the previous room (bedroom) or transit area (living/kitchen) before entering the bathroom. The nightstand was empty, so they weren't left there. They might be on the bed, desk, or floor in the bedroom, or on the coffee table/counter.
3. **Wallet Exception**: Wallet is the only item consistently carried. It has a stronger 'ON_PERSON' anchor than phone/keys/glasses in this household's current state.
4. **Strategy Update**: 
   - Do NOT assume all high-mobility items are ON_PERSON just because the resident is active.
   - If resident is in Room X, check if items are ON_PERSON. If not, they are likely in the *previous* room or a high-traffic surface in the *current* room (if set down).
   - For phone/keys/glasses: If not ON_PERSON and resident is in bathroom, look for them in bedroom (bed/desk) or living room (coffee table) as they were likely left there before moving to the bathroom.
5. **Remaining Looks (6 left)**: 
   - Priority 1: Locate phone_mara. Likely in bedroom (bed_b1, desk_b1) or living (coffee_table_l1).
   - Priority 2: Locate keys_mara. Similar to phone.
   - Priority 3: Locate glasses_mara. Could be in bedroom or living.
   - I will look at bedroom next to see if resident is still there (no, they are in bathroom) but to check receptacles. Wait, I can't look at bedroom if resident is in bathroom? No, I can look at any receptacle. But looking at a receptacle shows residents in that room. If I look at bedroom, I'll see if anyone is there (likely no one). This is a good way to check if items were left there.
   - Actually, looking at a receptacle in the bedroom will reveal if the resident is there. Since resident is in bathroom, bedroom looks will just show items. This is efficient.
   - Plan: Look at bed_b1 or desk_b1 to find phone/keys/glasses. If not there, look at coffee_table_l1.
