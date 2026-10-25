"""Describe every memory picture again with one vision model, so the text-search baseline compares like with like.

    python3 redescribe.py --probe 10                   # describe 10 pictures, print the rate (no stop-time needed)
    python3 redescribe.py --stop-at 08:00 --workers 4  # run in priority() order until done or until 08:00 PT, resumable

The live index (data/lab_agent/index.jsonl) is not touched: descriptions go to
data/lab_agent/descriptions_<model>.jsonl, one line per picture {"id", "seen", "seconds", "at"} or {"id", "error"}.
Pictures already in that file are skipped, so a stopped run picks up where it left off.

Backends (--backend):
  z690-8b   the control PC's Qwen3-VL-8B (z690:8000). Pauses while the dog is online or an agent holds control, since
            the 8B also serves the live tools (watch_go_to, scan_for, skills); ends at the stop time Z690 gave (08:00 PT
            on 2026-10-25, coordination/inbox/cheetah/).
  h100-27b  the H100's Qwen3.8-27B (172.17.45.79:8300), the same model that wrote the 27B descriptions in the live
            index. On demand: the first request starts it (about 90 s), so one goes alone before the rest; 8 at a time.

Same prompt as memory.describe. The schema is DESCRIBE_SCHEMA without its maxLength caps, strings clamped in Python
after parsing: Z690 measured maxLength alone making xgrammar about 10x slower on the 8B (one CPU core computing token
masks while the GPU idles); maxItems and minimum/maximum cost nothing and stop object-list loops (2026-10-25 01:51 and
02:18 messages).
"""
import argparse
import base64
import datetime as dt
import json
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lab_agent"))
import memory as M  # noqa: E402

BACKENDS = {"z690-8b": ("http://172.17.40.64:8000/v1/chat/completions", "qwen3-vl-8b", "qwen3-vl-8b", False),
            "h100-27b": ("http://172.17.45.79:8300/v1/chat/completions", "Qwen/Qwen3.8-27B", "qwen3.8-27b-h100", True)}
URL, MODEL, OUT, QWEN38 = None, None, None, False


def uncapped(schema):
    if isinstance(schema, dict):
        return {k: uncapped(v) for k, v in schema.items() if k != "maxLength"}
    return schema


SCHEMA = uncapped(M.DESCRIBE_SCHEMA)


def clamp(seen):
    s = lambda v, n: str(v)[:n]  # noqa: E731
    seen["summary"] = s(seen.get("summary", ""), 300)
    seen["objects"] = [{"name": s(o.get("name", ""), 60), "colour": s(o.get("colour", ""), 30), "on": s(o.get("on", ""), 40),
                        "across": min(1.0, max(0.0, float(o.get("across") or 0)))} for o in seen.get("objects", [])[:30]]
    seen["people"] = min(30, max(0, int(seen.get("people") or 0)))
    seen["people_notes"] = s(seen.get("people_notes", ""), 200)
    seen["states"] = [s(x, 80) for x in seen.get("states", [])[:8]]
    return seen
PT = dt.timezone(dt.timedelta(hours=-7))           # PDT until 2026-11-01
_LOCK = threading.Lock()


def priority(recs):
    """The order to describe in, since the 8B gets through only part of the set in a night (about 110 an hour):
    the benchmark's evidence pictures, then the deliberate photos (photo, look_around) from the two collect
    sessions, then those sessions' trail frames coarse to fine (every 8th, every 4th, every 2nd, the rest), so a
    stopped run leaves an even spread rather than one described hour; then everything else, newest first."""
    ev = set()
    for f in (M.DATA.parent / "collection" / "analysis").glob("questions_*.json"):
        for q in json.loads(f.read_text()):
            ev.update(q.get("evidence", []))
    t = lambda s: time.mktime(time.strptime(s, "%Y-%m-%d %H:%M"))  # noqa: E731
    sessions = [(t("2026-10-23 18:00"), t("2026-10-23 21:00")), (t("2026-10-24 15:00"), t("2026-10-24 18:00"))]
    in_s = lambda r: any(a <= r["t"] < b for a, b in sessions)  # noqa: E731
    recs = sorted(recs, key=lambda r: r["t"])
    trail = [r for r in recs if in_s(r) and r["source"] == "trail"]
    rank = {}
    for i, r in enumerate(trail):
        rank[r["id"]] = next(k for k, step in enumerate((8, 4, 2, 1)) if i % step == 0)

    def key(r):
        if r["id"] in ev:
            return (0, r["t"])
        if in_s(r) and r["source"] != "trail":
            return (1, r["t"])
        if r["id"] in rank:
            return (2 + rank[r["id"]], r["t"])
        return (6, -r["t"])
    return sorted(recs, key=key)


