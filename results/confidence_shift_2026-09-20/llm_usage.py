"""Token and wall-clock accounting for every LLM call of the study (local vLLM only; hosted spend is $0).

    python3 results/confidence_shift_2026-09-20/llm_usage.py [heldout_fb] -> markdown table on stdout

naive LLM: llm/llm_stats.json (written by baselines.patrol.llm) plus per-run calls.jsonl for the arms still running.
hypothesis library: results/llm_hypotheses/logs/longleaf_named/patrol/<hh>.json (rounds carry usage).
mixture revisions: hyp/study/*/arms/passive/*/revisions/*.json (rounds carry usage; cached rounds were replays).
"""
import glob
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
LIB = ROOT.parents[1] / "results/llm_hypotheses/logs/longleaf_named/patrol"


def usage(protocol_dir: str = "heldout_fb", label: str = "t03") -> str:
    D = ROOT / protocol_dir
    rows = []
    # naive
    calls = cached = pt = ct = 0; secs = 0.0
    for p in sorted(D.glob("llm/*/calls.jsonl")):
        for l in open(p):
            try:
                r = json.loads(l)
            except ValueError:
                continue
            u = r.get("usage") or {}
            calls += 1; pt += int(u.get("prompt_tokens") or 0); ct += int(u.get("completion_tokens") or 0)
    # calls.jsonl has no timing and stores every completion once; the run-level stats file has wall time and replays
    for p in D.glob("llm/llm_stats*.json"):
        s = json.loads(p.read_text()); cached += int(s.get("cached") or 0); secs += float(s.get("seconds") or 0)
    rows.append(("naive LLM (told + not told, one call per question)", calls + cached, cached, pt, ct, secs))
    # library
    hhs = sorted({p.name.split(f"_{label}")[0] for p in D.glob(f"hyp/study/*_{label}__bank0")})
    calls = pt = ct = 0; secs = 0.0
    for hh in hhs:
        p = LIB / f"{hh}.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        for r in d.get("rounds", []):
            calls += 1; pt += int(r.get("prompt_tokens") or 0); ct += int(r.get("completion_tokens") or 0)
            secs += float(r.get("generation_seconds") or 0)
    rows.append((f"hypothesis library elicitation ({len(hhs)} households, thinking mode)", calls, 0, pt, ct, secs))
    # revisions
    for arm in ("told", "nottold"):
        calls = cached = pt = ct = 0; secs = 0.0
        for p in D.glob(f"hyp/study/*_{label}__bank0/arms/passive/*__{arm}/revisions/*.json"):
            d = json.loads(pathlib.Path(p).read_text())
            for r in d.get("rounds", []):
                calls += 1
                if r.get("cached"):
                    cached += 1; continue
                pt += int(r.get("prompt_tokens") or 0); ct += int(r.get("completion_tokens") or 0)
                secs += float(r.get("generation_seconds") or 0)
        rows.append((f"mixture revisions, {arm} arms (thinking mode)", calls, cached, pt, ct, secs))
    out = ["| agent | calls | live | cache replays | prompt tokens | completion tokens | summed generation time |", "|---|---|---|---|---|---|---|"]
    for name, c, cc, p, t, s in rows:
        out.append(f"| {name} | {c} | {c - cc} | {cc} | {p / 1e6:.2f} M | {t / 1e6:.2f} M | {s / 3600:.1f} h |")
    out.insert(0, "Summed generation time is the sum over calls of each call's wall time; the calls ran 8-10 at a time on one "
                  "vLLM server (Qwen/Qwen3.8-27B), so wall-clock is roughly a tenth. Naive replays (same prompt hash in the "
                  "told and not-told arms before the first shift day) are counted in the stats file, not as calls.")
    out.insert(1, "")
    tot_p = sum(r[3] for r in rows); tot_c = sum(r[4] for r in rows); tot_s = sum(r[5] for r in rows)
    out.append(f"| **total** | | | | **{tot_p / 1e6:.2f} M** | **{tot_c / 1e6:.2f} M** | **{tot_s / 3600:.1f} h** |")
    return "\n".join(out)


if __name__ == "__main__":
    print(usage(*(sys.argv[1:] or ["heldout_fb"])))
