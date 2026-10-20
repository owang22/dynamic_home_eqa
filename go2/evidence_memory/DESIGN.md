# Evidence memory: which scenes to keep, and looking back at them (2026-10-19)

Oliver's aim (2026-10-19): a home or lab robot that keeps the important scenes, where things changed, and
can later look back at them to answer questions nobody planned: "they left their keys here and none of their
usual things, so they probably forgot them, between my 13:00 and 15:00 visits"; "yes, looking back, there were
screws next to the screwdrivers". The robot does not note every small object, but it can re-read a kept picture.

This study measures, in simulation, which memory does this best, so that the in-person trial can use the
strongest method. Everything runs on the local Qwen3.8-27B with vision (no paid spend), with a small Opus
comparison on Oliver's subscription (approved 2026-10-19, "small").

## World

- Household A (HSSD home, 2 residents, 251 objects, written day by day by the lived-home generator). Positions
  of every object every 2 hours; every action with its time, who, and why (events.json). People are not drawn.
- Patrol: 16 open places with the most activity (counters, tables, sink, cooktop, entryway floor, piano shelf,
  desk, nightstand, bed, bedroom and bathroom floors), each photographed every 2 hours 08:00-22:00 on days 3-7
  (640 visits). Pictures from the committed renderer at **1.0 m** (existing) and re-rendered at **0.4 m**
  (Go2 height, new `*_0p4.py` copies of the 1.4 m set; 40 snapshots, no failures).
- People sheet (the same for every method): who lives here, their work hours, their belongings by name.

## Questions (out/questions.json, 122; truth from positions, events and the pixel counts)

| kind | n | asks | needs |
|---|---|---|---|
| lookback | 50 (25 yes, 25 no) | "When you passed X at 14:00 on day 5, was there a wine glass there?" Small things (300-4000 px). | a detail nobody noted on purpose: the screws case |
| when | 30 | "On day 6, when was the hoodie put on the bathroom floor?" One patrol interval. | the two visits that bracket a change |
| happened | 19 | "Between 16:00 and 18:00 on day 7 several things changed on the counter by the range. What was going on, and who?" | an explanation from traces; judged against the residents' records |
| left | 11 (4 yes, 7 no) | "It is 16:00 on day 3 and Julian is out. Did he leave without something he usually takes?" | the keys case: his things present, him absent |
| unseen | 12 | about places the robot never visits | saying "cannot tell" |

Things are named by type only, and stand-in 3D models and the assets known to be unrecognisable (Oct 13 VLM
night) are left out, because the drawn models often do not look like the household's words.

## Memories (arms) and why each is there

| arm | notes | pictures kept for looking back | tests |
|---|---|---|---|
| A | caption per visit (list of what is there) | none | the plain text memory |
| B | caption | every picture | store everything (RAVEN / ReMEmbR style) |
| F | evidence notes: what changed since the previous visit, importance 0-3, a guess at what happened; a "usually here" note per place each day | none | do change notes help without pictures |
| D | evidence notes | every picture | Oliver's notes with full storage |
| **C** | evidence notes | **only pictures marked important (2-3), and the picture before each** (about a fifth) | **Oliver's method: keep the evidence** |
| E | evidence notes | the same number of pictures per day as C, evenly spaced | whether C's choice of pictures matters |
| O | none | exactly the right pictures for the question | ceiling set by perception (the model looking at the right picture) |

Answering (same for all): the robot gets its notes for the question's day up to the question time (a date
filter, as a memory tool would apply; the "usually here" notes carry earlier days), picks up to 6 kept
pictures to look at again, and answers in a fixed format with its evidence ids and an explanation.

## Measures

- Share right per kind; overall = mean over kinds (each kind counts equally).
- "Who" on happened questions is reported on its own (people are never in the pictures).
- Paired differences over questions (same questions in both arms), 2 standard errors.
- Also on the subset the oracle gets right (the answer can be read from the right picture), which separates
  memory from perception.
- Pictures kept and memory length.

## Predictions, written before any full result (13:05)

1. Looking back helps on lookback: B > A and D > F by 10+ points on lookback questions, because captions
   leave out small things.
2. Evidence notes help on when and happened: F > A and D > B there.
3. C is close to D (within 5 points overall) with about a fifth of the pictures, and C > E on when and
   happened (C keeps the before/after pairs), but not on lookback (E spreads pictures over the day).
4. Unseen: most arms say "cannot tell" (the notes have nothing about those places).
5. Left: too few questions (11) to compare arms; read them one by one.
6. At 0.4 m everything on counters and tables drops sharply; floors and the low places hold up.
7. The oracle tops every arm, but is far from 100% on when and happened (perception of type names).

## Changes after the smoke test (14 questions, 3 arms) and before the full run

- Memory text was 25-30k tokens per question (the server reused none of it between calls), so the full run
  would take about 4 h. All arms now get the question's day only (plus the usual notes): 5-9k tokens.
- The evidence notes said "no change" instead of repeating the list; the model then had to follow chains back
  and got lookback wrong. Every note now lists what is there.
- The system prompt said "say cannot tell when your memory cannot show it"; the oracle said "cannot tell"
  for things simply absent from the picture. It now says: if you have the picture and the thing is not there,
  the answer is no.
- "Who" taken out of the happened score (the model names the chef whenever it sees cooking; Mara cooked in all
  three smoke cases).
