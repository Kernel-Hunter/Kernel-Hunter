# Profile README

Copy this folder into the `Kernel-Hunter/Kernel-Hunter` repository (the one
GitHub shows on your profile).

## Files

| Path | What it is |
| --- | --- |
| `README.md` | The profile page. Every image has a dark and a light version. |
| `assets/dark/`, `assets/light/` | Generated SVGs. Do not edit by hand. |
| `scripts/build.py` | Draws every SVG. All text, links, projects and colors live at the top. |
| `scripts/data.json` | Last snapshot of your GitHub numbers, used when offline. |
| `scripts/preview.py` | Renders README.md through GitHub's Markdown API into `preview.html`. |
| `.github/workflows/refresh.yml` | Rebuilds the SVGs every night so stars, releases and the heatmap stay current. |

## Commands

```bash
python3 scripts/build.py            # fetch fresh data and redraw
python3 scripts/build.py --offline  # redraw from data.json
python3 scripts/preview.py && python3 -m http.server 8000   # open /preview.html
```

## After pushing

Settings → Actions → General → Workflow permissions → Read and write, so the
nightly job can commit the refreshed SVGs.

## Notes

- The "Shipping …" chip in the header and the "Now" row pick the featured
  project with the newest release, so they update on their own.
- To change the featured projects, edit `PROJECTS` in `scripts/build.py`
  and the card links in `README.md`.
- SVGs use system fonts (SF Pro on Mac, Segoe UI on Windows). GitHub blocks
  web fonts inside images.
