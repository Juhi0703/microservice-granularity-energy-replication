"""Report figure: energy and response time vs load, per system and granularity.

Mirrors the paper's Fig. 5 (energy) and Fig. 6 (response time), and makes the
Train Ticket users x granularity interaction visible.
Points = mean of 10 trials, error bars = standard deviation.

Usage (inside ~/sde/analysis, venv active):
    python plot_by_load.py            -> fig_by_load.png (+ fig_by_load.pdf)
Optional: python plot_by_load.py path/to/my_trials.csv
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

path = sys.argv[1] if len(sys.argv) > 1 else "my_trials.csv"
df = pd.read_csv(path)
df["system"] = df["system"].astype(str).str.strip().str.lower()
df["granu"] = df["granu"].astype(str).str.strip().str.lower()

# Fixed colour per granularity (validated categorical palette, slots 1-3),
# plus a distinct marker each so identity never relies on colour alone.
STYLE = {"coarse": ("#2a78d6", "o"), "medium": ("#eb6834", "s"),
         "fine": ("#1baf7a", "^")}
SYSTEMS = [("pet", "Pet Clinic"), ("train", "Train Ticket")]
METRICS = [("energy_j", "Energy per trial (J)"),
           ("response_time", "Mean response time (ms)")]
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED})
fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), constrained_layout=True)

for col, (sys_key, sys_name) in enumerate(SYSTEMS):
    sub = df[df["system"] == sys_key]
    for row, (metric, ylabel) in enumerate(METRICS):
        ax = axes[row, col]
        for g in ["coarse", "medium", "fine"]:
            d = sub[sub["granu"] == g]
            if d.empty:
                continue
            stats = d.groupby("users")[metric].agg(["mean", "std"])
            color, marker = STYLE[g]
            ax.errorbar(stats.index, stats["mean"], yerr=stats["std"],
                        color=color, marker=marker, markersize=7,
                        markeredgecolor="white", markeredgewidth=1.5,
                        linewidth=2, capsize=3, elinewidth=1, label=g)
        ax.set_xticks([40, 120, 200, 320, 400])
        ax.set_xlim(20, 420)
        ax.set_xlabel("Users (≈ requests / s)")
        ax.set_ylabel(ylabel)
        ax.set_title(sys_name, loc="left", fontsize=11, color=INK)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.legend(frameon=False, fontsize=9, loc="upper left")

fig.savefig("fig_by_load.png", dpi=200)
fig.savefig("fig_by_load.pdf")
print("saved fig_by_load.png and fig_by_load.pdf")
