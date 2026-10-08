# Brief: household generator with roleplaying residents (as given, 2026-10-07)

Build `src/lived_home`: a generator where LLM agents roleplay the residents of a home over many days, and every object moves only because a resident carried it. A working draft is in `examples/lived_home_draft/`. Read it first, keep what works, change what this brief says.

## Keep from the draft

- The world engine holds the truth. Every object is in exactly one spot: a place, a hand (two hands per person), or a pocket. A resident who leaves the house takes what they hold.
- Residents act through a small action set: go, pick up, put down, pocket, give, do (minutes), say, leave home. The engine rejects impossible actions and returns what the resident sees instead, and the resident replans.
- Each resident sees only the room they are in and keeps their own memory of where things were last seen.
- Calls per resident: one plan per morning, one call per activity. Both residents act in time order, one action at a time.
- Every response opens with free text written in character, before any structured field.
- A director schedules situations (one-off, recurring, lasting) and small disturbances, with a variation knob from 0 to 1. The schedule is saved as ground truth.
- Residents have object habits, response habits ("when stressed, I take a walk") with a stated frequency, and scheduled stressors. Each activity call reports stress, tiredness, mood and health (0 to 3) and the response habit followed, if any.
- Situation text describes what the person experiences, never what to do with objects.
- Reuse `HostedOpenAIClient` and `ResponseCache` from `dynamic_home_eqa.generation`. Cache key: hash of model, effort, stage, prompt and schema.

## Change

**Objects are physical things first.**
- Each object has a type (mug), attributes (color, material, size, pattern, condition) and an optional owner.
- Ids describe the object: `mug_red_ceramic`, `mug_white_chipped`.
- Many types have several instances: 4 to 8 mugs, 3 chargers, 2 pairs of reading glasses.
- Target 150 to 300 objects per household.
- Ownership is used only where people would use it, such as "Ben's work laptop".

**Many more places.**
- Generate the layout per household with the LLM: rooms, furniture, and the spots on and in each piece (each shelf of a bookshelf, each drawer, the left and right ends of a counter, under the bed, the couch cushions).
- Target 100 to 200 places. Each place is a surface or a closed container.
- Each place gets 2 to 4 plain descriptions a person might use ("the counter by the stove", "next to the kettle", "left of the sink").
- Keep the draft's hand-written layout as a fallback for tests.

**Positions can be relative.**
- `put_down` takes an optional relation (on, in, under, behind, next to, on top of) and an optional reference object, such as "on top of the stack of books" or "behind the toaster".
- Store this in the truth.
- Mark each position as visible or hidden from someone standing in the room: under, behind, and inside closed containers count as hidden.

**Prompt size.**
- With hundreds of objects and places, a resident's memory view lists only what matters right now: what they hold, what they touched or saw in the last 2 days, their owned items, and anything their current activity needs.
- The room view lists only non-empty places.
- OpenAI strict schemas allow at most 1000 enum values in total. If the object and place enums don't fit, use plain string ids and check them in code.

**Household creation.** Split it into several calls (layout, residents, objects per room, situations) if a single response gets too long. Check references between calls in code, and retry with the problem named.

**Format fallback.** If structured output makes the roleplay stiff, add a second call with reasoning effort none that only converts the free-text answer into the action schema. Decide from the pilot samples.

## Model and runs

- Effort medium.
- First run household creation only, then 7 days with `gpt-5.6-luna`, with the "sick" situation forced on days 3 to 5.
- Stop and report before running `gpt-5.6-terra` on the same settings.
- Raise `HOSTED_SPEND_CAP` before Terra.

## Report after the Luna pilot

Extend `read_pilot.py` and report:

1. Cost, calls, and the rate of rejected actions.
2. Per object type: how many instances moved, and where each instance ended each day. Learnable objects end up in a few places, not one and not many.
3. Per response habit: how often its trigger occurred and how often the habit followed.
4. How the sick days differ from normal days: which objects, rooms and times changed, for both residents.
5. Ten excerpts from `replay.md`: five that look lifelike and five that look wrong (teleport-like moves, forgotten habits, implausible routines, objects put in odd places with no reason).

## Not in scope yet

The robot, questions, the headroom table, the human-play page, rendering.
