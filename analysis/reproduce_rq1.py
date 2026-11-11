# usage: python reproduce_rq1.py
# Reproduces the paper's Table V (energy statistics) and Table VI (Mann-Whitney U + Holm + Cliff's delta)
# from the authors' own data in clean_data/encoded_combined_data.csv (899 trials).
import itertools, os
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

here = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(here, 'clean_data', 'encoded_combined_data.csv'))
d['system'] = np.where(d.system_train == 1, 'train', 'pet')
d['granularity'] = np.select([d.granularity_fine == 1, d.granularity_medium == 1], ['fine', 'medium'], 'coarse')
d['user'] = np.select([d.user_120 == 1, d.user_200 == 1, d.user_320 == 1, d.user_400 == 1], [120, 200, 320, 400], 40)

print('Table V: energy per trial (J)')
print(d.groupby(['system', 'granularity']).energy.describe().round(2).to_string())

def iqr(s):
    q1, q3 = s.quantile([.25, .75])
    return s[s.between(q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1))]

print('\nTable VI: pairwise tests after IQR outlier removal')
for system, g in d.groupby('system'):
    data = {l: iqr(g[g.granularity == l].energy) for l in ['fine', 'medium', 'coarse']}
    pairs = [('fine', 'medium'), ('fine', 'coarse'), ('medium', 'coarse')]
    tests = [mannwhitneyu(data[a], data[b]) for a, b in pairs]
    p_holm = multipletests([t.pvalue for t in tests], method='holm')[1]
    for (a, b), t, p in zip(pairs, tests, p_holm):
        delta = 2 * t.statistic / (len(data[a]) * len(data[b])) - 1
        print(f'  {system:5} {a} vs {b}: raw p = {t.pvalue:.3g}, Holm p = {p:.3g}, Cliff d = {delta:.3f}')
print('\nPaper: Pet 0.152/0.001/0.012 with d 0.221 and 0.168; Train 0.057/<0.001/<0.001 with d 0.503 and 0.397.')
print('Two Pet p-values in the paper equal the raw values here, not the Holm-corrected ones.')
