# E1 pilot on gpt-5.4-mini (profile banks, full condition grid)

**Status: pilot, not the reportable pass.** The experiment plan's reportable E1
is local-Qwen; this run (researcher-directed) checks the harness end-to-end on
the API axis and looks for preliminary patterns. 264 episodes = full grid
({typ_v1, atyp_v1} x D in {0,1,3,7,14} x {history-only, +profile-prose} x 3
households x 4 queries) + atyp_shift_v1 C4 control at D=7. One seed. n=12 per
cell — treat every number as directional.

Zero API/parse errors. Usage: 296,130 in + 30,158 out tokens (ledger:
`reports/llm_agent/api_usage.jsonl`). Raw rows: `rows_gpt-5.4-mini.jsonl`;
auto tables: `summary_gpt-5.4-mini.md`; prompt_hash d69077885dc3.

## 1. The moved/not-moved split replicates on the symbolic world

Pooled D>=1:

| bank | profile prose | not-moved acc | MOVED acc |
|---|---|---|---|
| typ_v1  | no  | 0.618 (n=34) | **0.000** (n=14) |
| typ_v1  | yes | 0.471 (n=34) | 0.071 (n=14) |
| atyp_v1 | no  | 0.703 (n=37) | **0.000** (n=11) |
| atyp_v1 | yes | 0.432 (n=37) | 0.091 (n=11) |

Same failure surface as the HSSD v2 receptacle bank: when the object moved
since the last observation, mini essentially never names the right receptacle.
The profile world reproduces the phenomenon with a fully-known generator —
which is exactly what E2/E3 need.

## 2. Most interesting pilot pattern: **correct routine text makes mini worse**

Giving the (accurate, deterministically-rendered) profile prose:

- not-moved accuracy DROPS (0.62→0.47 typ; 0.70→0.43 atyp) — the prose seduces
  the model away from parroting memory (correct for unmoved objects) into
  routine speculation (wrong at receptacle granularity);
- moved accuracy barely improves (0.00 → 0.07/0.09);
- confidence inflates 0.65 → 0.85 while accuracy falls; elsewhere-hedging
  collapses 0.12 → 0.02; ECE at D=7 atyp explodes 0.198 → 0.731.

Preliminary shape: a knowledge-injection failure — handed the true routine,
the weak model over-applies it and mis-calibrates. (Mirror image of the HSSD
finding where models ignore their own elicited knowledge; here provided
knowledge is misused.) Needs the Qwen pass + more seeds before leaning on it.

## 3. C1 preview (adaptation with history) — weak, right-signed

History-only (ct=False) accuracy vs D: atyp 0.417 → 0.833 at D=14 vs typ
0.250 → 0.500. Right-signed for C1 (atyp gains more from history) but n=12
per cell; not evidence yet.

## 4. C4 preview (held-out attribution)

Observed-object accuracy 0.533 vs held-out 0.143 on atyp_v1 (memory does the
work); atyp_v1 vs atyp_shift_v1 not yet separated (shift control ran only at
D=7, n=24). The full C4 comparison needs the shift bank across all D.

## Verdict for the harness

End-to-end clean: strict-schema JSON 264/264, resumable rows, ledger costs,
frozen reportable banks, all endpoint slices computable. Ready for the Qwen
pass when the GPU returns; E2 (one-shot prior help/harm) can build on this
substrate unchanged.
