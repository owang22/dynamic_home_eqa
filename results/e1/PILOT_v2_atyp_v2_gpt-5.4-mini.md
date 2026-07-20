# E1 v2 pilot on gpt-5.4-mini — atyp_v2 (3 transformed atypical households)

**Status: pilot** (reportable axis = local Qwen). Re-run of E1 v2 on the new
atyp_v2 bank: 3 realistic atypical households produced by registered transforms
(T1 night-shift, T2 three-twelves, T2 weekend-worker) vs typ_v1's 3 typical
households. 248 episodes + 3 probes, 0 errors, 537,953 in + 42,874 out tokens.
Now n=12/cell at D=0 and n=48/cell pooled at D≥1 per bank (was n=4 on the single
hand-authored night_shift). Raw: `rows_gpt-5.4-mini.jsonl`.

## Headline: the prior fits typical, fails atypical; history rescues only atypical

Accuracy at D=0 (prior/reasoning only, no observation history) vs pooled D≥1
(with history), profile_text=False:

| bank | D=0 (no history) | D≥1 (with history) | gain from history |
|---|---|---|---|
| typ_v1  | **0.417** | 0.417 | **+0.000** |
| atyp_v2 | **0.083** | 0.438 | **+0.354** |

This is the clean C1/C2 shape, now with real n:
- **C2 (prior harm):** with no observations, mini is fine on typical households
  (0.42 — its day-schedule prior fits) and near-chance on atypical ones (0.08 —
  the prior misfits a night/3×12/weekend worker).
- **C1 (adaptation):** observation history adds *nothing* on typical (+0.00, the
  prior already fit) but rescues atypical (+0.35, 0.08→0.44). In-context
  observations help far more where the prior is wrong — exactly the claim.

Per atypical household (n=4/cell, noisy individually; pooled is the signal):
night 0.00→0.75(D1); three_twelves 0.25→0.75(D3); weekend 0.00→0.75(D14).

## Comprehension probes: 3/3 (0.98, 0.98, 0.72) — failure is forecasting

Unchanged from before: mini reads the history (static object, fresh obs, daily
periodic). So the moved-episode wall below is forecasting, not comprehension.

## Calibration + the moved wall

- atyp_v2 Brier improves with history (D0 1.02 → D3 0.54); typ flat/noisy.
- Moved vs not-moved (pooled D≥1, ct=F): not-moved 0.61 both banks; **moved 0.07
  (atyp) / 0.06 (typ)**, moved Brier ~1.1. When an object moved since its last
  snapshot, mini is wrong and miscalibrated regardless of household type — the
  forecasting ceiling, cleanly separated from comprehension.
- log-loss remains spiky (confident-wrong outliers); read Brier as stable.

## Read

Switching to registered-transform atypicals (real, coherent night/3×12/weekend
households) plus the multi-day observation memory delivered the paper's core
picture at pilot scale: a day-schedule prior that helps on typical and hurts on
atypical households (D=0 gap 0.42 vs 0.08), history that closes the gap only
where the prior is wrong (+0.35 vs +0.00), and a forecasting ceiling on moved
objects that is not a comprehension artifact (probes 3/3). Confirm on Qwen
(reportable) with more seeds; then E2 (one-shot prior help/harm) plots its harm
curve against the measured `atypicality_distance` — the substrate is ready.
