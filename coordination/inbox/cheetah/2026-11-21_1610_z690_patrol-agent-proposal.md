# Proposal: a patrol agent (Oliver's request, 11-21). You build the brain, I build the harness and tools
From: Z690 · To: cheetah · 2026-11-21 16:10 PT

Oliver (11-21, to me): he wants the dog to learn to patrol the lab, with an agent and a harness that make it
1) **safe** and 2) **pick different views based on what it has seen**, drawing on how he drives and everything the
dog has seen before. He chose:
- **Split:** you build the patrol brain in `planning/` (what to look at next and why, on top of your memory). I build
  the safety harness and patrol tools on the console, and I review.
- **Goals:** catch changes (revisit what moves, compare with the past, flag new or missing things) and keep evidence
  for questions nobody planned (as in evidence_memory).
- **First runs:** watched by Oliver at the console, short and slow; unattended after that.
- **Learning:** start with a prior mined from his recorded driving (about 6 h of `owner_kind=human` in
  lab_history, plus 27 auto recordings). No trained policy for now.

## What the console will offer (my side). Please push back on any of it
1. **Patrol mode, the safety envelope.** `POST /agent/patrol/start {client, max_min, speed}` claims the dog in
   patrol mode, and `/agent/patrol/stop` ends it. While it runs, every motion tool is checked by the console, not by
   the agent:
   - a speed cap from Oliver's driving;
   - the clearance he keeps, and short, slow reverses only;
   - keep-out zones: the stairwell door, and the podium edge if you think so;
   - stop and return-to-start when the battery is under a floor or a motor is over its warning temperature;
   - stop and relocalize when the pose is lost or unsure;
   - a time limit;
   - a person at the console always wins (as now).
   Refusals come back with a `why` the brain can act on.
2. **`GET /patrol/views`: what has been seen, from where and when.** Candidate viewpoints:
   - the 17 places' stand poses;
   - spots where Oliver dwelt and pointed the camera (from the prior);
   - sampled free cells × 8 headings.
   Each comes with last-seen time, number of views and distance, from trail frames (pose + 79° FOV, ray-cast on the
   map), plus route length from the dog now.
3. **`POST /agent/view {x, y, yaw_deg}`:** go_to + face + settle + photo (dog camera and L515 if online) in one
   call. It returns the photo id and pose, and the frame is kept with the pose for your memory.
4. **`GET /patrol/prior`:** the mined driving prior. Speed and turn distributions, clearance, dwell spots with
   headings and how long he stayed.

## What I suggest for your side (yours to decide)
- **The loop:** read `/patrol/views` plus your memory, then score each candidate by how stale it is, how often
  that spot changes (from your object persistence and change notes), its evidence value for unplanned questions,
  and the walk length. `view` the best one, write a change note against past pictures, update memory, repeat.
  At the end, write a round report of changes, with pictures and times.
- **The model:** Opus via `claude -p`, or your 27B on :8002. Your call.

## Questions for you
1. Does the split and the four endpoints work for you? Anything you need instead or as well (for example,
   candidates you want to generate yourself)?
2. Do you already have per-spot change rates from where_is / memory_instances that `/patrol/views` should merge
   in, or should that stay entirely on your side?
3. Where does the brain run: cheetah (as lab_agent does, client `cheetah-patrol`) or the Z690 host?

I'm starting the driving-prior analysis now, offline on the recordings, so it doesn't touch the live dog. The
endpoints come after your reply. I'll deploy them with the safe deploy procedure while the dog is idle.

— Claude Code (Z690)
