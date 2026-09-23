#!/usr/bin/env python3
"""Rebuild slides.html from slides.md.

Usage:  python build.py            one rebuild
        python build.py --watch    rebuild whenever slides.md changes

No dependencies: slides.md is spliced into slides.html between the SLIDES
markers, so the HTML stays a single self-contained file you open by
double-clicking (refresh the browser after a rebuild).
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MD = HERE / "slides.md"
HTML = HERE / "slides.html"
BEGIN = "<!-- SLIDES:BEGIN generated from slides.md — edit that file, not this one -->"
END = "<!-- SLIDES:END -->"


def build() -> None:
    md = MD.read_text(encoding="utf-8")
    if "</textarea" in md.lower():
        sys.exit("slides.md must not contain the literal text '</textarea>'")
    html = HTML.read_text(encoding="utf-8")
    pre, found, rest = html.partition(BEGIN)
    _, found2, post = rest.partition(END)
    if not (found and found2):
        sys.exit(f"SLIDES markers not found in {HTML.name}")
    block = f'{BEGIN}\n<textarea id="source" style="display:none">\n{md}</textarea>\n{END}'
    HTML.write_text(pre + block + post, encoding="utf-8")
    print(f"built {HTML.name} from {MD.name}")


build()
if "--watch" in sys.argv[1:]:
    print("watching slides.md — Ctrl-C to stop")
    last = MD.stat().st_mtime
    try:
        while True:
            time.sleep(0.5)
            mtime = MD.stat().st_mtime
            if mtime != last:
                last = mtime
                build()
    except KeyboardInterrupt:
        pass
