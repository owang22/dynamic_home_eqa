"""Render every elicitation and revision log to readable markdown.

One ``.md`` beside each ``.json``: the system prompt, the user prompt
verbatim in a fenced block, then per round the model's reasoning, its
parsed output pretty-printed, and — for a revision — a before/after diff
of the hypothesis set so what the model changed is visible without
reading two JSON blobs. Hypotheses are labelled ``hyp1`` in prose.

Usage:  python -m baselines.llm_hypotheses.render_logs   # all logs
"""

from __future__ import annotations

import glob
import json
import pathlib
from typing import Any, Dict, List

from baselines.llm_hypotheses.elicit import DEFAULT_OUT_DIR, extract_json
from baselines.llm_hypotheses.prompt import SYSTEM_PROMPT

HYP = lambda s: str(s).replace("h", "hyp", 1) if str(s).startswith("h") and str(s)[1:].isdigit() else str(s)


def _rest_pairs(h: Dict[str, Any]) -> Dict[str, str]:
    rest = h.get("rest") or {}
    if isinstance(rest, list):
        return {str(e.get("target")): str(e.get("at", e.get("to"))) for e in rest if isinstance(e, dict)}
    return {str(k): str(v) for k, v in rest.items()}


def _summarize(h: Dict[str, Any]) -> List[str]:
    out = [f"### {HYP(h.get('hypothesis_id'))} — {h.get('rationale', '')}", ""]
    if h.get("distinguishing_prediction"):
        out.append(f"*Distinguishing prediction:* {h['distinguishing_prediction']}")
        if h.get("distinguishing_check"):
            c = h["distinguishing_check"]
            out.append(f"  (checkable form: {c.get('target')} at {c.get('at')}, {c.get('days')}, {c.get('hour')}h)")
        out.append("")
    rest = _rest_pairs(h)
    out.append(f"*Rest entries:* {len(rest)}" + (" — " + ", ".join(f"{k}→{v}" for k, v in list(rest.items())[:8]) + (" …" if len(rest) > 8 else "") if rest else ""))
    out.append("")
    for a in h.get("activities", []):
        out.append(f"- **{a.get('name')}** ({a.get('days')}, {a.get('frequency_per_week')}×/week, {a.get('start_hour')}h for {a.get('duration_h')}h)")
        for m in a.get("moves", []):
            out.append(f"  - {m.get('target')} → {m.get('to')} ({m.get('chance')}, {m.get('after')})")
    out.append("")
    return out


def _diff(before: List[Dict], after: List[Dict]) -> List[str]:
    """What changed per hypothesis id: rest entries, activities, moves."""
    b = {h.get("hypothesis_id"): h for h in before}; a = {h.get("hypothesis_id"): h for h in after}
    out = ["## What the revision changed", ""]
    for hid in sorted(set(b) | set(a), key=lambda s: (len(s), s)):
        if hid not in b:
            out.append(f"- **{HYP(hid)}: NEW** — {a[hid].get('rationale', '')}"); continue
        if hid not in a:
            out.append(f"- **{HYP(hid)}: REMOVED**"); continue
        hb, ha = b[hid], a[hid]
        rb, ra = _rest_pairs(hb), _rest_pairs(ha)
        acts_b = {x.get("name"): x for x in hb.get("activities", [])}; acts_a = {x.get("name"): x for x in ha.get("activities", [])}
        moves = lambda h: {(m.get("target"), m.get("to")) for x in h.get("activities", []) for m in x.get("moves", [])}
        mb, ma = moves(hb), moves(ha)
        changes = []
        if hb.get("rationale") != ha.get("rationale"): changes.append("rationale rewritten")
        if len(ra) != len(rb): changes.append(f"rest entries {len(rb)} → {len(ra)}")
        changed_rest = [k for k in rb if k in ra and rb[k] != ra[k]]
        if changed_rest: changes.append(f"rest moved for {', '.join(changed_rest[:5])}")
        added_a = set(acts_a) - set(acts_b); removed_a = set(acts_b) - set(acts_a)
        if added_a: changes.append(f"activities added: {', '.join(sorted(added_a))}")
        if removed_a: changes.append(f"activities removed: {', '.join(sorted(removed_a))}")
        for n in set(acts_a) & set(acts_b):
            xa, xb = acts_a[n], acts_b[n]
            for k in ("days", "start_hour", "duration_h", "frequency_per_week"):
                if xa.get(k) != xb.get(k): changes.append(f"{n}.{k} {xb.get(k)} → {xa.get(k)}")
        if ma - mb: changes.append(f"moves added: {', '.join(f'{t}→{d}' for t, d in sorted(ma - mb)[:6])}" + (" …" if len(ma - mb) > 6 else ""))
        if mb - ma: changes.append(f"moves removed: {', '.join(f'{t}→{d}' for t, d in sorted(mb - ma)[:6])}" + (" …" if len(mb - ma) > 6 else ""))
        out.append(f"- **{HYP(hid)}:** " + ("; ".join(changes) if changes else "unchanged"))
    out.append("")
    return out


