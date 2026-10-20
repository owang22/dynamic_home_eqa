# Lab routine simulation: does hypothesis writing beat simpler memories? (overnight 2026-10-17)

Oliver asked (01:10, 2026-10-17): run overnight a task with memory writing and hypothesis maintenance, compare
with more basic methods, using 2-3 of the six lab tasks proposed the evening before; weigh each first.

## Constraint that decides the format

The dog is off, and motion needs a person beside it. So tonight is a **simulation of the lab routine**, with the
same named places, props and daily schedule the real experiment would use. Perception is replaced by text
("under_desk_2: black backpack, cable bundle") with a 10% miss rate. The model is the local Qwen3.8-27B on
cheetah (no paid spend). The rule script each simulated lab uses is written out as a day-by-day experimenter sheet
(`scripts/seed_<k>.md`), so the same script can later be run in the real lab with the dog (task 6).

## The six tasks, weighed for tonight

| task | for | against | tonight |
|---|---|---|---|
| 1 Hidden routine | Exactly the hypothesis question: rules to find, a rule change to notice, predictions to score every day. Fully simulable. | In text, perception is perfect apart from misses, so it tests reasoning and memory only. | **Yes, the core** |
| 2 What changed since yesterday | Easiest real-lab task; tests memory accuracy. | In text it is a set difference, so it says nothing about the model; no hypotheses needed. Its value is with real pictures. | No: do it on the dog |
| 3 Where is X | The benchmark the dog will run (go2 search + robot_brain); looks-to-find is the number that matters in practice. | Shares the morning forecast with task 1, so it is not an independent test. | **Yes, same routine as 1** |
| 4 Missing or moved | Needs a hypothesis about people ("the backpack leaves on Tue/Thu"); gives a calibration score. Cheap to add: one prop, one number per forecast. | Few events per run (about 2 a week per lab). | **Yes, folded in** |
| 5 Count without double counting | Real weakness of the model. | A perception and view-merging test, not memory or hypotheses; needs pictures. | No |
| 6 Same script in sim and lab | Connects rendering work to the dog. | Needs real-lab data. | Tonight's scripts are its sim half |

So tonight runs tasks 1, 3 and 4 as **one daily routine**, which is also how the real experiment would run.

## The simulated lab

- 14 places at the dog's eye level (0.37 m): the dock by the door, under three desks, two seats, two low shelves,
  sink floor, cabinet aisle, cart tray, under the bench, corner floor, sofa. Each has fixed scenery.
- 7 props, each following one hidden rule (props and places assigned at random per lab, 10 labs):

| rule | what happens | which simple method can get it |
|---|---|---|
| weekday | place A on Mon/Wed/Fri, place B on Tue/Thu | same weekday |
| cue | place A on the day after a cleaning day (a wet-floor sign at the dock, which every patrol sees), else B | none of the simple ones |
| fixed | always place A | all |
| friday | place A on Fridays, else B | same weekday, most often (except Fridays) |
| away | out of the lab on Tue/Thu, else place A | same weekday |
| random | any of three places | none (best first look is 1 in 3) |
| rotation | A, B, C, A, ... one step per lab day | none |

- Every prop also lands somewhere random on 7% of days, and leaves the lab on 3%.
- **Rule change on day 16** (Monday of week 4, the "cleanup"): the weekday prop moves to a new pair of places and
  the fixed prop to a new place. Nothing announces it.
- 30 lab days (6 weeks, Mon-Fri; days are dated from Mon 2026-10-19).

## The day

1. **Morning forecast, before looking**: for each of the 7 props, up to 5 places in order, and the probability it
   is out of the lab today.
2. **Questions**: 3 props (drawn at random) are searched: the dog looks at the forecast places in order and stops
   when it sees the prop. Every look reports everything at that place (with 10% misses, fixed per place and day).
3. **Patrol**: the dock plus 4 other places on a fixed rotation (each place every 3-4 days).
4. **Evening**: the method updates its memory from what the dog saw today and how its forecasts did.

