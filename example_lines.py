"""Line + shaded band reference figure (synthetic data): python3 example_lines.py [output_dir]"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from paper_style import *  # noqa: E402,F403

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
rng = np.random.default_rng(0)
x = np.arange(3, 61)


def trials(start, end, decay, noise, n=5):
    """Synthetic metric that decays from start toward end, repeated over n seeds."""
    curve = end + (start - end) * np.exp(-(x - 3) / decay)
    return curve + rng.normal(0, noise, (n, len(x)))


panels = [
    ("(a) Error", "Average error", [("Ours", METHOD, 0.55, 0.15, 12, 0.04),
                                    ("Baseline A", ORANGE, 0.70, 0.38, 30, 0.05),
                                    ("Baseline B", TEAL, 0.65, 0.40, 25, 0.05)]),
    ("(b) Cost", "Cost", [("Ours", METHOD, 60, 8, 10, 3),
                          ("Baseline A", ORANGE, 80, 30, 30, 4),
                          ("Baseline B", TEAL, 85, 90, 20, 6)]),
]

with plt.rc_context(PAPER_RC):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.2))
    for axis, (title, ylabel, series) in zip(axes, panels):
        for label, color, start, end, decay, noise in series:
            runs = trials(start, end, decay, noise)
            mean, std = runs.mean(axis=0), runs.std(axis=0)
            line_with_band(axis, x, mean, mean - std, mean + std, color, label)
        axis.set_xlabel("Number of agents")
        axis.set_ylabel(ylabel)
        axis.set_xlim(x[0] - 1, x[-1] + 1)
        # Headroom above the data keeps the inside legend off the lines.
        axis.set_ylim(0, axis.get_ylim()[1] * 1.35)
        panel_title(axis, title)
        paper_axis(axis, grid_axis=None)
        inside_legend(axis)
    fig.subplots_adjust(wspace=0.28)
    save_paper(fig, out / "example_lines")
print(f"Wrote {out / 'example_lines.pdf'}")
