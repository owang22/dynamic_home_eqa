# a03 — scratch memory, final (live at the end; final weight 0.0000)

counter_k1: Stable hub for Marisol's tech (charger, notebook), mugs, meds, and shared lunchboxes/bottles. High persistence even when empty. Pan_shared_1 transient (p~0.30). Charger_nico is transient (p~0.10), not stable. Phone_talia is transient (p~0.05). Meds absent recently (p~0.10).
sink_k1: Primary storage for shared cookware (pan, pot, bowl) and plate_shared_1. High persistence for cookware. NOT a spot for phones, keys, or mugs. Phone_nico absent (p<0.05).
cupboard_k1: Holds plate_shared_1 (p>0.50). Keys/wallets/meds absent.
bedroom_1: Nightstand_b1 is NOT a stable drop zone for Marisol's items (glasses/phone) even when she is present (p<0.05). Marisol carries phone_marisol ON_PERSON (p>0.80) when in bedroom_1; carries no other items (keys/wallet/glasses p<0.05).
bedroom_3: Transient zones. Desk_b3 and floor_b3 are not storage hubs for Nico's items. Floor holds laundry_basket_shared_1. Nico's items move to common areas.
ON_PERSON: Talia carries nothing in kitchen (p~0.01). Nico's phone is likely in sink_k1, not ON_PERSON.
General: Resident presence dictates location. Common areas dominate daytime. Bedroom floors are not drop zones. Sink is key for cookware. Adjust priors down for non-core items in stable hubs to avoid overconfidence penalties.
d13 Sun 07:15: resident_1 in bedroom_1 carries phone_marisol. Confirms p(phone_marisol ON_PERSON | resident_1 in bedroom_1) > 0.80. No other items carried. Adjust priors: p(keys/wallet/glasses ON_PERSON) < 0.05 when in bedroom.
d13 Sun 07:15: d13 Sun 07:15 counter_k1: charger_marisol, lunchbox_nico, lunchbox_talia, mug_marisol, notebook_marisol, pan_shared_1, water_bottle_marisol, water_bottle_nico. No residents. My low priors for core Marisol items (mug, notebook, charger) caused massive penalty. Pan_shared_1 confirmed transient. Update: p(Marisol core items on counter_k1) > 0.80.
d13 Sun 07:15: d13 Sun 07:15 sink_k1: pot_shared_1, plate_shared_1. No residents. Confirms sink as stable cookware hub. My p(pot)=0.25 was too low; p(plate)=0.15 too low. Update: p(pot/plate in sink_k1) > 0.60. Absence of pan_shared_1 (p=0.35) and bowl_shared_1 (p=0.20) correct. No personal items in sink.
