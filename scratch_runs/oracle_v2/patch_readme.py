import pathlib

p = pathlib.Path("src/baselines/README.md")
s = p.read_text()
old = """`oracle_posterior_study.py` (OracleBelief, `beliefs/oracle_program_posterior.py`:
the routine oracle's realization ensemble weighted by the observation
history, with its ESS degeneracy gate), `voi_study.py`"""
new = """`oracle_posterior_study.py` (OracleBelief, `beliefs/oracle_program_posterior.py`:
the routine oracle's realization ensemble weighted by the observation
history with a per-disagreement `eps` and a forgetting half-life, the
weighting sweep that picks them on the calibration households, and the
ESS degeneracy gate), `voi_study.py`"""
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, new))
print("readme ok")
