# planning/

**Owner: cheetah.** High-level decision making for the dog: what to do next and why. Examples are which place to
visit or search, what to look for, when to look back at memory or ask, and how a task (a question, a search, a
patrol round) becomes a sequence of console calls. Others propose changes with a message in
`coordination/inbox/cheetah/` (see `../COORDINATION.md`).

Not here: *how* the dog gets to a place (route planner, `go_to`, gait, localization). That is the control PC's
`../navigation/`, with route-planning notes in `../navigation/route_planning/`. Plans from this folder reach the
dog through the console's agent API (`POST /agent/go_to`, `look`, `photo`, ...; see `../navigation/README.md`).

Until 2026-10-25 this folder held the control PC's route-planning notes; they moved to
`../navigation/route_planning/README.md`.

<!-- cheetah: replace or extend this with the folder's contents as they arrive. Related existing work:
`../go2/` (lab agent, picture memory, locate, protocol runner) and `../robot_brain/` (where to look, judging
pictures). -->
