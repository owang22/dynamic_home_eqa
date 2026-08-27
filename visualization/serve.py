#!/usr/bin/env python3
"""Serve the two viewers, each on its own port. Stdlib only, no flags needed.

    python serve.py            # -> object traces:   http://127.0.0.1:8710/
                               #    belief vs truth: http://127.0.0.1:8711/

One process, two listeners: the object-trace viewer answers `/` on the
first port and the belief-vs-truth viewer answers `/` on the second, so
each can live in its own browser tab and be reloaded independently. Both
ports serve the same tree (either page is still reachable on either port
by its full path); only what `/` means differs. Cross-links between the
pages point at the OTHER port, via a window.VIEWER_PORTS global injected
into the served HTML.

Both listeners serve the dynamic_home_eqa repo root (so both
/visualization/viewer/ and the trace.json files under /profiles/... are
reachable) with no-store cache headers — regenerated traces and re-baked
maps must never be served stale. Binds to 127.0.0.1 unless --host is
given explicitly.

The household list is rebuilt from disk on EVERY request for
/visualization/traces.json — every `*/timeline_seed*/trace.json` under
profiles/ and casas/ gets a row, rows whose file has gone are dropped.
The viewer polls it, so a household that finishes while you are watching
appears on its own, and one that is rebuilt reloads in place. Nothing
needs restarting to see new work.

Two things that used to make restarting painful are handled here too:
the port is taken over from an older viewer automatically (it runs
detached, so it is not in any shell's job table and was a nuisance to
find), and the listen backlog is raised well above the stdlib default of
5 — a browser opens half a dozen connections per page load, and queuing
behind them looked exactly like the server hanging on reload.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import pathlib
import signal
import threading
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
VIEWER_DIR = "/visualization/viewer"
# The two pages, one per port: short name -> file under viewer/.
PAGES = {"index.html": "index.html", "beliefs.html": "beliefs.html"}
MANIFEST = pathlib.Path(__file__).resolve().parent / "traces.json"
MANIFEST_URL = "/visualization/traces.json"
# revamp_v2 nests one level deeper than the older sets: the METHOD that
# produced a household (rule_based / freeform / freeform_grammar) sits
# above the model slug, because the same model generates the same
# household under both methods and the rows are otherwise indistinguishable.
BELIEF_TRACE_NAME = "belief_trace.json"
"""Written beside trace.json by `python -m baselines.belief_trace`; its
presence is what publishes a household to the belief-vs-truth page."""
TRACE_GLOBS = ("profiles/*/*/*/*/timeline_seed*/trace.json",
               "profiles/*/*/*/timeline_seed*/trace.json",
               "profiles/*/*/timeline_seed*/trace.json",
               "casas/*/timeline_*/trace.json")

# Directories the dropdown never offers. `_archive/` holds households kept
# for provenance whose hhN names no longer match the slot of the same
# number (see profiles/revamp_v2/_archive/*/README.md) — listing them means
# hunting past a dozen dead rows for the one that is current, and picking
# the wrong one is silent.
HIDDEN_PARTS = ("_archive",)

# The set currently being worked on. Its rows are marked with a leading
# marker and sort to the top, so "the one I am generating right now" is
# the first thing in the dropdown rather than something to search for.
# A plain string match on the trace url; empty disables the marking.
CURRENT_SET = "/revamp_v2/storyfirst/"


def _household_type(household_dir: pathlib.Path) -> str:
    """The household type, from whichever program file the set uses.

    trace.json does not carry it, and the type is the one thing that tells
    two rows apart at a glance ("hh_004" means nothing; "college_roommates"
    does), so it is worth reading the sibling program for.
    """
    # storyfirst names its assembled program program.yaml; the earlier
    # arms use routine_program.yaml. Without it the row fell back to the
    # parent dir name and read "hh_002 · gpt-5.6-terra" instead of the
    # household type, which is the one field that tells rows apart.
    for name in ("routine_program.yaml", "program.yaml",
                 "object_motions.yaml"):
        path = household_dir / name
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.startswith("household_type:"):
                return line.split(":", 1)[1].strip().strip("'\"")
    return household_dir.parent.name


def _label_for(trace_path: pathlib.Path) -> str:
    """A human row label, read from the trace itself so it stays true."""
    try:
        t = json.loads(trace_path.read_text())
    except (OSError, ValueError):
        return str(trace_path.relative_to(REPO_ROOT))
    household_dir = trace_path.parent.parent
    n_res = len(t.get("residents", {}))
    return (f"{t.get('household', household_dir.name)} · "
            f"{_household_type(household_dir)} · "
            f"{len(t.get('objects', {}))} objects, "
            f"{n_res} resident{'' if n_res == 1 else 's'} · "
            f"{t.get('days', '?')}d seed {t.get('seed', '?')}")


def _source_of(trace_path: pathlib.Path) -> str:
    """Which SET a timeline belongs to — the generation it came from plus
    the model that wrote it ("revamp_v2 · deepseek-v4-flash"). Every set
    numbers its households hh1..hh10, so without this the dropdown offers
    three rows called hh_001 and no way to tell them apart."""
    rel = trace_path.relative_to(REPO_ROOT).parts
    if rel[0] == "casas":
        return "casas (real ADLs)"
    if len(rel) >= 5 and rel[0] == "profiles" and rel[1] == "revamp_v2":
        return f"{rel[2]} · {rel[3]}"          # <method> · <model slug>
    if len(rel) >= 3 and rel[0] == "profiles":
        return f"{rel[1]} · {rel[2]}"          # <set> · <model slug>
    return rel[0]


def _sort_key(url: str) -> tuple:
    """revamp_v2 first, then by household NUMBER (hh2 before hh10)."""
    in_v2 = "/revamp_v2/" in url
    # The set under active work sorts above everything else; after that,
    # revamp_v2 methods, then other sets, then the real-data reference.
    group = (-1 if CURRENT_SET and CURRENT_SET in url
             else 0 if in_v2 and "/rule_based/" in url
             else 1 if in_v2 and "/freeform/" in url
             else 2 if in_v2                      # other revamp_v2 methods
             else 4 if "/casas/" in url else 3)
    digits = "".join(c for c in url.split("/hh")[-1].split("/")[0]
                     if c.isdigit())
    return (group, int(digits) if digits else 999, url)


def build_rows() -> list[dict]:
    """The dropdown, straight from disk: one row per timeline that exists
    right now. Called per request, so a household that finishes while the
    viewer is open shows up on the next poll."""
    found = []
    for pattern in TRACE_GLOBS:
        found += sorted(REPO_ROOT.glob(pattern))
    seen, rows = set(), []
    old = {}
    if MANIFEST.exists():
        try:
            old = {e["trace"]: e
                   for e in json.loads(MANIFEST.read_text()).get("traces", [])
                   if e.get("trace")}
        except ValueError:
            old = {}
    for path in found:
        rel = path.relative_to(REPO_ROOT)
        if any(part in HIDDEN_PARTS for part in rel.parts):
            continue
        url = "/" + str(rel)
        if url in seen:
            continue
        seen.add(url)
        # The label is always re-derived, never carried over: a preserved
        # label outlives the household it described (a rebuilt home with a
        # new object count kept advertising the old one).
        prior = old.get(url, {})
        source = _source_of(path)
        if CURRENT_SET and CURRENT_SET in url:
            source = f"★ CURRENT · {source}"
        row = {"label": _label_for(path), "trace": url, "source": source}
        if prior.get("runs"):
            row["runs"] = prior["runs"]           # keep published belief runs
        # Belief traces are DISCOVERED, not published by hand: one sits
        # next to trace.json whenever `python -m baselines.belief_trace`
        # has been run for that household, so the belief-vs-truth page
        # offers exactly the households that have one.
        belief = path.with_name(BELIEF_TRACE_NAME)
        if belief.exists():
            row["belief_trace"] = "/" + str(belief.relative_to(REPO_ROOT))
        rows.append(row)
    # revamp_v2 first (newest set), then the rest, real-data traces last
    rows.sort(key=lambda r: _sort_key(r["trace"]))
    return rows


def refresh_manifest() -> int:
    """Write traces.json once at startup, so the file on disk stays a
    truthful record for anything that reads it directly (the belief page,
    a human). The live dropdown comes from build_rows() per request."""
    rows = build_rows()
    MANIFEST.write_text(json.dumps({"traces": rows}, indent=1) + "\n")
    return len(rows)


class Handler(http.server.SimpleHTTPRequestHandler):
    # Which page `/` means on THIS port, and where the two viewers live —
    # filled in per listener by make_handler(). The ports dict is injected
    # into every served page as window.VIEWER_PORTS so cross-links between
    # the two viewers can point at the other port.
    ROOT_PAGE = "index.html"
    PORTS: dict = {}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _short_page(self) -> str | None:
        """The viewer page a short URL names, or None for anything else."""
        path = self.path.split("?")[0]
        if path == "/":
            return self.ROOT_PAGE
        return PAGES.get(path.lstrip("/"))

    def do_HEAD(self):
        # HEAD must answer for the same routes as GET (the viewer polls the
        # open trace with HEAD to notice a rebuild); without this, HEAD /
        # served a directory listing while GET / redirected.
        if self._short_page() or self.path.split("?")[0] == MANIFEST_URL:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        # `/` SERVES the viewer rather than redirecting to it. The redirect
        # was well-formed and curl followed it happily, but a browser was
        # observed taking the 302 and never requesting the target — one
        # `GET / 302` in the log and nothing after it, which presents as a
        # blank tab. A redirect buys nothing here (the viewer is the only
        # thing to serve) and browsers cache them, so the failure could
        # outlive the fix. Serving the bytes removes the whole class.
        page = self._short_page()
        if page:
            return self._serve_viewer(page)
        if self.path.split("?")[0] == MANIFEST_URL:
            return self._serve_manifest()
        super().do_GET()

    def _serve_viewer(self, page: str):
        """A viewer page, with a <base> so its relative assets (style.css,
        app.js) still resolve from the short URL, and the port map so its
        cross-link can target the other viewer's port."""
        html = (REPO_ROOT / f"{VIEWER_DIR.lstrip('/')}/{page}").read_text()
        ports = json.dumps(self.PORTS)
        html = html.replace(
            "<head>",
            f'<head>\n<base href="{VIEWER_DIR}/">\n'
            f"<script>window.VIEWER_PORTS = {ports};</script>", 1)
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_manifest(self):
        """The dropdown is rebuilt from disk on EVERY request, not just at
        startup: a household finished (or rebuilt) while the server runs
        should appear on the next poll, without anyone restarting anything.
        The scan is a glob plus a small JSON read per timeline — cheap
        enough to do per request, and it is the only way the viewer can
        follow a running build."""
        try:
            body = json.dumps({"traces": build_rows()}).encode()
        except OSError as e:                      # mid-build churn, say
            self.send_error(503, f"manifest unavailable: {e}")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Server(http.server.ThreadingHTTPServer):
    # A browser opens half a dozen connections for one page load, and the
    # stdlib default backlog of 5 meant a reload could queue behind its own
    # asset requests and look like a hang. Threads are daemons so a stuck
    # client can never hold up shutdown.
    request_queue_size = 128
    daemon_threads = True
    allow_reuse_address = True