def render(path: pathlib.Path) -> pathlib.Path:
    L = json.loads(path.read_text())
    kind = "Revision" if "call_index" in L else "Elicitation"
    title = f"# {kind} log — {L.get('household')}" + (f" · call {L['call_index']} (day {L['day']})" if kind == "Revision" else f" · {L.get('condition', '')}")
    out = [title, "", f"Rendered from `{path.name}`. Prompts are reproduced verbatim inside fenced blocks; hypotheses are labelled hyp1… in prose.", ""]
    out += ["## System prompt", "", "```text", SYSTEM_PROMPT, "```", ""]
    out += ["## Prompt", "", "```text", L["prompt"], "```", ""]
    previous = None
    if kind == "Revision":
        p = L["prompt"]; i = p.find("YOUR PREVIOUS HYPOTHESES:")
        if i > 0:
            try: previous = extract_json(p[i:]).get("hypotheses")
            except Exception: previous = None
    final = None
    for i, r in enumerate(L.get("rounds", [])):
        stats = ", ".join(f"{k}={r.get(k)}" for k in ("completion_tokens", "generation_seconds", "finish_reason", "think_closed", "cached") if k in r)
        out += [f"## Round {i + 1}: {r['kind']}  ({stats})", ""]
        if r.get("prompt"): out += ["### Prompt for this round", "", "```text", r["prompt"], "```", ""]
        if r.get("error"): out += [f"**Error:** `{r['error']}`", ""]
        if r.get("think"): out += ["### Model reasoning", "", "```text", r["think"], "```", ""]
        if r.get("payload"):
            try:
                obj = extract_json(r["payload"]); hyps = obj.get("hypotheses", [])
                out += ["### Model output — hypotheses", ""]
                for h in hyps: out += _summarize(h)
                out += ["<details><summary>raw JSON</summary>", "", "```json", json.dumps(obj, indent=1), "```", "", "</details>", ""]
                final = hyps
            except Exception:
                out += ["### Model output (raw, did not parse)", "", "```text", r["payload"], "```", ""]
    if kind == "Revision" and previous is not None and final is not None:
        out += _diff(previous, final)
    if L.get("dropped"):
        out += ["## Dropped hypotheses", ""] + [f"- {HYP(d['hypothesis'].get('hypothesis_id'))}: {d['error']}" for d in L["dropped"]] + [""]
    out += ["## Result", "", f"- valid hypotheses: {L.get('n_valid', len(L.get('hypotheses', [])))}",
            f"- outcome: {L.get('outcome', 'elicited')}", f"- generation seconds: {L.get('generation_seconds')}", ""]
    dst = path.with_suffix(".md"); dst.write_text("\n".join(out)); return dst


def main() -> None:
    root = DEFAULT_OUT_DIR
    paths = sorted(glob.glob(str(root / "logs" / "*" / "*.json"))) + sorted(glob.glob(str(root / "cold_start" / "*" / "*" / "revisions" / "*.json")))
    for p in paths:
        dst = render(pathlib.Path(p)); print("wrote", dst.relative_to(root))


if __name__ == "__main__":
    main()
