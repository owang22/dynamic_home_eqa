"""Night-by-night diaries of what each model wrote, for reading by a person.

For each home: Opus's five nightly answers and the note changes it made that night, and the same note
changes for Qwen (the original 50-day cell). A note's revision history stores, under `was`, the text a
revision replaced, so the text written on the night of revision j is the `was` of revision j+1 (or the
current text after the last one).

    python3 results/stronger_model/opus_vs_qwen/readable.py
writes coordination/studies/opus_beliefs/readable/<home>_{opus,qwen}.md
"""
import collections
import json
import pathlib

OUT = pathlib.Path("coordination/studies/opus_beliefs/readable")
HH = ["hh_s2_t03", "hh_s32_t03", "hh_s48_t03"]
NOTES = {"opus": "results/stronger_model/opus_beliefs/claude_opus/cells/walk/{h}/notes.json",
         "qwen": "results/self_improve/wave_the_second_illness/cells/the_log_and_notes_about_the_routine/{h}/notes.json"}
BELIEFS = "results/stronger_model/opus_beliefs/claude_opus/cells/walk/{h}/beliefs.jsonl"
PERIOD = lambda d: ("normal" if d < 14 else "UNWELL (spell 1)" if d < 24 else "back to normal" if d < 32
                    else "UNWELL (spell 2)" if d < 42 else "back to normal again")
WHO = {"hh_s2_t03": "Tomas (works from home)", "hh_s32_t03": "Leo (works from home)",
       "hh_s48_t03": "Marco (a student, at classes 8:40-2:30)"}


def changes_by_night(claims):
    by = collections.defaultdict(list)
    for c in claims:
        hist = c.get("revision_history") or []
        states = [h["was"] for h in hist] + [{k: c.get(k) for k in ("statement", "holds_under", "status", "standing")}]
        by[c.get("first_written_day") or 0].append((c["claim_id"], "added", states[0], ""))
        for j, h in enumerate(hist):
            new = states[j + 1]
            kind = "revised"
            if new.get("standing") != h["was"].get("standing"):
                kind = f"now: {new.get('standing')}"
            by[h["day"]].append((c["claim_id"], kind, new, h.get("why", "")))
    return by


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for h in HH:
        beliefs = {r["day"]: r["beliefs"] for r in map(json.loads, open(BELIEFS.format(h=h)))}
        for model in ("opus", "qwen"):
            claims = json.load(open(NOTES[model].format(h=h)))["claims"]
            by = changes_by_night(claims)
            lines = [f"# {h}: {model.capitalize()}'s nightly {'answers and ' if model == 'opus' else ''}note changes",
                     "", f"The resident who is unwell on days 14-23 and 32-41: {WHO[h]}. Neither model was told.",
                     "Both models saw exactly the same sightings (the original Qwen cell's record).", ""]
            for d in range(0, 50):
                if d not in by and d not in beliefs:
                    continue
                lines += [f"## Night {d} ({PERIOD(d)})", ""]
                if model == "opus" and d in beliefs and beliefs[d]:
                    lines.append("**Answers to the five questions (asked before writing notes):**")
                    for k, v in beliefs[d].items():
                        lines += ["", f"*{k.replace('_', ' ')}:* {v}"]
                    lines.append("")
                if d in by:
                    lines.append(f"**Note changes tonight ({len(by[d])}):**")
                    for cid, kind, s, why in by[d]:
                        lines.append(f"- [{cid}] {kind}: {s.get('statement')}"
                                     + (f"  *(when true: {s.get('holds_under')})*" if s.get("holds_under") else "")
                                     + (f"  \n  why: {why}" if why else ""))
                    lines.append("")
            (OUT / f"{h}_{model}.md").write_text("\n".join(lines))
    print("written:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
