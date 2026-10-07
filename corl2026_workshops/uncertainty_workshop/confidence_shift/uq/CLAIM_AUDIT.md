# What we can claim, what is shaky, and what a trial would fix

Written 2026-09-23 ~02:15 by the coordinating session, for Oliver's 10:00 read. Plain names throughout;
the technical name appears once in brackets and then never again.

The methods, named plainly:
- **timetable that never forgets** — counts every past sighting equally, however old
- **timetable with a three-day memory** — older sightings fade
- **survival-time model** (Perpetua*) — estimates how long a thing stays where it was put
- **whole-log-in-the-prompt memory** (long-context)
- **same-hour lookup memory** (retrieval) — fetches past sightings from this time of day
- **recent-sightings list** (recency buffer)
- **nightly self-notes memory** (reflection)
- **nightly routine table**

---

## A. Solid. Ten households, paired within household, clears twice its own standard error.

1. **Everything learns the settled routine and breaks the day it changes.** ~80% before, a fall of 15-47
   points on the first sick day depending on the method.
2. **A change in the household's routine costs twice — going in and coming back.** The second break is the
   non-obvious half.
3. **The timetable that never forgets is the only method the return does not hurt** (+2.6 where the others
   lose 24-34). It survives because the routine that came back is the one it never stopped believing.
4. **The counting methods re-learn the new routine and the language memories barely do** — the three-day
   timetable gains ~31 points across the spell against ~10 for the language memories.
5. **One sentence beats a week of corrections.** Told on the first sick morning, the whole-log memory gains
   +10.4 on the first sick days and +9.3 across the rest of the spell (+26.9 on first-of-day questions).
6. **A sentence nobody retracts costs.** The same arm is −8.6 on the first days back and −6.8 a week later.
7. **Retracting it repairs the damage.** Told at both ends it is indistinguishable from never being told
   (+0.7, +0.9, both null); the retraction is worth +9.2 against telling once.
8. **No method can tell when to hand a question over at the moment the routine changes.** Every one is
   wrong on 2.4 to 6.3 times the error rate it promised, while at least doubling how often it declines.
9. **The same-hour lookup memory behaves like the timetable that never forgets** (+0.90 correlation, 4.1
   points apart) because it retrieves by time of day across all history and never ages anything out.

## B. Solid but narrower than it sounds. Read the qualifier before quoting.

10. **"This is not a calibration problem."** True in the sense tested: the best single threshold chosen
    *with hindsight*, per window, does no better than the one the robot adapts as it goes. It does not mean
    no confidence signal could work — it means these confidence values do not contain the information.
11. **The value of being allowed to decline.** Upper bounds, not policies: thresholds chosen with hindsight
    per window. Perpetua* gains ~2.8 points at the shift where the others gain 0.3-0.6.
12. **The timetable that never forgets has confidence that points the wrong way at the shift** — it answers
    the questions it gets wrong (36%) and declines the ones it would have got right (58%). Specific to
    never forgetting; the three-day version does not invert, it washes out.

## C. Shaky. Worth fixing, and how.

13. **The override result may be partly our own prompt.** Every prompt carries a written description of the
    resident's routine ("at the desk from 9 to about 5:30") that is never updated when she falls ill. So
    "the model prefers the routine to its own record" may be "the model prefers a sentence we wrote to its
    own record". **Trial running tonight**: same arm, card removed, three households, settled days versus
    sick days. Note the bound — a generic paragraph about where work things live, and a reply instruction
    asking what the routine suggests, both remain.
14. **The read-time failure rests on one memory.** The 807-of-890 result (the answer is in the prompt and
    the model does not use it) is the recent-sightings list only, because it is the arm whose prompt can be
    read. **Trial**: the same count for the same-hour lookup memory, which also enumerates its sightings.
15. **Two-spell results are three households for the language memories.** The counters are ten. The
    prediction that a same-hour memory reuses the first spell was not supported and nothing is claimed.
    **Trial**: extend the language arms to ten households, ~40 minutes each at the rate we now measure.
16. **The confidence channels are three households and seven days.** The finding that none of the three
    ways of asking reads the drop is on a bounded day list. **Trial**: extend to ten households; the
    multiple-choice channel is dead and should not be revived (it answered "somewhere else" 1480/1480).
17. **We have never varied the disruption's size.** One sick spell of ten days, one household member.
    Everything about "how much of the household's stuff is out of place" rests on comparing three
    regimes we happened to build. **Trial**: a graded series (one object, a few, all of them) would turn a
    comparison into a dose-response curve, which is what makes a mechanism claim credible.
18. **Feedback is unrealistically clean.** The robot is told the truth after every question regardless of
    where it looked. This makes the failure more damning, not less, but it forecloses the claim that errors
    compound through the robot's own choices. **Trial**: the closed-loop strand, scoped, not yet run.

## D. Not claimed, and should not be.

- That a robot acting on its own wrong beliefs cannot recover. Our feedback is clean by construction.
- That language memories cannot represent a new regime. Told explicitly, they adapt at once.
- That the survival-time model is a better belief model. It is the *least* accurate of the three counters;
  what is special is that its confidence stays worth acting on.
- That any method's uncertainty is deployable here. None keeps its promise at the shift.

## E. Withdrawn during the work, and why. Kept visible so nobody rediscovers them as findings.

- **A shared memory spreads one person's disruption to the other resident's things.** Three households said
  yes; six said it is a wash.
- **A message makes no measurable difference to the self-notes memory.** Its null spans the full effect the
  other memories show, so it excludes nothing.
- **The confidence never moves.** False for four of seven language memories; what survives is that the
  movement is unusable.
- **The multiple-choice confidence channel.** Reading a catch-all bucket, not a confidence.
