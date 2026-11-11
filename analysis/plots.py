# usage: python plots.py   (reads my_trials.csv; writes one fig_<measure>.png per measure)
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import seaborn as sns

t = pd.read_csv('my_trials.csv')
for col, label in [('response_time', 'Response time (ms)'),
                   ('energy_j', 'Energy per trial (J, CPU package)'),
                   ('cpu_cores', 'CPU cores used')]:
    if col not in t or t[col].isna().all():
        continue
    g = sns.catplot(data=t.dropna(subset=[col]), x='users', y=col, hue='granu', col='system', kind='bar',
                    hue_order=['coarse', 'medium', 'fine'], sharey=False, height=4)
    g.set_axis_labels('Request frequency (users = requests/s)', label)
    g.savefig(f'fig_{col}.png', dpi=200)
    print(f'saved fig_{col}.png')
