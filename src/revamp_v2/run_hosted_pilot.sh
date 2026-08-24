#!/usr/bin/env bash
# Hosted-generation pilot, Task 3 runbook: one household (hh4), hard $5
# cap, full provenance. Every hosted call is priced into the shared
# ledger; crossing the cap aborts any stage with the spend summary.
#
# Sequence: schema probe -> spend checkpoint -> L2 (reused persona, no
# leak audit) -> escalation to terra ONLY if the whole L2 stage fails on
# luna -> checkpoint -> story_calendar arm (21 days, --bind-unbound,
# simulate inside) -> realism panel -> PILOT.md.
#
#   OPENAI_API_KEY=... bash src/revamp_v2/run_hosted_pilot.sh
set -euo pipefail
cd "$(dirname "$0")/../.."

: "${OPENAI_API_KEY:?set OPENAI_API_KEY (never committed, never logged)}"
MODEL="${PILOT_MODEL:-gpt-5.6-luna}"
ESCALATION_MODEL="${PILOT_ESCALATION_MODEL:-gpt-5.6-terra}"
QWEN_SRC="profiles/revamp_v2/rule_based/qwen3.8-27b/hh4"
OUT_RB="profiles/revamp_v2/rule_based/$MODEL"
OUT_SC="profiles/revamp_v2/story_calendar/$MODEL"
REPORTS="reports/hosted_pilot"
TIMINGS="$REPORTS/timings.txt"

export GENERATION_ENDPOINT="https://api.openai.com"
export HOSTED_SPEND_LEDGER="${HOSTED_SPEND_LEDGER:-/tmp/dynamic-home-eqa-hosted-spend.json}"
export HOSTED_SPEND_CAP="${HOSTED_SPEND_CAP:-5.0}"
mkdir -p "$REPORTS"

timed() {  # timed <label> <cmd...> — appends "label\tseconds"
    local label="$1"; shift
    local t0=$SECONDS
    "$@"
    local rc=$?
    printf '%s\t%s\n' "$label" "$((SECONDS - t0))" >> "$TIMINGS"
    return $rc
}

echo "== ledger: $HOSTED_SPEND_LEDGER (cap \$$HOSTED_SPEND_CAP)"
[ -f "$HOSTED_SPEND_LEDGER" ] && \
    echo "   (exists — resuming an earlier pilot session's spend)"

# ---- Task 2: schema probe (pennies; runs before any pilot generation) --
timed "schema probe" python3 src/revamp_v2/probe_hosted_schemas.py \
    --model "$MODEL"

checkpoint() {  # checkpoint <label> <remaining-calls>
    local rc=0
    python3 src/revamp_v2/hosted_checkpoint.py --label "$1" \
        --remaining-calls "$2" || rc=$?
    if [ "$rc" = 3 ]; then
        python3 src/revamp_v2/hosted_pilot_report.py --model "$MODEL" \
            --escalation-model "$ESCALATION_MODEL" || true
        echo "== STOPPED at checkpoint $1 (projection exceeds cap) — "
        echo "   partial report written to $REPORTS/PILOT.md"
        exit 3
    fi
    # rc 1 = ledger empty (nothing to project from): proceed, the hard
    # cap still guards every call.
}

# ~9 L2 calls worst case + 3 special + 84 story + 1 bind
checkpoint after-probe 100

# ---------------------------- L2 (reused persona, leak audit skipped) --
L2_RC=0
timed "L2 stage ($MODEL)" python3 src/revamp_v2/generate.py \
    --household hh4 --model "$MODEL" \
    --out-root "$OUT_RB" \
    --persona-from "$QWEN_SRC" \
    --cache-dir "/tmp/dynamic-home-eqa-gen-cache-revamp-v2-$MODEL" \
    || L2_RC=$?

if [ "$L2_RC" -ge 2 ]; then
    # exit 2 = spend-cap abort: stop and report, never escalate past it
    python3 src/revamp_v2/hosted_pilot_report.py --model "$MODEL" \
        --escalation-model "$ESCALATION_MODEL" || true
    echo "== SPEND CAP ABORT during L2 — partial report written"
    exit 2
fi
PROGRAM_SRC="$OUT_RB/hh4"
if [ "$L2_RC" = 1 ]; then
    echo "== L2 exhausted its attempts on $MODEL — escalating THAT ONE"
    echo "   stage to $ESCALATION_MODEL (same seeds); both outcomes stay"
    echo "   recorded in their build logs."
    ESC_RC=0
    timed "L2 stage ($ESCALATION_MODEL)" python3 src/revamp_v2/generate.py \
        --household hh4 --model "$ESCALATION_MODEL" \
        --out-root "profiles/revamp_v2/rule_based/$ESCALATION_MODEL" \
        --persona-from "$QWEN_SRC" \
        --cache-dir "/tmp/dynamic-home-eqa-gen-cache-revamp-v2-$ESCALATION_MODEL" \
        || ESC_RC=$?
    PROGRAM_SRC="profiles/revamp_v2/rule_based/$ESCALATION_MODEL/hh4"
fi
if [ ! -f "$PROGRAM_SRC/routine_program.yaml" ]; then
    # L2 exhausted on BOTH models: the pilot stops here with both build
    # logs intact — partial evidence is the deliverable.
    python3 src/revamp_v2/hosted_pilot_report.py --model "$MODEL" \
        --escalation-model "$ESCALATION_MODEL" || true
    echo "== L2 failed on $MODEL and $ESCALATION_MODEL — pilot stopped,"
    echo "   partial report written to $REPORTS/PILOT.md"
    exit 1
fi
# Any other stage exhausting retries stops the pilot with its build log
# intact (set -e) — partial evidence is the deliverable.

python3 src/revamp_v2/simulate.py "$PROGRAM_SRC" --seed 0
checkpoint after-L2 85

# --------------- story_calendar arm (story stays on $MODEL by design) --
timed "story calendar (21d)" python3 src/revamp_v2/story_calendar.py \
    --households "$PROGRAM_SRC" \
    --out-root "$OUT_SC" --model "$MODEL" --days 21 --seed 0 \
    --bind-unbound \
    --cache-dir "/tmp/dynamic-home-eqa-gen-cache-story-$MODEL"

timed "realism panel" python3 src/revamp_v2/realism_panel.py \
    "$OUT_SC"/hh4/timeline_seed0 --out "$OUT_SC/realism_panel.md"

# ------------------------------------------------ pilot markers + report --
for d in "$OUT_RB" "$OUT_SC"; do
    [ -d "$d" ] && printf '%s\n' \
        "PILOT DATA — hosted-generation pilot (hh4 only, $MODEL)." \
        "Not a release column; see reports/hosted_pilot/PILOT.md." \
        > "$d/README.md"
done
python3 src/revamp_v2/hosted_pilot_report.py --model "$MODEL" \
    --escalation-model "$ESCALATION_MODEL"
echo "== pilot complete -> $REPORTS/PILOT.md"
