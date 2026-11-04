#!/usr/bin/env python3
"""Build every SVG used by the profile README, in a dark and a light variant.

    python3 scripts/build.py            # fetch fresh data from GitHub, then draw
    python3 scripts/build.py --offline  # redraw from scripts/data.json only

Data comes from the GitHub GraphQL API. The token is read from GITHUB_TOKEN,
or from `gh auth token` when running locally. The last successful fetch is
cached in scripts/data.json so the page can be rebuilt without network.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA_FILE = ROOT / "scripts" / "data.json"
ICONS = json.loads((ROOT / "scripts" / "icons.json").read_text())

LOGIN = "Kernel-Hunter"

# --------------------------------------------------------------------------
# Content. Edit here, not in the SVGs.
# --------------------------------------------------------------------------

NAME = "Karim Masmoudi"
TAGLINE = [
    "Software engineer. I build native Mac apps,",
    "developer tools and sandboxes for AI agents.",
]
META = "TUNISIA  ·  SMU MEDTECH  ·  SYSTEMS · SECURITY · AI"

ABOUT = [
    "I'm a third-year software engineering student",
    "who likes software that runs close to the machine:",
    "native Mac apps, Linux kernel experiments, and",
    "local-first tools that keep your data on your computer.",
]
ABOUT_FOOT = "Open to internships, freelance work, research and collaboration."

LINKS = [
    # (file name, label, icon, href)
    ("portfolio", "Portfolio", "globe", "https://karimmasmoudi.vercel.app"),
    ("linkedin", "LinkedIn", "linkedin", "https://www.linkedin.com/in/karim-masmoudi-224816291/"),
    ("x", "X", "x", "https://x.com/Karim__Masmoudi"),
    ("email", "Email", "mail", "mailto:karim.masmoudi.pro@gmail.com"),
]

PROJECTS = [
    {
        "repo": "boost", "title": "Boost", "glyph": "gauge",
        "accent": ("#FFA552", "#D9701A"),
        "lines": ["Mac menu-bar app for memory and disk. See what",
                  "uses your RAM, find large files, uninstall cleanly."],
        "tag": "macOS  ·  no network access",
    },
    {
        "repo": "mudroom", "title": "Mudroom", "glyph": "cube",
        "accent": ("#A98BFF", "#7148E0"),
        "lines": ["Run Claude Code, Codex and other agents in a",
                  "local VM, then review their changes like a PR."],
        "tag": "macOS app  ·  Linux & Windows CLI",
    },
    {
        "repo": "kandle", "title": "Kandle", "glyph": "candles",
        "accent": ("#4CC3FF", "#0A7FC0"),
        "lines": ["Open-source charts for crypto, stocks and forex,",
                  "with an MCP server your AI agent can drive."],
        "tag": "Web  ·  MCP server",
    },
    {
        "repo": "narrata", "title": "Narrata", "glyph": "wave",
        "accent": ("#FF7AB8", "#D02C78"),
        "lines": ["Reads PDFs, EPUBs and web pages aloud with word",
                  "highlighting. The voice runs in your browser."],
        "tag": "Web app  ·  Chrome extension",
    },
]

STACK = [
    ("LANGUAGES", [("Swift", "swift"), ("TypeScript", "typescript"), ("Python", "python"),
                   ("JavaScript", "javascript"), ("C", "c"), ("Java", "openjdk"), ("Bash", "gnubash"),
                   ("PowerShell", "s:terminal"), ("HTML", "html5"), ("CSS", "css")]),
    ("WEB & APPS", [("SwiftUI", "swift"), ("React", "react"), ("Next.js", "nextdotjs"), ("Vue", "vuedotjs"),
                    ("Vuetify", "vuetify"), ("Vite", "vite"), ("Node.js", "nodedotjs")]),
    ("AI & DATA", [("Machine learning", "s:spark"), ("ONNX", "onnx"), ("OpenCV", "opencv"),
                   ("MCP", "modelcontextprotocol"), ("Claude Code", "claude"), ("MySQL", "mysql")]),
    ("SECURITY", [("Linux kernel", "s:chip"), ("Kali Linux", "kalilinux"), ("Burp Suite", "burpsuite"),
                  ("Wireshark", "wireshark"), ("Ethical hacking", "s:shield")]),
    ("EMBEDDED", [("ESP32", "espressif"), ("Arduino", "arduino"), ("Raspberry Pi", "raspberrypi"),
                  ("IoT", "s:signal")]),
    ("PLATFORMS", [("macOS", "apple"), ("Windows", "s:windows"), ("Linux", "linux"), ("Debian", "debian"),
                   ("Chrome extensions", "googlechrome")]),
    ("TOOLS", [("Git", "git"), ("GitHub Actions", "githubactions"), ("Xcode", "xcode"), ("Homebrew", "homebrew"),
               ("Vercel", "vercel"), ("Unity", "unity")]),
]

BRAND = {
    "swift": "#F05138", "typescript": "#3178C6", "python": "#4B8BBE", "c": "#A8B9CC",
    "openjdk": "#E76F00", "javascript": "#F7DF1E", "apple": "#000000", "linux": "#FCC624",
    "debian": "#D70A53", "githubactions": "#2088FF", "git": "#F05032", "mysql": "#4479A1",
    "vuedotjs": "#4FC08D", "wireshark": "#1679A7", "burpsuite": "#FF6633", "gnubash": "#4EAA25",
    "html5": "#E34F26", "css": "#663399", "react": "#61DAFB", "nextdotjs": "#000000",
    "vuetify": "#1867C0", "vite": "#9135FF", "nodedotjs": "#5FA04E", "onnx": "#7F7F7F",
    "opencv": "#5C3EE8", "modelcontextprotocol": "#000000", "claude": "#D97757",
    "kalilinux": "#557C94", "espressif": "#E7352C", "arduino": "#00878F", "raspberrypi": "#A22846",
    "googlechrome": "#4285F4", "xcode": "#147EFB", "homebrew": "#FBB040", "vercel": "#000000",
    "unity": "#000000", "s:terminal": "#5391FE", "s:windows": "#0078D4",
}

CREDENTIALS = [
    ("EDUCATION", [
        ("Engineering program, third year", "MedTech, South Mediterranean University"),
        ("Long-term goal", "Ph.D. in software engineering, AI and security"),
    ]),
    ("CERTIFICATES", [
        ("Database Management with Java and SQL", "Amazon"),
        ("Programming Fundamentals", "Duke University"),
        ("Game Design and Development with Unity", "Michigan State University"),
        ("Machine Learning & AI with Python", "Mind Luster"),
    ]),
    ("LANGUAGES", [
        ("Arabic", "Native"),
        ("English", "Fluent · IELTS 7.5"),
        ("French", "Intermediate"),
    ]),
    ("COMMUNITY", [
        ("Black Hat MEA · LEAP", "Researcher, 2022 to present"),
        ("GITEX Global · World AI Summit", "Attended"),
    ]),
]

# --------------------------------------------------------------------------
# Themes
# --------------------------------------------------------------------------

THEMES = {
    "dark": {
        "bg": "#0A0A0C", "surface": "#0F0F13", "chip": "#16161C",
        "line": "#FFFFFF", "line_op": 0.085, "dot_op": 0.07,
        "text": "#F5F5F7", "muted": "#A1A1AA", "subtle": "#6B6B76",
        "a1": "#7C8CFF", "a2": "#5EEAD4", "glow1": 0.30, "glow2": 0.18,
        "heat": ["#17171D", "#173A44", "#1A6B70", "#28A99C", "#5EEAD4"],
        "primary_bg": "#F5F5F7", "primary_fg": "#0A0A0C",
        "accent_index": 0, "tile_op": 0.14,
    },
    "light": {
        "bg": "#FFFFFF", "surface": "#FBFBFC", "chip": "#F4F4F6",
        "line": "#0A0A0C", "line_op": 0.09, "dot_op": 0.09,
        "text": "#0A0A0C", "muted": "#52525B", "subtle": "#8E8E98",
        "a1": "#5563E6", "a2": "#0EA597", "glow1": 0.16, "glow2": 0.12,
        "heat": ["#EEEEF2", "#BDEDE5", "#78D6C8", "#2BB0A0", "#0B7F75"],
        "primary_bg": "#0A0A0C", "primary_fg": "#FFFFFF",
        "accent_index": 1, "tile_op": 0.10,
    },
}

SANS = "Inter, 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SF Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

STROKE_ICONS = {
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9S9.4 5.6 12 3Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
    "gauge": '<path d="M4.5 16.5a8 8 0 1 1 15 0"/><path d="m12 14 4.2-4.6"/><circle cx="12" cy="14.5" r="1.4"/>',
    "cube": '<path d="M12 3 20 7.5v9L12 21l-8-4.5v-9Z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/>',
    "candles": '<path d="M7.5 3v3.5M7.5 15.5V21M16.5 3v5.5M16.5 17.5V21"/><rect x="5.5" y="6.5" width="4" height="9" rx="1"/><rect x="14.5" y="8.5" width="4" height="9" rx="1"/>',
    "wave": '<path d="M4 10.5v3M8 7.5v9M12 4.5v15M16 8v8M20 10.5v3"/>',
    "terminal": '<rect x="2.5" y="4" width="19" height="16" rx="3" fill="currentColor" stroke="none"/><path d="m7 9 3.5 3L7 15M12.5 15.5h4.5" stroke="#fff"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/><circle cx="12" cy="12" r="2.2"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9.5 2.5v3.5M14.5 2.5v3.5M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/>',
    "shield": '<path d="M12 3 4.5 6v5.5c0 4.6 3.1 8.3 7.5 9.5 4.4-1.2 7.5-4.9 7.5-9.5V6Z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "signal": '<circle cx="12" cy="12" r="1.8"/><path d="M8.2 8.2a5.4 5.4 0 0 0 0 7.6M15.8 8.2a5.4 5.4 0 0 1 0 7.6M5.3 5.3a9.5 9.5 0 0 0 0 13.4M18.7 5.3a9.5 9.5 0 0 1 0 13.4"/>',
    "windows": '<path d="M3 5.3 10.6 4.2v7.2H3ZM11.6 4.1 21 2.7v8.7h-9.4ZM3 12.4h7.6v7.3L3 18.6ZM11.6 12.4H21v8.8l-9.4-1.3Z" fill="currentColor" stroke="none"/>',
    "star": '<path d="m12 3.5 2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.8l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8Z"/>',
}
SOLID_ICONS = {
    "linkedin": "M6.94 8.5H3.56V20h3.38V8.5ZM5.25 3.5a1.96 1.96 0 1 0 0 3.92 1.96 1.96 0 0 0 0-3.92ZM20.5 13.6c0-3.4-1.8-5-4.2-5-1.9 0-2.8 1.05-3.3 1.8V8.5H9.6V20h3.4v-6.4c0-1.5.5-2.5 1.9-2.5 1.4 0 2.1.9 2.1 2.5V20h3.5v-6.4Z",
    "x": ICONS["x"]["d"],
}

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

NARROW = set("il.,:;'|!·I1 ()[]tfjr")
WIDE = set("mwMW@%")


def text_width(s: str, size: float, mono: bool = False, spacing: float = 0.0) -> float:
    """Rough advance width; good enough to size chips and pills."""
    if mono:
        return len(s) * size * 0.6 + spacing * max(len(s) - 1, 0)
    w = 0.0
    for ch in s:
        if ch in NARROW:
            w += 0.30
        elif ch in WIDE:
            w += 0.86
        elif ch.isupper():
            w += 0.66
        else:
            w += 0.55
    return w * size + spacing * max(len(s) - 1, 0)


def luminance(hex_: str) -> float:
    r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def svg(w: int, h: int, body: str, label: str, style: str = "") -> str:
    css = (f"<style>{style}@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}</style>"
           if style else "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'fill="none" role="img" aria-label="{escape(label)}">{css}{body}</svg>\n'
    )


def frame(t: dict, w: int, h: int, r: int = 16, fill: str | None = None) -> str:
    return (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{fill or t["surface"]}" '
        f'stroke="{t["line"]}" stroke-opacity="{t["line_op"]}"/>'
    )


def stroke_icon(name: str, x: float, y: float, size: float, color: str, width: float = 1.8) -> str:
    s = size / 24
    return (
        f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.4f})" color="{color}" stroke="{color}" '
        f'stroke-width="{width / s:.2f}" stroke-linecap="round" stroke-linejoin="round" fill="none">'
        f'{STROKE_ICONS[name]}</g>'
    )


def solid_icon(path: str, x: float, y: float, size: float, color: str) -> str:
    s = size / 24
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.4f})"><path d="{path}" fill="{color}"/></g>'


def txt(x, y, s, size, color, weight=400, mono=False, anchor="start", spacing=0.0) -> str:
    fam = MONO if mono else SANS
    extra = f' letter-spacing="{spacing}"' if spacing else ""
    extra += f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
        f'fill="{color}"{extra}>{escape(s)}</text>'
    )


def hline(t: dict, x: float, y: float, w: float, extra: float = 0.0) -> str:
    return f'<rect x="{x}" y="{y}" width="{w:.1f}" height="1" fill="{t["line"]}" fill-opacity="{t["line_op"] + extra:.3f}"/>'


def fmt(n: int) -> str:
    return f"{n:,}"


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        name stargazerCount
        primaryLanguage { name color }
        releases { totalCount }
        latestRelease { tagName publishedAt }
      }
    }
  }
}
"""


