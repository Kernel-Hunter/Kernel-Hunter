# Profile README

Lives in the `Kernel-Hunter/Kernel-Hunter` repository, the one GitHub shows on the profile page.

## How it works

- `scripts/build.py` holds all the text (name, about, focus areas, stack, credentials, links)
  and draws every SVG in a dark and a light version. It also writes `README.md`.
- Live numbers (contributions, stars, releases, repositories) come from the GitHub API and are
  cached in `scripts/data.json`.
- `.github/workflows/refresh.yml` reruns the script every night, so the numbers and the
  contribution grid stay current with no manual work.
- Nothing names a specific project. Pin the repositories you want to show on your profile and
  GitHub lists them right under the README.

## Editing

```bash
python3 scripts/build.py            # fetch fresh numbers and redraw everything
python3 scripts/build.py --offline  # redraw from data.json
python3 scripts/preview.py && python3 -m http.server 8000
# open http://localhost:8000/preview-dark.html (or preview-light.html)
```

Edit the content block at the top of `scripts/build.py`, not the SVGs or README.md: both are regenerated.

## Old version

The README from before the redesign is on the `backup/readme-2026-11-04` branch.
