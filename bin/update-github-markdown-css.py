#!/usr/bin/env python3
"""Regenerate the scoped stylesheet from github-markdown-css 5.9.0's npm tarball.

Usage: python3 bin/update-github-markdown-css.py /path/to/github-markdown-css-5.9.0.tgz
"""
from pathlib import Path
import sys
import tarfile

target = Path(__file__).resolve().parents[1] / "assets/css/github-markdown"
with tarfile.open(sys.argv[1]) as archive:
    def read(name):
        return archive.extractfile(f"package/{name}").read().decode()

    header = """/* github-markdown-css 5.9.0 (MIT), https://github.com/sindresorhus/github-markdown-css
 * Generated from upstream light/dark styles; selectors scoped to blog article bodies.
 * Regenerate with bin/update-github-markdown-css.py.
 */
"""
    light = read("github-markdown-light.css").replace(".markdown-body", "#markdown-content.markdown-body")
    dark = read("github-markdown-dark.css").replace(".markdown-body", 'html[data-theme="dark"] #markdown-content.markdown-body')
    target.mkdir(parents=True, exist_ok=True)
    (target / "github-markdown.css").write_text(header + light + "\n" + dark)
    (target / "LICENSE").write_text(read("license"))
