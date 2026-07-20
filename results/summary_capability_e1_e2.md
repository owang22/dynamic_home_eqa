# Model capability: forecasting curve (E1) & prior-source split (E2)

Date: 2026-07-20. Bank: `typ_v1` (3 typical households). Streams as noted.
Models: `gpt-5.4-mini` (small) vs `gpt-5.5` (frontier). All spend logged in
`reports/llm_agent/api_usage.jsonl`.

## Provenance / cost

- **E1 (gpt-5.5)**: one capped forecasting run — 210 API calls, 670k input +
  **66k output tokens** (19% of the 345,600 output-token hard cap;
  `--max-tokens 1200 --reasoning low`, mean 313 output tok/call). `gpt-5.4-mini`
  curve is the previously-completed run
  (`results/e1/rows_classical_grid_gpt-5.4-mini.jsonl`).
- **E2**: **zero API**. Per-model priors were re-derived offline from the
  already-saved raw elicitation dumps (`results/e2/raw/<base>/raw_<model>.json`),
  mixture-averaging **within each model's 5 samples only** — mini and gpt-5.5 are
  no longer pooled. Eval run once per model →
  `results/e2_mini/`, `results/e2_gpt55/` (100,800 rows each).

---

## E1 — accuracy vs history (typ_v1, moved_enriched, n=24/cell = 3 hh × 8 ep)

| D (days) | gpt-5.5 top1 / top3 / Brier | mini top1 / top3 / Brier |
|---|---|---|
| 0  | **0.71** / 0.88 / 0.659 | 0.33 / 0.71 / 0.791 |
| 1  | 0.71 / 0.96 / 0.445 | 0.50 / 0.85 / 0.724 |
| 3  | 0.67 / 0.92 / 0.434 | 0.49 / 0.90 / 0.693 |
| 7  | 0.54 / 0.96 / 0.565 | 0.51 / 0.94 / 0.668 |
| 14 | 0.71 / 1.00 / 0.443 | 0.50 / 0.94 / 0.646 |
| 28 | 0.54 / 0.96 / 0.490 | 0.56 / 0.92 / 0.621 |

**Headline — the better the model, the flatter the accuracy-vs-days curve.**
gpt-5.5 starts near its ceiling at **D0** (0.71 top-1 with *zero* observation
history): its world-knowledge prior already knows where objects live in a
typical home, so more history adds little. mini starts low (0.33) and *climbs*
with history because its prior is weaker and it needs the data to catch up. The
frontier model buys at D0 roughly what the small model needs weeks of history to
approach.

**Caveats.** n=24/cell — the D7 dip (gpt-5.5 top-1 0.54) is within noise; top-3
is the stable read (gpt-5.5 0.88→1.00, mini 0.71→0.94, both monotone-ish). Brier
improves with history for both (gpt-5.5 0.66→~0.45; mini 0.79→0.62), i.e.
history still helps *calibration* even where it barely moves top-1.

---

## E2 — one-shot LLM prior as a help/harm source, split by model

Setup (unchanged): a classical C3 filter given a prior injected as pseudo-obs at
strength kappa (weak=1d / moderate=7d / strong=28d). **P0** = no prior, **Pllm**
= the model's elicited prior, **Porc** = oracle prior (machinery control, passes).
The only change here vs the pooled report: **Pllm is now per-model.**

| metric | mini | gpt-5.5 |
|---|---|---|
| D0 help, typ (Pllm−P0, moderate) | +0.240 | **+0.304** |
| D0 help, atyp (Pllm−P0, moderate) | +0.257 | **+0.323** |
| not-moved acc, P0 (D≥1) | 0.978 | 0.978 |
| not-moved acc, Pllm strong (D≥1) | 0.757 | 0.774 |
| harm drop (P0 − Pllm strong) | 0.221 | **0.204** |

**gpt-5.5 is a uniformly better prior source** — it helps *more* at D0 and harms
*slightly less* on the easy not-moved slice.

**Prediction that failed.** Because gpt-5.5 assigns systematically *higher*
move-rates than mini (backpack/glasses/mug all medium→high; 10 of 18 classes
differ on home or move_rate), we expected it to cause *more* phantom-movement
harm. It does not: its home accuracy is good enough that belief still sits on the
correct receptacle despite more mass on "might have moved," so net harm is
*lower*. Better homes outweigh higher move-rates.

**What the split did NOT fix.** The original E2 headline — "helps typical, harms
atypical" — remains weak for *both* models: D0 help is in fact slightly *higher*
on atypical homes (the opposite of the hypothesis). Separating the models
sharpened the **capability axis** (gpt-5.5 > mini as a prior, cleanly) but the
**typical-vs-atypical axis** stays blunt, because both models get object *homes*
right even for unusual households; the misalignment lives only in *timing*. A
clean crossover would require queries placed at the hours where day- and
night-schedules actually diverge.

---

## Takeaways

1. **E1 is the clean, primary story:** capability → flatter accuracy-vs-history
   curve; the frontier model's prior is worth ~weeks of observation to the small
   model.
2. **E2 now ranks the two models as prior sources** (gpt-5.5 strictly better on
   both help and harm), but does not deliver the typ/atyp crossover — treat it as
   a supporting/negative result pending the targeted-hour query slice.
