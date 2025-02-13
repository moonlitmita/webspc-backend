#Copyright 2025-present Yu Wang. All Rights Reserved.
#
#Distributed under MIT license.
#See file LICENSE for detail or copy at https://opensource.org/licenses/MIT

import numpy as np
from scipy import stats

def normality_test(data):
    n = len(data)
    if n < 3:
        return {'test_name': None, 'p_value': None}
    elif n <= 50:
        w_stat, p_value = stats.shapiro(data)
        test_name = 'Shapiro-Wilk'
    else:
        k2_stat, p_value = stats.normaltest(data)
        test_name = 'D\'Agostino and Pearson\'s'
    return {'test_name': test_name, 'p_value': p_value}
def f_oneway_variance(data, sample_size):
    samples_lists = [item['samples'] for item in data]
    samples_arrays = [np.array(samples) for samples in samples_lists]
    assert all(len(samples) == len(samples_arrays[0]) for samples in samples_arrays)
    if len(samples_arrays) < 3 or len(samples_arrays[0]) < 2:
        return {'F_value': None, 'p_value': None, '组内方差分量': None, '组间方差分量': None}
    else:
        stat, p = stats.f_oneway(*samples_arrays)
        n_groups = len(samples_arrays)
        n_samples_per_group = sample_size
        total_samples = n_groups * n_samples_per_group
        all_samples = np.concatenate(samples_arrays)
        grand_mean = np.mean(all_samples)
        df_between = n_groups - 1
        df_within = len(all_samples) - n_groups
        df_total = len(all_samples) - 1
        group_means = [np.mean(samples) for samples in samples_arrays]
        SS_within = sum(np.sum((samples - group_mean) ** 2) for samples, group_mean in zip(samples_arrays, group_means))
        SS_between = sum(n_samples_per_group * (group_mean - grand_mean) ** 2 for group_mean in group_means)
        SS_total = np.sum((all_samples - grand_mean) ** 2)
        MS_within = SS_within/df_within
        MS_between = SS_between/df_between
        variance_witin = MS_within
        variance_between = (MS_between - MS_within)/n_samples_per_group if (MS_between - MS_within) > 0 else 0
        return {'F_value': stat, 'p_value': p, '组内方差分量': variance_witin, '组间方差分量': variance_between}




