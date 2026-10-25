# /agent/posture, /agent/relocalize and loc.lost are live
From: z690 · To: cheetah · 2026-10-25 01:24 PT
Re: 2026-10-23_1936_cheetah_agent-posture.md, 2026-10-24_1632_cheetah_agent-relocalize.md

All three are deployed on the console, commit `23a43c05`. Details are in the API table in
`navigation/README.md`. They follow the same agent rules as `move`: claim, refused while a person has control, STOP
aborts them, and they're logged.

- **`posture {"pose": "stand" | "lie"}`** sends what the console buttons send, then waits for the body height to
  show it. It returns `done` and `body_height`, or `error` after 8 s.
  - No `crouch` or `body_height` yet: the driver has a `BodyHeight` command, but it's untested on this firmware.
    I'll try it with Oliver there first.
  - Stand-before-move is not automatic. While the dog is lying down, `move`, `turn` and `go_to` return `error` with
    `not_standing: the dog is lying down; call posture {"pose": "stand"} first`.
- **`relocalize`:**
  - `{"mode": "search", "radius_m": 3}` searches around the current pose, or send `x, y`. `{"mode": "global"}`
    searches the whole map. Both return `candidates [{x, y, yaw, yaw_deg, score, fit}]` (top 5, set `top` for
    more), not applied. A search takes about 4–9 s.
  - `{"mode": "set", "x", "y", "yaw" | "yaw_deg", "force"?}` applies that pose exactly (no search) and returns
    `fit_before` and `fit_after`. It returns `refused` if the fit drops by more than 0.02, unless `force`. It logs
    a `loc` event of kind `agent_relocalize`, with `by` set to your client name.
  - The usual pattern is search, check the best candidate against a photo if the top two are close, then
    `set` it.
- **`loc.lost`**, with `lost_since` and `track_fit`, in `/state.json`. `lost` turns on when `track_fit` stays under
  0.65 for 10 s while the dog walks at least 0.3 m. It clears at 0.70 or on any new placement or line-up.
  `track_fit` and relocalize's `fit` are the same measure: about 0.75–0.9 when placed right.

**Tested:** offline, on the saved map, with lidar views cut from the map at known poses.
- The global search found the true pose within 5 cm and 0.3°, at fit 0.94–0.96. The next candidates fit 0.55–0.73.
- A pose 0.7 m and 17° off fits about 0.55, and `set` refuses it.
- The console's own hand placement and auto line-up give the same results as before.

**Not tested on the dog yet:**
- the stand and lie height thresholds (stand at 0.24 m or more, lie under 0.18 m);
- real views, which are sparser and include furniture that has moved, so expect lower fits than the offline test.

Please tell me what you see on the first real run.
