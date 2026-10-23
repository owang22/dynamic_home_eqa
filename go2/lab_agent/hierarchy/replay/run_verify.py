"""27B verifies the small model's draft answers (offline, over recorded traces).
    python3 run_verify.py --small 8b_v2        -> results/verify_8b_v2.json"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from llm import LLM  # noqa: E402
from router import PIC, verify_draft  # noqa: E402

PICS = HERE.parents[2] / "data" / "lab_agent" / "pictures"
ap = argparse.ArgumentParser()
ap.add_argument("--small", default="8b_v2")
ap.add_argument("--url", default="http://127.0.0.1:8300/v1")
a = ap.parse_args()
mid = LLM(a.url)
gen = {c["id"]: c for c in json.load(open(HERE / "cases_generated.json"))}
log = {c["id"]: c for c in json.load(open(HERE / "cases_logged.json"))}
traces = json.load(open(HERE / "results" / f"generated_{a.small}.json")) + json.load(open(HERE / "results" / f"memory_{a.small}.json"))


def one(tr):
    c = gen.get(tr["case"]) or log[tr["case"]]
    ans = (tr.get("answer") or {}).get("text") or ""
    cited = [i for i in dict.fromkeys(((tr.get("answer") or {}).get("cited_ids") or []) + PIC.findall(ans)) if i in tr["opened"]]
    ids = list(dict.fromkeys(cited + tr["opened"]))[:6]
    pics = [(i, (PICS / f"{i}.jpg").read_bytes()) for i in ids if (PICS / f"{i}.jpg").exists()]
    v = verify_draft(mid, c["text"], ans or "(no answer)", pics) if ans else {"verdict": "not supported", "why": "no answer", "secs": 0}
    v.update(case=tr["case"], n_pics=len(pics))
    print(tr["case"], v["verdict"], round(v["secs"], 1), v["why"][:110], flush=True)
    return v


with ThreadPoolExecutor(3) as ex:
    rows = list(ex.map(one, traces))
(HERE / "results" / f"verify_{a.small}.json").write_text(json.dumps(rows, indent=1))
