import os
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "examples"), str(ROOT / "tools")]

import matplotlib.pyplot as plt  # noqa: E402
import gallery  # noqa: E402
from package_skill import build  # noqa: E402
from paper_style import cdf_line, figsize, save_paper, use_venue  # noqa: E402
from validate_palette import GROUPS, worst_pair  # noqa: E402


class SmokeTests(unittest.TestCase):
    def test_styles_load(self):
        for style in sorted((ROOT / "styles").glob("*.mplstyle")):
            with self.subTest(style=style.name), plt.style.context(style):
                figure, axis = plt.subplots(figsize=(1, 1))
                axis.plot([0, 1])
                plt.close(figure)

    def test_all_chart_forms_render(self):
        use_venue("ieee")
        for title, draw in gallery.CHARTS:
            with self.subTest(chart=title):
                figure, axis = plt.subplots(figsize=figsize("column", 2.2))
                draw(axis)
                figure.canvas.draw()
                plt.close(figure)

    def test_save_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            figure, axis = plt.subplots()
            axis.plot([0, 1])
            output = save_paper(figure, Path(directory) / "nested" / "figure")
            self.assertTrue(output.is_file())

    def test_empty_cdf_has_clear_error(self):
        figure, axis = plt.subplots()
        with self.assertRaisesRegex(ValueError, "at least one value"):
            cdf_line(axis, [], "blue", "empty")
        plt.close(figure)

    def test_documented_palette_measurements(self):
        expected = {
            "method vs. baseline bars": (7.8, "method", "baseline", "protanopia"),
            "line series": (8.9, "method", "teal", "tritanopia"),
            "stacked outcomes": (7.6, "orange", "red", "tritanopia"),
            "forbidden teal + baseline": (3.2, "teal", "baseline", "deuteranopia"),
        }
        for group, names in GROUPS.items():
            distance, first, second, vision = worst_pair(names)
            rounded = (round(distance, 1), first, second, vision)
            self.assertEqual(rounded, expected[group])

    def test_upload_zip_has_named_root(self):
        with tempfile.TemporaryDirectory() as directory:
            output = build(Path(directory) / "paper-figures.zip")
            with zipfile.ZipFile(output) as archive:
                names = archive.namelist()
            self.assertIn("paper-figures/SKILL.md", names)
            self.assertTrue(all(name.startswith("paper-figures/") for name in names))


if __name__ == "__main__":
    unittest.main()
