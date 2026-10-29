"""Nine common research chart forms in the paper style (synthetic data).

python3 examples/gallery.py [output_dir]   # one PDF per chart
Each draw_* function takes an axis and fills it; copy the one you need.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paper_style import *  # noqa: E402,F403

SEED = 7


def draw_grouped_bars(ax):
    """Mean of seeds per condition, min–max whiskers, target line."""
    rng = np.random.default_rng(SEED)
    conditions = ["Low", "Mid", "High", "Peak"]
    base = {"Baseline": [0.93, 0.84, 0.52, 0.31], "Ours": [0.95, 0.91, 0.78, 0.62]}
    width = 0.38
    for offset, (policy, color) in zip((-width / 2, width / 2), (("Baseline", BASELINE), ("Ours", METHOD))):
        for i, center in enumerate(base[policy]):
            values = center + rng.normal(0, 0.025, 3)
            ax.bar(i + offset, values.mean(), width, label=policy if i == 0 else None, **bar_style(color))
            range_whisker(ax, i + offset, values.mean(), values)
    ax.set_ylim(0, 1.3)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    target_line(ax, 0.90, "target", 3.6)
    ax.set_xticks(range(4), conditions)
    ax.set_ylabel("SLO attainment")
    ax.legend(ncol=2, loc="upper left", handlelength=1.0, columnspacing=0.8)
    paper_axis(ax)


def draw_stacked_breakdown(ax):
    """Share of requests by outcome; labels on segments ≥ 8 %."""
    categories = [("Met", TEAL), ("Late start", ORANGE), ("Slow decode", GRAY), ("Both", RED)]
    shares = np.array([[0.22, 0.18, 0.02, 0.58], [0.47, 0.12, 0.06, 0.35]])
    left = np.zeros(2)
    for column, (name, color) in enumerate(categories):
        ax.barh([0, 1], shares[:, column], left=left, height=0.55, label=name, **bar_style(color))
        for row in range(2):
            if shares[row, column] >= 0.08:
                ax.text(left[row] + shares[row, column] / 2, row, f"{shares[row, column]:.0%}", ha="center",
                        va="center", color=LABEL_ON_FILL, fontsize=6)
        left += shares[:, column]
    ax.set_yticks([0, 1], ["Baseline", "Ours"])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 0.5, 1], ["0%", "50%", "100%"])
    ax.set_xlabel("Share of requests")
    ax.tick_params(axis="y", length=0)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.42), handlelength=0.9, handletextpad=0.3,
              columnspacing=0.6, fontsize=6)


def draw_line_band(ax):
    """Metric over a swept parameter, mean ± std across seeds."""
    rng = np.random.default_rng(SEED)
    x = np.arange(4, 65, 4)
    for (label, start, end), color, marker in zip([("Ours", 0.5, 0.12), ("Baseline A", 0.7, 0.4),
                                                   ("Baseline B", 0.65, 0.5)], PALETTE, MARKERS):
        runs = end + (start - end) * np.exp(-(x - 4) / 15) + rng.normal(0, 0.03, (5, len(x)))
        mean, std = runs.mean(0), runs.std(0)
        line_with_band(ax, x, mean, mean - std, mean + std, color, label, marker=marker)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("Number of agents")
    ax.set_ylabel("Error")
    paper_axis(ax, grid_axis=None)
    inside_legend(ax)


def draw_cdf(ax):
    """Latency CDF on a log axis with p99 markers."""
    rng = np.random.default_rng(SEED)
    for (label, mu, sigma), color, marker in zip([("Ours", -1.6, 0.5), ("Baseline", -1.2, 0.8)],
                                                 (METHOD, ORANGE), MARKERS):
        cdf_line(ax, rng.lognormal(mu, sigma, 4000), color, label, marker=marker)
    ax.set_xscale("log")
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("TTFT (s)")
    ax.set_ylabel("CDF")
    ax.text(0.98, 0.06, "markers: p99", transform=ax.transAxes, ha="right", fontsize=6, color=MUTED_INK)
    paper_axis(ax, grid_axis="both")
    ax.legend(loc="upper left")


def draw_heatmap(ax):
    """Parameter sweep with a sequential ramp and a value in every cell."""
    rng = np.random.default_rng(SEED)
    rates = np.linspace(0.2, 1.0, 5)
    budgets = np.array([1, 2, 4, 8])
    matrix = np.clip(1 - np.outer(1 / np.sqrt(budgets), rates) * 0.9 + rng.normal(0, 0.02, (4, 5)), 0, 1)
    image = annotated_heatmap(ax, matrix, [f"{r:.1f}" for r in rates], [f"{b}k" for b in budgets])
    ax.set_xlabel("Load (req/s per GPU)")
    ax.set_ylabel("KV budget")
    colorbar = ax.figure.colorbar(image, ax=ax, fraction=0.05, pad=0.03)
    colorbar.outline.set_linewidth(0.4)
    colorbar.ax.tick_params(width=0.4, length=2, labelsize=6)


def draw_pareto(ax):
    """Throughput vs. latency trade-off; the method's frontier is drawn as a line."""
    rng = np.random.default_rng(SEED)
    baseline_x = rng.uniform(20, 90, 14)
    baseline_y = 0.4 + 2.2 / (110 - baseline_x) * 40 + rng.normal(0, 0.15, 14)
    ours_x = np.linspace(25, 95, 7)
    ours_y = 0.3 + 1.2 / (110 - ours_x) * 40
    ax.scatter(baseline_x, baseline_y, s=10, color=BASELINE, edgecolor=EDGE, linewidth=0.4, marker="s",
               label="Baseline configs", zorder=2)
    ax.plot(ours_x, ours_y, color=METHOD, marker="o", markersize=3.5, markeredgecolor=EDGE,
            markeredgewidth=0.4, label="Ours (frontier)", zorder=3)
    ax.text(0.97, 0.04, "lower right is better", transform=ax.transAxes, ha="right", fontsize=6,
            color=MUTED_INK)
    ax.set_xlabel("Throughput (req/s)")
    ax.set_ylabel("p95 latency (s)")
    paper_axis(ax, grid_axis="both")
    ax.legend(loc="upper left")


