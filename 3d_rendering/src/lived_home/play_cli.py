"""The search task from lived_home.play, played from the command line (for a
tester without a browser). Same rules as the page.

  python -m lived_home.play_cli <state.json> start <play_data.json>
  python -m lived_home.play_cli <state.json> q                 the current question
  python -m lived_home.play_cli <state.json> plan              rooms and furniture keys
  python -m lived_home.play_cli <state.json> owners            who owns what
  python -m lived_home.play_cli <state.json> notes [word]      patrol notes and your earlier looks
  python -m lived_home.play_cli <state.json> guess <key> [<key> <key>] [--note "..."]
  python -m lived_home.play_cli <state.json> look <key>
  python -m lived_home.play_cli <state.json> pick <look#> <thing#>   "that's it"
  python -m lived_home.play_cli <state.json> answer putaway <spot id> | someone <who> | out <who> | cant
  python -m lived_home.play_cli <state.json> rate <clear 1-5> <answerable 1-5> "<comment>"   (saves, next)
  python -m lived_home.play_cli <state.json> results
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

WD = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def when(d, t):
    return f"{WD[(d - 1) % 7]}, day {d}, {t}"


class Game:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.s = json.loads(path.read_text())
        self.D = json.loads(pathlib.Path(self.s["data"]).read_text())
        self.F = {f["key"]: f for f in self.D["layout"]["furniture"]}
        self.SPOT = {s["id"]: dict(s, fkey=f["key"]) for f in self.D["layout"]["furniture"] for s in f["spots"]}
        self.first = {r["id"]: r["name"].split()[0] for r in self.D["residents"]}

    def save(self):
        self.path.write_text(json.dumps(self.s, indent=1))

    @property
    def q(self):
        n = len(self.s["done"])
        return self.D["questions"][n] if n < len(self.D["questions"]) else None

    def cur(self):
        return self.s.setdefault("cur", {"guesses": [], "looks": [], "picks": [], "metres": 0.0, "answer": None})

    def where_am_i(self):
        return self.s.get("at")

    def fname(self, k):
        f = self.F.get(k)
        return f"{f['name']} ({f['room'].replace('_', ' ')})" if f else k

    def show(self):
        q = self.q
        if not q:
            print("All questions answered. Use `results`.")
            return
        c = self.cur()
        print(f"Question {q['n']} of {len(self.D['questions'])} | {when(q['day'], q['time'])} | "
              f"looks {len(c['looks'])}/{self.D['rules']['max_looks']} | walked {c['metres']:.1f} m")
        print(q["text"])
        for i, L in enumerate(c["looks"], 1):
            print(f"  look {i}: {self.fname(L['fkey'])}: " +
                  ("; ".join(f"[{j}] {t['thing']}" + (f" ({t['where']})" if t["where"] else "")
                             for j, t in enumerate(L["things"], 1)) or "nothing you can see"))
            closed = [s["name"] for s in self.F[L["fkey"]]["spots"] if s["kind"] == "closed"]
            if closed:
                print(f"     closed, can't see inside: {', '.join(closed)}")
            for p in L["people"]:
                print(f"     {self.first[p['who']]} is in the room" + (f", holding {', '.join(p['holding'])}" if p["holding"] else ""))
        if c["answer"]:
            print("Answered:", c["verdict"]["text"], "| Where it really was:", self.truth())
            print("Now: rate <clear 1-5> <answerable 1-5> \"<comment>\"")

    def plan(self):
        rooms = {}
        for f in self.D["layout"]["furniture"]:
            rooms.setdefault(f["room"], []).append(f)
        for r, fs in rooms.items():
            print(f"{r}:")
            for f in fs:
                sp = ", ".join(s["name"] + (" (closed)" if s["kind"] == "closed" else "") for s in f["spots"])
                xz = f" at x={f['x']:.1f} z={f['z']:.1f}" if f["x"] is not None else ""
                print(f"  {f['key']}{xz}: {sp}")

    def owners(self):
        for r in self.D["residents"]:
            print(f"{r['name']} ({r['job']}) owns: {', '.join(r['owns'])}")
        if self.D["residents"][0].get("household"):
            print(self.D["residents"][0]["household"])

    def notes(self, word=""):
        q = self.q
        w = word.lower()
        for p in self.D["patrols"]:
            if q and (p["day"], p["time"]) >= (q["day"], q["time"]):
                break
            lines = []
            for s in p["seen"]:
                txt = ", ".join(t["thing"] + (f" ({t['where']})" if t["where"] else "") for t in s["things"])
                full = f"{self.fname(s['furniture'])}: {txt}"
                if txt and (not w or w in full.lower()):
                    lines.append("   " + full)
            for room, ps in p["people"].items():
                for pp in ps:
                    t = f"{self.first[pp['who']]} was in the {room}" + (f", holding {', '.join(pp['holding'])}" if pp["holding"] else "")
                    if not w or w in t.lower():
                        lines.append("   " + t)
            if lines or not w:
                print(f"PATROL {when(p['day'], p['time'])} (rooms: {', '.join(p['rooms'])})")
                print("\n".join(lines) or "   nothing seen")
        for r in self.s["done"]:
            lines = [f"   {self.fname(L['furniture'])}: {', '.join(L['saw']) or 'nothing'}" for L in r["looks"]]
            lines = [l for l in lines if not w or w in l.lower()]
            if lines:
                print(f"YOUR LOOKS {when(r['day'], r['time'])} (question {r['n']})")
                print("\n".join(lines))

    def guess(self, keys, note):
        self.cur()["guesses"] = [{"furniture": k, "note": note} for k in keys if k in self.F]
        self.save()
        print("Guesses:", [self.fname(g["furniture"]) for g in self.cur()["guesses"]])

    def look(self, k):
        c, q = self.cur(), self.q
        if c["answer"]:
            print("Already answered; rate it.")
            return
        if k not in self.F:
            print(f"No furniture {k}; see `plan`.")
            return
        if len(c["looks"]) >= self.D["rules"]["max_looks"]:
            print("No looks left: answer without seeing it.")
            return
        f = self.F[k]
        if f["x"] is not None:
            at = self.s.get("at") or self.entry()
            c["metres"] += math.dist(at, (f["x"], f["z"]))
            self.s["at"] = [f["x"], f["z"]]
        c["looks"].append({"fkey": k, "things": q["looks"].get(k, []), "people": q["people"].get(f["room"], [])})
        self.save()
        self.show()

    def entry(self):
        s = self.SPOT.get(self.D["layout"]["entry"])
        f = self.F[s["fkey"]] if s else None
        return [f["x"], f["z"]] if f and f["x"] is not None else [0, 0]

    def pick(self, i, j):
        c, q = self.cur(), self.q
        t = c["looks"][i - 1]["things"][j - 1]
        right = t["oid"] in q["accept"]
        c["picks"].append({"thing": t["thing"], "right": right})
        if right:
            self.finish({"type": "found", "thing": t["thing"], "spot": t["spot"]})
        else:
            self.save()
            twin = any(self.D["names"].get(a) == t["thing"] for a in q["accept"])
            print("That one looks the same, but it is not the one asked for." if twin
                  else f"Not that one: the {t['thing']} is not what was asked for.")

    def answer(self, kind, arg=None):
        if kind == "putaway":
            self.finish({"type": "putaway", "spot": arg, "fkey": self.SPOT.get(arg, {}).get("fkey")})
        elif kind in ("someone", "out"):
            self.finish({"type": kind, "who": arg})
        else:
            self.finish({"type": "cant"})

    def finish(self, ans):
        c = self.cur()
        c["answer"] = ans
        c["verdict"] = self.judge(ans)
        self.save()
        self.show()

    def judge(self, ans):
        c = self.cur()
        if ans["type"] == "found":
            return {"level": "good", "text": f"Found it in {len(c['looks'])} looks."}
        for a in self.q["answer"].values():
            if ans["type"] == "putaway" and a["kind"] == "put away":
                if ans.get("spot") == a["spot"]:
                    return {"level": "good", "text": "Right: it was put away there."}
                if ans.get("fkey") and ans["fkey"] == a.get("furniture"):
                    return {"level": "part", "text": "Right piece of furniture, different spot."}
                if ans.get("fkey") and self.F.get(ans["fkey"], {}).get("room") == a.get("room"):
                    return {"level": "part", "text": "Right room, different furniture."}
            if ans["type"] == "someone" and a["kind"] == "someone has it":
                return {"level": "good" if ans["who"] == a["who"] else "part",
                        "text": "Right." if ans["who"] == a["who"] else "Someone had it, but not that person."}
            if ans["type"] == "out" and a["kind"] == "out of the house":
                return {"level": "good" if ans["who"] == a["who"] else "part",
                        "text": "Right." if ans["who"] == a["who"] else "Out of the house, with the other person."}
        if ans["type"] == "cant":
            return {"level": "part", "text": "You said you could not tell."}
        return {"level": "bad", "text": "Not right."}

    def truth(self):
        out = []
        for oid, a in self.q["answer"].items():
            name = self.D["names"].get(oid, oid)
            if a["kind"] in ("someone has it", "out of the house"):
                out.append(f"the {name}: {a['kind']} ({self.first[a['who']]})")
            else:
                s = self.SPOT.get(a["spot"], {})
                ref = f"{a['relation'].replace('_', ' ')} the {self.D['names'].get(a['reference'], a['reference'])}, " \
                    if a.get("reference_kind") == "object" else ""
                out.append(f"the {name}: {ref}{s.get('name', a['spot'])} of the {self.fname(s.get('fkey'))}"
                           + (" (out of sight)" if a["kind"] == "put away" else ""))
        return "; ".join(out)

    def rate(self, clear, fair, comment):
        c, q = self.cur(), self.q
        if not c["answer"]:
            print("Answer first.")
            return
        self.s["done"].append({"n": q["n"], "day": q["day"], "time": q["time"], "text": q["text"], "kind": q["kind"],
                               "probe": q["probe"], "guesses": c["guesses"],
                               "looks": [{"furniture": L["fkey"], "saw": [t["thing"] for t in L["things"]]} for L in c["looks"]],
                               "wrong_picks": [p["thing"] for p in c["picks"] if not p["right"]],
                               "answer": c["answer"], "verdict": c["verdict"]["level"], "verdict_text": c["verdict"]["text"],
                               "n_looks": len(c["looks"]), "metres": round(c["metres"], 2),
                               "clear": clear, "fair": fair, "comment": comment})
        self.s["cur"] = None
        self.s.pop("cur")
        self.save()
        print("Saved.")
        self.show()

    def results(self):
        d = self.s["done"]
        good = sum(r["verdict"] == "good" for r in d)
        print(f"{good} right of {len(d)}")
        for r in d:
            print(f"{r['n']:2d} {r['verdict']:4s} looks {r['n_looks']} clear {r['clear']} fair {r['fair']} | {r['text']} | {r['comment']}")


def main():
    path = pathlib.Path(sys.argv[1])
    cmd, args = sys.argv[2], sys.argv[3:]
    if cmd == "start":
        path.write_text(json.dumps({"data": str(pathlib.Path(args[0]).resolve()), "done": []}))
        g = Game(path)
        print("Started. Rules:", json.dumps(g.D["rules"]))
        g.show()
        return
    g = Game(path)
    if cmd == "q":
        g.show()
    elif cmd == "plan":
        g.plan()
    elif cmd == "owners":
        g.owners()
    elif cmd == "notes":
        g.notes(args[0] if args else "")
    elif cmd == "guess":
        note = ""
        if "--note" in args:
            i = args.index("--note")
            note, args = " ".join(args[i + 1:]), args[:i]
        g.guess(args, note)
    elif cmd == "look":
        g.look(args[0])
    elif cmd == "pick":
        g.pick(int(args[0]), int(args[1]))
    elif cmd == "answer":
        g.answer(args[0], args[1] if len(args) > 1 else None)
    elif cmd == "rate":
        g.rate(int(args[0]), int(args[1]), " ".join(args[2:]))
    elif cmd == "results":
        g.results()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
