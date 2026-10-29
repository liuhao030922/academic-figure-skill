"""Grouped bars with seed-range whiskers (synthetic data): python3 examples/bars.py [output_dir]"""
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_style import *  # noqa: E402,F403

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
conditions = ["Low", "Mid", "60$\\times$", "200$\\times$"]
runs = {  # policy -> per-condition list of seed values
    "Baseline": [[0.90, 0.91], [0.85, 0.80], [0.40], [0.22, 0.23]],
    "Ours": [[0.92, 0.93], [0.88, 0.86], [0.55], [0.30, 0.34]],
}
colors = {"Baseline": BASELINE, "Ours": METHOD}

use_venue("ieee")
fig, ax = plt.subplots(figsize=figsize("column", 2.2))
width = 0.38
for offset, policy in [(-width / 2, "Baseline"), (width / 2, "Ours")]:
    for i, values in enumerate(runs[policy]):
        mean = statistics.fmean(values)
        ax.bar(i + offset, mean, width, label=policy if i == 0 else None, **bar_style(colors[policy]))
        range_whisker(ax, i + offset, mean, values)
        ax.text(i + offset, max(values) + 0.015, f"{mean:.2f}", ha="center", va="bottom", fontsize=5.6, color=INK)
ax.set_ylim(0, 1.05)
target_line(ax, 0.90, "target 0.90", 3.55)
group_separator(ax, 1.5)
ax.set_xticks(range(len(conditions)), conditions)
ax.set_ylabel("Attainment")
panel_title(ax, "(a) SLO attainment")
paper_axis(ax)
handles, labels = ax.get_legend_handles_labels()
top_legend(fig, handles + [range_legend_handle()], labels + ["Seed range"], ncol=3, top=0.85)
save_paper(fig, out / "bars")
print(f"Wrote {out / 'bars.pdf'}")