def done_ids():
    if not OUT.exists():
        return set()
    return {json.loads(l)["id"] for l in OUT.read_text().splitlines() if l.strip() and '"seen"' in l}


def busy():
    """The dog is online (fresh state) or an agent holds control: leave the 8B to the live tools."""
    if not URL.startswith("http://172.17.40.64"):
        return False          # only the control PC's 8B is shared with the live tools
    try:
        s = M.get_json("/state.json", 10)
    except Exception:  # noqa: BLE001
        return False          # console down: the dog cannot be running through it
    return (s.get("age") or {}).get("state", 1e9) < 60 or bool((s.get("agents") or {}).get("owner"))


def describe(rec):
    jpg = Path(rec["path"]).read_bytes()
    body = {"model": MODEL, "temperature": 0, "max_tokens": M.DESCRIBE_MAX_TOKENS,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(jpg).decode()}},
                {"type": "text", "text": M.DESCRIBE_ASK}]}],
            "response_format": {"type": "json_schema", "json_schema": {"name": "a", "schema": SCHEMA}}}
    if QWEN38:
        body["chat_template_kwargs"] = {"enable_thinking": False}
    t0 = time.time()
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            ch = json.loads(r.read())["choices"][0]
        if ch.get("finish_reason") == "length":
            raise RuntimeError("cut off at max_tokens")
        row = {"id": rec["id"], "seen": clamp(json.loads(ch["message"]["content"])), "seconds": round(time.time() - t0, 1)}
    except Exception as e:  # noqa: BLE001
        row = {"id": rec["id"], "error": f"{type(e).__name__}: {e}"[:200], "seconds": round(time.time() - t0, 1)}
    row["at"] = round(time.time(), 1)
    with _LOCK, OUT.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", type=int, help="describe this many pictures and report the rate, then stop")
    ap.add_argument("--stop-at", help="HH:MM Pacific; required for a full run")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--backend", choices=BACKENDS, default="z690-8b")
    a = ap.parse_args()
    global URL, MODEL, OUT, QWEN38
    URL, MODEL, name, QWEN38 = BACKENDS[a.backend]
    OUT = M.DATA / f"descriptions_{name}.jsonl"
    if a.backend == "z690-8b" and not a.stop_at and not a.probe:
        sys.exit("z690-8b needs --stop-at (08:00, as agreed with Z690)")
    stop = None
    if a.stop_at:
        h, m = map(int, a.stop_at.split(":"))
        now = dt.datetime.now(PT)
        stop = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if stop <= now:
            stop += dt.timedelta(days=1)
        print("stop at", stop.isoformat(timespec="minutes"), flush=True)
    have = done_ids()
    todo = [r for r in priority(M.load()) if r["id"] not in have]
    if a.probe:
        todo = todo[:a.probe]
    print(f"{len(have)} already described, {len(todo)} to go, {a.workers} in flight", flush=True)
    t0, n, errs = time.time(), 0, 0
    if a.backend == "h100-27b" and todo:          # wake the on-demand server with one request first
        print("warm-up:", describe(todo.pop(0)).get("seconds"), "s", flush=True)
    it = iter(todo)

    def worker():
        nonlocal n, errs
        for rec in it:
            while busy():
                if stop and dt.datetime.now(PT) >= stop:
                    return
                time.sleep(60)
            if stop and dt.datetime.now(PT) >= stop:
                return
            row = describe(rec)
            with _LOCK:
                n += 1
                errs += "error" in row
                if n % 25 == 0 or a.probe:
                    rate = n / (time.time() - t0) * 3600
                    print(f"{time.strftime('%H:%M')} {n}/{len(todo)} done ({errs} errors), {rate:.0f}/h, "
                          f"last {row['seconds']} s", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        for f in [ex.submit(worker) for _ in range(a.workers)]:
            f.result()
    el = time.time() - t0
    print(f"finished: {n} in {el / 60:.1f} min ({n / el * 3600:.0f}/h), {errs} errors", flush=True)


if __name__ == "__main__":
    main()
