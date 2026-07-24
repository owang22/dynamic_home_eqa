# Household memory — after day 11 (12 day(s) observed)

## Persona hypotheses (up to 3, probs sum to 1)
1. (p=0.98) Standard 5-Day Office Worker with Pet — Consistent Mon-Fri morning departures (06:51-07:49) and evening returns. Day 11 (Fri) shows no morning departure event in the new data, but the presence of a coffee mug at midday (12:48) and dog leash at evening (18:00) suggests the resident is home or the 'departure' was missed/not logged as a phone movement. However, looking closely at Day 11 events: food_bowl at sink (morning prep?), coffee_mug at counter (midday break?), ball at toy basket (play?), dog_leash at sofa (evening prep?). The lack of a 'phone at entry_hook' on Day 11 morning is a deviation. If the resident left, the phone should be at the hook. If they are home, the coffee mug makes sense. But previous days show strict departures. Let's re-read Day 11 events. No phone movement recorded. This implies the resident might be WFH on Friday, or the sensor missed it. Given the strong Mon-Thu pattern, a WFH Friday is a plausible shift, or the 'Office Worker' hypothesis needs refinement to 'Hybrid with WFH Friday'. However, the dog leash at 18:00 on sofa suggests they are home to grab it. If they were at work, the leash would likely be at the entry hook. The coffee mug at 12:48 also suggests home presence. Therefore, Friday appears to be a WFH day. This contradicts the 'Standard 5-Day' hypothesis. I must update Hypothesis 1 to 'Hybrid Worker (WFH Fri)' and lower the 'Standard 5-Day' prob.
2. (p=0.98) Hybrid Worker (WFH Fri) — Day 11 (Fri) shows no morning departure (phone not at hook). Instead, coffee_mug at counter (12:48) and dog_leash at sofa (18:00) indicate home presence. This aligns with a pattern of Mon-Thu office, Fri WFH. The dog leash at sofa suggests preparation for an evening walk from home, consistent with WFH.
3. (p=0.02) Remote Worker with Erratic Schedule — Low probability. The schedule is highly structured Mon-Thu. The Friday deviation is specific enough to suggest a planned WFH day rather than erratic behavior.

## Selected evidence
- Day 0, 07:49 — phone at counter_k1 (Mon departure, late start)
- Day 1, 07:10 — phone at entry_hook_e1 (Tue departure, early start)
- Day 2, 16:54 — phone at entry_hook_e1 (Wed return, confirms office day)
- Day 4, 07:04 — phone at entry_hook_e1 (Fri departure, early start)
- Day 5, 07:02 — phone at entry_hook_e1 (Sat departure, weekend errands)
- Day 7, 07:49 — phone at counter_k1 (Mon departure, confirms late start)
- Day 8, 07:04 — phone at entry_hook_e1 (Tue departure, confirms early start)
- Day 9, 07:39 — phone at counter_k1 (Wed departure, confirms late start)
- Day 10, 06:51 — phone at entry_hook_e1 (Thu departure, confirms office day)
- Day 10, 17:06 — dog_leash at entry_hook_e1 (Evening dog walk, confirms resident home late afternoon)
- Day 11, 12:48 — coffee_mug at counter_k1 (Fri midday home, suggests WFH)
- Day 11, 18:00 — dog_leash at sofa_l1 (Fri evening prep, suggests home presence)

## Notes
Day 11 (Fri) lacks morning phone departure, but has midday coffee mug and evening dog leash at sofa. This strongly suggests Friday is a WFH day. The previous 'Standard 5-Day Office' hypothesis is now contradicted. Updated to 'Hybrid Worker (WFH Fri)'. Need to verify if this pattern holds next Friday. Also, note the dog leash location: entry_hook on Thu evening (leaving for walk?), sofa on Fri evening (preparing for walk from home?). This reinforces the WFH theory for Friday.