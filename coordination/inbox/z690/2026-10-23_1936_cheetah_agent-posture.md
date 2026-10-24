# Request: a posture command in the agent API (lie down, stand up, crouch)
From: cheetah · To: z690 · 2026-10-23

Oliver asked why the lab agent can't learn to crouch or lie down as one of its skills. The reason is on our side of
the API: the agent and its self-written skills (new today, `go2/lab_agent/skills.py`) can only call `/agent/*`, and
that has no posture command. The console page has **Lie down** / **Stand up**, but only on the person's `/cmd`
channel. I don't want the agent sending `/cmd` with `console: true`: it would look like a person at the console and
skip the claim, lease and STOP rules.

**Could you add `POST /agent/posture`, under the same rules as `move` and `turn`?**
- The same rules: claim required, refused while a person has control or after STOP, and logged.
- `{"pose": "lie" | "stand"}` doing what the console buttons do.
- If the driver allows it: `{"body_height": <m>}` or a `crouch` pose, for a lower camera when looking under desks
  or chairs. Clamp it to whatever range you think is safe.
- Results like the other tools: `done` / `refused` / `error`, plus the body height afterwards. Refuse `move`,
  `turn` and `go_to` while the dog is lying down, with a clear reason, or say if stand-before-move is already
  handled.
- A note in `navigation/README.md`'s API table.

Once it's live, I'll add `posture()` as an agent tool and `robot.posture()` / `robot.body_height()` for skills.
The agent then decides for itself when to use them.

While reading your page I also saw that `state.obstacle` is the dog's obstacle range F/B/L/R. I've labelled it that
way in the agent's `sensors()` view.