def draw_ablation(ax):
    """Each component removed; delta from the full method, full method highlighted."""
    rows = ["Full method", "w/o pinning", "w/o admission", "w/o offload", "w/o all"]
    scores = np.array([0.82, 0.74, 0.69, 0.77, 0.51])
    colors = [METHOD] + [BASELINE] * 4
    y = np.arange(len(rows))
    ax.barh(y, scores, height=0.6, **bar_style(colors))
    for index, score in enumerate(scores):
        delta = "" if index == 0 else f"  ({score - scores[0]:+.2f})"
        ax.text(score + 0.01, index, f"{score:.2f}{delta}", va="center", fontsize=6, color=INK)
    ax.set_yticks(y, rows)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.1)
    ax.set_xlabel("SLO attainment")
    ax.tick_params(axis="y", length=0)
    paper_axis(ax, grid_axis="x")


def draw_timeseries(ax):
    """Resource usage over time with a shaded burst window."""
    rng = np.random.default_rng(SEED)
    t = np.arange(0, 300)
    burst = (t > 110) & (t < 190)
    base = 0.45 + 0.4 * burst + rng.normal(0, 0.03, len(t)).cumsum() * 0.05
    ours = np.clip(base - 0.12 * burst, 0, 1)
    baseline = np.clip(base + 0.05 * burst, 0, 1)
    ax.axvspan(110, 190, color=GRID, linewidth=0, zorder=0)
    ax.text(150, 1.04, "burst", ha="center", fontsize=6, color=MUTED_INK)
    ax.plot(t, baseline, color=ORANGE, label="Baseline", linewidth=0.9)
    ax.plot(t, ours, color=METHOD, label="Ours", linewidth=0.9)
    ax.axhline(0.9, color=MUTED_INK, linestyle=(0, (4, 2)), linewidth=0.6)
    ax.text(298, 0.92, "limit", ha="right", va="bottom", fontsize=6, color=MUTED_INK)
    ax.set_ylim(0, 1.12)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("KV cache usage")
    paper_axis(ax, grid_axis=None)
    ax.legend(loc="lower center", ncol=2)


def draw_boxplot(ax):
    """Per-method distribution: box = IQR, line = median."""
    rng = np.random.default_rng(SEED)
    data = [rng.lognormal(m, s, 300) for m, s in [(0.0, 0.45), (-0.2, 0.35), (-0.5, 0.25)]]
    paper_boxplot(ax, data, ["FCFS", "Priority", "Ours"], [BASELINE, ORANGE, METHOD])
    ax.set_ylabel("Job completion (min)")
    paper_axis(ax)


CHARTS = [
    ("(a) Grouped bars", draw_grouped_bars),
    ("(b) Stacked breakdown", draw_stacked_breakdown),
    ("(c) Line + band", draw_line_band),
    ("(d) CDF", draw_cdf),
    ("(e) Heatmap", draw_heatmap),
    ("(f) Trade-off", draw_pareto),
    ("(g) Ablation", draw_ablation),
    ("(h) Time series", draw_timeseries),
    ("(i) Distribution", draw_boxplot),
]


def gallery_figure():
    """All nine charts on one double-column page."""
    figure, axes = plt.subplots(3, 3, figsize=figsize("text", 6.3))
    for axis, (title, draw) in zip(axes.flat, CHARTS):
        draw(axis)
        axis.set_title(title, loc="left", fontsize=8, pad=4)
    figure.subplots_adjust(hspace=0.85, wspace=0.55)
    return figure


if __name__ == "__main__":
    use_venue("ieee")
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    for title, draw in CHARTS:
        fig, ax = plt.subplots(figsize=figsize("column", 2.2))
        draw(ax)
        stem = draw.__name__.removeprefix("draw_")
        save_paper(fig, out / stem)
        print(f"Wrote {out / stem}.pdf")
