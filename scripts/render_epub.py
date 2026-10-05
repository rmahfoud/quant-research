#!/usr/bin/env python3
"""
Builds every research document into one EPUB book, for e-readers.

Chapter order and titles come from docs/index.html, the same source as the
site's "Chapter N" labels. Each document is read on its own with
drop_toc_section.lua and epub_chapter.lua, which together turn it into a
chapter: the title becomes the chapter heading, identifiers get a per-document
prefix and links between documents become links within the book. The chapters
are then joined into one EPUB 3 file with SVG figures and PNG mermaid diagrams
(PNG because mermaid's SVG draws its labels in HTML, which e-readers drop).

Equations avoid MathML, which many readers (Google Play Books among them) lay
out one token per line. Simple inline math is set as text, with italics,
sub/superscripts and Unicode symbols, so it reflows with the prose and follows
the reader's night theme; everything else becomes an SVG image drawn by MathJax
(tex_to_svg.mjs), the engine the site uses.

The book is written to docs/quant_research.epub, published beside the pages it
collects. It is rebuilt only when one of its inputs (the chapters, the index,
the figures or this build's own files) is newer than it, or with --force. The
build is reproducible, timestamps pinned like the figure generators', so a
rebuild from unchanged inputs (a fresh checkout reorders mtimes) leaves the
committed file byte-identical.

Usage (from anywhere):
    python3 quant-research/scripts/render_epub.py [--force] [-o OUT]
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor

QR_DIR = pathlib.Path(__file__).resolve().parent.parent
RENDER_ROOT = QR_DIR.parent
REL = QR_DIR.name
INDEX = QR_DIR / "docs" / "index.html"
EPUB = QR_DIR / "docs" / "quant_research.epub"
BUILD_FILES = [
    "scripts/render_epub.py",
    "scripts/epub_chapter.lua",
    "scripts/drop_toc_section.lua",
    "scripts/tex_to_svg.mjs",
    "assets/epub.css",
]
SOURCE_DATE_EPOCH = "1735689600"

SITE_URL = "https://rmahfoud.github.io/quant-research/"
TITLE = "Quant Research"
SUBTITLE = "Notes on Quantitative Finance"
AUTHOR = "Robert Mahfoud"
RIGHTS = (
    "These documents were generated in whole or in part with the help of a large language model. "
    "Dedicated to the public domain under the "
    "[CC0 1.0 Universal Public Domain Dedication](https://creativecommons.org/publicdomain/zero/1.0/)."
)

ARTICLE_RE = re.compile(r'<article class="doc">.*?</article>', re.DOTALL)
SLUG_RE = re.compile(r'href="([a-z0-9_]+)\.html"')
DESCRIPTION_RE = re.compile(r'<meta name="description" content="(.*?)">')

# Inline math simple enough to set as text: letters, digits, Greek, common
# operators and scripts, plus only those blackboard and calligraphic capitals
# with a Basic Multilingual Plane code point, which e-reader fonts cover.
_SYMBOL = (
    r"\\(?:alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|lambda|mu|nu|xi|pi"
    r"|rho|sigma|tau|upsilon|phi|varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Phi|Psi|Omega"
    r"|ell|le|leq|ge|geq|ne|neq|equiv|approx|sim|times|cdot|pm|to|in|mid|infty|ldots|dots|cdots|quad"
    r"|ln|log|exp)(?![A-Za-z])"
    r"|\\[,;!%{}]|\\mathrm\{[A-Za-z]+\}|\\mathbb\{[CNPQRZ]\}|\\mathcal\{[BEFHILMR]\}"
    r"|[A-Za-z0-9 +\-=<>,.()\[\]|'/:!*]"
)
SIMPLE_MATH_RE = re.compile(rf"^(?:{_SYMBOL}|[_^](?:{_SYMBOL}|\{{(?:{_SYMBOL})+\}}))+$")
SQRT_RE = re.compile(r"\\sqrt\{([^{}]*)\}")
VIEWBOX_RE = re.compile(r'viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"')
SVG_TAG_RE = re.compile(r"<svg [^>]*>")
DATA_ATTR_RE = re.compile(r' data-[\w-]+="[^"]*"')
# MathJax on the web scales its glyphs to the text's x-height, about this much
# larger than TeX's in a typical book face.
MATH_SCALE = 1.1
# Intrinsic size, for readers that rasterise SVG: sharp on a 3x screen, within
# Google Play Books' 3200px cap.
PX_PER_EM = 48

# Elements whose pandoc JSON carries an Attr, and where it sits in "c".
ATTR_POS = {"Header": 1, "Div": 0, "Span": 0, "Link": 0, "Image": 0, "CodeBlock": 0, "Code": 0, "Table": 0, "Figure": 0}


def read_index() -> tuple[list[str], str]:
    text = INDEX.read_text()
    slugs = [SLUG_RE.search(m.group(0)).group(1) for m in ARTICLE_RE.finditer(text)]
    if not slugs:
        sys.exit(f"{INDEX}: no chapters found")
    return slugs, html.unescape(DESCRIPTION_RE.search(text).group(1))


def is_current(output: pathlib.Path, slugs: list[str]) -> bool:
    inputs = [QR_DIR / f"{slug}.md" for slug in slugs] + [INDEX] + sorted(QR_DIR.glob("figures/*.svg"))
    inputs += [QR_DIR / f for f in BUILD_FILES]
    return output.exists() and all(f.stat().st_mtime <= output.stat().st_mtime for f in inputs)


def read_chapter(slug: str, number: int, slugs: list[str]) -> dict:
    src = QR_DIR / f"{slug}.md"
    args = ["pandoc", f"{REL}/{slug}.md", "-t", "json"]
    if re.search(r"^```mermaid", src.read_text(), re.MULTILINE):
        args += ["-F", "mermaid-filter"]
    args += [
        f"--lua-filter={REL}/scripts/drop_toc_section.lua",
        f"--lua-filter={REL}/scripts/epub_chapter.lua",
        f"--metadata=epub-chapter={slug}",
        f"--metadata=epub-number={number}",
        f"--metadata=epub-chapters={','.join(slugs)}",
    ]
    env = os.environ | {"MERMAID_FILTER_FORMAT": "png", "MERMAID_FILTER_SCALE": "2"}
    result = subprocess.run(args, cwd=RENDER_ROOT, env=env, capture_output=True, text=True, check=False)
    sys.stderr.write(result.stderr)
    if result.returncode:
        sys.exit(f"pandoc failed on {slug}.md")
    return json.loads(result.stdout)


def walk(node: object, visit: Callable[[dict], None]) -> None:
    if isinstance(node, dict):
        visit(node)
        for value in node.values():
            walk(value, visit)
    elif isinstance(node, list):
        for value in node:
            walk(value, visit)


def check_links(blocks: list) -> None:
    ids, targets = set(), []

    def visit(node: dict) -> None:
        pos = ATTR_POS.get(node.get("t"))
        if pos is not None and node["c"][pos][0]:
            ids.add(node["c"][pos][0])
        if node.get("t") == "Link" and node["c"][2][0].startswith("#"):
            targets.append(node["c"][2][0][1:])

    walk(blocks, visit)
    for target in sorted({t for t in targets if t not in ids}):
        print(f"warning: link to #{target}, which no heading or anchor in the book carries", file=sys.stderr)


def find_math(node: object, in_header: bool = False) -> Iterator[tuple[dict | list, int | str, bool]]:
    items = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ()
    for key, child in items:
        if isinstance(child, dict) and child.get("t") == "Math":
            yield node, key, in_header
        else:
            yield from find_math(child, in_header or (isinstance(child, dict) and child.get("t") == "Header"))


def tex_to_svg(exprs: list[tuple[str, bool]]) -> list[str]:
    npm_root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, check=True).stdout.strip()
    mathjax = pathlib.Path(npm_root) / "mathjax"
    if not (mathjax / "node-main.mjs").exists():
        sys.exit("MathJax not found. Run ./scripts/setup_dev.sh")
    result = subprocess.run(
        ["node", str(QR_DIR / "scripts" / "tex_to_svg.mjs"), str(mathjax)],
        input=json.dumps(exprs),
        capture_output=True,
        text=True,
        check=False,
    )
    sys.stderr.write(result.stderr)
    if result.returncode:
        sys.exit("MathJax failed")
    return json.loads(result.stdout)


def math_image(tex: str, display: bool, svg: str, media: pathlib.Path) -> dict:
    viewbox = VIEWBOX_RE.search(svg)
    y, w, h = (float(v) for v in viewbox.groups()[1:])
    px = min(PX_PER_EM / 1000, 3200 / max(w, h))
    root = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * px:.1f}" height="{h * px:.1f}" {viewbox.group(0)}>'
    svg = DATA_ATTR_RE.sub("", SVG_TAG_RE.sub(root, svg, count=1)).replace("currentColor", "#000")
    path = media / f"{hashlib.sha1(f'{display}{tex}'.encode()).hexdigest()}.svg"
    path.write_text(svg)
    # Sized in em, from MathJax's 1000 units per em, so it scales with the
    # reader's font; inline images sit on the baseline by their depth.
    em = MATH_SCALE / 1000
    style = f"width:{w * em:.3f}em"
    if not display:
        style += f";height:{h * em:.3f}em;vertical-align:{-(h + y) * em:.3f}em"
    attr = ["", ["math", "display" if display else "inline"], [["style", style]]]
    return {"t": "Image", "c": [attr, [{"t": "Str", "c": tex}], [str(path), ""]]}


def render_math(blocks: list, media: pathlib.Path) -> None:
    images: dict[tuple[str, bool], list[tuple[dict | list, int | str]]] = {}
    for parent, key, in_header in list(find_math(blocks)):
        kind, tex = parent[key]["c"][0]["t"], parent[key]["c"][1]
        if in_header:
            # Headings feed the reader's table of contents, which shows text only.
            parent[key]["c"][1] = SQRT_RE.sub(r"√{\1}", tex)
        elif kind == "DisplayMath" or not SIMPLE_MATH_RE.match(tex.strip()):
            images.setdefault((tex, kind == "DisplayMath"), []).append((parent, key))
    for (tex, display), svg in zip(images, tex_to_svg(list(images)), strict=True):
        image = math_image(tex, display, svg, media)
        for parent, key in images[(tex, display)]:
            parent[key] = image


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--output", type=pathlib.Path, default=EPUB)
    ap.add_argument("--force", action="store_true", help="rebuild even if newer than every input")
    args = ap.parse_args()
    output = args.output.resolve()

    if REL != "quant-research":
        sys.exit(f"This directory must be named quant-research (got: {REL})")
    if not shutil.which("pandoc"):
        sys.exit("pandoc not found. Run ./scripts/setup_dev.sh")
    if not shutil.which("mermaid-filter"):
        sys.exit("mermaid-filter not found. Run ./scripts/setup_dev.sh")
    if not shutil.which("node"):
        sys.exit("node not found. Run ./scripts/setup_dev.sh")

    slugs, description = read_index()
    if not args.force and is_current(output, slugs):
        print(f"{output} is up to date")
        return 0

    with ThreadPoolExecutor() as pool:
        docs = list(pool.map(read_chapter, slugs, range(1, len(slugs) + 1), [slugs] * len(slugs)))
    (RENDER_ROOT / "mermaid-filter.err").unlink(missing_ok=True)

    blocks = [block for doc in docs for block in doc["blocks"]]
    check_links(blocks)
    book = {"pandoc-api-version": docs[0]["pandoc-api-version"], "meta": {}, "blocks": blocks}
    meta = {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "author": AUTHOR,
        "lang": "en",
        "description": description,
        "rights": RIGHTS,
        # Stable across builds, so an e-reader replaces the book rather than
        # shelving a second copy.
        "identifier": f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, SITE_URL)}",
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        render_math(blocks, pathlib.Path(tmp))
        meta_file = pathlib.Path(tmp) / "meta.json"
        meta_file.write_text(json.dumps(meta))
        result = subprocess.run(
            [
                "pandoc",
                "--from=json",
                f"--output={output}",
                f"--metadata-file={meta_file}",
                "--toc",
                "--toc-depth=2",
                "--split-level=2",
                f"--css={REL}/assets/epub.css",
            ],
            cwd=RENDER_ROOT,
            env=os.environ | {"SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH},
            input=json.dumps(book),
            text=True,
            check=False,
        )
    if result.returncode:
        return result.returncode
    print(f"\033[32m✅ {output}\033[0m")
    return 0


if __name__ == "__main__":
    sys.exit(main())