def _port_holder(host: str, port: int) -> tuple[int, str] | None:
    """(pid, cmdline) of whatever is listening on host:port, via /proc —
    no lsof/ss dependency."""
    targets = set()
    for proto in ("tcp", "tcp6"):
        try:
            lines = pathlib.Path(f"/proc/net/{proto}").read_text().splitlines()[1:]
        except OSError:
            continue
        for line in lines:
            f = line.split()
            if len(f) < 10 or f[3] != "0A":               # 0A = LISTEN
                continue
            if int(f[1].split(":")[1], 16) == port:
                targets.add(f[9])                          # inode
    if not targets:
        return None
    for proc in pathlib.Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            for fd in (proc / "fd").iterdir():
                # an fd on a socket reads back as "socket:[12345]"; the
                # inode inside the brackets is what /proc/net/tcp keys on
                link = os.readlink(fd)
                if not link.startswith("socket:["):
                    continue
                if link[8:-1] in targets:
                    cmd = (proc / "cmdline").read_bytes().decode().replace("\0", " ")
                    return int(proc.name), cmd.strip()
        except OSError:
            continue
    return None


def take_port(host: str, port: int) -> None:
    """Free the port if OUR OWN previous server is holding it.

    Restarting used to mean hunting a detached process by hand: the holder
    is not in any shell's job table, `ps` shows it as a bare
    "python serve.py", and until it dies the port just answers "address
    already in use". Only a process whose command line is this same
    serve.py is ever signalled; anything else is reported and left alone.
    """
    holder = _port_holder(host, port)
    if holder is None:
        return
    pid, cmd = holder
    if pid == os.getpid():
        return
    if "serve.py" not in cmd:
        raise SystemExit(
            f"port {port} is held by pid {pid} ({cmd or 'unknown'}), which is "
            f"not a viewer — stop it yourself or use --port <other>")
    print(f"replacing the viewer already on :{port} (pid {pid})")
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            return
        for _ in range(40):                        # up to ~4 s per signal
            time.sleep(0.1)
            if _port_holder(host, port) is None:
                return
    raise SystemExit(f"could not free port {port} (pid {pid} still listening)")


