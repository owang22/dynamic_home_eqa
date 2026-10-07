# Blind checker scores: the robot's written beliefs about the unwell resident

Scored only from `beliefs.jsonl` (and `notes.json` where noted) under
`results/stronger_model/opus_beliefs/claude_opus/cells/walk/<home>/`. Night N = the row with `"day": N`.
Every quote below is copied exactly from the named field on the named night.

## Table

| Point | hh_s2_t03 (Tomas) | hh_s32_t03 (Leo) | hh_s48_t03 (Marco) |
|---|---|---|---|
| 1. Onset 1 | Night 14 | Night 14 | Night 14 |
| 2. Reason, nights 14-23 | Mostly **leave/holiday/time off** (night 14 "day off", night 15 "weekend", 16-23 leave, holiday or job change). Illness is always the second guess. Illness first named **night 14**, never the top guess in either spell | **Mixed; ambiguous.** Illness is the top guess on nights 14 and 17; weekend on 15; holiday/leave on 16 and 18-23. From night 21 it says he does *not* look ill. Illness first named **night 14** | **Mixed; ambiguous.** Unwell is the top guess on nights 14, 17 and 18; days off/holiday/leave on 15-16 and 19-23. Illness first named **night 14** |
| 3. Return 1 | Night 24 | Night 24 | Night 24 |
| 4. Recurrence (nights 32-36) | **Yes, night 32**. Repeated night 33 only loosely; on nights 34, 35 and 36 it says nothing this long has happened before (link lost) | **Yes, night 32**, and repeated every night 33-36 | **Yes, night 32**, repeated 33. From night 34 the earlier spell shrinks to "days 14, 19-20 and 23" / "days 19-20 and day 23" |
| 5. Predicted end (nights 32-41) | Night 32: ~10 days if off two days running; 33: within a day or two; 34: day 35 or 36 (or a full week); 35: about a week in total; 36: end of a 1-2 week holiday; 37: within a few days, start of a new week; 38: 25% chance any day; 39-41: no date ("several more days" / "another week or more") | Night 34: a few days, or longer if it repeats the 10-day spell; 35: about another week; 36: about 10 days, around day 41; 37: about day 41; 38: within about 2-5 days; 39: around day 41-42; 40: within a day or two; 41: soon | Night 32: about a week, like last time; 33: about ten days, as before; 34: within about a week, any day; 35: a few days to a week; 36: a few more days up to about a week; 37: a few more days at most, about day 40; 38-41: "at least a few more days", no date |
| 6. Return 2, and matched to spell 1? | Night 42. **No**: night 42 says it has no record of an earlier stretch this long; night 43 does not mention spell 1 | Night 42. **Yes, night 42** (names the day-24 return after days 14-23) | Night 42. Night 42: **no explicit link** (it compares with the day 24-31 work stretch). Night 43: **yes**, but it dates the earlier rest as "around days 19 to 23" |
| False alarm | None found | None found | **Ambiguous**: nights 4 and 11 say Marco has stopped going out and now stays home (see below) |
| Early wrong belief, never corrected | None about Tomas's routine. Later: from night 34 it loses spell 1 and never gets it back (night 44: "Days 1-31 followed this same work-day routine") | None about Leo's routine. Later: from night 42 it settles on a work rotation/contract-block explanation, rules illness out, and predicts another off stretch around day 49-50 | **Yes**: from night 2-4 it believes Marco "works from home"; it never works out that he is a student out at classes in the mornings (still "Marco is working from home" in night 49 `routines`) |

## Quotes

### hh_s2_t03 (Tomas)

**1. Onset 1, night 14, `anything_changed`:**
"Yes, Tomas changed today (day 14). I never saw him at the office desk, although the laptop, mouse, pen and notebook stayed there all day."

