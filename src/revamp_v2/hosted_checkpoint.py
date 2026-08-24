#!/usr/bin/env python3
"""Spend checkpoint for the hosted pilot: project total pilot cost from
what the ledger has actually measured, and exit nonzero if the projection
exceeds the cap — the agreed alternative to asking for more budget. A
pilot stopped here with "the economics show it" is a complete answer.

Projection formula (printed, not hidden): spent_so_far +
remaining_calls x mean_cost_per_recorded_call. The mean comes from the
ledger's own totals; --remaining-calls is the caller's estimate of the
calls still ahead (e.g. 21 days x 4 residents = 84 story calls + 1 bind
call after the L2 stage).

Exit codes: 0 = proceed, 3 = projection exceeds the cap (stop and
report), 1 = no ledger yet.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from dynamic_home_eqa.generation.hosted_spend import SpendGuard  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--remaining-calls", type=int, required=True,
                    help="estimated hosted calls still ahead of this point")
    ap.add_argument("--label", default="checkpoint")
    args = ap.parse_args()
    guard = SpendGuard.from_env()
    led = guard._read()
    if not led["calls"]:
        print(f"[{args.label}] ledger has no calls yet — nothing to "
              f"project from")
        raise SystemExit(1)
    spent = float(led["spent_usd"])
    mean = spent / led["calls"]
    projected = spent + args.remaining_calls * mean
    print(f"[{args.label}] spent ${spent:.4f} over {led['calls']} calls "
          f"(mean ${mean:.4f}/call); projecting {args.remaining_calls} "
          f"more calls -> ${projected:.4f} total vs ${guard.cap_usd:.2f} "
          f"cap")
    print(f"[{args.label}] {guard.summary()}")
    if projected > guard.cap_usd:
        print(f"[{args.label}] PROJECTION EXCEEDS CAP — stop and report "
              f"(see reports/hosted_pilot/PILOT.md verdicts): partial "
              f"evidence is the deliverable, not a forced success")
        raise SystemExit(3)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
