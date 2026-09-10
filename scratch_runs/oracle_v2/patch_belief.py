import pathlib

p = pathlib.Path("src/baselines/beliefs/oracle_program_posterior.py")
s = p.read_text()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:60], s.count(old))
    s = s.replace(old, new)


rep("""prediction or the degeneracy diagnostic asks for them. Empty looks are
therefore in the weights already, so the base pipeline's negative-
evidence step is skipped (``consumes_negative_evidence_natively``); the
floor mix and the sighting-at-the-prediction-instant short circuit apply
as for every model.
""", """prediction or the degeneracy diagnostic asks for them. Empty looks are
therefore in the weights already, so the base pipeline's negative-
evidence step is skipped (``consumes_negative_evidence_natively``); the
floor mix and the sighting-at-the-prediction-instant short circuit apply
as for every model.

**Forgetting.** With ``half_life_h`` set, every observation's factor
decays: the log-weights are multiplied by ``0.5 ** (dt / half_life)``
whenever the clock advances by ``dt`` (at each observation and at each
prediction), so a disagreement ``h`` hours old costs ``log(eps) *
0.5 ** (h / half_life)`` instead of ``log(eps)`` forever. Without it
(``half_life_h`` None, the original setting) the weights match the
whole episode, and on the fleet banks they collapse onto one
realization within days (see ``results/oracle_program_posterior/``):
no seed re-realizes the bank's world for more than a few days, so
whole-episode matching picks the least-wrong realization instead of a
posterior over routines. A half-life keeps the realizations that match
the recent past in play even when they diverged earlier.
""")

rep('''DEFAULT_EPS = 0.05
"""Multiplier a realization's weight takes for every observation it
disagrees with. Constructor argument; never tuned per bank."""
''', '''DEFAULT_EPS = 0.05
"""Multiplier a realization's weight takes for every observation it
disagrees with. Constructor argument; never tuned per bank."""

DEFAULT_HALF_LIFE_H: Optional[float] = None
"""Half-life, in hours, of an observation's factor on the log-weights
(None: observations are never forgotten, the whole-episode matching of
the original study). Constructor argument; never tuned per bank."""
''')

rep('''    :meth:`reset`. ``eps`` is the per-disagreement weight multiplier.
    """''', '''    :meth:`reset`. ``eps`` is the per-disagreement weight multiplier;
    ``half_life_h`` the forgetting half-life of every observation's factor
    (None: never forget).
    """''')

rep('''                 eps: float = DEFAULT_EPS,
                 floor_mass: float = DEFAULT_FLOOR_MASS,
                 negative_half_life_h: Optional[float] = None) -> None:
        super().__init__(rng, floor_mass=floor_mass,
                         negative_half_life_h=negative_half_life_h)
        if not 0.0 < eps < 1.0:
            raise ValueError(f"OracleBelief: eps {eps} outside (0, 1)")
        self._eps = float(eps)
        self._log_eps = math.log(self._eps)
''', '''                 eps: float = DEFAULT_EPS,
                 half_life_h: Optional[float] = DEFAULT_HALF_LIFE_H,
                 floor_mass: float = DEFAULT_FLOOR_MASS,
                 negative_half_life_h: Optional[float] = None) -> None:
        super().__init__(rng, floor_mass=floor_mass,
                         negative_half_life_h=negative_half_life_h)
        if not 0.0 < eps < 1.0:
            raise ValueError(f"OracleBelief: eps {eps} outside (0, 1)")
        if half_life_h is not None and not half_life_h > 0.0:
            raise ValueError(
                f"OracleBelief: half_life_h {half_life_h} must be positive")
        self._eps = float(eps)
        self._log_eps = math.log(self._eps)
        self._half_life_s: Optional[float] = (
            None if half_life_h is None else float(half_life_h) * 3600.0)
        self._logw_t = 0                      # clock of the log-weights
''')

rep('''    @property
    def name(self) -> str:
        return "OracleBelief"

    @property
    def eps(self) -> float:
        return self._eps
''', '''    @property
    def name(self) -> str:
        hl = ("" if self._half_life_s is None
              else f",hl={self._half_life_s / 3600.0:g}h")
        return f"OracleBelief(eps={self._eps:g}{hl})"

    @property
    def eps(self) -> float:
        return self._eps

    @property
    def half_life_h(self) -> Optional[float]:
        return None if self._half_life_s is None else self._half_life_s / 3600.0
''')

rep('''        self._logw = np.zeros(ens.n_seeds, dtype=np.float64)
        self._last = None
        self.n_observations = 0
''', '''        self._logw = np.zeros(ens.n_seeds, dtype=np.float64)
        self._logw_t = 0
        self._last = None
        self.n_observations = 0
''')

rep('''        if codes is None or code is None:
            return                          # an object/receptacle the program lacks
        at = codes[:, self.ensemble.minute_index(t)] == code
''', '''        if codes is None or code is None:
            return                          # an object/receptacle the program lacks
        self._decay_to(t)
        at = codes[:, self.ensemble.minute_index(t)] == code
''')

rep('''    # ------------------------------------------------------- weights

    def weights(self) -> NDArray[np.float64]:''', '''    def _decay_to(self, t: int) -> None:
        """Age every observation's factor to ``t``: nothing without a
        half-life, or when ``t`` is not later than the log-weights' clock
        (evidence arrives in time order; nothing is un-aged)."""
        if self._half_life_s is None or t <= self._logw_t:
            return
        self._logw *= 0.5 ** ((t - self._logw_t) / self._half_life_s)
        self._logw_t = int(t)

    # ------------------------------------------------------- weights

    def weights(self) -> NDArray[np.float64]:''')

rep('''                            t: int) -> Prediction:
        w = self.weights()
        self._last = {"ess": float(1.0 / np.square(w).sum()),''', '''                            t: int) -> Prediction:
        self._decay_to(t)
        w = self.weights()
        self._last = {"ess": float(1.0 / np.square(w).sum()),''')

p.write_text(s)

r = pathlib.Path("src/baselines/registry.py")
s = r.read_text()
rep('''    DEFAULT_EPS, DEFAULT_REALIZATION_CACHE, OracleProgramPosterior,
    default_loader)''', '''    DEFAULT_EPS, DEFAULT_HALF_LIFE_H, DEFAULT_REALIZATION_CACHE,
    OracleProgramPosterior, default_loader)''')
rep('''    observation history (display name ``OracleBelief``). ``n_seeds``
    defaults to the routine oracle's count; ``cache_dir`` (None disables)''', '''    observation history (display name ``OracleBelief``). ``eps`` and
    ``half_life_h`` (None: never forget) are the weighting knobs; ``n_seeds``
    defaults to the routine oracle's count; ``cache_dir`` (None disables)''')
rep('''    return OracleProgramPosterior(rng, ensemble,
                                  eps=float(spec.get("eps", DEFAULT_EPS)),
                                  **_base_kwargs(spec))''', '''    raw_hl = spec.get("half_life_h", DEFAULT_HALF_LIFE_H)
    return OracleProgramPosterior(
        rng, ensemble, eps=float(spec.get("eps", DEFAULT_EPS)),
        half_life_h=None if raw_hl is None else float(raw_hl),
        **_base_kwargs(spec))''')
r.write_text(s)
print("patched")