The method sees only what the dog saw: never the rules, unvisited places, the change day, or whether a prop
that was not found was out of the lab.

## Methods compared

| method | memory | model |
|---|---|---|
| no memory | none: common sense about labs | Qwen |
| last seen | place where each prop was last seen, then earlier places by recency | rule |
| most often | places by how often each prop was seen there | rule |
| same weekday | place seen on the most recent same weekday, then most often | rule |
| full log | every observation so far, verbatim, no writing | Qwen |
| notes | free notes it rewrites each evening; nothing else carries over | Qwen |
| hypotheses | a list of hypotheses it maintains (statement, evidence for and against, confidence, active or set aside; set aside rather than deleted) plus short notes | Qwen |
| rules known | the true rules, including the change (ceiling; not a method) | rule |

The hypotheses method is run twice on 4 labs to measure how much reruns alone differ (vLLM at temperature 0 is
not deterministic).

## Changes made before launch (01:40-02:05)

- **Thinking.** With thinking on, one call took 3-6 minutes and 11-14k tokens; the hypothesis update ran out of its
  14k budget on day 1 and fell back, while notes just fitted. So the **main run (10 labs) uses no thinking for any
  model method**, the same for all. A second run on labs 0-3 turns thinking on with a 28k budget: `notes_think`,
  `hypotheses_think` (evening) and `full_log_think` (forecast).
- **FP8 weights** (serve_qwen.sh) so that ~40 chains fit at once.
- From an independent audit: plans are exactly 5 places for every method; equal memory size (notes 8000 characters;
  hypotheses 16 x (160 + 2 x 120) + 1600 notes); a server failure stops the chain instead of saving an empty day;
  full log also gets the forecast check; looks counted only for props in the lab; "said out" split into props really
  out vs in the lab but not found; paired differences computed; the grader counts a change as noticed only when the
  memory says in words that the pattern changed (checked on three hand-written memories: noticed / silent / stale
  were graded yes / no / wrong).

- **02:35: thinking variants restarted with a thinking budget.** Unbudgeted, the *_think calls took 15-25k tokens and
  15-25 minutes each under load (one hit 28k), so 30 days would not finish. They now think up to 4000 tokens, then the
  thinking is closed ("I have to stop thinking and give the answer now.") and the answer is written under the JSON
  grammar (`llm.ask_json_budget`). The first unbudgeted days are kept in `runs_discarded/`.

## What is measured

- **First look right** (task 1): the forecast's first place, for every prop that is in the lab. By rule type and by
  period: week 1 (days 1-5), weeks 2-3 (6-15), week 4 after the change (16-20), weeks 5-6 (21-30).
- **Looks to find** (task 3): for the 3 searched props; not found within 5 counts as 6. Also found within 3.
- **Out of the lab** (task 4): Brier score of the out-of-lab probability; and, on searches that fail, whether it
  says "someone has it" (probability >= 0.5) correctly.
- **Rules written down** (notes and hypotheses only): on days 5, 10, 15, 20, 25 and 30, a grader call (Qwen,
  thinking on, given the true rules) marks each prop's rule as stated correctly, partly, wrongly, or not at all,
  and after day 16 whether the change was noticed. I read a sample of grades by hand.
- **Effect bar**: a difference counts if it exceeds 2 standard errors of the per-lab paired difference (10 labs),
  and also exceeds the rerun difference.

## Predictions written before the run

1. Same weekday will be the strongest simple method, and close to the Qwen methods on weekday, away, friday and
   fixed props.
2. Hypotheses beat notes and full log on the cue and rotation props (the ones no simple rule gets), if anything.
3. After the change, last seen recovers fastest; hypotheses and notes may hold on to the old rule for some days
   (Qwen's notes never recorded a change in the Oct 3 study).
4. Full log will be as good as notes on first looks: 30 days fit easily in its context.
5. Out-of-lab calibration: hypotheses best, last seen and most often worst.