def make_handler(root_page: str, ports: dict):
    """A Handler subclass bound to one listener: `/` on that listener
    serves `root_page`, and every served page learns the full port map."""
    return type(f"Handler_{root_page}", (Handler,),
                {"ROOT_PAGE": root_page, "PORTS": ports})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8710,
                    help="object-trace viewer port (default 8710)")
    ap.add_argument("--beliefs-port", type=int, default=8711,
                    help="belief-vs-truth viewer port (default 8711)")
    ap.add_argument("--keep-existing", action="store_true",
                    help="fail if a port is busy instead of replacing an "
                         "older viewer on it")
    args = ap.parse_args()

    if not args.keep_existing:
        take_port(args.host, args.port)
        take_port(args.host, args.beliefs_port)
    n = refresh_manifest()
    ports = {"traces": args.port, "beliefs": args.beliefs_port}
    servers = []
    for root_page, port in (("index.html", args.port),
                            ("beliefs.html", args.beliefs_port)):
        handler = functools.partial(make_handler(root_page, ports),
                                    directory=str(REPO_ROOT))
        servers.append(Server((args.host, port), handler))
    print(f"serving {REPO_ROOT} (pid {os.getpid()})")
    print(f"{n} timeline(s) in the household dropdown, refreshed per request")
    print(f"object traces:   http://{args.host}:{args.port}/")
    print(f"belief vs truth: http://{args.host}:{args.beliefs_port}/")
    for srv in servers[1:]:
        threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        servers[0].serve_forever()
    finally:
        for srv in servers:
            srv.server_close()


if __name__ == "__main__":
    main()
