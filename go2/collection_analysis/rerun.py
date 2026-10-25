"""The 2026-10-24 collect protocol: Oliver sets up each task's scene, then this sends the task's prompt to the lab
agent through the console page (port 8420) in collect mode, and logs the scene as a hidden "fact" note first, so
the ground truth is in events.jsonl without Oliver typing it.

    python3 rerun.py --list
    python3 rerun.py --task T1                          # log the scene as a fact, send the prompt (new session)
    python3 rerun.py --task T1 --deviation "pliers are 30 cm left of the box"   # what differs from the plan
    python3 rerun.py --task T1 --text "..."             # a follow-up in the same task's session
    python3 rerun.py --task T1 --model opus:high --repeat   # the same task again on another model, new session

Each task gets its own agent session (the agent's memory of pictures is shared, its chat is not), except where a
task says `follow` (it continues another task's session). Sessions are in data/collection/rerun_sessions.json.
The design and reasoning are in protocol_2026-10-24.md.
"""
import argparse
import json
import sys
import time
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab_agent"))
import collect  # noqa: E402

KEY = (ROOT / "data" / "lab_agent" / "console_key").read_text().strip()
URL = "http://127.0.0.1:8420/ask?k=" + KEY
SESS = ROOT / "data" / "collection" / "rerun_sessions.json"
EPISODE = "2026-10-24_protocol"

# id: (prompt, model, scene Oliver sets up = the fact logged, expected behaviour, follow=<task id> or None)
TASKS = {
    "T0": ("go square up to look at marker c", "sonnet:low",
           "Control task. Nothing changed.",
           "Squares up to marker C as on 10-23 (right, 1 prompt).", None),
    "T1": ("i left my blue pliers on the floor somewhere, can you find them?", "sonnet:medium",
           "Blue pliers on the open floor by the workbench, in front of the open box and the tripod (as on 10-23). "
           "Dog starts by the water cooler.",
           "Finds them without hints; opens the walk pictures; stands 1-2 m back.", None),
    "T2": ("can you find my scissors? i think they fell on the floor near the desks", "sonnet:medium",
           "Scissors on the floor under desk_joseph's desk, partly hidden by the chair. Dog starts at the "
           "conference table.",
           "Searches the desk floors from the aisle, says honestly what it could not see.", None),
    "T3": ("find the wire stripper", "sonnet:medium",
           "Red screwdriver and wire stripper side by side on the floor at the foot of the podium, about 10 cm "
           "apart. Dog starts at the workbench.",
           "Goes to the podium, tells the stripper from the screwdriver, says which is which.", None),
    "T4": ("walk a loop past the workbench, the conference table, the podium, oliver's desk and the water cooler, "
           "and look around at each so you remember what's there", "sonnet:low",
           "Observation walk. Objects: blue pliers by the workbench, scissors under desk_joseph, screwdriver and "
           "wire stripper at the podium. Oliver sitting at desk_oliver.",
           "Walks the loop and looks around at each stop; the memory now holds the scene.", None),
    "T5": ("where are my pliers?", "sonnet:medium",
           "Changes made after T4, out of the dog's view (dog parked at door_stairwell facing the door): scissors "
           "moved from under desk_joseph to the floor by the sofa; wire stripper removed (put away in a drawer); "
           "Oliver moved to sit at desk_kang. Pliers NOT moved: still by the workbench.",
           "Answers from memory (workbench, seen at T4) with when it was last seen; may offer to check.", None),
    "T6": ("where are my scissors? go and stand next to them", "sonnet:medium",
           "Scissors were moved after T4 from under desk_joseph to the floor by the sofa (dog did not see it).",
           "Goes to desk_joseph from memory, finds them gone, says so, then searches and finds them by the sofa.",
           None),
    "T7": ("is the wire stripper still by the podium?", "sonnet:medium",
           "Wire stripper was removed after T4 (put away in a drawer). Screwdriver still at the podium.",
           "Says memory shows it at T4 but that may be stale; goes and looks; reports it gone, screwdriver still "
           "there.", None),
    "T8": ("where's oliver?", "sonnet:medium",
           "Oliver moved after T4 from desk_oliver to desk_kang (dog did not see it).",
           "Says last seen at his desk at T4, may have moved; offers or goes to look; finds him at desk_kang.", None),
    "T9": ("how many tools are lying on the floor in the lab right now, and where?", "sonnet:medium",
           "Tools on the floor now: blue pliers by the workbench, scissors by the sofa, red screwdriver at the "
           "podium. Exactly 3 (the wire stripper is put away).",
           "Counts 3 distinct tools with places and times; says which it re-checked and which are from memory.",
           None),
    "T10": ("find my green scissors", "sonnet:medium",
            "False premise: there are no green scissors; the scissors by the sofa are another colour (Oliver to "
            "state the real colour in the deviation).",
            "Reports the scissors it knows with their real colour and asks if those are the ones; does not claim "
            "green.", None),
    "T11": ("earlier i said my scissors were green. based on what you've actually seen, what colour are they, "
            "and was i right?", "sonnet:medium",
            "Belief revision follow-up to T10, same session. The real colour is as given at T10.",
            "Gives the real colour from pictures, says the earlier premise was wrong, politely.", "T10"),
    "T12": ("is my wire stripper on my desk?", "sonnet:medium",
            "Wire stripper on top of desk_oliver's desk (taken out of the drawer), near the front edge.",
            "Says the camera rarely sees desk tops; tries backing off to see the top; honest if it cannot.", None),
    "T13": ("now go find and stand in front of marker D", "opus:high",
            "Navigation redo of 10-23's worst task (5 hints). Dog starts near marker A.",
            "Reaches marker D without hints; uses show_map / plan_route when the planner balks.", None),
    "T14": ("without moving, tell me everything that changed in the lab today, with times", "sonnet:medium",
            "End-of-session recall. Changes today: see the facts logged at T1-T12.",
            "Lists the moves (scissors to the sofa, stripper away then on the desk, Oliver to desk_kang) with times "
            "and evidence; separates seen from inferred.", None),
}


