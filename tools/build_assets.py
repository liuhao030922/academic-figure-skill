"""Regenerate every README image and the .mplstyle presets: python3 tools/build_assets.py

All figures use synthetic data.
"""
import io
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "examples")]
import gallery  # noqa: E402
from paper_style import *  # noqa: E402,F403

ASSETS = ROOT / "assets"
DPI = 250


def to_array(figure, dpi=DPI):
    """Rasterize a figure (tight bbox) into an RGB float array."""
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(figure)
    buffer.seek(0)
    return plt.imread(buffer)[..., :3]


def save(figure, name, dpi=DPI):
    figure.savefig(ASSETS / name, dpi=dpi, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(figure)
    print(f"Wrote assets/{name}")


def image_axis(axis, image, title=None):
    axis.imshow(image, interpolation="lanczos")
    axis.set_axis_off()
    if title:
        axis.set_title(title, fontsize=9, pad=6, loc="left")


def build_styles():
    for name in VENUES:
        write_mplstyle(name, ROOT / "styles" / f"{name}.mplstyle")
    print(f"Wrote styles/*.mplstyle ({', '.join(VENUES)})")


def build_gallery():
    with plt.rc_context(venue_rc("ieee")):
        save(gallery.gallery_figure(), "gallery.png", dpi=200)


SAMPLE = {  # condition -> (baseline seeds, method seeds)
    "Low": ([0.92, 0.94, 0.93], [0.95, 0.96, 0.94]),
    "Mid": ([0.80, 0.84, 0.83], [0.90, 0.92, 0.89]),
    "High": ([0.51, 0.55, 0.53], [0.73, 0.76, 0.74]),
    "Peak": ([0.29, 0.33, 0.31], [0.58, 0.63, 0.61]),
}


def build_before_after():
    names = list(SAMPLE)
    x = np.arange(len(names))
    means = {k: [np.mean(SAMPLE[n][k]) for n in names] for k in (0, 1)}
    errors = {k: [np.std(SAMPLE[n][k]) for n in names] for k in (0, 1)}

    # Default matplotlib figure, then scaled into a 3.45 in column like \includegraphics would.
    with plt.style.context("default"):
        figure, axis = plt.subplots()
        axis.bar(x - 0.2, means[0], 0.4, yerr=errors[0], label="Baseline", capsize=3)
        axis.bar(x + 0.2, means[1], 0.4, yerr=errors[1], label="Ours", capsize=3)
        axis.axhline(0.9, color="r", linestyle="--")
        axis.set_xticks(x, names)
        axis.set_ylabel("SLO attainment")
        axis.set_title("SLO attainment")
        axis.legend()
        before = to_array(figure, dpi=DPI * 3.45 / 6.4)

    with plt.rc_context(venue_rc("ieee")):
        figure, axis = plt.subplots(figsize=figsize("column", 2.2, venue="ieee"))
        for offset, key, color, label in ((-0.19, 0, BASELINE, "Baseline"), (0.19, 1, METHOD, "Ours")):
            for i, name in enumerate(names):
                values = SAMPLE[name][key]
                axis.bar(i + offset, np.mean(values), 0.38, label=label if i == 0 else None, **bar_style(color))
                range_whisker(axis, i + offset, np.mean(values), values)
        axis.set_ylim(0, 1.3)
        axis.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        target_line(axis, 0.90, "target 0.90", 3.6)
        axis.set_xticks(x, names)
        axis.set_ylabel("SLO attainment")
        panel_title(axis, "(a) SLO attainment")
        paper_axis(axis)
        handles, labels = axis.get_legend_handles_labels()
        axis.legend(handles + [range_legend_handle()], labels + ["Seed range"], ncol=3, loc="upper left",
                    handlelength=1.0, columnspacing=0.8)
        after = to_array(figure)

    figure, axes = plt.subplots(1, 2, figsize=(9, 3.6), gridspec_kw={"wspace": 0.06})
    image_axis(axes[0], before, "Before: matplotlib defaults, scaled to column width")
    image_axis(axes[1], after, "After: paper-figures, IEEE preset")
    for axis in axes:
        axis.set_anchor("N")
    save(figure, "before_after.png", dpi=170)


def build_venues():
    shown = [("ieee", "IEEE · 3.5 in column · Times"), ("neurips", "NeurIPS · 5.5 in text · Times"),
             ("article", "LaTeX article · 4.77 in · Computer Modern")]
    images = []
    for name, _ in shown:
        with plt.rc_context(venue_rc(name)):
            figure, axis = plt.subplots(figsize=figsize("column", 1.9, venue=name))
            gallery.draw_line_band(axis)
            images.append(to_array(figure))
    # Keep true relative widths so the size difference between venues is visible.
    widths = [image.shape[1] for image in images]
    figure, axes = plt.subplots(1, 3, figsize=(16, 3.4), gridspec_kw={"width_ratios": widths, "wspace": 0.05})
    for axis, image, (_, title) in zip(axes, images, shown):
        image_axis(axis, image, title)
        axis.set_anchor("S")
    save(figure, "venues.png", dpi=110)


# Machado et al. (2009) dichromacy matrices at full severity, applied in linear RGB.
CVD = {
    "Protanopia": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "Deuteranopia": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    "Tritanopia": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def simulate(image, matrix):
    image = image.astype(np.float64)
    linear = np.where(image <= 0.04045, image / 12.92, ((image + 0.055) / 1.055) ** 2.4)
    with np.errstate(all="ignore"):  # NumPy's Accelerate matmul raises spurious warnings on macOS
        mixed = np.clip(linear @ np.asarray(matrix).T, 0, 1)
    return np.where(mixed <= 0.0031308, mixed * 12.92, 1.055 * mixed ** (1 / 2.4) - 0.055)


def build_cvd():
    swatches = [("Method", METHOD), ("Baseline", BASELINE), ("Orange", ORANGE), ("Teal", TEAL),
                ("Red", RED), ("Gray", GRAY)]
    with plt.rc_context(venue_rc("ieee")):
        figure, axes = plt.subplots(1, 3, figsize=(7.16, 1.75), gridspec_kw={"width_ratios": [0.8, 1.1, 1.1],
                                                                             "wspace": 0.45})
        for index, (name, color) in enumerate(swatches):
            axes[0].add_patch(plt.Rectangle((0, -index), 0.55, 0.75, facecolor=color, edgecolor=EDGE,
                                            linewidth=0.5))
            axes[0].text(0.68, -index + 0.37, name, va="center", fontsize=7)
        axes[0].set_xlim(0, 2.0)
        axes[0].set_ylim(-len(swatches) + 0.8, 0.9)
        axes[0].set_axis_off()
        gallery.draw_stacked_breakdown(axes[1])
        axes[1].get_legend().remove()
        gallery.draw_line_band(axes[2])
        source = to_array(figure, dpi=200)

    rows = [("Normal vision", source)] + [(name, simulate(source, matrix)) for name, matrix in CVD.items()]
    height = source.shape[0] / source.shape[1] * 9
    figure, axes = plt.subplots(len(rows), 1, figsize=(9, height * len(rows) * 1.12))
    for axis, (name, image) in zip(axes, rows):
        image_axis(axis, image, name)
    figure.subplots_adjust(hspace=0.25)
    save(figure, "colorblind.png", dpi=130)


def build_social_preview():
    with plt.rc_context(venue_rc("ieee")):
        thumbs = []
        for draw in (gallery.draw_grouped_bars, gallery.draw_line_band, gallery.draw_heatmap, gallery.draw_cdf):
            figure, axis = plt.subplots(figsize=(2.6, 1.9))
            draw(axis)
            thumbs.append(to_array(figure, dpi=170))

        figure = plt.figure(figsize=(12.8, 6.4), dpi=100)
        figure.patch.set_facecolor("white")
        figure.add_artist(plt.Rectangle((0, 0), 0.012, 1, transform=figure.transFigure, color=METHOD))
        figure.text(0.05, 0.74, "Academic Figure Skill", fontsize=40, color=INK)
        figure.text(0.05, 0.64, "Publication-ready matplotlib figures, as a Claude skill", fontsize=17,
                    color=MUTED_INK)
        for i, line in enumerate(["IEEE · ACM · USENIX · ICML · NeurIPS presets",
                                  "Nine research chart forms",
                                  "Colorblind-checked soft palette",
                                  "Claude Code · Claude app · plain Python"]):
            figure.text(0.05, 0.47 - i * 0.075, f"—  {line}", fontsize=15, color=INK)
        figure.text(0.05, 0.08, "github.com/liuhao030922/academic-figure-skill", fontsize=13, color=MUTED_INK)
        for index, image in enumerate(thumbs):
            row, column = divmod(index, 2)
            axis = figure.add_axes([0.53 + column * 0.235, 0.52 - row * 0.44, 0.22, 0.4])
            image_axis(axis, image)
        # Exact 1280×640 canvas: GitHub crops anything else.
        with plt.rc_context({"savefig.bbox": "standard"}):
            figure.savefig(ASSETS / "social_preview.png", dpi=100, facecolor="white")
        plt.close(figure)
    print("Wrote assets/social_preview.png (1280×640)")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    (ROOT / "styles").mkdir(exist_ok=True)
    build_styles()
    build_gallery()
    build_before_after()
    build_venues()
    build_cvd()
    build_social_preview()