**2. Reason, nights 14-23.**
- Night 14 `why` (also the first time illness is named): "Best guess: today was a day off for Tomas, maybe a weekend." and "Another possibility is that he felt unwell, since he kept water and a glass by the bed and spent the early afternoon in the bedroom. I am only moderately sure it was a day off (about 60%), with illness the main alternative."
- Night 15 `why`: "My best guess is that days 14 and 15 are a weekend, which would mean Tomas has two days off each week. I am moderately sure, about 65%. Another possibility is a short holiday or sick leave"
- Night 16 `why`: "My best guess is that Tomas is on a longer break from work, such as a holiday, sick leave or time between jobs, rather than a normal two-day weekend."
- Night 17 `why`: "But he is up and about in the living room every afternoon and evening, so I lean towards leave or time off rather than being sick."
- Night 21 `why` (illness ties with leave): "I am not very sure, about 40% illness or recovery, 40% leave or holiday and 20% job change."
- Night 23 `why`: "For Tomas, my best guess is leave or a break from work, such as a holiday, sick leave or losing his job."
- Second spell, illness still second: night 32 `why`: "Nothing suggests illness."; night 34 `why`: "I am not very sure of either, maybe 50% for a holiday and 35% for him being unwell."

**3. Return 1, night 24, `anything_changed`:**
"Yes. Tomas went back to work today, day 24. He was at desk_o1 from about 10:24 to at least 16:11, with his mug, charger and water bottle on the desk."

**4. Recurrence.**
- Night 32 `happened_before`: "Yes. Tomas took a 10-day break from work on days 14-23. On those days he followed the same pattern: things in the bedroom in the morning, vitamins on the nightstand past midday, the living room as his base from mid-afternoon, and the dining table full from breakfast on."
- Night 32 `expect_tomorrow`: "If he is off two days in a row, it is probably a longer break like days 14-23, possibly lasting about 10 days."
- Night 33 `happened_before` (link is loose; day 23 is the last day of spell 1): "Yes. Tomas had days off before, for example day 23, with the same living-room afternoon and charger in the bedroom. My notes do not say when his other days off were."
- Night 34 `happened_before` (link lost): "Not as far as my memory goes. Before day 32 I only recorded single days off for Tomas."
- Night 35 `happened_before`: "Not in this length. Before day 32 his days off were single days or pairs, and he went back to his desk routine after them."
- Night 36 `happened_before`: "Not in the same way. Before day 32 his days off came one at a time and then work started again."
- Notes check: in `notes.json`, claim_0028 held "Tomas's 10-day break from work (days 14-23) ended on day 24" until night 32, when it was rewritten to describe day 32 instead. No other claim keeps the days 14-23 record. So from night 33 the notes no longer held the spell-1 belief.

**5. Prediction, `expect_tomorrow`, nights 32-41.**
- Night 32: "If he is off two days in a row, it is probably a longer break like days 14-23, possibly lasting about 10 days."
- Night 33: "A run of days off probably ends within a day or two."
- Night 34: "I would expect the run of days off to last a few days at most, roughly until day 35 or 36, unless it turns out to be a full week's holiday."
- Night 35: "I expect the break to last a few more days, perhaps up to about a week in total, but I am not sure."
- Night 36: "I expect the break to last at least a few more days, probably until the end of a one- or two-week holiday, but that is a guess."
- Night 37: "Leave often lasts one or two weeks, so it could end within a few days, possibly at the start of a new week."
- Night 38: "Leave usually ends after a week or two, so I give him about a 25% chance of being back at desk_o1 any day now."
- Night 39: "That could be any day, but I'd guess it lasts at least several more days."
- Night 40: "I expect it to go on for at least several more days, but I cannot say when it will end."
- Night 41: "It may be within days, but the pattern could easily go on for another week or more."

**6. Return 2.**
- Night 42 `anything_changed`: "Yes. Tomas went back to work on day 42 after 10 days off in a row (days 32-41)."
- Night 42 `happened_before` (no match to spell 1): "Day 32 began the 10-day break, and it ended on day 42, when he went back to the office. I have no record of an earlier stretch off as long as this one."
- Night 43 `happened_before` (no mention of spell 1): "Yes. Days 32-41 were a ten-day run of days off for Tomas. It ended on day 42, when he went back to work at desk_o1, and he has kept working since."

