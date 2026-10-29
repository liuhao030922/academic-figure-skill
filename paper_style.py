"""Publication-ready matplotlib style for academic papers.

Usage:
    import sys; sys.path.insert(0, "<directory containing paper_style.py>")
    from paper_style import *

    venue = use_venue("ieee")          # ieee | acm | usenix | icml | neurips | article
    fig, ax = plt.subplots(figsize=figsize("column", 2.2))
    ax.bar(x, y, **bar_style(METHOD))
    paper_axis(ax)
    save_paper(fig, "out/figure")      # writes out/figure.pdf

`PAPER_RC` (the IEEE preset) still works with `plt.rc_context(PAPER_RC)`.
"""
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.colors import LinearSegmentedColormap

# ---------------------------------------------------------------- colors

# Soft fills with thin dark outlines. The baseline is always gray; the
# proposed method takes the blue.
BASELINE = "#a6a6a6"
METHOD = "#6b9bc8"
EDGE = "#2b2b2b"
INK = "#1a1a1a"
MUTED_INK = "#3a3a3a"
GRID = "#e3e3e3"
SEPARATOR = "#bdbdbd"

# Outcome categories for stacked charts: good, warn, neutral, bad. The neutral
# gray is light so it stays apart from teal under deuteranopia.
TEAL = "#79c0b6"
ORANGE = "#f4a65c"
GRAY = "#d9d9d9"
RED = "#ec7f7c"
LABEL_ON_FILL = "#0b0b0b"  # in-bar text is near-black on every fill above

# Series order for lines: method first, then baselines. Pair each color with
# its marker so series stay distinct without color.
PALETTE = [METHOD, ORANGE, TEAL, RED, BASELINE]
MARKERS = ["o", "s", "^", "D", "v"]

SEQUENTIAL = ["#f3f7fb", "#c6d9ec", METHOD, "#2f5f8f", "#1b3a5c"]


def sequential_cmap():
    """One-hue light-to-dark blue ramp for magnitudes (heatmaps)."""
    return LinearSegmentedColormap.from_list("paper_blues", SEQUENTIAL)


# ---------------------------------------------------------------- venues


@dataclass(frozen=True)
class Venue:
    name: str
    column: float  # \columnwidth in inches
    text: float  # \textwidth in inches
    serif: tuple
    mathtext: str
    font_size: float


_TIMES = ("STIXGeneral", "Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif")
_LIBERTINE = ("Linux Libertine O", "Linux Libertine", "Libertinus Serif") + _TIMES
_COMPUTER_MODERN = ("cmr10", "CMU Serif", "Computer Modern Roman", "DejaVu Serif")

VENUES = {
    "ieee": Venue("IEEE (IEEEtran)", 3.50, 7.16, _TIMES, "stix", 7.5),
    "acm": Venue("ACM (acmart sigconf)", 3.33, 7.00, _LIBERTINE, "stix", 7.5),
    "usenix": Venue("USENIX", 3.33, 7.00, _TIMES, "stix", 7.5),
    "icml": Venue("ICML", 3.25, 6.75, _TIMES, "stix", 7.5),
    "neurips": Venue("NeurIPS / ICLR", 5.50, 5.50, _TIMES, "stix", 8.5),
    "article": Venue("LaTeX article / thesis", 4.77, 4.77, _COMPUTER_MODERN, "cm", 8.5),
}
_current = VENUES["ieee"]


