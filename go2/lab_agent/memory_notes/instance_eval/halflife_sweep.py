"""Scale every half-life by k and recompute the prequential AUC (all kinds) - one parameter, to see whether the
time decay helps at all on this data."""
import runpy, sys, io, contextlib
sys.argv = ["x"]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(__file__.replace("halflife_sweep.py", "prequential.py"))
I, rows, auc = g["I"], g["rows"], g["auc"]
ys = [r["hit"] for r in rows]
base = dict(I.HALF_LIFE_H)
for k in (0.3, 1, 3, 10, 30, 100, 1e6):
    I.HALF_LIFE_H.clear(); I.HALF_LIFE_H.update({n: h * k for n, h in base.items()})
    d0 = I.DEFAULT_HALF_LIFE_H; I.DEFAULT_HALF_LIFE_H = d0 * k
    print(f"half-lives x{k:g}: AUC {auc([I.p_still(r['name'], r['hours'], r['misses'], r['later']) for r in rows], ys):.3f}")
    I.DEFAULT_HALF_LIFE_H = d0
