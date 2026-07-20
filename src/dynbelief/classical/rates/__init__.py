"""Rate models, one module per arm. Each plugs into the shared Filter and
differs ONLY in how occupancy(obj, recep, t) / rate(obj, recep, t) are
estimated from the observation stream (L1: never from the profile YAML)."""
from dynbelief.classical.rates.c0_lastobs import C0LastObs        # noqa: F401
from dynbelief.classical.rates.c1_constant import C1Constant      # noqa: F401
from dynbelief.classical.rates.c2_spectral import C2Spectral      # noqa: F401
from dynbelief.classical.rates.c3_glm import C3PeriodicGLM        # noqa: F401
from dynbelief.classical.rates.c4_regime import C4RegimeHMM       # noqa: F401
