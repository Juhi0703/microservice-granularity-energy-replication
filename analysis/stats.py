# usage: python stats.py   (reads my_trials.csv and my_requests.csv)
# RQ1 (energy, HWiNFO), RQ2 (response time) and RQ3 (load) with the paper's methods:
# IQR outlier removal, Mann-Whitney U with Holm-Bonferroni, Cliff's delta, OLS with dummy variables.
import itertools
import pandas as pd
import statsmodels.api as sm
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

def iqr(s):
    q1, q3 = s.quantile([.25, .75])
    return s[s.between(q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1))]

def size(d):
    d = abs(d)
    return 'negligible' if d < .147 else 'small' if d < .33 else 'medium' if d < .474 else 'large'

def pairwise(df, col):
    for system, g in df.groupby('system'):
        levels = [l for l in ['coarse', 'medium', 'fine'] if l in set(g.granu)]
        data = {l: iqr(g[g.granu == l][col]) for l in levels}
        print(f'\n{system}: {col}')
        print(pd.DataFrame({l: v.describe() for l, v in data.items()}).round(2).to_string())
        pairs = list(itertools.combinations(levels, 2))
        tests = [mannwhitneyu(data[a], data[b]) for a, b in pairs]
        if not tests:
            continue
        p_holm = multipletests([t.pvalue for t in tests], method='holm')[1]
        for (a, b), t, p in zip(pairs, tests, p_holm):
            d = 2 * t.statistic / (len(data[a]) * len(data[b])) - 1   # Cliff's delta
            print(f'  {a} vs {b}: Holm p = {p:.3g}, Cliff d = {d:.3f} ({size(d)})')

def ols(df, col):
    X = pd.get_dummies(df[['users', 'granu', 'system']], columns=['users', 'granu', 'system'], drop_first=True).astype(float)
    fit = sm.OLS(df[col], sm.add_constant(X)).fit()
    out = pd.DataFrame({'coef': fit.params, 'holm_p': multipletests(fit.pvalues, method='holm')[1]})
    print(f'\nOLS for {col} (adj. R2 = {fit.rsquared_adj:.3f})\n{out.round(4).to_string()}')

requests, trials = pd.read_csv('my_requests.csv'), pd.read_csv('my_trials.csv')
if 'n_processes' in trials:
    expected = trials.system.map({'train': 4}).fillna(1)
    bad = trials.n_processes < expected
    if bad.any():
        print(f'Excluded {bad.sum()} trials where a Locust process did not start (see process_logs warnings)')
        trials = trials[~bad]

print('=' * 70, '\nRQ2: response time per request')
pairwise(requests, 'response_time')
print('\n' + '=' * 70, '\nRQ3: response time per trial')
ols(trials, 'response_time')

for col, title in [('energy_j', 'RQ1: energy per trial (HWiNFO CPU package, J)'),
                   ('cpu_cores', 'Energy proxy: CPU cores used per trial')]:
    if col in trials and trials[col].notna().any():
        t = trials.dropna(subset=[col])
        print('\n' + '=' * 70, f'\n{title}   ({len(t)} trials)')
        pairwise(t, col)
        ols(t, col)

trials[['system', 'users', 'granu', 'response_time']].to_csv('average_response_times.csv', index=False)
print('\nFailure rate by configuration:\n', trials.pivot_table('failure_rate', ['system', 'granu'], 'users').round(3))
if 'n_requests' in trials:
    print('\nActual requests per second (n_requests / 120 s):\n',
          (trials.pivot_table('n_requests', ['system', 'granu'], 'users') / 120).round(1))