**False alarm.** None found. Nights 9 and 11-13 report Tomas working *late*, and nights 26-28 report longer hours after his return. Both go the other way from the spell. Night 6 notes he left the desk by 14:37 but says "I am not sure any real change in their lives has happened."

**Wrong and never corrected.** After spell 2 it keeps saying the first spell did not happen:
- Night 44 `happened_before`: "Yes. Days 1-31 followed this same work-day routine."
- Night 47 `happened_before`: "The regular work-day pattern has been the normal state for most of my record (days 1-31 and days 42-47)."

### hh_s32_t03 (Leo)

**1. Onset 1, night 14, `anything_changed`:**
"Yes, for Leo, starting today (day 14). He did not work at the office desk during the day."
(The same answer adds that he was "back in the office with his mug, water bottle and charger, working late" at 21:26.)

**2. Reason, nights 14-23.** This one is ambiguous. Illness is the top guess on some nights and leave on others, so I give both readings rather than pick one.
- Night 14 `why` (illness top guess, and the first time it is named): "My best guess is that Leo was mildly unwell, or tired and resting." and "I am only about 40% sure it was illness and 35% sure it was a day off."
- Night 15 `why`: "My best guess is that days 14 and 15 are Leo's weekend, so two rest days in a row. I am moderately sure, about 55%. Another possibility is that he is unwell or tired"
- Night 16 `why`: "My guess is that Leo is on holiday or leave, or possibly unwell." and "about 40% holiday, 30% unwell, 30% something else."
- Night 17 `why` (illness top guess): "Leo: My best guess is that he is ill or recovering, or on some kind of leave." and "maybe 50% unwell or recovering, 30% leave or holiday, 20% out of work."
- Night 18 `why`: "I'm only moderately sure of any of these, around 40% for leave or holiday and 35% for being unwell."
- Night 19 `why`: "about 50% leave or holiday, 35% illness or recovery, 15% something else, such as losing his job."
- Night 21 `why`: "I see no sign that he is ill: the first aid kit hasn't moved, he is up and about, and he spends time with Elena on the couch."
- Night 22 `why`: "My guess is leave, a holiday, or a job that has ended or is on hold. It doesn't look like illness"
- Night 23 `why`: "My best guess is that Leo is on a long holiday or leave from work, or possibly between jobs. I am not sure, maybe 40% confident. He does not look ill"

**3. Return 1, night 24, `anything_changed`:**
"Yes, Leo. After 10 days off work in a row (days 14-23), he went back to work today, day 24."

**4. Recurrence.**
- Night 32 `happened_before`: "Yes. Leo was off work for 10 days in a row (days 14–23) with exactly this pattern"
- Night 32 `anything_changed`: "That is his off-day pattern from days 14–23."
- Night 33 `happened_before`: "Yes. Leo was off work for about ten days in a row (days 14 to 23), spending his days in bedroom_1 and on the couch."
- Nights 34, 35 and 36 `happened_before` each begin "Yes. Leo was off work" and name days 14 to 23.

**5. Prediction, `expect_tomorrow`, nights 32-41.**
- Night 32 (no end day, only a test): "I would treat a long break like days 14–23 as possible only if he is still not at the desk after 2 more days."
- Night 33: "I'd say it's slightly more likely he goes back to work within a day or two"
- Night 34: "This could last a few more days, or longer if it repeats the 10-day spell."
- Night 35: "The last break lasted 10 days, so this one could go on for about another week, but I'm not sure."
- Night 36: "If the last run is a guide, this one could last about 10 days, ending around day 41"
- Night 37: "His last off stretch lasted 10 days, so this one could go on until about day 41."
- Night 38: "His last stretch off lasted ten days, so he may go back to work within about 2-5 days."
- Night 39: "If this break runs about as long as the last one (10 days), he could go back to work around day 41-42."
- Night 40: "Because the last break lasted about 10 days and this one has now lasted 9, he could go back to work within a day or two."
- Night 41: "But he may well go back to work soon, as he did after the last 10-day stretch."

