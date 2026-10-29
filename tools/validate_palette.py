"""Reproduce the README's color-vision separation measurements.

Uses the full-severity Machado et al. (2009) matrices in linear RGB and reports
Euclidean OKLab distance multiplied by 100. Run from any directory:

    python3 tools/validate_palette.py
"""
from itertools import combinations
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from paper_style import BASELINE, GRAY, METHOD, ORANGE, RED, TEAL  # noqa: E402

CVD = {
    "protanopia": np.array([
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281, 0.099216],
        [-0.003882, -0.048116, 1.051998],
    ]),
    "deuteranopia": np.array([
        [0.367322, 0.860646, -0.227968],
        [0.280085, 0.672501, 0.047413],
        [-0.011820, 0.042940, 0.968881],
    ]),
    "tritanopia": np.array([
        [1.255528, -0.076749, -0.178779],
        [-0.078411, 0.930809, 0.147602],
        [0.004733, 0.691367, 0.303900],
    ]),
}

M1 = np.array([
    [0.4122214708, 0.5363325363, 0.0514459929],
    [0.2119034982, 0.6806995451, 0.1073969566],
    [0.0883024619, 0.2817188376, 0.6299787005],
])
M2 = np.array([
    [0.2104542553, 0.7936177850, -0.0040720468],
    [1.9779984951, -2.4285922050, 0.4505937099],
    [0.0259040371, 0.7827717662, -0.8086757660],
])

COLORS = {
    "method": METHOD,
    "baseline": BASELINE,
    "orange": ORANGE,
    "teal": TEAL,
    "red": RED,
    "gray": GRAY,
}

GROUPS = {
    "method vs. baseline bars": ("method", "baseline"),
    "line series": ("method", "orange", "teal"),
    "stacked outcomes": ("teal", "orange", "gray", "red"),
    "forbidden teal + baseline": ("teal", "baseline"),
}


def linear_rgb(hex_color):
    """Convert a #rrggbb color to linear RGB."""
    rgb = np.array([int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def oklab(linear):
    """Convert linear RGB to OKLab."""
    return M2 @ np.cbrt(M1 @ linear)


def simulated_oklab(hex_color, matrix):
    """Apply a CVD matrix in linear RGB, clip to gamut, and convert to OKLab."""
    return oklab(np.clip(matrix @ linear_rgb(hex_color), 0, 1))


def separation(first, second, matrix):
    """Return OKLab Euclidean distance × 100 after CVD simulation."""
    a = simulated_oklab(COLORS[first], matrix)
    b = simulated_oklab(COLORS[second], matrix)
    return 100 * float(np.linalg.norm(a - b))


def worst_pair(names):
    """Return the least separated pair across all simulated vision types."""
    candidates = []
    for first, second in combinations(names, 2):
        for vision, matrix in CVD.items():
            candidates.append((separation(first, second, matrix), first, second, vision))
    return min(candidates)


def main():
    print("OKLab ΔE × 100; higher is easier to distinguish")
    for group, names in GROUPS.items():
        distance, first, second, vision = worst_pair(names)
        print(f"{group}: {first} / {second} = {distance:.1f} ({vision})")


if __name__ == "__main__":
    main()
