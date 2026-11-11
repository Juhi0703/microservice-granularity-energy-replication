# usage: python process_logs.py <system> <granularity> <run folder>
# e.g.   python process_logs.py pet coarse ~/sde/script_data/paper/experiment/pet_system/coarse
# Appends one row per trial to my_trials.csv and every successful request to my_requests.csv.
# Run it once per configuration; delete both CSVs to start over.
#
# Energy: reads every HWiNFO log in D:\SDE_results (hwinfo*.csv, any case) and, for each trial,
# averages "CPU Package Power [W]" over the first 110 s after the trial's first request
# (the paper used 11 PowerStat samples x 10 s = 110 s). energy_j = mean power x 110 s.
# Another folder: HWINFO='/mnt/d/other/hwinfo*.csv' python process_logs.py ...
import csv, glob, os, re, sys
from datetime import datetime, timedelta
import pandas as pd

LINE = re.compile(r'\[(?P<ts>[\d\-: ]+),\d+\] \S+/(?:INFO|ERROR)/locust: '
                  r'(?P<status>SUCCESS|FAILURE): \w+ \S+ (?P<rt>[\d.]+)ms')
WINDOW_S = 110
HWINFO_GLOB = os.environ.get('HWINFO', '/mnt/d/SDE_results/hwinfo*.[cC][sS][vV]')

system, granu, run = sys.argv[1], sys.argv[2], os.path.expanduser(sys.argv[3])
mult = 4 if system == 'train' else 1      # Train Ticket: 4 Locust processes per trial


def read_hwinfo(paths):
    """CPU Package Power [W] from HWiNFO CSV logs, indexed by Windows local time."""
    parts = []
    for p in paths:
        rows = list(csv.reader(open(p, encoding='cp1252', errors='replace')))
        if not rows:
            continue
        col = next((i for i, c in enumerate(rows[0]) if c.startswith('CPU Package Power')), None)
        if col is None:
            print(f'{p}: no "CPU Package Power" column, skipped')
            continue
        ts, watts = [], []
        for r in rows[1:]:
            if len(r) <= col or r[0] in ('', 'Date'):
                continue                      # HWiNFO repeats the header and adds a footer row
            try:
                d, m, y = map(int, r[0].split('.'))
                hh, mm, ss = r[1].split(':')
                ts.append(datetime(y, m, d, int(hh), int(mm)) + timedelta(seconds=float(ss)))
                watts.append(float(r[col]))
            except ValueError:
                continue
        parts.append(pd.Series(watts, index=pd.DatetimeIndex(ts)))
    if not parts:
        return None
    s = pd.concat(parts).sort_index()
    return s[~s.index.duplicated()]


cpu_files = glob.glob(os.path.join(run, 'cpu_*.csv'))
if cpu_files:
    cpu = pd.read_csv(cpu_files[0])
    cpu['ts'] = pd.to_datetime(cpu['ts'])
    cpu['cores'] = cpu['cpu_pct'].str.rstrip('%').astype(float) / 100
    cpu_total = cpu.groupby('ts')['cores'].sum()   # all containers together
else:
    print('No cpu_*.csv found: cpu_cores will be empty')
    cpu_total = None

hw_files = sorted(glob.glob(HWINFO_GLOB))
power = read_hwinfo(hw_files)
print(f'HWiNFO logs read: {len(hw_files)}' + ('' if power is not None else ' (no power data: energy_j will be empty)'))

trials, requests = [], []
for f in sorted(glob.glob(os.path.join(run, 'result05', granu, 'locustfile_*.log'))):
    _, _, users, _, _, it = os.path.basename(f)[:-4].split('_')
    if it == '0':
        continue                              # skip smoke tests
    users, ok, fail, stamps, starts = int(users) * mult, [], 0, [], 0
    for line in open(f):
        if 'Starting Locust' in line:
            starts += 1
        m = LINE.search(line)
        if not m:
            continue
        stamps.append(m['ts'])
        if m['status'] == 'SUCCESS':
            ok.append(float(m['rt']))
        else:
            fail += 1
    if not stamps:
        print(f'skipped (no requests logged): {f}')
        continue
    rt = pd.Series(ok, dtype=float)
    q1, q3 = rt.quantile([.25, .75])
    rt = rt[rt.between(q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1))]
    start, end = pd.to_datetime(min(stamps)), pd.to_datetime(max(stamps))
    cores = cpu_total[start:end].mean() if cpu_total is not None else float('nan')
    p_mean = float('nan')
    if power is not None:
        win = power[start:start + pd.Timedelta(seconds=WINDOW_S)]
        if len(win) >= 0.8 * WINDOW_S:        # at least 88 of 110 one-second samples
            p_mean = win.mean()
    trials.append({'system': system, 'users': users, 'granu': granu, 'trial': int(it),
                   'response_time': rt.mean(), 'failure_rate': fail / (fail + len(ok)),
                   'cpu_cores': cores, 'power_w': p_mean, 'energy_j': p_mean * WINDOW_S,
                   'n_requests': fail + len(ok), 'n_processes': starts,
                   'start': start.strftime('%Y-%m-%d %H:%M:%S')})
    requests += [{'system': system, 'users': users, 'granu': granu, 'response_time': r} for r in ok]

bad = [t for t in trials if t['n_processes'] < mult]
for t in bad:
    print(f"WARNING: users={t['users']} trial={t['trial']}: only {t['n_processes']} of {mult} Locust processes started "
          f"({t['n_requests']} requests) - rerun this configuration or exclude these trials")
no_energy = sum(pd.isna(t['energy_j']) for t in trials)
if power is not None and no_energy:
    print(f'NOTE: {no_energy} trials have no energy value (HWiNFO was not logging during them)')
for name, rows in [('my_trials.csv', trials), ('my_requests.csv', requests)]:
    pd.DataFrame(rows).to_csv(name, mode='a', header=not os.path.exists(name), index=False)
print(f'{len(trials)} trials added (expect 50 per configuration)')
print(pd.DataFrame(trials).groupby('users')[['response_time', 'failure_rate', 'cpu_cores', 'energy_j']].mean().round(2))
