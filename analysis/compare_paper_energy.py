"""RQ1 energy: our results vs the paper (Table V / VI), same method as the paper.

The paper removed outliers with the IQR rule (per system, on the energy
distribution) BEFORE the Mann-Whitney U tests. This script runs the pairwise
tests both without and with that IQR filter, so our numbers can be compared
with the paper's Table VI like for like.

Cliff's d sign follows the paper: d(A vs B) > 0 means A consumes MORE than B
(e.g. 'fine vs coarse' = +0.221 in the paper's Pet Clinic results).

Usage (inside ~/sde/analysis, venv active):
    python compare_paper_energy.py > results_compare_paper.txt
Optional: python compare_paper_energy.py path/to/my_trials.csv
"""
import sys
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

path = sys.argv[1] if len(sys.argv) > 1 else "my_trials.csv"
df = pd.read_csv(path)
df["system"] = df["system"].astype(str).str.strip().str.lower()
df["granu"] = df["granu"].astype(str).str.strip().str.lower()

ORDER = ["fine", "medium", "coarse"]          # finer first, as in the paper
PAPER = {  # Table V means (J) and Table VI (Holm p, Cliff's d)
    "pet": {"mean": {"coarse": 3250.27, "medium": 3328.89, "fine": 3377.24},
            "pairs": {("fine", "medium"): (0.152, None),
                      ("fine", "coarse"): (0.001, 0.221),
                      ("medium", "coarse"): (0.012, 0.168)}},
    "train": {"mean": {"coarse": 3527.14, "medium": 4475.92, "fine": 3988.30},
              "pairs": {("fine", "medium"): (0.057, None),
                        ("fine", "coarse"): (0.0009, 0.503),
                        ("medium", "coarse"): (0.0009, 0.397)}},
}


def cliffs_d(a, b):
    a = np.asarray(a)[:, None]
    b = np.asarray(b)[None, :]
    return float(((a > b).sum() - (a < b).sum()) / (a.size * b.size))


def magnitude(d):
    d = abs(d)
    return ("negligible" if d < 0.147 else "small" if d < 0.33
            else "medium" if d < 0.474 else "large")


def iqr_filter(sub):
    q1, q3 = sub["energy_j"].quantile([0.25, 0.75])
    iqr = q3 - q1
    keep = sub["energy_j"].between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    return sub[keep], int((~keep).sum())


for s in sorted(df["system"].unique()):
    full = df[df["system"] == s]
    grans = [g for g in ORDER if g in full["granu"].unique()]
    paper = PAPER.get(s, {})
    print("=" * 70)
    print(f"SYSTEM: {s}")

    # descriptive: mean and % change vs coarse, ours vs paper
    print("\nMean energy (J) and change vs coarse")
    print(f"{'granu':8s} {'ours':>9s} {'ours %':>8s} {'paper':>9s} {'paper %':>8s}")
    oc = full.loc[full["granu"] == "coarse", "energy_j"].mean()
    pc = paper["mean"]["coarse"]
    for g in reversed(grans):
        om = full.loc[full["granu"] == g, "energy_j"].mean()
        pm = paper["mean"][g]
        print(f"{g:8s} {om:9.1f} {100*(om/oc-1):+7.1f}% {pm:9.1f} {100*(pm/pc-1):+7.1f}%")

    for label, data, removed in [("WITHOUT outlier removal", full, 0),
                                 ("WITH IQR outlier removal (paper method)",
                                  *iqr_filter(full))]:
        print(f"\n{label}: n = {len(data)}, removed = {removed}")
        rows = []
        for a, b in combinations(grans, 2):
            x = data.loc[data["granu"] == a, "energy_j"]
            y = data.loc[data["granu"] == b, "energy_j"]
            p = mannwhitneyu(x, y, alternative="two-sided").pvalue
            rows.append([f"{a} vs. {b}", p, cliffs_d(x, y), (a, b)])
        holm = multipletests([r[1] for r in rows], method="holm")[1]
        print(f"{'pair':18s} {'holm_p':>8s} {'cliff_d':>8s} {'size':>11s}"
              f" | {'paper_p':>8s} {'paper_d':>8s}")
        for r, hp in zip(rows, holm):
            pp, pd_ = paper["pairs"].get(r[3], (None, None))
            pps = "-" if pp is None else ("<0.001" if pp < 0.001 else f"{pp:.3f}")
            pds = "-" if pd_ is None else f"{pd_:.3f}"
            print(f"{r[0]:18s} {hp:8.4f} {r[2]:+8.3f} {magnitude(r[2]):>11s}"
                  f" | {pps:>8s} {pds:>8s}")
    print()
