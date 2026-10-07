"""Conformal-triggered sensing: calibrate a belief's confidence with split
conformal prediction and sense only when the prediction set is not a
singleton. See :mod:`baselines.conformal.calibration` (the quantile
fitting and the household split) and :mod:`baselines.conformal.sweep`
(the alpha x age-binning sweep with its csvs and plots); the policy itself
is :mod:`baselines.policies.conformal_sense`.
"""

from baselines.conformal.calibration import (CalibrationPair, QhatTable,
                                             age_bin_index, age_bin_labels,
                                             collect_pairs, conformal_qhat,
                                             coverage_by_age,
                                             fit_age_binned_qhat,
                                             fit_global_qhat,
                                             household_split, prediction_set)

__all__ = ["CalibrationPair", "QhatTable", "age_bin_index",
           "age_bin_labels", "collect_pairs", "conformal_qhat",
           "coverage_by_age", "fit_age_binned_qhat", "fit_global_qhat",
           "household_split", "prediction_set"]