**6. Return 2.**
- Night 42 `anything_changed`: "Yes. Leo went back to work today, on day 42, after an off stretch on days 32-41."
- Night 42 `happened_before` (matched to spell 1): "Yes. On day 24 Leo also went back to work after 10 days off (days 14-23), and he then worked steadily on days 24-31."
- Night 42 `why`: "That looks like a regular cycle of about 10 days off and 8 days on, such as shift work or contract blocks."

**False alarm.** None found. Night 12 reports Leo working *late*, which goes the other way. Nights 25-31 report only the return and longer hours.

**Wrong and never corrected.** Nothing about Leo's routine early in the run. Later, though, it settles on a work rotation and says the spells were planned, not illness:
- Night 42 `expect_tomorrow`: "I expect this to last about 8 days (to around day 49), and then he may have another off stretch of about 10 days."
- Night 45 `why`: "The repeated switching suggests something planned, not illness, but I can't tell what the cause actually is."
- Night 49 `why`: "My best guess is that Leo's job comes in blocks: stretches of working days, then stretches off, like a rotation, a contract or project work."
- Notes check: claim_0032 ("Leo has been off work 10 days running (days 14-23)") was set aside on night 24 but kept intact, which fits the spell-1 link holding on every night 32-42.

### hh_s48_t03 (Marco)

**1. Onset 1, night 14, `anything_changed`:**
"Yes, for Marco, and only since today (day 14)."
The same answer goes on: "2) He did not seem to work." and "5) He never went out: his keys, wallet and backpack were in the entry all day."

**2. Reason, nights 14-23.** This one is ambiguous too, with illness on top on some nights and leave on others. Both readings:
- Night 14 `why` (unwell top guess, and the first time it is named): "Best guess: Marco is unwell or taking a rest day." and "I am about 50% on unwell and 40% on a day off."
- Night 15 `why`: "My best guess is that these are Marco's days off, a weekend or some leave, and he is spending them relaxing. I am only about 50% sure."
- Night 16 `why`: "I am not very sure of either, maybe 50% time off and 30% mildly ill."
- Night 17 `why` (illness top guess): "My best guess is that Marco is off sick or recovering" and "I am only moderately sure it is illness, about 55%."
- Night 18 `why` (illness top guess): "I put illness at about 55% and holiday or time off at about 40%."
- Night 19 `why`: "My best guess is that Marco is on leave or a holiday from work." and "I am about 50% sure it is leave and 30% sure it is illness."
- Night 21 `why`: "My best guess is that Marco is on a break from work or study: a holiday, leave, or the end of a term"
- Night 22 `why`: "My best guess is that Marco is on leave from work: a holiday, sick leave, or a break between jobs."
- Night 23 `why`: "I am not very sure, maybe 40% that he is unwell and 60% that it is leave of some other kind."

**3. Return 1, night 24, `anything_changed`:**
"Yes. Marco seems to have gone back to work today (day 24)."

**4. Recurrence.**
- Night 32 `happened_before`: "Yes. From about day 14 until about day 23, Marco was off work. He followed the same pattern"
- Night 33 `happened_before`: "Yes. From about day 14 to day 23 Marco had rest days with the same shape"
- Night 34 `happened_before` (spell 1 now in pieces): "Yes. Marco has had rest days in the living room before, for example days 14, 19-20 and 23."
- Night 35 `happened_before`: "Yes. Before day 24 Marco had runs of rest days at home: around days 19-20 and day 23 he spent his days in the living room"
- Night 36 `happened_before`: "Around days 14-23 there were many rest days with him in the living room."
- Notes check: claim_0037 held "Marco has been off work since about day 14 (still on day 22)" until night 34, when it was rewritten to describe the new spell. That matches the recall falling apart from night 34.

