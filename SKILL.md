---
name: paper-figures
description: Publication-ready matplotlib figures for academic papers — venue presets (IEEE, ACM, USENIX, ICML, NeurIPS, LaTeX article) with matching serif fonts and column widths, a soft colorblind-checked palette (gray baseline / blue method), outlined bars, min–max seed whiskers, lines with uncertainty bands, CDFs, heatmaps, trade-off, ablation, time-series and box plots, vector PDF output. Use when making figures for a paper, report, thesis, or any LaTeX document, or when the user asks for "论文风格的图", "paper-style figures", "IEEE/ACM figure", or "publication-quality plot".
---

# Paper figures

Style module: `paper_style.py` in this skill's directory. Import it instead of
retyping values (or copy the file next to the user's script):

```python
import sys; sys.path.insert(0, "<this skill's directory>")
from paper_style import *

venue = use_venue("ieee")   # ieee | acm | usenix | icml | neurips | article
fig, ax = plt.subplots(figsize=figsize("column", 2.2))   # or "text", or a fraction like 0.5
...
save_paper(fig, "figures/result")                          # writes figures/result.pdf
```

Ready-made code for nine chart forms is in `examples/gallery.py` (one `draw_*`
function per form). Copy the closest one and adapt it rather than starting from scratch.

## 1. Pick the venue

- If the user hasn't said where the figure goes, infer it from their LaTeX
  class (`IEEEtran`, `acmart`, `usenix`, `icml20xx`, `neurips_20xx`, `article`) or ask.
- `use_venue(name)` sets the font (Times / Libertine / Computer Modern),
  font sizes and default color cycle. `figsize("column" | "text", height)` gives the
  exact width. Include in LaTeX with `\includegraphics[width=\columnwidth]{...}`
  (or `\textwidth`). Design at final size; never shrink a big figure in LaTeX.
- Heights: 2.2 in for one panel, 3.55 in for two stacked panels (`sharex=True`,
  `hspace=0.28`), 1.45 in for a horizontal strip.

## 2. Pick the form

| Data's job | Form | Helper / example |
|---|---|---|
| Policy × condition comparison | grouped bars + min–max whiskers | `bar_style`, `range_whisker` · `draw_grouped_bars` |
| Outcome shares | stacked horizontal bars, % labels | `bar_style` · `draw_stacked_breakdown` |
| Metric over a swept parameter | line + shaded band | `line_with_band` · `draw_line_band` |
| Latency / tail distribution | CDF, log x, p99 markers | `cdf_line` · `draw_cdf` |
| Two-parameter sweep | annotated sequential heatmap | `annotated_heatmap` · `draw_heatmap` |
| Throughput vs. latency | scatter + method frontier | `draw_pareto` |
| Component contributions | ablation barh with deltas | `draw_ablation` |
| Behavior over time | line, shaded event window | `draw_timeseries` |
| Per-method spread | box plot | `paper_boxplot` · `draw_boxplot` |

Never use dual y-axes, pie charts, 3-D, or radar charts.

## 3. Color

- Baseline = gray `BASELINE #a6a6a6`; proposed method = blue `METHOD #6b9bc8`.
- Lines: `PALETTE` order (method, orange, teal, red, gray) paired with `MARKERS`
  (o, s, ^, D, v). Always pass the marker so series differ without color.
- Stacked outcomes: good `TEAL`, warning `ORANGE`, neutral `GRAY #d9d9d9`, bad `RED`;
  in-segment text `LABEL_ON_FILL`.
- Magnitudes: `sequential_cmap()` (one-hue blue). Never a rainbow.
- Every filled mark gets the thin dark outline from `bar_style(color)`.
- Text is ink (`INK`, `MUTED_INK`), never the series color.
- Colorblind limits of this soft palette (checked with Machado 2009 simulation):
  never put `TEAL` and `BASELINE` gray in the same chart (ΔE 3.2 under deuteranopia);
  baseline-gray vs. method-blue is at the floor (ΔE 7.8 protan), so keep outlines,
  legends and direct labels; use at most four colored series and let markers carry the fifth.
- New colors must pass the dataviz skill's `validate_palette.js` before use.

## 4. Axes, annotations, legend

- `paper_axis(ax)`: no top/right spines, light grid behind data
  (`grid_axis=None` for line charts, `"both"` for CDF/scatter).
- Left-aligned panel titles `panel_title(ax, "(a) ...")`.
- Divide condition groups with `group_separator(ax, x)`; label a run of
  related ticks with one bracket and caption instead of repeating a prefix.
- Bars are means over seeds; `range_whisker` only when > 1 seed, plus
  `range_legend_handle()` labelled "Seed range"; say in the caption that
  single-seed bars have no whisker. Bands: say whether they are std, CI, or min–max.
- Targets: `target_line(ax, y, "target 0.90", x_text)`.
- Value labels only on the headline panel; stacked % labels only on segments ≥ 4.5–8 %.
- Legend: frameless one row above the panels (`top_legend`) for bars;
  `inside_legend(ax)` for line charts with ~35 % y headroom so it never covers data.
- Math in labels: `"200$\\times$"`.

## 5. Check before finishing

1. Render the PDF and look at it (convert a page to PNG if needed): no label
   collisions, legend never on a title or data, nothing clipped.
2. Text is ≥ 5.5 pt at final size.
3. Caption states what bars, whiskers and bands mean.
4. Never publish figures built from the user's unpublished experimental data
   as examples (READMEs, public repos, slides for others) without asking; use synthetic data.
