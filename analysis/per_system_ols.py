"""Per-system OLS models for the SDE partial replication.

Fixes the pooled-OLS issue in stats.py: 'fine' exists only in Pet Clinic,
so pooling both systems confounds granularity with system. Here each system
gets its own models:
  Model A: metric ~ users + granularity        (baseline: 40 users, coarse)
  Model B: metric ~ users x granularity        (does the effect depend on load?)
  F-test B vs A tells whether the interaction is significant.
p-values are Holm-corrected within each model (same as stats.py).

Usage (inside ~/sde/analysis, venv active):
    python per_system_ols.py > results_per_system.txt
Optional: python per_system_ols.py path/to/my_trials.csv
"""
import re
import sys

import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multitest import multipletests

path = sys.argv[1] if len(sys.argv) > 1 else "my_trials.csv"
df = pd.read_csv(path)
print("file:", path)
print("columns:", list(df.columns))


def pick(cands):
    for c in cands:
        if c in df.columns:
            return c
    sys.exit(f"STOP: column not found, tried {cands}")


SYS = pick(["system"])
GRAN = pick(["granu", "granularity", "gran"])
USR = pick(["users", "n_users", "user"])
df[SYS] = df[SYS].astype(str).str.strip().str.lower()
df[GRAN] = df[GRAN].astype(str).str.strip().str.lower()
df[USR] = df[USR].astype(int)
metrics = [m for m in ["energy_j", "response_time", "cpu_cores"] if m in df.columns]
print("metrics:", metrics)


def clean(name):
    return re.sub(r"C\((\w+)[^\]]*\)\[T\.([^\]]+)\]", r"\1_\2", name)


def show(fit, title):
    holm = multipletests(fit.pvalues, method="holm")[1]
    out = pd.DataFrame({"coef": fit.params, "p": fit.pvalues, "holm_p": holm})
    out.index = [clean(i) for i in out.index]
    print(f"\n{title}  (adj. R2 = {fit.rsquared_adj:.3f}, n = {int(fit.nobs)})")
    print(out.round(4).to_string())


U = f"C({USR}, Treatment(reference=40))"
G = f"C({GRAN}, Treatment(reference='coarse'))"

for s in sorted(df[SYS].unique()):
    sub = df[df[SYS] == s]
    print("\n" + "=" * 70)
    print(f"SYSTEM: {s}   trials = {len(sub)}   "
          f"granularities = {sorted(sub[GRAN].unique())}")
    for y in metrics:
        a = smf.ols(f"{y} ~ {U} + {G}", data=sub).fit()
        b = smf.ols(f"{y} ~ {U} * {G}", data=sub).fit()
        show(a, f"[{s}] {y}  Model A: users + granularity")
        show(b, f"[{s}] {y}  Model B: users x granularity")
        f = anova_lm(a, b)
        print(f"  Interaction F-test (B vs A): F = {f['F'].iloc[1]:.3f}, "
              f"p = {f['Pr(>F)'].iloc[1]:.4g}")