def token() -> str | None:
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def fetch() -> dict:
    tok = token()
    if not tok:
        raise RuntimeError("no GitHub token (set GITHUB_TOKEN or log in with gh)")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json",
                 "User-Agent": f"{LOGIN}-profile-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    u = payload["data"]["user"]
    repos = {r["name"]: r for r in u["repositories"]["nodes"]}
    cal = u["contributionsCollection"]["contributionCalendar"]

    def proj(name: str) -> dict:
        r = repos.get(name, {})
        lang = r.get("primaryLanguage") or {}
        rel = r.get("latestRelease") or {}
        return {"stars": r.get("stargazerCount", 0), "language": lang.get("name", ""),
                "color": lang.get("color") or "#888888", "release": rel.get("tagName", ""),
                "published": rel.get("publishedAt", "")}

    return {
        "fetched": dt.date.today().isoformat(),
        "contributions": cal["totalContributions"],
        # each week: list of [weekday, count]; the first and last week can be partial
        "weeks": [[[d["weekday"], d["contributionCount"]] for d in w["contributionDays"]] for w in cal["weeks"]],
        "first_day": cal["weeks"][0]["contributionDays"][0]["date"],
        "stars": sum(r["stargazerCount"] for r in repos.values()),
        "releases": sum(r["releases"]["totalCount"] for r in repos.values()),
        "repos": u["repositories"]["totalCount"],
        "followers": u["followers"]["totalCount"],
        "projects": {p["repo"]: proj(p["repo"]) for p in PROJECTS},
    }


