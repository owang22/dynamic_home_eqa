"""dynbelief — dynamics-aware belief maintenance + EQA evaluation backbone.

Staged build (Coding Agent Brief v3). The Habitat/HSSD simulation side
(dynamic_home_eqa's generation pipeline, manifests, realized-day builder) is
consumed READ-ONLY: dynbelief adapts its logs, never modifies simulation
logic.

Layout:
  logging/     Stage 0.1 — ground-truth event/snapshot logger
  perception/  Stage 0.2 — Perceiver protocol, OraclePerceiver, VLM stub
  replay/      Stage 0.3/0.4/0.6 — viewpoints, ReplayWorld, schedules,
               runner, metrics
  beliefs/     Stage 0.5 — belief-model protocol + tier zoo (b0..b3)
  eqa/         Stage 1 — MCQ generation, displacement probe, symbolic answerer
  priors/      Stage 1.4 — offline schedule prior
  control/     Stage 2 — VoI scheduler, stopping rules
  experiments/ per-stage gate runners (one YAML per stage in configs/)

Conventions:
  - Time is `t_min`: integer minutes since episode start. Day k spans
    [k*1440, (k+1)*1440).
  - Objects and receptacles are integer ids via the episode registry
    (logging/gt_logger.py). Receptacle id 0 is always ELSEWHERE ("object is
    away / absent / not on any tracked receptacle").
  - Everything seeded; result filenames encode config.
"""

ELSEWHERE_ID = 0
ELSEWHERE_LABEL = "elsewhere"
MIN_PER_DAY = 1440
