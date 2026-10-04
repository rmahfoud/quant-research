#!/usr/bin/env python3
"""
Builds every research document into one EPUB book, for e-readers.

Chapter order and titles come from docs/index.html, the same source as the
site's "Chapter N" labels. Each document is read on its own with
drop_toc_section.lua and epub_chapter.lua, which together turn it into a
chapter: the title becomes the chapter heading, identifiers get a per-document
prefix and links between documents become links within the book. The chapters
are then joined into one EPUB 3 file with MathML equations, SVG figures and PNG
mermaid diagrams (PNG because mermaid's SVG draws its labels in HTML, which
e-readers drop).

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
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

QR_DIR = pathlib.Path(__file__).resolve().parent.parent
RENDER_ROOT = QR_DIR.parent
REL = QR_DIR.name
INDEX = QR_DIR / "docs" / "index.html"
EPUB = QR_DIR / "docs" / "quant_research.epub"
BUILD_FILES = ["scripts/render_epub.py", "scripts/epub_chapter.lua", "scripts/drop_toc_section.lua", "assets/epub.css"]
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
                "--mathml",
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
