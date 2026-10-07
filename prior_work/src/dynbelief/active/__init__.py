"""Active displacement probe (Stage 2): budget-constrained active perception —
value-of-information over a predictive belief. Replay-only, single-object,
single-(t_seen,t_query) episodes. NOT embodied navigation; cost is per-look.
"""
from dynbelief.active.room_belief import (ELSEWHERE, room_belief,
                                          condition_absent, sensable_rooms)
