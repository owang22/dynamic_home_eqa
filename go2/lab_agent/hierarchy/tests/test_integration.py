"""integration.register() with the real server.py functions, against fake_console.py. Everything server.py would
write (calls.jsonl, pictures, index.jsonl, stop_flag) is redirected to a temp dir, and the real files are checked
unchanged afterwards.    python3 go2/lab_agent/hierarchy/tests/test_integration.py"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
REAL = HERE.parents[1] / "data" / "lab_agent"
before = {f: (REAL / f).stat().st_size for f in ("index.jsonl", "calls.jsonl")}
n_pics = len(list((REAL / "pictures").iterdir()))

import server as S  # noqa: E402  (the lab agent's MCP tools module; mcp.run() is not called)
import fake_console  # noqa: E402
import integration  # noqa: E402
from agent import run_turn  # noqa: E402
from llm import LLM  # noqa: E402

PORT = 8495
tmp = Path(tempfile.mkdtemp(prefix="hier_integ_"))
S.M.CONSOLE = f"http://127.0.0.1:{PORT}"
S.M.DATA, S.M.PICS, S.M.INDEX = tmp, tmp / "pictures", tmp / "index.jsonl"
S.M.describe = lambda jpg: {"summary": "test", "objects": [], "people": 0, "people_notes": "", "states": []}
S.LOG, S.STOP_FLAG = tmp / "calls.jsonl", tmp / "stop_flag"


class FakeMCP:
    def tool(self):
        return lambda fn: fn


LAB = json.load(open(HERE / "watch_data" / "labels.json"))
NEG = [f["id"] for f in LAB if f["teal"] == "0"][:30]
POS = [f["id"] for f in LAB if f["teal"] == "1"]
ok = {}
wg, sf = integration.register(FakeMCP(), S)

srv, C = fake_console.serve(NEG[:6] + POS[:8] + NEG[6:20], PORT, fps=1.0, go_to_s=40)
out = wg("a person wearing a teal t-shirt", place="desk_oliver")
print(out[0])
calls = [c["call"] for c in C.calls if not c["call"].startswith("GET")]
print(calls)
ok["watch_go_to via server.py stops on sight"] = "STOPPED ON SIGHT" in out[0] and "POST stop" in calls \
    and calls.index("POST stop") < calls.index("go_to returned")
ok["photo after stop indexed into the temp memory only"] = (tmp / "index.jsonl").exists()
srv.shutdown(); srv.server_close()

srv, C = fake_console.serve(NEG[:20], PORT, fps=1.0, go_to_s=3)
P = list(json.loads((HERE / "replay" / "data" / "places_snapshot.json").read_text()))
r = run_turn("walk to kang's desk", integration.ServerEnv(S), LLM(integration.SMALL_URL), lambda t, h: "big", P,
             S.list_places())
print(r["tier"], [(s["tool"], s.get("args")) for s in r.get("small_steps", [])], r["answer"][:120])
g = [c for c in C.calls if c["call"] == "POST go_to"]
ok["router + ServerEnv: 8B drives server.go_to(desk_kang)"] = r["tier"] == "small" and g and g[0]["args"].get("place") == "desk_kang"
srv.shutdown(); srv.server_close()

after = {f: (REAL / f).stat().st_size for f in ("index.jsonl", "calls.jsonl")}
ok["real calls.jsonl untouched"] = after["calls.jsonl"] == before["calls.jsonl"]
ok["no new real pictures"] = len(list((REAL / "pictures").iterdir())) == n_pics
print("real index.jsonl grew by", after["index.jsonl"] - before["index.jsonl"], "bytes (the memory backfill also appends to it)")
for k, v in ok.items():
    print("PASS" if v else "FAIL", k)
sys.exit(0 if all(ok.values()) else 1)
