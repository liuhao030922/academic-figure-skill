"""Build a deterministic, upload-ready paper-figures skill ZIP."""
import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "paper-figures"
INCLUDE = (
    "SKILL.md",
    "paper_style.py",
    "requirements.txt",
    "assets",
    "examples",
    "styles",
    "tools/validate_palette.py",
)


def included_files():
    """Yield repository files needed by the installed skill."""
    for relative in INCLUDE:
        source = ROOT / relative
        if source.is_dir():
            yield from sorted(path for path in source.rglob("*") if path.is_file())
        else:
            yield source


def build(output):
    """Write the skill with a correctly named top-level folder."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in included_files():
            relative = source.relative_to(ROOT)
            info = zipfile.ZipInfo(f"{SKILL_NAME}/{relative.as_posix()}")
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / f"{SKILL_NAME}.zip")
    args = parser.parse_args()
    print(f"Wrote {build(args.output)}")


if __name__ == "__main__":
    main()
