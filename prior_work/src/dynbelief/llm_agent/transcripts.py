"""Render agent episodes as readable transcripts. Prompts are reconstructed
via build_prompt (deterministic in the stored row fields), so this works on
old parquets that predate raw-prompt capture as well as new ones.

    python -m dynbelief.llm_agent.transcripts <parquet> [--n 20] [--variant A3] [--only-wrong]
"""
from __future__ import annotations

import argparse
import pathlib

import pandas as pd

from dynamic_home_eqa.paths import REPO_ROOT
from dynbelief.llm_agent.prelim import build_prompt
from dynbelief.replay import ReplayWorld

_EP_DIR = {
    "family": "logs/dynbelief_daybudget_102344049_family_with_kids",
    "roommates": "logs/dynbelief_daybudget_102344022_roommates_shared_house",
    "single_parent": "logs/dynbelief_daybudget_102343992_single_parent_young_kids",
    "retired": "logs/dynbelief_daybudget_102344049_retired_couple",
}
_DESC = {
    "family": "a family home: two working parents, a teenage son, a toddler daughter",
    "roommates": "a shared house: three adult roommates",
    "single_parent": "a single-parent home with young kids",
    "retired": "a retired couple's home",
}


def render(df: pd.DataFrame, out_path: pathlib.Path, limit: int = 30) -> None:
    worlds: dict = {}
    lines = []
    for i, (_, r) in enumerate(df.head(limit).iterrows()):
        sc = r["scene"]
        if sc not in worlds:
            worlds[sc] = ReplayWorld(REPO_ROOT / _EP_DIR[sc])
        w = worlds[sc]
        # reconstruct the exact prompt the model saw
        if "prompt_full" in r and isinstance(r.get("prompt_full"), str):
            prompt = r["prompt_full"]
        else:
            system, user, _ = build_prompt(w, int(r["obj"]), int(r["t_snap"]),
                                           int(r["t_query"]), r["variant"], _DESC[sc])
            prompt = system + "\n\n---\n\n" + user
        lines += [
            f"## Episode {i}  [{sc} / {r['variant']} / {r['label']} / Δt={r['dt_min']//60}h]",
            "", "**PROMPT (what the model saw):**", "```", prompt.strip(), "```", "",
            "**MODEL RESPONSE:**",
            f"- action: `{r['action']}`   answer: `{r['answer']}`   "
            f"confidence: {r['confidence']}"
            + (f"   est_p_moved: {r['est_p_moved']}" if r.get("est_p_moved") is not None else ""),
            f"- reason: {r['reason']}",
            "", "**GROUND TRUTH:** true room = "
            f"`{r['true_answer']}`  →  answer {'✓ correct' if r['answer_correct'] else '✗ WRONG'}"
            + (f"  (object HAD moved since snapshot)" if r.get("moved_since_snap") else ""),
            "", "---", "",
        ]
    out_path.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("parquet")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--variant", default=None)
    ap.add_argument("--only-wrong", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    df = pd.read_parquet(args.parquet)
    if args.variant:
        df = df[df.variant == args.variant]
    if args.only_wrong:
        df = df[df.answer_correct == 0]
    out = pathlib.Path(args.out or (pathlib.Path(args.parquet).with_suffix(".transcripts.md")))
    render(df, out, args.n)
    print(f"{len(df)} episodes available; wrote {min(args.n, len(df))} -> {out}")


if __name__ == "__main__":
    main()
