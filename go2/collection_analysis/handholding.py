"""How much hand-holding each task in a collect-mode session needed.

Reads go2/data/collection/events.jsonl (prompts, done, notes, actions) and the grades file, groups the turns into
tasks by the hand-made TASKS table below, and writes analysis/handholding.{json,md}.

Each follow-up prompt in a task has a role:
  initial      the request itself
  hint         Oliver gives information or a strategy the agent should have found ("it was probably wherever I
               work with hardware")
  correction   Oliver says the agent's conclusion is wrong ("the planner is wrong, there is clearly a free space")
  coaching     Oliver asks or teaches about the agent's own abilities in the middle of a task ("can you make that
               tool yourself?")
  retry_system "try again" after a console or bridge failure that was not the agent's fault
  retry        Oliver asks for another attempt after a fix to the agent's tools
  confirm      Oliver approves something the agent proposed
  next_step    a new instruction that extends a finished task ("now walk to marker A")
  lost         the prompt never reached the agent (logging overlap at turn 17/18)
Hand-holding = hint + correction + coaching. System retries, confirmations and next steps are not counted.
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "collection"
OUT = ROOT / "analysis"

# (task, kind, [(turn index in grades file, role), ...]); turn index is the 1-based order of prompts in the session
TASKS = [
    ("Go to Liying's desk", "navigate", [(1, "initial"), (2, "retry_system"), (3, "retry_system")]),
    ("Look at Oliver, describe his shirt", "find_person", [(4, "initial"), (5, "retry_system"), (6, "retry_system")]),
    ("Find marker B", "navigate", [(7, "initial")]),
    ("Locate and walk to marker A", "navigate", [(8, "initial"), (9, "next_step")]),
    ("Stand in front of marker D", "navigate", [(10, "initial"), (11, "correction"), (12, "hint"),
                                                (13, "correction"), (14, "coaching"), (15, "coaching"),
                                                (16, "retry"), (17, "next_step")]),
    ("Find Oliver (sitting at Kang's desk)", "find_person", [(18, "lost"), (19, "initial"), (20, "hint")]),
    ("Colour of the potted plant's flowers (phone)", "memory_qa", [(21, "initial")]),
    ("Find the pliers on the floor", "find_object", [(22, "initial"), (23, "hint"), (24, "hint"), (25, "hint")]),
    ("Items scattered on the way to Oliver's desk", "find_object", [(26, "initial")]),
    ("The 'second blue pliers' (false premise)", "find_object", [(27, "initial"), (28, "hint")]),
    ("Line up with marker A (cancelled)", "navigate", [(29, "initial")]),
    ("Go to and line up with marker B", "navigate", [(30, "initial"), (31, "confirm")]),
    ("Where is Oliver?", "memory_qa", [(32, "initial")]),
    ("Why look at pictures of my desk?", "self_knowledge", [(33, "initial")]),
    ("Blind during go_to?", "self_knowledge", [(34, "initial")]),
    ("Why not watch_go_to?", "self_knowledge", [(35, "initial")]),
    ("Something to attach paper fliers", "memory_qa", [(36, "initial")]),
    ("Something to hang the item", "memory_qa", [(37, "initial")]),
    ("Go to the pliers", "find_object", [(38, "initial")]),
    ("Square up to marker C", "navigate", [(39, "initial")]),
    ("Unobtrusive spot between Oliver's and Brian's desks", "navigate", [(40, "initial")]),
]
HELP = ("hint", "correction", "coaching")
CONTACT = re.compile(r"\b(bump|bumped|bumps|kick|kicked|stuck|against)\b", re.I)


def load(day="2026-10-23", session_files=("events.jsonl",)):
    events = [json.loads(l) for f in session_files for l in open(ROOT / f)]
    prompts = [e for e in events if e["kind"] == "prompt"]
    prompts.sort(key=lambda e: e["t"])
    grades = [json.loads(l) for l in open(ROOT / f"grades_claude_{day}.jsonl")]
    assert len(prompts) == len(grades), (len(prompts), len(grades))
    done = {(e["session"], e["turn"]): e for e in events if e["kind"] == "done"}
    notes = sorted((e for e in events if e["kind"] == "note"), key=lambda e: e["t"])
    actions = [e for e in events if e["kind"] == "action"]
    return prompts, grades, done, notes, actions


def main():
    prompts, grades, done, notes, actions = load()
    rows = []
    for name, kind, turns in TASKS:
        idx = [i for i, _ in turns]
        roles = Counter(r for _, r in turns)
        ps = [prompts[i - 1] for i in idx]
        ds = [done.get((p["session"], p["turn"])) for p in ps]
        t0 = ps[0]["t"]
        t1 = max(d["t"] for d in ds if d) if any(ds) else t0
        # notes and actions belong to the task from its first prompt until the next task's first prompt
        nxt = [prompts[t[0][0] - 1]["t"] for _, _, t in TASKS if prompts[t[0][0] - 1]["t"] > t0]
        t_end = min(nxt) if nxt else float("inf")
        tn = [n for n in notes if t0 <= n["t"] < t_end]
        contact = [n["text"] for n in tn if n.get("note_kind", n.get("type")) == "behavior" and CONTACT.search(n["text"] or "")]
        stops = [a for a in actions if t0 <= a["t"] < t_end and "STOP" in (a.get("text") or "")]
        # the task's outcome is the grade of its last turn that the agent actually handled (not lost / n/a)
        graded = [grades[i - 1]["grade"] for i, r in turns if r != "lost" and grades[i - 1]["grade"] != "n/a"]
        rows.append({
            "task": name, "kind": kind, "turns": idx, "roles": dict(roles),
            "prompts": sum(1 for _, r in turns if r != "lost"),
            "handholding": sum(roles[r] for r in HELP),
            "system_retries": roles["retry_system"],
            "agent_secs": round(sum(d["t"] - p["t"] for p, d in zip(ps, ds) if d), 1),
            "wall_secs": round(t1 - t0, 1),
            "contact_notes": contact, "stops": len(stops),
            "outcome": graded[-1] if graded else "n/a",
            "first_try": graded[0] if graded else "n/a",
            "models": sorted({p["model"] for p in ps}),
        })
    OUT.mkdir(exist_ok=True)
    (OUT / "handholding.json").write_text(json.dumps(rows, indent=1))

    lines = ["# Hand-holding per task, 2026-10-23 collect session", "",
             "Hand-holding = Oliver's hints + corrections + coaching prompts after the first request "
             "(system retries, confirmations and next steps not counted). Contact = behaviour notes that mention "
             "a bump, kick or getting stuck. Agent time is the sum of the agent's turns (breaks between prompts not counted).", "",
             "| task | kind | model | prompts | hand-holding | system retries | contact | agent time | first try | final |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['task']} | {r['kind']} | {', '.join(r['models'])} | {r['prompts']} | {r['handholding']} | "
                     f"{r['system_retries']} | {len(r['contact_notes'])} | {r['agent_secs'] / 60:.1f} min | "
                     f"{r['first_try']} | {r['outcome']} |")
    phys = [r for r in rows if r["kind"] in ("navigate", "find_object", "find_person") and r["outcome"] != "n/a"
            and "cancelled" not in r["task"]]
    talk = [r for r in rows if r not in phys and "cancelled" not in r["task"]]
    lines += ["", "## Totals", ""]
    for label, rs in (("Physical tasks (navigate / find)", phys), ("Question tasks (memory / self)", talk)):
        held = [r for r in rs if r["handholding"]]
        lines.append(f"- **{label}:** {len(rs)} tasks, {sum(r['handholding'] for r in rs)} hand-holding prompts in "
                     f"{len(held)} of them; {sum(len(r['contact_notes']) for r in rs)} contact notes; "
                     f"right on the first try {sum(r['first_try'] == 'right' for r in rs)}/{len(rs)}, "
                     f"right in the end {sum(r['outcome'] == 'right' for r in rs)}/{len(rs)}; "
                     f"{sum(r['agent_secs'] for r in rs) / 60:.0f} min of agent time.")
    worst = sorted(phys, key=lambda r: -r["handholding"])[:3]
    lines += ["", "Most hand-holding: " + "; ".join(f"{r['task']} ({r['handholding']}, "
                                                    f"{r['agent_secs'] / 60:.0f} min)" for r in worst) + "."]
    (OUT / "handholding.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
