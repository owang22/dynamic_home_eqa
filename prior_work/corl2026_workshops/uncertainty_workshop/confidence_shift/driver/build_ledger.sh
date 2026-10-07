#!/bin/bash
# Rebuild the Longleaf Ledger page for the feedback protocol and insert a status banner.
# Usage: build_ledger.sh "<one-line status>"   -> writes R/ledger_live_fb.html (publish with the Artifact tool, url KJPMaPPbgv4UmeVakrDSTA)
set -e
cd ~/robot/dynamic_home_eqa/src
R=../results/confidence_shift_2026-09-20
python3 -m baselines.patrol.hyp_explorer --study $R/heldout_fb/hyp/study --banks $R/heldout_fb/banks --classical $R/heldout_fb/classical --naive $R/heldout_fb/llm --out $R/ledger_live_fb.html
STATUS="$1"
python3 - "$R/ledger_live_fb.html" "$STATUS" <<'PY'
import sys, pathlib, datetime
p = pathlib.Path(sys.argv[1]); s = p.read_text()
now = datetime.datetime.now().strftime("%d %b %H:%M")
banner = ('<div class="card" style="border-color:var(--told);margin-top:14px"><b>Protocol: nightly patrol at 03:00 + found-it feedback '
          '(the robot learns where the object turned out to be 10 min after each question). Updated ' + now + '.</b> '
          'Run v4 (02:02): likelihood floor 1e-3, recency term (4 h half-life) in the documents, share-cap entry for revised documents. ' + sys.argv[2] +
          ' Reference lines are the classical logs on the same protocol; the naive LLM line is built from its call log. '
          'Overnight log: results/confidence_shift_2026-09-20/overnight_status.md.</div>')
anchor = '<div id="res" class="cards"></div>'
assert anchor in s
s = s.replace(anchor, banner + "\n" + anchor, 1)
s = s.replace("patrol every ${H.patrol} h", "nightly patrol + found-it feedback", 1)
p.write_text(s); print("banner inserted", now)
PY
