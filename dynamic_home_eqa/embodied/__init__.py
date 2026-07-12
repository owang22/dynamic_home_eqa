"""
embodied/ — the embodied agent phase.

Four layers, dependencies pointing strictly downward:

    QuestionEpisodeRunner        # episode protocol, scoring, logging
      -> DecisionPolicy          # answer vs resense-route   (research)
        -> BeliefStore           # timestamped decaying map  (research)
          -> EmbodiedWorld       # replay + geometry oracle + sensor

Objects are not physically instantiated in habitat_sim in this phase —
habitat_sim is a geometry oracle only (navmesh for geodesic distance/path
following, ray casting for occlusion). The authoritative object state is
the same manifest.json Change-log the generation/trace-integrity phase
already produces and validates; see world.py's module docstring.

ground_truth.py is intentionally excluded from this package's normal import
surface: it is the only module allowed to answer "where is this label
really, right now" and is for scoring code only — see its docstring and
tests/test_embodied_layout.py, which enforces this by import inspection.
"""
