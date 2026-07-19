# gpt-5.4-mini on the v2 bank (receptacle-level, varied times, calendar prompts)

408 episodes (family 64/variant, roommates 72/variant), A1/A2/A3, seed 7. Bank has a
50/50 uniform/moved component split. 8m20s, no failures. Raw:
`v2_mini_episodes.parquet`; usage in `api_usage.jsonl`.

## Split accuracy (the base-rate fix, receptacle-level)

| variant | resense | conf | NOT-moved rec-acc | MOVED rec-acc | MOVED room-acc |
|---|---|---|---|---|---|
| A1 | 0.007 | 0.83 | 1.000 | 0.039 | 0.342 |
| A2 | 0.029 | 0.78 | 1.000 | 0.027 | 0.324 |
| A3 | 0.074 | 0.67 | 1.000 | 0.014 | 0.314 |

- Aggregate accuracy is again **pure base rate**: perfect on non-moved, ~0 on moved. Split
  reporting is now mandatory (done here).
- MOVED **room-acc ≈ 0.32 > receptacle-acc ≈ 0.03**: when an object moves, mini often lands
  the right *room* but the wrong *receptacle* — the receptacle-level task the redesign added
  has real, non-trivial headroom (room-level alone hid this).

## Behavior: mini is essentially age-blind (like Qwen, unlike the flagship)

- **Spontaneous resense ≈ 0** (A1 0.007, A2 0.029). Making age visible barely moves it.
- **No dose-response**: A2 resense by Δt = 0.00 / 0.04 / 0.08 / 0.00 across 1–3/3–6/6–12/12–26h
  — flat, not tracking the true P(moved) (0.36/0.76/0.68/0.29).
- **Weak volatility discrimination**: A2 resense static 0.00 / occ 0.02 / dyn 0.04.
- **Scaffold (A3) barely engages mini**: resense only 0.074, moved effective-acc 0.103.
  (Contrast: Qwen3.6 A3 on the family scene resensed 0.53 on moved objects, eff-acc 0.53 —
  the open-weights model responded to the scaffold *more* than mini did. Caveat: Qwen v2 is
  family-only, n small; treat as directional pending the GPU-blocked roommates half.)

## Capability ladder so far (spontaneous A2 resense, receptacle bank)

| model | A2 resense | discrimination (sta/occ/dyn) | dose-response | note |
|---|---|---|---|---|
| Qwen3.6-35B (family, v2) | ~0.08 | flat | flat | age-blind |
| gpt-5.4-mini (v2) | 0.029 | 0.00/0.02/0.04 | flat | age-blind |
| gpt-5.5 (v1 40-ep preview) | 0.250 | 0.00/0.38/0.50 | 0.10→0.40 | age-SENSITIVE |

The story holds and sharpens: spontaneous age-sensitivity is **not** present in the
open-weights model or the API mini; it appears at the flagship tier. The flagship needs a
full v2 run to confirm (the preview was v1/room-level, 40 episodes).

## Usage / cost (ledger)

- 408 calls, **608,199 input + 35,797 output tokens** (avg 1,490 in / 87 out — the long
  memory table + 42–84-option enum), mean latency 1.2s.
- `est_cost` is N/A: the `PRICES` table in `clients.py` is intentionally empty (no guessed
  rates). Token counts are exact, so filling gpt-5.4-mini's $/1M rates back-computes cost
  for every logged call. Full-bank frontier run (~816 calls both scenes × 3 variants) ≈
  1.2M input tokens.
