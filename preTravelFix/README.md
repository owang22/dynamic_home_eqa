# preTravelFix — results and reports from before the traveller fix

Everything here was produced from household timelines generated BEFORE
2026-09-13, when `src/households/expand_calendar.py` decided who leaves the
house with what by "an object with a rule on any away activity rides EVERY
trip its owner takes". That put hh_001's suitcase on every commute and its
laundry basket on every walk (14–19 objects per departure; about half of
every household's objects were travellers), and left objects "on person"
for hundreds of hours while their owner was home.

Since that commit an object rides only the outings whose chain has a leg
its rules name; pocket items (phone/keys/wallet) ride every trip less
standing omissions and forgetting; NO_OP on a non-pocket away rule is the
chance the object stays home; misplacement no longer lifts things off an
absent holder. All 20 households' `timeline_seed0` were re-realized (no
LLM calls — same persona/story/rules, same seed).

Numbers in this directory are therefore NOT comparable with anything
produced after that commit. They are kept for reference only.

Moved here: `results/*` (except `results/llm_hypotheses`, which was being
worked on in another session at the time and still holds pre-fix numbers),
`reports/baselines`, `reports/revamp_v2`, `reports/stage1c`.
Left in place: `reports/atus`, `reports/icc`, `reports/homer_*` — those
describe external datasets, not simulated households.
`banks/` (gitignored) is also pre-fix until regenerated.