def venue_rc(name="ieee"):
    """rcParams for a venue: matching serif font, sizes relative to its body text."""
    venue = VENUES[name]
    base = venue.font_size
    rc = {
        "font.family": "serif",
        "font.serif": list(venue.serif),
        "mathtext.fontset": venue.mathtext,
        "font.size": base,
        "axes.labelsize": base,
        "axes.titlesize": base + 0.5,
        "axes.linewidth": 0.6,
        "axes.edgecolor": MUTED_INK,
        "axes.labelcolor": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": cycler(color=PALETTE),
        "xtick.color": MUTED_INK,
        "ytick.color": MUTED_INK,
        "xtick.labelcolor": INK,
        "ytick.labelcolor": INK,
        "xtick.labelsize": base - 0.5,
        "ytick.labelsize": base - 0.5,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "legend.fontsize": base - 0.5,
        "legend.frameon": False,
        "lines.linewidth": 1.0,
        "lines.markersize": 2.2,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "savefig.facecolor": "white",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
    if venue.mathtext == "cm":
        # cmr10 has no Unicode minus; render tick labels through mathtext instead.
        rc["axes.formatter.use_mathtext"] = True
        rc["axes.unicode_minus"] = False
    return rc


def use_venue(name="ieee"):
    """Apply a venue preset globally and make it the default for figsize()."""
    global _current
    _current = VENUES[name]
    plt.rcParams.update(venue_rc(name))
    return _current


def figsize(width="column", height=2.2, venue=None):
    """Figure size in inches: width is 'column', 'text', or a fraction of \\textwidth."""
    venue = VENUES[venue] if venue else _current
    if width == "column":
        inches = venue.column
    elif width == "text":
        inches = venue.text
    else:
        inches = venue.text * float(width)
    # A hair under the full width so tight bounding boxes never overflow the column.
    return (round(inches * 0.985, 2), height)


def write_mplstyle(name, path):
    """Write a venue preset as a .mplstyle file for plt.style.use()."""
    lines = [f"# paper-figures preset: {VENUES[name].name}"]
    for key, value in venue_rc(name).items():
        if key == "axes.prop_cycle":
            colors = ", ".join(f"'{color.lstrip('#')}'" for color in PALETTE)
            value = f"cycler('color', [{colors}])"
        elif isinstance(value, (list, tuple)):
            value = ", ".join(value)
        elif isinstance(value, str) and value.startswith("#"):
            value = value.lstrip("#")  # '#' starts a comment in .mplstyle
        lines.append(f"{key}: {value}")
    with open(path, "w") as handle:
        handle.write("\n".join(lines) + "\n")


PAPER_RC = venue_rc("ieee")

# IEEE sizes in inches, kept for existing scripts; prefer figsize().
SINGLE_COLUMN = (3.45, 2.2)
SINGLE_COLUMN_TWO_PANEL = (3.45, 3.55)
SINGLE_COLUMN_STRIP = (3.45, 1.45)
DOUBLE_COLUMN = (7.0, 2.4)

# ---------------------------------------------------------------- axes


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
    axis.set_title(text, loc="left", fontsize=plt.rcParams["axes.titlesize"], pad=3)


def group_separator(axis, x):
    """Dotted vertical divider between groups of conditions."""
    axis.axvline(x, color=SEPARATOR, linewidth=0.5, linestyle=(0, (2, 2)), zorder=1)


def target_line(axis, y, label, x_text):
    """Dashed reference line (e.g. an SLO target) with a small right-aligned label."""
    axis.axhline(y, color=MUTED_INK, linestyle=(0, (4, 2)), linewidth=0.8, zorder=1)
    axis.text(x_text, y + 0.03 * (axis.get_ylim()[1] - axis.get_ylim()[0]), label,
              ha="right", va="bottom", fontsize=plt.rcParams["font.size"] - 1, color=MUTED_INK)


# ---------------------------------------------------------------- marks


def range_whisker(axis, x, mean, values):
    """Min–max whisker over seeds; skipped when only one run exists."""
    if len(values) > 1:
        axis.errorbar(x, mean, yerr=[[mean - min(values)], [max(values) - mean]], fmt="none",
                      ecolor=INK, elinewidth=0.7, capsize=1.8, capthick=0.7, zorder=3)


def range_legend_handle():
    """Legend entry explaining the whiskers."""
    return plt.Line2D([], [], marker="|", linestyle="", markersize=6, markeredgecolor=INK, markeredgewidth=0.7)


def line_with_band(axis, x, mean, low, high, color, label, marker="o"):
    """Mean line with small markers over a translucent band (std, CI, or min–max)."""
    axis.fill_between(x, low, high, color=color, alpha=0.22, linewidth=0, zorder=1)
    axis.plot(x, mean, color=color, linewidth=1.0, marker=marker, markersize=2.2, markeredgewidth=0,
              label=label, zorder=2)


def cdf_line(axis, values, color, label, marker="o", mark_quantile=0.99):
    """Empirical CDF with one marker at a tail quantile (p99 by default)."""
    ordered = np.sort(np.asarray(values))
    if ordered.size == 0:
        raise ValueError("cdf_line() requires at least one value")
    fraction = np.arange(1, len(ordered) + 1) / len(ordered)
    axis.plot(ordered, fraction, color=color, linewidth=1.0, label=label, zorder=2)
    if mark_quantile is not None:
        tail = np.quantile(ordered, mark_quantile)
        axis.plot(tail, mark_quantile, marker=marker, color=color, markersize=3.5, markeredgecolor=EDGE,
                  markeredgewidth=0.4, zorder=3)


def annotated_heatmap(axis, matrix, xlabels, ylabels, fmt="{:.2f}"):
    """Sequential-blue heatmap with a value in every cell; text flips to white on dark cells."""
    matrix = np.asarray(matrix)
    image = axis.imshow(matrix, cmap=sequential_cmap(), aspect="auto")
    low, high = matrix.min(), matrix.max()
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = matrix[row, column]
            dark = (value - low) / (high - low or 1) > 0.6
            axis.text(column, row, fmt.format(value), ha="center", va="center",
                      fontsize=plt.rcParams["font.size"] - 1.5, color="white" if dark else INK)
    axis.set_xticks(range(len(xlabels)), xlabels)
    axis.set_yticks(range(len(ylabels)), ylabels)
    axis.tick_params(length=0)
    axis.spines[:].set_visible(False)
    return image


def paper_boxplot(axis, data, labels, colors):
    """Outlined boxes with a dark median, no fliers clutter (fliers as small open dots)."""
    parts = axis.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55,
                         medianprops={"color": INK, "linewidth": 0.9},
                         whiskerprops={"color": EDGE, "linewidth": 0.6},
                         capprops={"color": EDGE, "linewidth": 0.6},
                         flierprops={"marker": "o", "markersize": 1.8, "markerfacecolor": "none",
                                     "markeredgecolor": MUTED_INK, "markeredgewidth": 0.4})
    for box, color in zip(parts["boxes"], colors):
        box.set(facecolor=color, edgecolor=EDGE, linewidth=0.5)
    return parts


# ---------------------------------------------------------------- legends and output


def top_legend(figure, handles, labels, ncol, top=0.9, x=0.55):
    """Frameless legend above the panels without overlapping titles."""
    figure.legend(handles, labels, ncol=ncol, frameon=False, loc="lower center",
                  bbox_to_anchor=(x, top + 0.025), handlelength=1.2, columnspacing=1.0)
    figure.subplots_adjust(top=top)


def inside_legend(axis, loc="upper right"):
    """Small framed legend inside the plot area, for line charts with free space."""
    axis.legend(loc=loc, frameon=True, fancybox=False, framealpha=0.9, edgecolor="#cccccc",
                handlelength=1.6, borderpad=0.4, labelspacing=0.3)


def save_paper(figure, path_without_suffix):
    """Save a vector PDF, creating parent directories when needed."""
    output = Path(f"{path_without_suffix}.pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, bbox_inches="tight", pad_inches=0.02, facecolor="white")
    plt.close(figure)
    return output
