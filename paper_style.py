"""IEEE-paper matplotlib style (from the CS555 midterm figures).

Usage:
    import sys; sys.path.insert(0, "<directory containing paper_style.py>")
    from paper_style import *
    with plt.rc_context(PAPER_RC):
        fig, ax = plt.subplots(figsize=SINGLE_COLUMN)
        ax.bar(x, y, **bar_style(BASELINE))
        paper_axis(ax)
        save_paper(fig, "out/figure")
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Times-like serif to match IEEEtran body text; TrueType fonts embedded in the PDF.
PAPER_RC = {
    "font.family": "STIXGeneral",
    "mathtext.fontset": "stix",
    "font.size": 7.5,
    "axes.labelsize": 7.5,
    "axes.titlesize": 8,
    "axes.linewidth": 0.6,
    "axes.edgecolor": "#3a3a3a",
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 2.5,
    "ytick.major.size": 2.5,
    "legend.fontsize": 7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
}

# Figure sizes in inches (IEEE column = 3.5 in, page width = 7.16 in).
SINGLE_COLUMN = (3.45, 2.2)
SINGLE_COLUMN_TWO_PANEL = (3.45, 3.55)
SINGLE_COLUMN_STRIP = (3.45, 1.45)
DOUBLE_COLUMN = (7.0, 2.4)

# Soft fills with thin dark outlines. The baseline is always gray; the
# proposed method takes the blue. Extra categories use the order in PALETTE.
BASELINE = "#a6a6a6"
METHOD = "#6b9bc8"
EDGE = "#2b2b2b"
INK = "#1a1a1a"
MUTED_INK = "#3a3a3a"
GRID = "#e3e3e3"
SEPARATOR = "#bdbdbd"

# Categorical order for stacked/multi-series charts: good, warn, neutral, bad.
TEAL = "#79c0b6"
ORANGE = "#f4a65c"
GRAY = "#b3b3b3"
RED = "#ec7f7c"
PALETTE = [METHOD, TEAL, ORANGE, RED, BASELINE, GRAY]
LABEL_ON_FILL = "#0b0b0b"  # in-bar text is near-black on every fill above


def bar_style(color, **extra):
    """Outlined bar keyword arguments shared by bar() and barh()."""
    return {"color": color, "edgecolor": EDGE, "linewidth": 0.5, "zorder": 2, **extra}


def paper_axis(axis, grid_axis="y"):
    """Open top/right spines, light grid behind the data."""
    axis.spines[["top", "right"]].set_visible(False)
    if grid_axis:
        axis.grid(axis=grid_axis, color=GRID, linewidth=0.5)
    axis.set_axisbelow(True)


def panel_title(axis, text):
    """Left-aligned '(a) ...' panel title."""
    axis.set_title(text, loc="left", fontsize=8, pad=3)


def range_whisker(axis, x, mean, values):
    """Min–max whisker over seeds; skipped when only one run exists."""
    if len(values) > 1:
        axis.errorbar(x, mean, yerr=[[mean - min(values)], [max(values) - mean]], fmt="none",
                      ecolor=INK, elinewidth=0.7, capsize=1.8, capthick=0.7, zorder=3)


def target_line(axis, y, label, x_text):
    """Dashed reference line (e.g. an SLO target) with a small right-aligned label."""
    axis.axhline(y, color=MUTED_INK, linestyle=(0, (4, 2)), linewidth=0.8, zorder=1)
    axis.text(x_text, y + 0.03 * (axis.get_ylim()[1] - axis.get_ylim()[0]), label,
              ha="right", va="bottom", fontsize=6.5, color=MUTED_INK)


def group_separator(axis, x):
    """Dotted vertical divider between groups of conditions."""
    axis.axvline(x, color=SEPARATOR, linewidth=0.5, linestyle=(0, (2, 2)), zorder=1)


def range_legend_handle():
    """Legend entry explaining the whiskers."""
    return plt.Line2D([], [], marker="|", linestyle="", markersize=6, markeredgecolor=INK, markeredgewidth=0.7)


def top_legend(figure, handles, labels, ncol, top=0.9, x=0.55):
    """Frameless legend above the panels without overlapping titles."""
    figure.legend(handles, labels, ncol=ncol, frameon=False, loc="lower center",
                  bbox_to_anchor=(x, top + 0.025), handlelength=1.2, columnspacing=1.0)
    figure.subplots_adjust(top=top)


def line_with_band(axis, x, mean, low, high, color, label, marker="o"):
    """Mean line with small markers over a translucent band (std, CI, or min–max)."""
    axis.fill_between(x, low, high, color=color, alpha=0.22, linewidth=0, zorder=1)
    axis.plot(x, mean, color=color, linewidth=1.0, marker=marker, markersize=2.2, markeredgewidth=0,
              label=label, zorder=2)


def inside_legend(axis, loc="upper right"):
    """Small framed legend inside the plot area, for line charts with free space."""
    axis.legend(loc=loc, frameon=True, fancybox=False, framealpha=0.9, edgecolor="#cccccc",
                handlelength=1.6, borderpad=0.4, labelspacing=0.3)


def save_paper(figure, path_without_suffix):
    """Vector PDF, tight bounding box, white background."""
    figure.savefig(f"{path_without_suffix}.pdf", bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(figure)
