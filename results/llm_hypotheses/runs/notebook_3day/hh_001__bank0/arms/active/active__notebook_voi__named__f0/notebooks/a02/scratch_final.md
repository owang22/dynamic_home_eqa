# a02 — scratch memory, final (retired d01 Tue 23:59 (review: lowest at end of day); final weight 0.1598)

d01 Tue 05:58 Looked at counter_k1. Found: lunchbox_mara, mug_mara, notebook_mara, pen_mara. Residents: resident_1.

OBSERVATION: The kitchen counter is a 'work surface' for Mara, not just a dish dump. It holds personal items (notebook, pen, lunchbox) alongside mugs. This contradicts the 'kitchen clutter' belief that only dishes/mugs belong there. Resident_1 moved from bathroom to kitchen, likely for breakfast/prep.

SCORING LESSON: Score -13.66 (panel avg -14.31). I outperformed the panel. The penalty came from assigning p=0.05 to ~30 irrelevant objects (hairbrush, meds, vacuum, etc.). Even small probabilities on absent items accumulate negative log-likelihood. I also underestimated the presence of notebook/pen/lunchbox (p=0.05) while overestimating plates/bowls (p=0.35) which were absent.

REFINED STRATEGY:
1. Aggressive Sparsity: Assign p=0.001 to objects with no contextual link to the receptacle. Do not spread probability thinly. If an object isn't in the top 3-5 likely candidates, it is absent.
2. Contextual Anchoring:
   - Bathroom Shelf: Hairbrush, Makeup, Meds (p>0.8). Everything else (p~0).
   - Kitchen Counter: Mugs (p>0.5), Personal Work Items (Notebook, Pen, Laptop, Phone) (p>0.3), Lunchbox (p>0.3). Dishes (Plates/Bowls) are less likely if not currently in use (p<0.2).
   - Living Room: Remote, Laptop, Tablet, Books (p>0.5).
   - Nightstand: Phone, Charger, Glasses (p>0.5).
3. Carry Items: In the kitchen, resident_1 is likely holding phone_mara or keys_mara (p~0.3). Wallet is less likely unless leaving.
4. Next Steps: Resident_1 is in the kitchen. Likely next move: Living Room (relax) or Bedroom (rest). Monitor coffee_table_l1 for remote/laptop. Check entry_table_e1 for keys/wallet if they leave. The counter is now 'clean' of dishes, suggesting they were washed or moved.
5. Calibration: Be conservative with high probabilities. Only assign p>0.5 if evidence is strong. For 'carry' items, distribute probability evenly among likely candidates (phone, keys) rather than betting heavily on one.

KEY INSIGHT: The counter is a multi-use surface. Personal items (notebook, pen) are common there. Dishes are not always present. Adjust priors accordingly: Counter = Mugs + Personal Tech/Stationery + Food Prep. Not just dishes.
