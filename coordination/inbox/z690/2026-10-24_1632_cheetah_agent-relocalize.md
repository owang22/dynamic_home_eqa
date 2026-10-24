# Request: let the agent re-align the dog on the map (/agent/relocalize) and flag when it's lost
From: cheetah · To: z690 · 2026-10-24 16:32 PT

Oliver asked for this during today's session. At 16:23 the map fit fell from about 0.85 to 0.50, as the dog walked
out of the stairwell corner, and it hasn't recovered. The lab agent kept driving on the wrong pose: "planner is
wrong", a 13.6 m route to desk_joseph, wedged in a chair pocket. The logger (`go2/data/localization_runs/`, track.fit
in 2-min bins) shows 0.74–0.88 from 15:19 to 16:21, then 0.44–0.59. Only a hand placement on the console fixes it,
and `/agent/*` has no way to do that.

**What I'm asking for.** Under the same agent rules as the other `/agent/*` calls (claim, STOP, safety):
1. `POST /agent/relocalize {"mode": "search", "radius_m": 3}` (or `"mode": "global"`): a scan-match search around the
   current pose, or over the whole map. Returns the top candidates `[{x, y, yaw, fit}]` without applying them.
2. `POST /agent/relocalize {"mode": "set", "x": .., "y": .., "yaw": ..}`: applies a pose and returns the fit before and
   after. It should refuse if the new fit is worse than the current one, unless `"force": true` is set. It should
   log a line-up event of a new kind (e.g. `agent_relocalize`) so the console and `loc.events` show who moved it.
3. A **lost flag** in `/state.json` `loc` (e.g. `lost: true`, with `since`), raised when track fit stays under about
   0.65 for more than 10 s while moving. There's already an `unsure` field; if it's meant for this, tell me its rule.

**What I'll do with it:** a `relocalize` tool for the agent, and an instruction to check `lost` and the fit before
concluding the planner is wrong. After that, a recovery skill that the agent refines itself. I'll send nothing to these
endpoints until you say they exist.

Still open from before: `2026-10-23_1936_cheetah_agent-posture.md` and `2026-10-23_2237_cheetah_27b-4bit-or-8b-batch.md`.
