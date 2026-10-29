---
name: paper-figures
description: Hao's IEEE research-paper figure style for matplotlib — STIX serif 7–8 pt fonts, gray-baseline/blue-method outlined bars, teal/orange/gray/red stacked categories, min–max seed whiskers, single-column 3.45 in sizes, vector PDF output. Use when making figures for a paper, report, or LaTeX/IEEE document, or when the user asks for "论文风格的图", "paper-style figures", or "same style as the midterm figures".
---

# Paper figure style

A reusable matplotlib style taken from the CS555 midterm report figures
(`scripts/generate_midterm_figures.py`, `plot_paper_main` / `plot_paper_x200_breakdown`
in the CS555-project repo). Import the helpers from `paper_style.py` in this
skill's directory instead of retyping values (or copy that file next to
your script):

```python
import sys; sys.path.insert(0, "<this skill's directory>")  # e.g. ~/.claude/skills/paper-figures locally
from paper_style import *
```

## Rules

**Fonts and output**
- Wrap every figure in `with plt.rc_context(PAPER_RC):`. STIXGeneral serif matches IEEEtran Times; base 7.5 pt, ticks/legend 7 pt, panel titles 8 pt, small annotations 6.5 pt, value labels ≈5.6 pt.
- Save with `save_paper(fig, path)` — PDF only, embedded TrueType (`pdf.fonttype 42`), `bbox_inches="tight"`, white background. Include in LaTeX with `\includegraphics[width=\columnwidth]{...}`.

**Size**
- Single column: width 3.45 in. Heights: 2.2 (one panel), 3.55 (two stacked panels, `sharex=True`, `hspace=0.28`), 1.45 (horizontal strip). Double column: 7.0 in wide.
- Design at final size — never shrink a large figure in LaTeX.

**Color**
- Baseline = gray `#a6a6a6`, proposed method = soft blue `#6b9bc8`.
- Stacked outcome categories: good = teal `#79c0b6`, warning/minor = orange `#f4a65c`, neutral = gray `#b3b3b3`, bad = red `#ec7f7c`. Text on fills is `#0b0b0b`.
- Every filled mark gets a thin dark outline: `**bar_style(color)` (edge `#2b2b2b`, 0.5 pt).
- Text is ink (`#1a1a1a` / `#3a3a3a`), never the series color.
- If you add new colors, run the dataviz skill's `validate_palette.js` on them first.

**Axes**
- `paper_axis(ax)`: no top/right spines, light `#e3e3e3` y-grid behind the data.
- Panel titles are left-aligned: `panel_title(ax, "(a) Chatbot SLO attainment")`.
- Divide condition groups with `group_separator(ax, x)` (dotted gray). Label a run of related ticks with one bracket and caption under the axis rather than repeating a prefix on each tick.
- Use LaTeX-style math in ticks: `"200$\\times$"`.

**Uncertainty and annotations**
- Bars are means over seeds; `range_whisker(ax, x, mean, values)` draws min–max whiskers only when there is more than one seed. Add `range_legend_handle()` to the legend as "Seed range", and say in the caption that single-seed bars have no whisker. Don't scatter individual points.
- Targets/thresholds: `target_line(ax, 0.90, "target 0.90", x_text)` — dashed dark line with a small label.
- Value labels: only on the headline panel, above the whisker top. For stacked bars, label in-segment percentages only when the segment is ≥ 4.5 %; put derived totals (e.g. "TPOT miss 60%") just right of the bar.

**Line charts with uncertainty bands** (metric vs. a swept parameter, many x values)
- `line_with_band(ax, x, mean, low, high, color, label)`: 1 pt line with 2.2 pt dot markers over a translucent band (alpha 0.22). Use mean ± std across seeds, a confidence interval, or min–max, and say which in the caption.
- Colors: method = blue `METHOD`, then baselines in order `ORANGE`, `TEAL`, `RED`, `GRAY`. Draw the method first so it tops the legend.
- No grid (`paper_axis(ax, grid_axis=None)`), y from 0, and about 35 % headroom so the legend never covers a line.
- Legend inside the panel: `inside_legend(ax)` (small, light frame, upper right). Side-by-side panels use `figsize=(7.0, 2.2)` with `(a)`/`(b)` titles.
- See `example_lines.py`.

**Legend**
- Frameless, above the panels in one row: `top_legend(fig, handles, labels, ncol=3)` for multi-panel figures, or `ax.legend(ncol=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.04))` for a single axis. Check that it never overlaps a panel title.

## Workflow
1. Choose the form (grouped bars for policy × condition, stacked barh for outcome shares, line + band for a metric over a swept parameter).
2. Build with the helpers above.
3. Render the PDF and look at it (convert a page to PNG if needed) for label collisions, legend overlap, and clipped text before you finish.

`example.py` (bars) and `example_lines.py` (lines with bands) draw complete reference figures from synthetic data.

Never commit or publish figures made from unpublished experimental data as examples; use synthetic data.