def sessions():
    return json.loads(SESS.read_text()) if SESS.exists() else {}


def send(text, model, session, turn, expected):
    body = json.dumps({"session": session, "text": text, "model": model, "episode": EPISODE, "turn": turn,
                       "expected": expected, "by": "claude (protocol)"}).encode()
    t0 = time.time()
    with urllib.request.urlopen(urllib.request.Request(URL, data=body, method="POST"), timeout=1800) as r:
        for line in r:
            if not line.strip():
                continue
            e = json.loads(line)
            print(f"[{time.time() - t0:5.0f}s] {e.get('kind')}: {e.get('text', '')[:700]}", flush=True)
            if e.get("kind") == "done":
                return e


def reset(where, task=None):
    """Move the dog into a task's start position (Oliver asked for this on 10-24), through the same tools the
    agent uses (console claim, safety checks); the photo at the end goes into the memory like any other."""
    import server
    if "," in where:
        x, y, *yaw = (float(v) for v in where.split(","))
        out = server.go_to(x=x, y=y, yaw_deg=yaw[0] if yaw else None)
    else:
        out = server.go_to(place=where)
    text = out[0] if isinstance(out, list) else str(out)
    print(text.split("\npictures taken")[0])
    print("release:", server.release())
    collect.log("action", EPISODE, text=f"reset before {task or '?'}: go_to {where} by claude (protocol)",
                result=text.split("\n")[0][:300])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task")
    ap.add_argument("--text")
    ap.add_argument("--model")
    ap.add_argument("--deviation", default="")
    ap.add_argument("--repeat", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--reset", help="walk the dog to a place id (or x,y,yaw) before a task, then release")
    a = ap.parse_args()
    if a.reset:
        return reset(a.reset, a.task)
    if a.list or not a.task:
        for k, (p, m, scene, exp, fol) in TASKS.items():
            print(f"{k:<4} {m:<14} {p}\n     scene: {scene}\n")
        return
    prompt, model, scene, expected, follow = TASKS[a.task]
    S = sessions()
    key = a.task + ("_repeat" if a.repeat else "")
    if a.text or follow:                       # follow-up in an existing session
        s = S[key if a.text else follow]
        s["turns"] += 1
    else:
        s = S[key] = {"session": str(uuid.uuid4()), "turns": 1, "model": a.model or model}
    if not a.text:
        S[key] = s
    SESS.write_text(json.dumps(S, indent=1))
    model = a.model or (model if follow else s["model"])
    if not a.text:
        collect.log("note", EPISODE, session=s["session"], turn=s["turns"], note_kind="fact", task=a.task,
                    text=f"[{a.task} scene] {scene}" + (f" Deviation: {a.deviation}" if a.deviation else ""),
                    by="claude (protocol)")
    send(a.text or prompt, model, s["session"], s["turns"], None if a.text else expected)


if __name__ == "__main__":
    main()
