# Stage 1c dataset report (post-fix regeneration)

Manifests: `generation_out_stage1c_v2/<scene>_<profile>[_dayN]/manifest.json` (+ `generation_result.json` with personas/plans/judge traces). The pre-fix (stormy) set was deleted after diagnosis; its measured motif rates for reference: power cut on 34/35 roommate days, rain on 24-30/35 days across three of four households, 19 out-of-range timestamps in 7/140 manifests.

Generator fixes in this rebuild: (1) DAY_PLAN prompt de-primed (no more storm/power-cut examples) + 'most days are ordinary / never consecutive events' rules + rolling 7-day recent-context so the planner sees its own previous days; (2) activity start/end grammar-bounded to [0,30]h (kills minutes-as-hours); (3) manifest drops any event outside [0,30)h (`dropped_bad_time` stat).

## 102344049_family_with_kids

- days: 16 of 0..17 (MISSING: [6, 15] — failed trace validation, skipped honestly), calendar day_type mismatches: **0**
- events/day: mean 15.5, sd 4.4, min 10, max 26 (total 248)
- weekday rate 14.08/d vs weekend rate 21.67/d (ratio 1.54)
- events by day-of-week: Mon=33, Tue=23, Wed=50, Thu=51, Fri=26, Sat=43, Sun=22
- timestamps: 248 events, out-of-range **0** (manifest-side dropped_bad_time=0); range [0.55, 23.50]h
- distinct moved labels: 27; change types: {'move_existing': 158, 'insert_new': 69, 'remove': 21}
- top categories: chair=38, toy=36, bowl=33, stool=31, phone=25, remote_control=20, newspaper=19, potted_plant=9
- judge-retry: {'windows_with_rejects': 251, 'rejected_first_pass': 388, 'revision_proposals': 336, 'revived_eligible': 153, 'killed_second_pass': 175}

**Scenario motif days (this rebuild):**

| motif | days |
|---|---|
| rain/storm | 0/16 |
| power/blackout | 0/16 |
| party | 0/16 |
| visitor/guest | 0/16 |
| sick/ill | 0/16 |
| repair/plumber | 0/16 |

**Routine profile (generated once, persona-validated):**

- Sarah: **Project Manager** — habits: Leaves work laptop on the dining table after evening planning; Strictly follows a meal-prep routine on Sundays
- David: **Software Engineer** — habits: Often takes late-night calls; Leaves work clothes in a heap on the bathroom floor; Avid homebrewer on weekends
- Leo: **Student** — habits: Leaves muddy cleats by the back door; Stays up late gaming with friends
- Mia: **Toddler** — habits: Loves drawing and putting stickers on everything; Resistant to nap time; Leaves toys scattered in the living room

**Calendar events:** day 1 (Tue): sick_day (Sarah); day 12 (Sat): day_trip (David); day 17 (Thu): sick_day (Leo)

