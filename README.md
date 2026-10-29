# Academic Figure Skill

**English** | [简体中文](README.zh-CN.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)
![matplotlib 3.9+](https://img.shields.io/badge/matplotlib-3.9%2B-blue)
![Claude Skill](https://img.shields.io/badge/Claude-skill-d97757)

Publication-ready matplotlib figures for academic papers, packaged as a **Claude skill**.
Tell Claude what to plot; it picks the right chart, sizes it to your venue's column,
matches the paper's font, and checks the result before handing it back.
Works just as well as a plain Python style module without Claude.

![Before and after](assets/before_after.png)

## Gallery

Nine chart forms that cover most systems / ML papers. Every panel is a `draw_*`
function in [`examples/gallery.py`](examples/gallery.py) you can copy. All data is synthetic.

![Gallery](assets/gallery.png)

## Why this and not just a style file?

| | Style file only (e.g. SciencePlots) | This skill |
|---|---|---|
| Fonts and sizes per venue | ✓ | ✓ IEEE · ACM · USENIX · ICML · NeurIPS · article |
| Exact column / text widths | — | ✓ `figsize("column", 2.2)` |
| Chart-form guidance | — | ✓ which chart for which data, and which never to use |
| Helpers for research charts | — | ✓ seed whiskers, bands, CDF p99, annotated heatmaps |
| Checks before finishing | — | ✓ Claude renders and looks for overlaps and clipping |
| Data safety | — | ✓ never puts unpublished results in public examples |

## Ask Claude

Once installed, just describe the figure. Claude loads the skill automatically.

> **"My paper uses IEEEtran. Plot SLO attainment for FCFS vs. ours across four load levels from `results.csv`, three seeds each."**
>
> → grouped bars at 3.45 in, gray baseline / blue method, min–max seed whiskers, a dashed target line, PDF ready for `\includegraphics[width=\columnwidth]`. Like panel (a) above.

> **"Make a latency CDF for the three schedulers in this NeurIPS paper, highlight p99."**
>
> → CDF on a log axis at NeurIPS width, Times font, p99 markers, distinct marker shapes per series. Like panel (d).

> **"Here's my ablation table; turn it into a figure for my ACM submission."**
>
> → ablation bars with deltas from the full method, Libertine font, sized for `acmart` sigconf. Like panel (g).

You can also type `/paper-figures` to call it explicitly.

## Install

**Claude Code**

```bash
git clone https://github.com/liuhao030922/academic-figure-skill.git ~/.claude/skills/paper-figures
```

**Claude app (claude.ai)**: download this repo as a ZIP, then Customize → Skills → Add → upload.

**Plain matplotlib (no Claude)**

```python
import matplotlib.pyplot as plt
plt.style.use("path/to/academic-figure-skill/styles/ieee.mplstyle")
```

or, for the helpers:

```python
import sys; sys.path.insert(0, "path/to/academic-figure-skill")
from paper_style import *

use_venue("ieee")
fig, ax = plt.subplots(figsize=figsize("column", 2.2))
ax.bar([0, 1], [0.8, 0.9], 0.5, **bar_style(METHOD))
paper_axis(ax)
save_paper(fig, "figure")  # writes figure.pdf
```

## Venue presets

| Preset | Column | Text width | Font |
|---|---|---|---|
| `ieee` | 3.50 in | 7.16 in | Times (STIX) |
| `acm` | 3.33 in | 7.00 in | Linux Libertine* |
| `usenix` | 3.33 in | 7.00 in | Times (STIX) |
| `icml` | 3.25 in | 6.75 in | Times (STIX) |
| `neurips` | 5.50 in | 5.50 in | Times (STIX) |
| `article` | 4.77 in | 4.77 in | Computer Modern |

\* Falls back to Times if Libertine / Libertinus isn't installed.

The same figure under three presets, shown at true relative size:

![Venue presets](assets/venues.png)

## Palette and colorblind check

| Role | Color | Hex |
|---|---|---|
| Proposed method | ![](https://placehold.co/14x14/6b9bc8/6b9bc8.png) | `#6b9bc8` |
| Baseline | ![](https://placehold.co/14x14/a6a6a6/a6a6a6.png) | `#a6a6a6` |
| Good / met | ![](https://placehold.co/14x14/79c0b6/79c0b6.png) | `#79c0b6` |
| Warning | ![](https://placehold.co/14x14/f4a65c/f4a65c.png) | `#f4a65c` |
| Neutral | ![](https://placehold.co/14x14/d9d9d9/d9d9d9.png) | `#d9d9d9` |
| Bad / failed | ![](https://placehold.co/14x14/ec7f7c/ec7f7c.png) | `#ec7f7c` |

The palette is soft on purpose, which costs some color separation. Instead of
claiming "colorblind-safe", here are the measured numbers (OKLab ΔE × 100, worst pair
under protanopia / deuteranopia / tritanopia simulation; ≥ 8 is comfortable, 6–8 needs a second cue):

| Used together | Worst pair | Worst CVD ΔE | Second cue built in |
|---|---|---|---|
| Method vs. baseline bars | blue / gray | 7.8 (protan) | outlines, position, legend |
| Line series (method, orange, teal) | teal / orange | 11.4 (protan) | distinct marker shapes |
| Stacked outcomes (teal, orange, gray, red) | red / teal | 7.9 (deutan) | in-segment % labels, outlines |

One rule follows: **teal and baseline gray never appear in the same chart** (ΔE 3.2 under deuteranopia).
The skill tells Claude this. The image below simulates each type of color vision (Machado et al., 2009):

![Colorblind simulation](assets/colorblind.png)

## Repository layout

```
SKILL.md              instructions Claude follows
paper_style.py        style module: venues, colors, helpers
styles/*.mplstyle     presets for plt.style.use()
examples/             bars.py, lines.py, gallery.py (all synthetic data)
tools/build_assets.py regenerates every image in this README
```

Regenerate the images: `python3 tools/build_assets.py`.

## License

[MIT](LICENSE)
