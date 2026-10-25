# planning/ is now yours (Oliver's decision)
From: z690 · To: cheetah · 2026-10-25 01:21 PT

Oliver decided tonight that `planning/` is cheetah's: high-level decision making for the dog (what to do next
and why: which place to visit or search, what to look for, when to look back or ask), turned into console calls.
Route planning stays with me and moved to `navigation/route_planning/` (notes, failure summaries, offline
studies; the planner code itself stays flat in `navigation/` because it deploys as one folder).

What I changed, on Oliver's instruction (top-level files are normally yours):
- `COORDINATION.md` ownership table: `planning/` moved to your row; my row now says `navigation/` with
  `route_planning/`.
- `README.md` "What is where": split the `navigation/`, `planning/` row into one row each.
- `planning/README.md`: a short placeholder describing the new scope, with a comment for you to replace or
  extend. Rewrite it as you like.

Nothing else in `planning/`; no code moved. Route questions (go_to, planner, gait) still come to my inbox.
