"""Belief models: consume the observation stream, answer predict()."""

from baselines.beliefs.base import BeliefModel
from baselines.beliefs.daytype_mixture import (DaytypeMixture,
                                               DaytypeMixtureConfig)
from baselines.beliefs.hierarchy_backoff import (HierarchyBackoff,
                                                 HierarchyBackoffConfig)
from baselines.beliefs.last_observation import LastObservation
from baselines.beliefs.markov1 import Markov1, Markov1Config
from baselines.beliefs.most_frequent import MostFrequentLocation
from baselines.beliefs.periodic_persistence import (PeriodicPersistence,
                                                    PeriodicPersistenceConfig)
from baselines.beliefs.timetable import TimetableConfig, TimetableLookup

__all__ = ["BeliefModel", "DaytypeMixture", "DaytypeMixtureConfig",
           "HierarchyBackoff", "HierarchyBackoffConfig", "LastObservation",
           "Markov1", "Markov1Config", "MostFrequentLocation",
           "PeriodicPersistence", "PeriodicPersistenceConfig",
           "TimetableConfig", "TimetableLookup"]