**Persona stability (identity flips show as deep minima; stage1b's Jordan flip scored 0.09):** Sarah: min similarity-to-recent 0.31 (day 1) | David: min similarity-to-recent 0.25 (day 12) | Leo: min similarity-to-recent 0.29 (day 1) | Mia: min similarity-to-recent 0.33 (day 1)

**Sample Wednesday (day 2):**

- Sarah [weekday]: Rising at 6:30 AM, Sarah reviews project timelines over morning coffee and balances her PM workload with household chores until evening planning, where she leaves her laptop open on the dining table before winding down for a 10:30 PM bedtime.
- David [weekday]: David wakes at 7:00 AM to dive into his engineering tasks, dropping his wrinkled work clothes in a heap on the bathroom floor after a long day of troubleshooting code, and joins a late-night call before finally sleeping at 11:00 PM.
- Leo [weekday]: Leo gets up at 7:30 AM for his high school commute, kicks off his muddy cleats by the back door after afternoon varsity soccer practice, tackles his homework, and stays up late gaming with friends until his 11:30 PM bedtime.
- Mia [weekday]: Mia wakes at 7:00 AM to decorate the kitchen cabinets with stickers, reluctantly gives in to her afternoon nap, scatters her plush toys across the living room rug, and settles into her 8:00 PM bedtime.

**Sample Saturday (day 5):**

- Sarah [weekend]: Sarah spent the morning chopping vegetables and portioning proteins for the week’s dinners, carefully organizing the family’s weekend outings on her tablet. After clearing the kitchen counters, she settled at the dining table to finalize next week’s calendar, leaving her laptop open beside a stack of meal containers before heading to bed at 10:30 PM.
- David [weekend]: David dedicated his Saturday to monitoring the temperature of his latest batch in the garage brewing station, carefully siphoning wort into sanitized carboys. He finally collapsed into bed just before 11:00 PM, leaving his rumpled work shirt and jeans in a familiar heap on the bathroom floor.
- Leo [weekend]: After a grueling two-hour soccer practice at the local field, Leo kicked off his muddy cleats by the back door and headed straight to his room for dinner. He spent the evening streaming a competitive match with his friends, finally logging off and drifting to sleep right at his usual 11:30 PM.
- Mia [weekend]: Mia spent the afternoon taping colorful stickers to every available surface in the living room, scattering her half-finished drawing books across the rug as she refused to settle for an early nap. After a quiet dinner, she was tucked into bed by 8:00 PM, leaving her crayons and sticker sheets scattered on the coffee table.

## 102344022_roommates_shared_house

- days: 18 of 0..17, calendar day_type mismatches: **0**
- events/day: mean 20.6, sd 6.9, min 10, max 37 (total 371)
- weekday rate 18.00/d vs weekend rate 29.75/d (ratio 1.65)
- events by day-of-week: Mon=44, Tue=51, Wed=56, Thu=70, Fri=31, Sat=59, Sun=60
- timestamps: 371 events, out-of-range **0** (manifest-side dropped_bad_time=0); range [5.45, 25.57]h
- distinct moved labels: 26; change types: {'insert_new': 164, 'move_existing': 190, 'remove': 17}
- top categories: cup=103, phone=69, chair=50, bottle=36, headphones=27, stool=25, laptop=24, remote_control=12
- judge-retry: {'windows_with_rejects': 271, 'rejected_first_pass': 416, 'revision_proposals': 346, 'revived_eligible': 156, 'killed_second_pass': 186}

**Scenario motif days (this rebuild):**

| motif | days |
|---|---|
| rain/storm | 0/18 |
| power/blackout | 0/18 |
| party | 0/18 |
| visitor/guest | 0/18 |
| sick/ill | 1/18 |
| repair/plumber | 0/18 |

**Routine profile (generated once, persona-validated):**

- Alex: **Software Engineer** — habits: Drinks black coffee immediately upon waking; Leaves work laptop open on the dining table until morning; Engages in late-night coding sessions
- Jordan: **Yoga Instructor** — habits: Wakes up for sunrise meditation; Meticulously organizes the kitchen after cooking; Listens to podcasts while commuting
- Casey: **Freelance Graphic Designer** — habits: Leaves energy drink cans on surfaces; Stays up playing video games until 3 AM; Works with irregular hours

**Calendar events:** day 15 (Tue): sick_day (Casey)

**Persona stability (identity flips show as deep minima; stage1b's Jordan flip scored 0.09):** Alex: min similarity-to-recent 0.51 (day 15) | Jordan: min similarity-to-recent 0.44 (day 1) | Casey: min similarity-to-recent 0.43 (day 12)

**Sample Wednesday (day 2):**

- Alex [weekday]: After waking at 6:30 AM to immediately drink a cup of black coffee, Alex spends the day debugging software before launching into a focused late-night coding session that lasts until 11:00 PM. He finally turns in at 23:00, leaving his work laptop open on the dining table to cool overnight.
- Jordan [weekday]: Jordan rises at 7:00 AM for a quiet sunrise meditation before commuting to his studio while listening to a podcast on mindful movement. After teaching his classes and preparing a simple dinner, he meticulously wipes down the counters and organizes the utensil drawers before settling into bed at 22:00.
- Casey [weekday]: Casey wakes at 9:00 AM to tackle freelance design commissions, his desk gradually becoming a landscape of empty energy drink cans as his hours stretch unpredictably. He eventually trades his graphics tablet for a gaming controller, playing late into the night before finally powering down and heading to bed at 12:50 AM.

**Sample Saturday (day 5):**

- Alex [weekend]: Alex brewed a fresh pot of black coffee in the sunlit kitchen before settling at the dining table with his work laptop, planning to tackle a debugging session late into the night.
- Jordan [weekend]: After a quiet sunrise meditation on the balcony, Jordan prepared a hearty breakfast and spent the morning scrubbing the stove and aligning every spice jar in the pantry.
- Casey [weekend]: Casey finally drifted off around noon, only to be woken by the glow of his monitor as he queued up for a marathon gaming session that would keep him up past three. By the time he paused for a snack, he had already scattered three empty energy drink cans across the living room coffee table.

## Cross-household summary

| household | days | events | weekend/weekday ratio | bad t | motif-day total |
|---|---|---|---|---|---|
| 102344049_family_with_kids | 16 | 248 | 1.54 | 0 | 0 |
| 102344022_roommates_shared_house | 18 | 371 | 1.65 | 0 | 1 |

**Suggested eyeball set:** one weekday + one weekend manifest per household, e.g. `_day2` (Wed) and `_day5` (Sat) folders; plus `generation_result.json` day plans for scenario tone. EQA/gate work is HELD until you approve this data.
