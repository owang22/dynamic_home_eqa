"""Run the big model (Opus via claude -p, memory-only MCP, memory frozen) on replay cases. Cached; budgeted.

    python3 run_opus.py generated [--only G01 ...]      # the 30 generated questions
    python3 run_opus.py logged --only L01 L03           # re-runs of logged memory turns (Opus vs its own log)
"""
import argparse
import glob
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from bigmodel import calls_made, opus_memory_turn  # noqa: E402

INDEX = Path(sorted(glob.glob(str(HERE / "data" / "index_snapshot_*.jsonl")))[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["generated", "logged"])
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    cs = json.load(open(HERE / f"cases_{a.which}.json"))
    cs = [c for c in cs if (not a.only or c["id"] in a.only) and c.get("kind", "memory") != "driving"]
    sys.path.insert(0, str(HERE))
    from run_replay import dog_status_for

    def one(c):
        try:
            r = opus_memory_turn(c["text"], INDEX, c["K"], c["t"], c["history"] or None,
                                 dog_status_for(c) if a.which == "logged" else None, tag=c["id"],
                                 stamp_time=a.which == "logged")
        except Exception as e:  # noqa: BLE001
            r = {"error": f"{type(e).__name__}: {e}"}
        r["case"] = c["id"]
        print(c["id"], r.get("cached"), r.get("secs"), len(r.get("calls", [])), "calls |",
              (r.get("answer") or r.get("error") or "")[:160].replace("\n", " "), flush=True)
        return r
    with ThreadPoolExecutor(a.workers) as ex:
        rows = list(ex.map(one, cs))
    out = HERE / "results" / f"opus_{a.which}.json"
    if a.which == "logged" and out.exists():   # keep the unstamped first runs (date bug) beside the stamped ones
        bak = HERE / "results" / "opus_logged_unstamped_v1.json"
        if not bak.exists():
            bak.write_text(out.read_text())
    old = json.loads(out.read_text()) if out.exists() else []
    by = {r["case"]: r for r in old}
    by.update({r["case"]: r for r in rows if "error" not in r})
    out.write_text(json.dumps(list(by.values()), indent=1))
    print("claude -p calls so far:", calls_made(), "->", out)


if __name__ == "__main__":
    main()