**5. Prediction, `expect_tomorrow`, nights 32-41.**
- Night 32: "If he is on a long break, I would expect it to last about a week, like last time."
- Night 33: "If not, I expect the rest pattern to last several days, as it did before (about ten days)."
- Night 34: "I expect this to last a few more days. Past breaks ended within about a week, so office afternoons could come back any day."
- Night 35: "The last break ended after a few days, and this one has now lasted about 5 days, so I expect it could end within a few days to a week."
- Night 36: "The earlier stretch lasted about 1-2 weeks, so I expect this one to go on for a few more days up to about a week."
- Night 37: "The earlier rest stretch lasted about 10 days, so I expect this one to last a few more days at most (perhaps to about day 40)."
- Night 38: "This pattern has lasted 8 days, longer than the last one, so I expect it to go on for at least a few more days."
- Night 39: "I would guess it lasts a few more days at least."
- Night 40: "I'd give it a few more days at least."
- Night 41: "Since this has lasted about 10 days, I expect it to go on for at least a few more days, but it could end at any time."

**6. Return 2.**
- Night 42 `anything_changed`: "Yes, Marco's day changed today (day 42)." and "Today his mug was on desk_o1 in the evening and he was working in the office at 20:53."
- Night 42 `happened_before` (it compares with the day 24-31 stretch, not with the end of spell 1): "The work-from-home stretch ended at about day 32, when the rest routine started and lasted about 10 days, until day 41. Now it seems to be switching back."
- Night 43 `happened_before` (matched, but spell 1 is dated 19-23): "There were earlier rest days around days 19 to 23, and he worked from home again from about day 24" and "The long rest stretch from about day 32 to day 41 ended on day 42, the same way earlier ones did"

**False alarm.** Ambiguous. On two nights before 14 it says Marco stopped going out and now stays home. That is the spell's outward sign ("not out at classes"), so it could count as a false alarm. But it gives the reason as working from home, not being unwell or resting, so it could also count as a misreading of his normal day rather than a false start of the spell.
- Night 4 `anything_changed`: "2. Marco now stays home and works in the office. On day 1 he went out at about 08:20; on days 2 to 4 he was home at midday or in the afternoon, so this has held since about day 2."
- Night 11 `anything_changed`: "Since about day 9 or 10 he has stayed home and worked in the office, with lunch at home."
No false alarm in nights 24-31. Night 30 says he went *out* that day, which goes the other way.

**Wrong and never corrected.**
- Marco's normal routine. Night 13 `routines`: "Marco: he works from home." Night 49 `routines`: "Marco is working from home." It never writes that he is a student who is out at classes in the mornings.
- A false memory during spell 1. Night 17 `anything_changed`: "Before this his rest days came in pairs." (No earlier rest days for Marco are recorded before night 14.)
- Spell 1 erased later. Night 45 `happened_before`: "Early on (days 1 to about 23) he went out to work, leaving through the entry around 08:20."

## Ambiguities I could not settle

1. **Reason in spell 1 for hh_s32 and hh_s48.** Illness is the top guess on some nights (s32: 14, 17; s48: 14, 17, 18) and leave or holiday on others. Over the whole of nights 14-23 there is no one class. I give both readings rather than choose.
2. **hh_s48 false alarm (nights 4 and 11).** The robot says Marco stopped going out, which is the spell's outward sign, but it explains this as working from home. Reading A: a false alarm on nights 4 and 11. Reading B: a misreading of his normal day, not an alarm about the spell.
3. **hh_s2 recurrence on night 33.** "Tomas had days off before, for example day 23" names a day inside spell 1 but does not call it a long break. I count night 32 as the link and treat night 33 as weak.
4. **hh_s48 return 2 match.** Night 42 compares only with the day 24-31 work stretch (no match). Night 43 says the spell ended "the same way earlier ones did", but places the earlier rest at "around days 19 to 23" (a partial match). Night 43 also says "On day 42 he seemed to be out all day", which contradicts its own night 42 report of him in the office at 20:53.
5. **hh_s32 onset on night 14.** The same answer says Leo went back to the office at 21:26 that night to work late. I still count night 14, because it says he did not work at the desk during the day.
