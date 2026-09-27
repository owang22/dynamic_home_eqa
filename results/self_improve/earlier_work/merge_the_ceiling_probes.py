"""Build the ceiling probe over many households and merge them into one set.

One household yields about eight leak-free questions - one per object that the disruption
moves - and the ceiling is now a number the write-up leans on, so it needs more than that.
Question ids are prefixed with the household so nothing collides, and the leak test that the
reasoner taught us is re-run across the MERGED file rather than trusted per household.

    python3 results/self_improve/merge_the_ceiling_probes.py <out dir> <cell> <cell> ...
"""
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).parent


def main() -> int:
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    questions, truth = [], []
    for cell in sys.argv[2:]:
        work = pathlib.Path(tempfile.mkdtemp())
        done = subprocess.run(
            [sys.executable, str(HERE / "build_the_ceiling_probe.py"), cell, str(work)],
            capture_output=True, text=True)
        if done.returncode:
            print(f"skipped {cell}: {done.stderr.strip().splitlines()[-1:]}")
            continue
        home = json.loads((pathlib.Path(cell) / "searches.jsonl").open()
                          .readline())["household"]
        q = json.loads((work / "questions_for_the_reasoner.json").read_text())
        t = json.loads((work / "the_answers_it_should_have_given.json").read_text())
        for row in q:
            row["id"] = f"{home}/{row['id']}"
            row["home"] = home
        for row in t:
            row["id"] = f"{home}/{row['id']}"
            row["home"] = home
        questions += q
        truth += t
        print(f"{home}: {len(q)} questions")

    # The leak test, on the merged file. Two records can only share a moment if they are
    # about the same object in the same household, which one-question-per-object forbids -
    # but it is checked rather than assumed, because assuming it is what went wrong before.
    leaks = 0
    for a in questions:
        for b in questions:
            if a is b or a["where is"] != b["where is"] or a["home"] != b["home"]:
                continue
            for seen in b["every time you have seen it"]:
                if seen["day"] == a["asked on day"] and seen["clock"] == a["at"]:
                    leaks += 1
    # THE RESIDUE, stated rather than chased. A sibling record still shows that the robot was
    # standing in some room at the asked instant, and a look lists everything in a room - so if
    # the asked object has no sighting at that instant, it was not in that room. Counted over
    # the ten households: 87 of these exist, each ruling out ONE room of about eight. Closing
    # it completely needs every question in its own file with a reader that cannot look ahead,
    # which is one agent per question. Until then this is a known weak channel and the number
    # belongs beside any score from this probe.
    residue = 0
    for a in questions:
        for b in questions:
            if b is a or a["home"] != b["home"]:
                continue
            for seen in b["every time you have seen it"]:
                if seen["day"] == a["asked on day"] and seen["clock"] == a["at"]:
                    residue += 1
    print(f"known weak channel, stated not fixed: {residue} sibling sighting(s) at an asked "
          f"instant show which room the robot was in, ruling out one room of about eight")

    if leaks:
        print(f"REFUSING TO WRITE: {leaks} question(s) have their own moment printed inside "
              f"another question's record, which is the fault that voided the first probe")
        return 2
    (out / "questions_for_the_reasoner.json").write_text(json.dumps(questions, indent=1))
    (out / "the_answers_it_should_have_given.json").write_text(json.dumps(truth, indent=1))
    right = sum(1 for t in truth if t["was the small model's FIRST ROOM right"])
    print(f"\n{len(questions)} questions over "
          f"{len({q['home'] for q in questions})} households, no leaks")
    print(f"the small model's first room was right on {right} of {len(truth)} "
          f"({right/max(len(truth),1):.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
