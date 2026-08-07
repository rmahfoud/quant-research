# Converts every hand-authored *.svg in this directory to *.pdf for the LaTeX
# build. xelatex cannot include SVG; the HTML build uses the SVG directly.

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def convert(svg: Path) -> None:
    pdf = svg.with_suffix(".pdf")
    subprocess.run(
        ["rsvg-convert", "--format=pdf", "--output", str(pdf), str(svg)],
        check=True,
    )
    print(f"  {svg.name} -> {pdf.name}")


def main() -> int:
    svgs = sorted(HERE.glob("*.svg"))
    if not svgs:
        return 0
    if shutil.which("rsvg-convert") is None:
        print("rsvg-convert not found. Install with: brew install librsvg", file=sys.stderr)
        return 1
    for svg in svgs:
        convert(svg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
