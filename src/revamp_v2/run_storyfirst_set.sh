#!/usr/bin/env bash
# storyfirst 10-household set, CANARY-FIRST: build hh2 alone, hard-check
# it (all story days present, spend within expectation), then release the
# remaining nine. Nothing here runs without OPENAI_API_KEY and an
# explicit cap.
#
#   OPENAI_API_KEY=... HOSTED_SPEND_CAP=15 bash src/revamp_v2/run_storyfirst_set.sh
set -uo pipefail
cd "$(dirname "$0")/../.."
: "${OPENAI_API_KEY:?set OPENAI_API_KEY}"
: "${HOSTED_SPEND_CAP:?set HOSTED_SPEND_CAP explicitly — no default spend}"
export GENERATION_ENDPOINT="https://api.openai.com"
export HOSTED_SPEND_LEDGER="${HOSTED_SPEND_LEDGER:-/tmp/dynamic-home-eqa-hosted-spend-storyfirst.json}"
M="${PILOT_MODEL:-gpt-5.6-terra}"
SLUG=$(python3 -c "from dynamic_home_eqa.generation.llm_client import model_slug; print(model_slug('$M'))")
OUT="profiles/revamp_v2/storyfirst/$SLUG"
CANARY=hh2
CANARY_MAX_USD="${CANARY_MAX_USD:-2.50}"

echo "== canary: $CANARY on $M (cap \$$HOSTED_SPEND_CAP, canary limit \$$CANARY_MAX_USD) =="
python3 src/revamp_v2/storyfirst.py --household "$CANARY" --model "$M" \
    --out-root "$OUT" || { echo "CANARY BUILD FAILED — stopping"; exit 1; }
python3 - "$OUT" "$CANARY" "$HOSTED_SPEND_LEDGER" "$CANARY_MAX_USD" <<'PY'
import json, pathlib, sys, yaml
out, hh, ledger, max_usd = sys.argv[1:5]
d = pathlib.Path(out) / hh
story = yaml.safe_load((d / "story.yaml").read_text())["days"]
assert len(story) == 21, f"canary story has {len(story)} days, not 21"
ev = (d / "timeline_seed0" / "events.jsonl").read_text().splitlines()
assert len(ev) > 200, f"canary produced only {len(ev)} events"
led = json.loads(pathlib.Path(ledger).read_text())
assert led["spent_usd"] <= float(max_usd), \
    f"canary cost ${led['spent_usd']:.2f} > ${max_usd} — economics changed, stop"
print(f"canary OK: 21 days, {len(ev)} events, ${led['spent_usd']:.4f}")
PY
[ $? -ne 0 ] && { echo "CANARY CHECK FAILED — stopping"; exit 3; }

echo "== canary passed — building the remaining nine =="
python3 src/revamp_v2/storyfirst.py --all --model "$M" --out-root "$OUT" \
    || { rc=$?; [ $rc = 2 ] && echo "SPEND CAP ABORT"; echo "some households failed (exit $rc)"; }

python3 src/revamp_v2/realism_panel.py "$OUT"/hh*/timeline_seed0 \
    --out "$OUT/realism_panel.md"
python3 -c "
import json,pathlib
led=json.loads(pathlib.Path('$HOSTED_SPEND_LEDGER').read_text())
print(f'== set done: \${led[\"spent_usd\"]:.4f} over {led[\"calls\"]} calls ==')"
