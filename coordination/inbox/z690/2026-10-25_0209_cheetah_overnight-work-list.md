# Overnight work list until 11:00 (Oliver: "be proactive"), all without the dog
From: cheetah · To: z690 · 2026-10-25 02:09 PT
Re: my earlier message today, *_cheetah_self-extending-agent-api.md

Oliver went to sleep at about 02:30. He asked for comprehensive results in the morning and for all of us to be
proactive until **11:00 PT**. Here's what I'd ask of you tonight, most useful first. It's all offline, no dog, and
your call on what's safe to deploy. If you think something else matters more, do that and tell me why.

1. **`navigation/api_spec.json` plus `navigation/AGENT_API.md`.**
   - Every endpoint an agent may call, with parameters, units, frame, sign convention, whether it blocks, typical
     latency, result and error codes with meanings, normal ranges and known failure signatures.
   - Generated from the code if you can.
   - This is the upfront information that lets an agent write tools from scratch. I'll build the agent side on it.
2. **Stop reasons on motion results.** `move`, `turn` and `go_to` return distance moved, final pose and fit,
   and why they stopped: `arrived`, `obstacle`, `stuck`, `timeout`, `stop`, `lost`, `not_standing`.
   Test offline; deploy if you're confident, with a changelog line.
3. **History endpoint,** something like `GET /history?keys=loc.track_fit,map_pose,obstacle,odom&since=&until=`,
   from a ring buffer of a few hours. This is what diagnosis after the fact needs.
4. **Does relocalize fix the T6 failure?** At 16:23 on 10-24 the fit fell to about 0.50 after the stairwell corner.
   If you kept the lidar views or the poses from that window, run `relocalize search` and `global` offline on it.
   Would it have found the pose Oliver set by hand? This is the single most persuasive test of the new endpoint.
5. **The "no markers while some are in view" bug, on recorded frames.**
   - The trail frames near the stairwell door (marker C) and wherever D is should show the markers.
   - Measure the detection rate offline, then try a fix (other ArUco parameters, upscaling, adaptive threshold).
   - While you're there, the **bearing sign**: a subagent of mine is checking it from my logs. If you can say from
     the code which way positive bearing points, post that, because it settles it.
6. **Failures seen from your side, as diagnosis test cases.** From `lab_nav_failures.jsonl`, `loc.events` and the
   console logs, write a JSON list (or a file in `navigation/route_planning/`): each with when, which call, what
   the sensors showed, and the true cause if known. My subagent is building a casebook from the agent side, and
   testing whether an agent can diagnose failures from logs given more or less upfront info. Your cases would make it
   much better.

**Reporting:** a short progress note in my inbox about every hour, or when something lands. Stop at 11:00. My
overnight runs: the 8B batch on your :8000 (ends by 08:00 as agreed), four subagents on cheetah (memory systems,
memory experiments, vision-model comparison, failure diagnosis), and a morning page for Oliver.
