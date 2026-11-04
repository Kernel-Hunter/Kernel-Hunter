#!/usr/bin/env python3
"""Render README.md through GitHub's own Markdown API into preview.html.

    python3 scripts/preview.py && python3 -m http.server 8000
    # open http://localhost:8000/preview.html

The output uses GitHub's sanitizer and markdown CSS, so what you see is
close to the profile page. Light/dark follows your system setting.
"""
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
md = (ROOT / "README.md").read_text()
html = subprocess.run(
    ["gh", "api", "markdown", "--input", "-"],
    input=json.dumps({"text": md, "mode": "gfm", "context": "Kernel-Hunter/Kernel-Hunter"}),
    capture_output=True, text=True, check=True,
).stdout
page = f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Profile preview</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown.min.css">
<style>
 body{{margin:0;background:#fff}} @media (prefers-color-scheme:dark){{body{{background:#0d1117}}}}
 .box{{max-width:896px;margin:32px auto;border:1px solid #d0d7de;border-radius:6px;padding:24px}}
 @media (prefers-color-scheme:dark){{.box{{border-color:#30363d}}}}
 .head{{font:12px -apple-system,sans-serif;color:#57606a;margin-bottom:16px}}
</style></head><body><div class="box"><div class="head">Kernel-Hunter / README.md</div>
<article class="markdown-body">{html}</article></div></body></html>"""
(ROOT / "preview.html").write_text(page)
# Forced-theme copies, for checking one theme regardless of the system setting.
import re
for theme, bg, border in (("dark", "#0d1117", "#30363d"), ("light", "#ffffff", "#d0d7de")):
    forced = re.sub(r'<source media="\(prefers-color-scheme: dark\)" srcset="[^"]*">', "", page)
    forced = forced.replace("assets/light/", f"assets/{theme}/")
    forced = forced.replace("<body>", f'<body data-color-mode="{theme}" data-{theme}-theme="{theme}">')
    forced = forced.replace("</style>", f"body{{background:{bg}!important}}.box{{border-color:{border}!important}}"
                            f".markdown-body{{color-scheme:{theme}}}</style>")
    css = "github-markdown-dark.min.css" if theme == "dark" else "github-markdown-light.min.css"
    forced = forced.replace("github-markdown.min.css", css)
    (ROOT / f"preview-{theme}.html").write_text(forced)
print("wrote preview.html, preview-dark.html, preview-light.html")