def load_data(offline: bool) -> dict:
    if not offline:
        try:
            data = fetch()
            DATA_FILE.write_text(json.dumps(data, separators=(",", ":")) + "\n")
            return data
        except Exception as exc:  # keep the last good snapshot rather than break the page
            print(f"fetch failed, using cached data: {exc}", file=sys.stderr)
    return json.loads(DATA_FILE.read_text())


def latest_ship(data: dict) -> tuple[str, str]:
    shipped = [p for p in PROJECTS if data["projects"][p["repo"]]["release"]]
    best = max(shipped, key=lambda p: data["projects"][p["repo"]]["published"])
    return best["title"], data["projects"][best["repo"]]["release"]


# --------------------------------------------------------------------------
# Drawings
# --------------------------------------------------------------------------

def hero(t: dict, data: dict) -> str:
    W, H = 880, 290
    ship_name, ship_tag = latest_ship(data)
    cx, cy = 728, 145
    orbit = [(58, 30, 22, PROJECTS[0]), (92, 140, 34, PROJECTS[1]),
             (92, 320, 34, PROJECTS[2]), (124, 230, 48, PROJECTS[3])]
    dots = []
    for r, start, secs, p in orbit:
        col = p["accent"][t["accent_index"]]
        dots.append(
            f'<g class="o" style="animation-duration:{secs}s;animation-delay:-{start / 360 * secs:.2f}s">'
            f'<circle cx="{cx + r}" cy="{cy}" r="9" fill="{col}" fill-opacity=".18"/>'
            f'<circle cx="{cx + r}" cy="{cy}" r="4" fill="{col}"/></g>'
        )
    chip_label = f"SHIPPING {ship_name.upper()} {ship_tag}"
    chip_w = 42 + text_width(chip_label, 11, mono=True, spacing=1.2)
    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{t['line']}" fill-opacity="{t['dot_op']}"/></pattern>
  <radialGradient id="fade" cx="{cx}" cy="{cy}" r="440" gradientUnits="userSpaceOnUse"><stop stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
  <radialGradient id="g1" cx="{cx - 20}" cy="30" r="340" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a1']}" stop-opacity="{t['glow1']}"/><stop offset="1" stop-color="{t['a1']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="g2" cx="{W}" cy="{H}" r="300" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a2']}" stop-opacity="{t['glow2']}"/><stop offset="1" stop-color="{t['a2']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="tile" x1="{cx - 36}" y1="{cy - 36}" x2="{cx + 36}" y2="{cy + 36}" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
  <linearGradient id="top" x1="0" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a1']}" stop-opacity="0"/><stop offset=".6" stop-color="{t['a1']}" stop-opacity=".9"/><stop offset="1" stop-color="{t['a2']}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="{t['bg']}"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#m)"/>
  <rect width="{W}" height="{H}" fill="url(#g1)"/>
  <rect width="{W}" height="{H}" fill="url(#g2)"/>
  <rect x="160" width="{W - 200}" height="1.2" fill="url(#top)"/>
  <circle cx="{cx}" cy="{cy}" r="58" stroke="{t['line']}" stroke-opacity="{t['line_op'] + .04:.3f}"/>
  <circle cx="{cx}" cy="{cy}" r="92" stroke="{t['line']}" stroke-opacity="{t['line_op'] + .02:.3f}" stroke-dasharray="2 5"/>
  <circle cx="{cx}" cy="{cy}" r="124" stroke="{t['line']}" stroke-opacity="{t['line_op']:.3f}"/>
  {''.join(dots)}
  <rect x="{cx - 36}" y="{cy - 36}" width="72" height="72" rx="20" fill="url(#tile)"/>
  <rect x="{cx - 35.5}" y="{cy - 35.5}" width="71" height="71" rx="19.5" stroke="#fff" stroke-opacity=".35"/>
  {txt(cx, cy + 9, "KM", 25, "#FFFFFF", 700, anchor="middle", spacing=-0.5)}

  <rect x="48.5" y="40.5" width="{chip_w:.0f}" height="27" rx="13.5" fill="{t['chip']}" stroke="{t['line']}" stroke-opacity="{t['line_op']}"/>
  <circle class="p" cx="64" cy="54" r="6" fill="{t['a2']}" fill-opacity=".35"/>
  <circle cx="64" cy="54" r="3" fill="{t['a2']}"/>
  {txt(78, 58, chip_label, 11, t['muted'], 500, mono=True, spacing=1.2)}

  {txt(45, 134, NAME, 52, t['text'], 700, spacing=-1.8)}
  {txt(48, 174, TAGLINE[0], 18, t['muted'], 400, spacing=-0.1)}
  {txt(48, 199, TAGLINE[1], 18, t['muted'], 400, spacing=-0.1)}
  <rect x="48" y="226" width="28" height="1.5" rx=".75" fill="{t['a1']}"/>
  {txt(48, 252, META, 11, t['subtle'], 500, mono=True, spacing=1.6)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="17.5" stroke="{t['line']}" stroke-opacity="{t['line_op']}"/>
"""
    style = (
        f".o{{transform-origin:{cx}px {cy}px;animation:spin linear infinite}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        ".p{transform-origin:64px 54px;animation:pulse 2.4s ease-out infinite}"
        "@keyframes pulse{0%{transform:scale(.6);opacity:1}100%{transform:scale(1.9);opacity:0}}"
    )
    return svg(W, H, body, f"{NAME}. {' '.join(TAGLINE)}", style)


def pill(t: dict, label: str, icon: str, primary: bool) -> str:
    H = 40
    w = int(18 + 16 + 9 + text_width(label, 14) + 20)
    bg = t["primary_bg"] if primary else t["surface"]
    fg = t["primary_fg"] if primary else t["text"]
    ic = (stroke_icon(icon, 18, 12, 16, fg, 1.7) if icon in STROKE_ICONS
          else solid_icon(SOLID_ICONS[icon], 18, 12, 16, fg))
    stroke = "" if primary else f' stroke="{t["line"]}" stroke-opacity="{t["line_op"] + .04:.3f}"'
    body = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{H - 1}" rx="{(H - 1) / 2}" fill="{bg}"{stroke}/>'
        f"{ic}{txt(43, 25, label, 14, fg, 500)}"
    )
    return svg(w, H, body, label)


def section(t: dict, num: str, title: str) -> str:
    W, H = 880, 36
    x = 2 + text_width(num, 11.5, True, 2) + 14
    end = x + text_width(title, 11.5, True, 2.2) + 16
    body = f"""
<defs><linearGradient id="l" x1="{end:.1f}" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="{t['line']}" stop-opacity="{t['line_op'] + .06:.3f}"/><stop offset="1" stop-color="{t['line']}" stop-opacity="0"/></linearGradient></defs>
{txt(2, 22, num, 11.5, t['a1'], 600, mono=True, spacing=2)}
{txt(round(x, 1), 22, title, 11.5, t['muted'], 600, mono=True, spacing=2.2)}
<rect x="{end:.1f}" y="18" width="{W - end:.1f}" height="1" fill="url(#l)"/>
"""
    return svg(W, H, body, title.title())


def about(t: dict, data: dict) -> str:
    W, H = 880, 212
    ship_name, ship_tag = latest_ship(data)
    facts = [
        ("NOW", f"Shipping {ship_name} {ship_tag}"),
        ("STUDYING", "Engineering at SMU MedTech"),
        ("FOCUS", "Systems, security and AI agents"),
        ("BASED IN", "Ariana, Tunisia  ·  UTC+1"),
    ]
    lines = "".join(txt(36, 58 + i * 28, s, 16.5, t["text"] if i == 0 else t["muted"], 400, spacing=-0.1)
                    for i, s in enumerate(ABOUT))
    fx = 552
    rows = []
    for i, (k, v) in enumerate(facts):
        y = 32 + i * 38
        if i:
            rows.append(hline(t, fx, y - 7, W - fx - 32, -0.02))
        rows.append(txt(fx, y + 17, k, 10.5, t["subtle"], 600, mono=True, spacing=1.6))
        rows.append(txt(fx + 92, y + 17, v, 14, t["text"], 500))
    body = f"""
{frame(t, W, H)}
<rect x="520" y="28" width="1" height="{H - 56}" fill="{t['line']}" fill-opacity="{t['line_op']}"/>
{lines}
<circle cx="40" cy="{58 + 4 * 28 + 14}" r="3" fill="{t['a2']}"/>
{txt(51, 58 + 4 * 28 + 18, ABOUT_FOOT, 13, t['subtle'], 400)}
{''.join(rows)}
"""
    return svg(W, H, body, " ".join(ABOUT))


def card(t: dict, p: dict, info: dict) -> str:
    W, H = 432, 212
    acc = p["accent"][t["accent_index"]]
    tag = info["release"] or "source"
    tag_w = text_width(tag, 11, True) + 22
    lang_w = text_width(info["language"], 13)
    star_x = 46 + lang_w + 16
    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <radialGradient id="g" cx="{W}" cy="0" r="280" gradientUnits="userSpaceOnUse"><stop stop-color="{acc}" stop-opacity="{t['glow1'] * .75:.2f}"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>
  <linearGradient id="top" x1="0" y1="0" x2="{W}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="{acc}" stop-opacity="0"/><stop offset=".72" stop-color="{acc}" stop-opacity=".85"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#c)">
  {frame(t, W, H)}
  <rect width="{W}" height="{H}" fill="url(#g)"/>
  <rect x="60" width="{W - 80}" height="1.2" fill="url(#top)"/>
</g>
<rect x="28" y="28" width="44" height="44" rx="12" fill="{acc}" fill-opacity="{t['tile_op']}"/>
<rect x="28.5" y="28.5" width="43" height="43" rx="11.5" stroke="{acc}" stroke-opacity=".38"/>
{stroke_icon(p['glyph'], 39, 39, 22, acc, 1.8)}
{txt(88, 49, p['title'], 19, t['text'], 650, spacing=-0.3)}
{txt(88, 67, f"{LOGIN.lower()}/{p['repo']}", 11.5, t['subtle'], 400, mono=True)}
<rect x="{W - 28.5 - tag_w:.1f}" y="31.5" width="{tag_w:.1f}" height="23" rx="11.5" fill="{t['chip']}" stroke="{t['line']}" stroke-opacity="{t['line_op']}"/>
{txt(round(W - 28.5 - tag_w / 2, 1), 47, tag, 11, t['muted'], 500, mono=True, anchor="middle")}
{txt(28, 110, p['lines'][0], 14, t['muted'], 400)}
{txt(28, 131, p['lines'][1], 14, t['muted'], 400)}
{hline(t, 28, 158, W - 56, -0.02)}
<circle cx="33" cy="183" r="5" fill="{info['color']}"/>
{txt(45, 187.5, info['language'], 13, t['muted'], 500)}
{stroke_icon('star', round(star_x, 1), 175.5, 15, t['muted'], 1.7)}
{txt(round(star_x + 20, 1), 187.5, fmt(info['stars']), 13, t['muted'], 500)}
{txt(W - 28, 187.5, p['tag'], 12, t['subtle'], 400, anchor="end")}
"""
    return svg(W, H, body, f"{p['title']}: {' '.join(p['lines'])}")


def stack(t: dict) -> str:
    W, row_h, gap, x0, pad = 880, 34, 8, 160, 28
    def chip_w(name: str) -> float:
        return 12 + 16 + 8 + text_width(name, 13) + 13
    layout, y = [], pad
    for gi, (label, items) in enumerate(STACK):
        if gi:
            layout.append(("rule", y + 4))
            y += 9 + 8
        layout.append(("label", label, y))
        x = x0
        for name, icon in items:
            w = chip_w(name)
            if x + w > W - 28:
                x, y = x0, y + row_h + gap
            layout.append(("chip", name, icon, x, y, w))
            x += w + 8
        y += row_h
    H = int(y + pad)
    parts = [frame(t, W, H)]
    for item in layout:
        if item[0] == "rule":
            parts.append(hline(t, 32, item[1], W - 64, -0.04))
        elif item[0] == "label":
            parts.append(txt(32, item[2] + 21.5, item[1], 10.5, t["subtle"], 600, mono=True, spacing=1.6))
        else:
            _, name, icon, x, y, w = item
            col = BRAND.get(icon, t["text"])
            if contrast(col, t["chip"]) < 1.7:
                col = t["text"]
            parts.append(
                f'<rect x="{x + .5:.1f}" y="{y + .5}" width="{w - 1:.1f}" height="{row_h - 1}" rx="9" '
                f'fill="{t["chip"]}" stroke="{t["line"]}" stroke-opacity="{t["line_op"]}"/>'
            )
            if icon.startswith("s:"):
                parts.append(stroke_icon(icon[2:], x + 12, y + 9, 16, col, 1.8))
            else:
                parts.append(solid_icon(ICONS[icon]["d"], x + 12, y + 9, 16, col))
            parts.append(txt(round(x + 36, 1), y + 21.5, name, 13, t["text"], 500))
    return svg(W, H, "".join(parts), "Stack: " + ", ".join(n for _, it in STACK for n, _ in it))


def credentials(t: dict) -> str:
    W = 880
    col_w = (W - 64 - 32) / 2
    blocks = []
    heights = []
    for label, rows in CREDENTIALS:
        heights.append(30 + len(rows) * 44)
    H = int(28 + max(heights[0], heights[2]) + 24 + max(heights[1], heights[3]) + 20)
    parts = [frame(t, W, H)]
    top2 = 28 + max(heights[0], heights[2]) + 12
    parts.append(hline(t, 32, top2 - 2, W - 64, -0.02))
    parts.append(f'<rect x="{W / 2:.0f}" y="28" width="1" height="{H - 56}" fill="{t["line"]}" fill-opacity="{t["line_op"]}"/>')
    order = [(0, 32, 28), (2, 32 + col_w + 32, 28), (1, 32, top2 + 12), (3, 32 + col_w + 32, top2 + 12)]
    for idx, x, y in order:
        label, rows = CREDENTIALS[idx]
        x = round(x + (8 if x > 32 else 4), 1)
        parts.append(txt(x, y + 14, label, 10.5, t["a1"], 600, mono=True, spacing=1.6))
        for i, (title, sub) in enumerate(rows):
            ry = y + 30 + i * 44
            parts.append(txt(x, ry + 15, title, 14, t["text"], 500))
            parts.append(txt(x, ry + 33, sub, 12.5, t["muted"], 400))
    return svg(W, H, "".join(parts), "; ".join(f"{a}: {b}" for _, r in CREDENTIALS for a, b in r))


def activity(t: dict, data: dict) -> str:
    W, H = 880, 312
    stats = [
        (fmt(data["contributions"]), "CONTRIBUTIONS", "in the past 12 months"),
        (fmt(data["stars"]), "STARS", "across my repositories"),
        (fmt(data["releases"]), "RELEASES", "shipped to date"),
        (fmt(data["repos"]), "PROJECTS", "original public repos"),
    ]
    parts = [frame(t, W, H)]
    col_w = (W - 64) / 4
    for i, (val, label, sub) in enumerate(stats):
        x = 36 + i * col_w
        if i:
            parts.append(f'<rect x="{x - 18:.1f}" y="32" width="1" height="64" fill="{t["line"]}" fill-opacity="{t["line_op"]}"/>')
        parts.append(txt(round(x, 1), 44, label, 10.5, t["subtle"], 600, mono=True, spacing=1.6))
        parts.append(txt(round(x - 1.5, 1), 80, val, 32, t["text"], 650, spacing=-1))
        parts.append(txt(round(x, 1), 99, sub, 12, t["muted"], 400))
    parts.append(hline(t, 32, 124, W - 64))

    counts = sorted(c for w in data["weeks"] for _, c in w if c)
    q = [counts[int(len(counts) * f)] for f in (0.25, 0.5, 0.75)] if counts else [0, 0, 0]

    def level(c: int) -> int:
        return 0 if not c else 1 + sum(c > v for v in q)

    cell, step = 11, 14
    weeks = data["weeks"]
    grid_w = len(weeks) * step - 3
    gx = round((W - grid_w) / 2, 1)
    gy = 172
    first = dt.date.fromisoformat(data["first_day"])
    first = first - dt.timedelta(days=weeks[0][0][0])  # Sunday of the first column
    last_label = -10
    for wi, week in enumerate(weeks):
        for weekday, count in week:
            parts.append(
                f'<rect x="{gx + wi * step:.1f}" y="{gy + weekday * step}" width="{cell}" height="{cell}" '
                f'rx="2.5" fill="{t["heat"][level(count)]}"/>'
            )
        sunday = first + dt.timedelta(days=wi * 7)
        if sunday.day <= 7 and wi - last_label >= 3 and wi < len(weeks) - 1:
            parts.append(txt(round(gx + wi * step, 1), gy - 10, sunday.strftime("%b"), 10.5, t["subtle"], 500, mono=True))
            last_label = wi

    fy = gy + 7 * step + 20
    parts.append(txt(gx, fy, f"Updated {data['fetched']}", 11, t["subtle"], 400, mono=True))
    lx = gx + grid_w - 5 * step - 34
    parts.append(txt(round(lx - 8, 1), fy, "Less", 11, t["subtle"], 400, mono=True, anchor="end"))
    for i, c in enumerate(t["heat"]):
        parts.append(f'<rect x="{lx + i * step:.1f}" y="{fy - 10}" width="{cell}" height="{cell}" rx="2.5" fill="{c}"/>')
    parts.append(txt(round(lx + 5 * step + 5, 1), fy, "More", 11, t["subtle"], 400, mono=True))
    return svg(W, H, "".join(parts),
               f"{fmt(data['contributions'])} contributions in the last year, {data['stars']} stars, "
               f"{data['releases']} releases, {data['repos']} public projects")


# --------------------------------------------------------------------------

def main() -> None:
    data = load_data(offline="--offline" in sys.argv)
    for name, t in THEMES.items():
        out = ASSETS / name
        out.mkdir(parents=True, exist_ok=True)
        files = {
            "hero.svg": hero(t, data),
            "about.svg": about(t, data),
            "stack.svg": stack(t),
            "activity.svg": activity(t, data),
            "section-about.svg": section(t, "01", "ABOUT"),
            "section-work.svg": section(t, "02", "SELECTED WORK"),
            "section-stack.svg": section(t, "03", "STACK"),
            "section-activity.svg": section(t, "05", "ACTIVITY"),
            "section-credentials.svg": section(t, "04", "EDUCATION & CREDENTIALS"),
            "credentials.svg": credentials(t),
        }
        for i, (slug, label, icon, _) in enumerate(LINKS):
            files[f"link-{slug}.svg"] = pill(t, label, icon, primary=(i == 0))
        for p in PROJECTS:
            files[f"card-{p['repo']}.svg"] = card(t, p, data["projects"][p["repo"]])
        for fname, content in files.items():
            (out / fname).write_text(content)
    print(f"built {len(files)} assets x {len(THEMES)} themes")


if __name__ == "__main__":
    main()
