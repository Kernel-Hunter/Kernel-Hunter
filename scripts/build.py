#!/usr/bin/env python3
"""Build the profile README and every SVG it uses, in dark and light.

    python3 scripts/build.py            # fetch fresh numbers from GitHub, then draw
    python3 scripts/build.py --offline  # redraw from scripts/data.json only

Projects are not hard-coded: the cards are drawn from the repositories you
pin on your profile, so pinning or unpinning on GitHub updates the page. Live numbers (contributions, stars,
releases, repositories) are fetched from the GitHub GraphQL API, using
GITHUB_TOKEN or `gh auth token`, and cached in scripts/data.json.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
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

# ==========================================================================
# Content: the only part you should need to edit
# ==========================================================================

NAME = "Karim Masmoudi"
STATUS = "OPEN TO INTERNSHIPS & RESEARCH"
TAGLINE = ["Software engineer working across systems,", "security and AI, from the kernel to the browser."]
META = "ARIANA, TUNISIA  ·  SMU MEDTECH  ·  @KERNEL-HUNTER"

LINKS = [  # (slug, label, icon, href)
    ("portfolio", "Portfolio", "s:globe", "https://karimmasmoudi.vercel.app"),
    ("linkedin", "LinkedIn", "s:linkedin", "https://www.linkedin.com/in/karim-masmoudi-224816291/"),
    ("x", "X", "x", "https://x.com/Karim__Masmoudi"),
    ("email", "Email", "s:mail", "mailto:karim.masmoudi.pro@gmail.com"),
]

ABOUT = [
    "Engineer in training, based in Tunisia.",
    "I like software that runs close to the machine, and I",
    "care about tools that are fast, private and free to use.",
    "Most of what I build is open source.",
]
FACTS = [
    ("STUDYING", "Software engineering, MedTech"),
    ("FOCUS", "Systems, security and AI"),
    ("GOAL", "Ph.D. in software engineering"),
    ("SPEAKS", "Arabic, English, French"),
]

FOCUS = [  # (icon, hue index, title, two lines)
    ("s:window", 0, "Native apps", ["Desktop software for macOS, Windows and", "Linux that feels at home on the system."]),
    ("s:spark", 1, "AI & developer tools", ["Agents, MCP servers and tooling that", "make everyday engineering faster."]),
    ("s:shield", 2, "Security & systems", ["Kernel modules, sandboxing, and", "hands-on offensive security practice."]),
    ("s:signal", 3, "Embedded & IoT", ["ESP32, Arduino and Raspberry Pi builds", "that connect sensors to software."]),
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

CREDENTIALS = [
    ("EDUCATION", [("Engineering program, third year", "MedTech, South Mediterranean University"),
                   ("Baccalaureate, experimental sciences", "Tunisia")]),
    ("COMMUNITY", [("Black Hat MEA · LEAP", "Researcher, 2022 to present"),
                   ("GITEX Global · World AI Summit", "Attended")]),
    ("CERTIFICATES", [("Database Management with Java and SQL", "Amazon"),
                      ("Programming Fundamentals", "Duke University"),
                      ("Game Design and Development with Unity", "Michigan State University"),
                      ("Machine Learning & AI with Python", "Mind Luster")]),
    ("LANGUAGES", [("Arabic", "Native"), ("English", "Fluent · IELTS 7.5"), ("French", "Intermediate")]),
]

BRAND = {
    "swift": "#F05138", "typescript": "#3178C6", "python": "#4B8BBE", "c": "#A8B9CC",
    "openjdk": "#E76F00", "javascript": "#F7DF1E", "linux": "#FCC624", "debian": "#D70A53",
    "githubactions": "#2088FF", "git": "#F05032", "mysql": "#4479A1", "vuedotjs": "#4FC08D",
    "wireshark": "#1679A7", "burpsuite": "#FF6633", "gnubash": "#4EAA25", "html5": "#E34F26",
    "css": "#663399", "react": "#61DAFB", "vuetify": "#1867C0", "vite": "#9135FF",
    "nodedotjs": "#5FA04E", "opencv": "#5C3EE8", "claude": "#D97757", "kalilinux": "#557C94",
    "espressif": "#E7352C", "arduino": "#00878F", "raspberrypi": "#C51A4A", "googlechrome": "#4285F4",
    "xcode": "#147EFB", "homebrew": "#FBB040", "s:terminal": "#5391FE", "s:windows": "#0078D4",
}

# A card's icon is picked from the repository's topics, first match wins.
TOPIC_ICONS = [
    ({"virtualization", "sandbox", "microvm", "container"}, "cube"),
    ({"tts", "text-to-speech", "read-aloud", "audio"}, "wave"),
    ({"trading", "charting", "charts", "candlestick-chart", "stocks"}, "chart"),
    ({"security", "privacy", "pentest"}, "shield"),
    ({"ai-agents", "mcp", "llm", "ai"}, "spark"),
    ({"macos", "macos-app", "menu-bar-app", "desktop"}, "window"),
    ({"iot", "embedded", "esp32", "arduino"}, "signal"),
    ({"kernel", "linux-kernel"}, "chip"),
]

# ==========================================================================
# Themes: tuned to sit on GitHub's own dark (#0d1117) and light canvases
# ==========================================================================

THEMES = {
    "dark": dict(
        card="#0F141B", card2="#121822", chip="#161C26", line="#E6EDF3", lo=0.09,
        text="#E6EDF3", muted="#9AA4B1", subtle="#6A7380",
        a1="#8B7BFF", a2="#4CC9F0", a3="#F472B6",
        hues=["#8B7BFF", "#4CC9F0", "#F472B6", "#F5B54A"],
        glow=0.34, tile=0.13,
        heat=["#161C26", "#2B2768", "#4637B3", "#6E5AF0", "#A99CFF"],
        btn_bg="#E6EDF3", btn_fg="#0D1117",
    ),
    "light": dict(
        card="#FFFFFF", card2="#FAFBFC", chip="#F6F8FA", line="#1F2328", lo=0.11,
        text="#1F2328", muted="#59636E", subtle="#8C959F",
        a1="#6248F5", a2="#0A8BD6", a3="#D9307E",
        hues=["#6248F5", "#0A8BD6", "#D9307E", "#C27803"],
        glow=0.13, tile=0.09,
        heat=["#EFF2F5", "#DAD4FF", "#B2A5FF", "#7F68F6", "#5236DB"],
        btn_bg="#1F2328", btn_fg="#FFFFFF",
    ),
}

SANS = "Inter,'SF Pro Display',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

STROKE = {
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9S9.4 5.6 12 3Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
    "linkedin": '<rect x="3" y="3" width="18" height="18" rx="3.5"/><path d="M8 10.5V16M8 7.6v.1M11.5 16v-5.5M11.5 13c0-1.6 1-2.6 2.3-2.6s2.2.9 2.2 2.6V16"/>',
    "window": '<rect x="3" y="4.5" width="18" height="15" rx="3"/><path d="M3 9h18"/><circle cx="6.2" cy="6.8" r=".4"/><circle cx="8.4" cy="6.8" r=".4"/>',
    "spark": '<path d="M12 3.5c.6 4.4 2.6 6.4 7 7-4.4.6-6.4 2.6-7 7-.6-4.4-2.6-6.4-7-7 4.4-.6 6.4-2.6 7-7Z"/><path d="M19 3v3M17.5 4.5h3"/>',
    "shield": '<path d="M12 3 4.5 6v5.5c0 4.6 3.1 8.3 7.5 9.5 4.4-1.2 7.5-4.9 7.5-9.5V6Z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "signal": '<circle cx="12" cy="12" r="1.8"/><path d="M8.2 8.2a5.4 5.4 0 0 0 0 7.6M15.8 8.2a5.4 5.4 0 0 1 0 7.6M5.3 5.3a9.5 9.5 0 0 0 0 13.4M18.7 5.3a9.5 9.5 0 0 1 0 13.4"/>',
    "chart": '<path d="M4 19.5h16"/><path d="M7.5 4v2.5M7.5 14.5V17M16.5 4v4M16.5 15v2"/><rect x="5.5" y="6.5" width="4" height="8" rx="1"/><rect x="14.5" y="8" width="4" height="7" rx="1"/>',
    "wave": '<path d="M4 10.5v3M8 7.5v9M12 4.5v15M16 8v8M20 10.5v3"/>',
    "cube": '<path d="M12 3 20 7.5v9L12 21l-8-4.5v-9Z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/>',
    "code": '<path d="m8.5 7.5-5 4.5 5 4.5M15.5 7.5l5 4.5-5 4.5M13.5 5l-3 14"/>',
    "star": '<path d="m12 3.5 2.6 5.3 5.8.8-4.2 4.1 1 5.8L12 16.8l-5.2 2.7 1-5.8-4.2-4.1 5.8-.8Z"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9.5 2.5v3.5M14.5 2.5v3.5M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5"/>',
    "terminal": '<rect x="2.5" y="4" width="19" height="16" rx="3" fill="currentColor" stroke="none"/><path d="m7 9 3.5 3L7 15M12.5 15.5h4.5" stroke="#fff"/>',
    "windows": '<path d="M3 5.3 10.6 4.2v7.2H3ZM11.6 4.1 21 2.7v8.7h-9.4ZM3 12.4h7.6v7.3L3 18.6ZM11.6 12.4H21v8.8l-9.4-1.3Z" fill="currentColor" stroke="none"/>',
}

# ==========================================================================
# Helpers
# ==========================================================================

NARROW, WIDE = set("il.,:;'|!·I1 ()[]tfjr"), set("mwMW@%")


def tw(s: str, size: float, mono: bool = False, sp: float = 0.0) -> float:
    """Approximate text advance, used to size chips and buttons."""
    if mono:
        return len(s) * size * 0.6 + sp * max(len(s) - 1, 0)
    w = sum(0.30 if c in NARROW else 0.86 if c in WIDE else 0.66 if c.isupper() else 0.55 for c in s)
    return w * size + sp * max(len(s) - 1, 0)


def lum(h: str) -> float:
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a: str, b: str) -> float:
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def n(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def T(x, y, s, cls: str, fill: str, anchor: str = "") -> str:
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{n(x)}" y="{n(y)}" class="{cls}" fill="{fill}"{a}>{escape(s)}</text>'


# text styles: shared once per file instead of repeated on every <text>
STYLES = {
    "h1": f"font:700 50px {SANS};letter-spacing:-1.8px",
    "lead": f"font:400 18px {SANS};letter-spacing:-.1px",
    "body": f"font:400 15.5px {SANS};letter-spacing:-.1px",
    "b14": f"font:500 14px {SANS}",
    "t17": f"font:600 17px {SANS};letter-spacing:-.2px",
    "s13": f"font:500 13px {SANS}",
    "r13": f"font:400 13px {SANS}",
    "r135": f"font:400 13.5px {SANS}",
    "r12": f"font:400 12.5px {SANS}",
    "num": f"font:650 32px {SANS};letter-spacing:-1px",
    "eye": f"font:600 11px {MONO};letter-spacing:2px",
    "lab": f"font:600 10.5px {MONO};letter-spacing:1.6px",
    "m11": f"font:500 11px {MONO};letter-spacing:1.2px",
    "m10": f"font:500 10.5px {MONO}",
}


def svg(w: int, h: int, body: str, label: str, extra_css: str = "") -> str:
    used = set(re.findall(r'class="(\w+)"', body))
    css = "".join(f".{k}{{{v}}}" for k, v in STYLES.items() if k in used) + extra_css
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" '
           f'height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img" aria-label="{escape(label)}">'
           f"<style>{css}</style>{body}</svg>\n")
    return re.sub(r">\s+<", "><", out)


def icon(name: str, x: float, y: float, size: float, color: str, width: float = 1.8) -> str:
    s = size / 24
    if name.startswith("s:"):
        return (f'<g transform="translate({n(x)} {n(y)}) scale({s:.4g})" color="{color}" stroke="{color}" '
                f'stroke-width="{width / s:.2f}" stroke-linecap="round" stroke-linejoin="round">'
                f"{STROKE[name[2:]]}</g>")
    return f'<path transform="translate({n(x)} {n(y)}) scale({s:.4g})" d="{ICONS[name]["d"]}" fill="{color}"/>'


def card(t: dict, w: int, h: int, body: str, eyebrow: str = "", num: str = "", accent_line: bool = True) -> str:
    """Shared surface: soft gradient, hairline border, top highlight, optional eyebrow."""
    top = (f'<rect x="80" y="0" width="{w - 160}" height="1" fill="url(#hl)"/>' if accent_line else "")
    eye = ""
    if eyebrow:
        x2 = 28 + tw(num, 11, True, 2) + 12
        eye = T(28, 38, num, "eye", t["a1"]) + T(x2, 38, eyebrow, "eye", t["subtle"])
    return f"""
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="0" y2="{h}" gradientUnits="userSpaceOnUse"><stop stop-color="{t['card2']}"/><stop offset="1" stop-color="{t['card']}"/></linearGradient>
 <linearGradient id="hl" x1="80" y1="0" x2="{w - 80}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a1']}" stop-opacity="0"/><stop offset=".5" stop-color="{t['a1']}" stop-opacity=".7"/><stop offset="1" stop-color="{t['a2']}" stop-opacity="0"/></linearGradient>
</defs>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="url(#bg)" stroke="{t['line']}" stroke-opacity="{t['lo']}"/>
{top}{eye}{body}"""


def rule(t: dict, x, y, w, op_delta=-0.03) -> str:
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="1" fill="{t["line"]}" fill-opacity="{t["lo"] + op_delta:.3f}"/>'


def vrule(t: dict, x, y, h) -> str:
    return f'<rect x="{n(x)}" y="{n(y)}" width="1" height="{n(h)}" fill="{t["line"]}" fill-opacity="{t["lo"] - .02:.3f}"/>'


# ==========================================================================
# Data
# ==========================================================================

QUERY = """query($login:String!){user(login:$login){
 contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount weekday}}}}
 pinnedItems(first:6,types:REPOSITORY){nodes{... on Repository{name url description stargazerCount
  primaryLanguage{name color} latestRelease{tagName} repositoryTopics(first:20){nodes{topic{name}}}}}}
 repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100){totalCount nodes{stargazerCount releases{totalCount}}}}}"""


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
        raise RuntimeError("no GitHub token")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json", "User-Agent": "profile-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        p = json.load(r)
    if p.get("errors"):
        raise RuntimeError(p["errors"])
    u = p["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    repos = u["repositories"]["nodes"]
    return {
        "fetched": dt.date.today().isoformat(),
        "contributions": cal["totalContributions"],
        "weeks": [[[d["weekday"], d["contributionCount"]] for d in w["contributionDays"]] for w in cal["weeks"]],
        "first_day": cal["weeks"][0]["contributionDays"][0]["date"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "releases": sum(r["releases"]["totalCount"] for r in repos),
        "repos": u["repositories"]["totalCount"],
        "pinned": [{
            "name": r["name"], "url": r["url"], "description": r["description"] or "",
            "stars": r["stargazerCount"], "release": (r["latestRelease"] or {}).get("tagName", ""),
            "language": (r["primaryLanguage"] or {}).get("name", ""),
            "color": (r["primaryLanguage"] or {}).get("color") or "#8C959F",
            "topics": [x["topic"]["name"] for x in r["repositoryTopics"]["nodes"]],
        } for r in u["pinnedItems"]["nodes"]],
    }


def load_data(offline: bool) -> dict:
    if not offline:
        try:
            d = fetch()
            DATA_FILE.write_text(json.dumps(d, separators=(",", ":")) + "\n")
            return d
        except Exception as e:
            print(f"fetch failed, using cache: {e}", file=sys.stderr)
    return json.loads(DATA_FILE.read_text())


# ==========================================================================
# Drawings
# ==========================================================================

def hero(t: dict) -> str:
    W, H, cx, cy = 880, 268, 730, 134
    chip_w = 40 + tw(STATUS, 11, True, 1.2)
    rings = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{t["line"]}" stroke-opacity="{op}"{da}/>'
        for r, op, da in ((54, t["lo"] + .05, ""), (86, t["lo"] + .02, ' stroke-dasharray="2 6"'), (118, t["lo"], "")))
    orbit = "".join(
        f'<g class="o" style="animation-duration:{s}s;animation-delay:-{d}s">'
        f'<circle cx="{cx + r}" cy="{cy}" r="8" fill="{c}" fill-opacity=".2"/><circle cx="{cx + r}" cy="{cy}" r="3.5" fill="{c}"/></g>'
        for r, s, d, c in ((54, 20, 4, t["a2"]), (86, 32, 20, t["a1"]), (118, 46, 9, t["a3"])))
    arc = (f'<g class="o" style="animation-duration:14s"><circle cx="{cx}" cy="{cy}" r="86" stroke="url(#arc)" '
           f'stroke-width="1.6" stroke-dasharray="90 450" stroke-linecap="round"/></g>')
    body = f"""
<defs>
 <clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
 <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" stroke="{t['line']}" stroke-opacity=".045"/></pattern>
 <radialGradient id="fade" cx="{cx}" cy="{cy}" r="380" gradientUnits="userSpaceOnUse"><stop stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
 <mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
 <radialGradient id="g1" cx="{cx}" cy="20" r="320" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a1']}" stop-opacity="{t['glow']}"/><stop offset="1" stop-color="{t['a1']}" stop-opacity="0"/></radialGradient>
 <radialGradient id="g2" cx="{W}" cy="{H}" r="280" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a2']}" stop-opacity="{t['glow'] * .6:.2f}"/><stop offset="1" stop-color="{t['a2']}" stop-opacity="0"/></radialGradient>
 <radialGradient id="g3" cx="40" cy="{H}" r="260" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a3']}" stop-opacity="{t['glow'] * .3:.2f}"/><stop offset="1" stop-color="{t['a3']}" stop-opacity="0"/></radialGradient>
 <linearGradient id="tile" x1="{cx - 34}" y1="{cy - 34}" x2="{cx + 34}" y2="{cy + 34}" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
 <linearGradient id="arc" x1="{cx - 86}" y1="0" x2="{cx + 86}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}"/></linearGradient>
 <linearGradient id="hl" x1="120" y1="0" x2="{W - 40}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="{t['a3']}" stop-opacity="0"/><stop offset=".45" stop-color="{t['a1']}"/><stop offset="1" stop-color="{t['a2']}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#c)">
 <rect width="{W}" height="{H}" fill="{t['card']}"/>
 <rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#m)"/>
 <rect width="{W}" height="{H}" fill="url(#g1)"/><rect width="{W}" height="{H}" fill="url(#g2)"/><rect width="{W}" height="{H}" fill="url(#g3)"/>
 <rect x="120" width="{W - 160}" height="1.2" fill="url(#hl)"/>
 {rings}{arc}{orbit}
 <rect x="{cx - 34}" y="{cy - 34}" width="68" height="68" rx="19" fill="url(#tile)"/>
 <rect x="{cx - 33.5}" y="{cy - 33.5}" width="67" height="67" rx="18.5" stroke="#fff" stroke-opacity=".4"/>
 {T(cx, cy + 8.5, "KM", "t17", "#FFFFFF", "middle").replace('class="t17"', 'class="t17" style="font-size:24px;font-weight:700"')}
 <rect x="44.5" y="38.5" width="{n(chip_w)}" height="27" rx="13.5" fill="{t['chip']}" stroke="{t['line']}" stroke-opacity="{t['lo']}"/>
 <circle class="p" cx="59" cy="52" r="6" fill="#3FB950" fill-opacity=".4"/><circle cx="59" cy="52" r="3" fill="#3FB950"/>
 {T(72, 56, STATUS, "m11", t['muted'])}
 {T(42, 128, NAME, "h1", t['text'])}
 {T(44, 166, TAGLINE[0], "lead", t['muted'])}
 {T(44, 191, TAGLINE[1], "lead", t['muted'])}
 <rect x="44" y="214" width="26" height="1.5" rx=".75" fill="url(#tile)"/>
 {T(44, 238, META, "m11", t['subtle'])}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" stroke="{t['line']}" stroke-opacity="{t['lo']}"/>"""
    css = (f".o{{transform-origin:{cx}px {cy}px;animation:spin linear infinite}}@keyframes spin{{to{{transform:rotate(360deg)}}}}"
           ".p{transform-origin:59px 52px;animation:pulse 2.4s ease-out infinite}"
           "@keyframes pulse{0%{transform:scale(.6);opacity:1}100%{transform:scale(2);opacity:0}}"
           "@media (prefers-reduced-motion:reduce){.o,.p{animation:none}}")
    return svg(W, H, body, f"{NAME}. {' '.join(TAGLINE)}", css)


def button(t: dict, label: str, ic: str, primary: bool) -> str:
    H = 38
    w = int(16 + 16 + 9 + tw(label, 14) + 18)
    bg, fg = (t["btn_bg"], t["btn_fg"]) if primary else (t["chip"], t["text"])
    border = "" if primary else f' stroke="{t["line"]}" stroke-opacity="{t["lo"] + .04:.2f}"'
    body = (f'<rect x=".5" y=".5" width="{w - 1}" height="{H - 1}" rx="{(H - 1) / 2}" fill="{bg}"{border}/>'
            + icon(ic, 16, 11, 16, fg, 1.7) + T(41, 24, label, "b14", fg))
    return svg(w, H, body, label)


def about(t: dict) -> str:
    W, H = 880, 216
    lines = "".join(T(28, 78 + i * 26, s, "body", t["text"] if i == 0 else t["muted"]) for i, s in enumerate(ABOUT))
    fx, rows = 540, []
    for i, (k, v) in enumerate(FACTS):
        y = 58 + i * 36
        if i:
            rows.append(rule(t, fx, y - 6, W - fx - 28))
        rows.append(T(fx, y + 18, k, "lab", t["subtle"]) + T(fx + 96, y + 18, v, "b14", t["text"]))
    body = vrule(t, 508, 58, H - 86) + lines + "".join(rows)
    return svg(W, H, card(t, W, H, body, "ABOUT", "01"), " ".join(ABOUT))


def focus(t: dict) -> str:
    W, tile_h, gap = 880, 96, 14
    tile_w = (W - 56 - gap) / 2
    H = int(60 + 2 * tile_h + gap + 28)
    tiles = []
    for i, (ic, hue, title, lines) in enumerate(FOCUS):
        col = t["hues"][hue]
        x, y = 28 + (i % 2) * (tile_w + gap), 60 + (i // 2) * (tile_h + gap)
        tiles.append(
            f'<rect x="{n(x + .5)}" y="{n(y + .5)}" width="{n(tile_w - 1)}" height="{tile_h - 1}" rx="12" fill="{t["chip"]}" '
            f'stroke="{t["line"]}" stroke-opacity="{t["lo"] - .02:.2f}"/>'
            f'<rect x="{n(x + 18)}" y="{y + 20}" width="40" height="40" rx="11" fill="{col}" fill-opacity="{t["tile"]}"/>'
            f'<rect x="{n(x + 18.5)}" y="{y + 20.5}" width="39" height="39" rx="10.5" stroke="{col}" stroke-opacity=".35"/>'
            + icon(ic, x + 28, y + 30, 20, col, 1.8)
            + T(x + 74, y + 34, title, "t17", t["text"])
            + T(x + 74, y + 56, lines[0], "r13", t["muted"])
            + T(x + 74, y + 74, lines[1], "r13", t["muted"]))
    return svg(W, H, card(t, W, H, "".join(tiles), "WHAT I WORK ON", "03"),
               "; ".join(f"{a}: {' '.join(c)}" for _, _, a, c in FOCUS))


def wrap(text: str, width: float, size: float, lines: int = 2) -> list[str]:
    words, out, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if tw(trial, size) <= width:
            cur = trial
        else:
            out.append(cur)
            cur = w
            if len(out) == lines:
                break
    if len(out) < lines and cur:
        out.append(cur)
    if len(out) == lines and " ".join(out) != " ".join(words):
        last = out[-1]
        while tw(last + "…", size) > width and " " in last:
            last = last.rsplit(" ", 1)[0]
        out[-1] = last.rstrip(",.;:") + "…"
    return out


def pretty(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title() if name.islower() else name


def project_icon(topics: list[str]) -> str:
    ts = set(topics)
    return next((ic for keys, ic in TOPIC_ICONS if ts & keys), "code")


def section_header(t: dict, num: str, title: str) -> str:
    W, H = 880, 34
    x2 = 28 + tw(num, 11, True, 2) + 12
    end = x2 + tw(title, 11, True, 2) + 16
    body = (f'<defs><linearGradient id="l" x1="{n(end)}" y1="0" x2="{W - 28}" y2="0" gradientUnits="userSpaceOnUse">'
            f'<stop stop-color="{t["line"]}" stop-opacity="{t["lo"] + .05:.2f}"/><stop offset="1" stop-color="{t["line"]}" stop-opacity="0"/></linearGradient></defs>'
            + T(28, 21, num, "eye", t["a1"]) + T(x2, 21, title, "eye", t["subtle"])
            + f'<rect x="{n(end)}" y="16.5" width="{n(W - 28 - end)}" height="1" fill="url(#l)"/>')
    return svg(W, H, body, title.title())


def project(t: dict, r: dict, i: int) -> str:
    W, H = 432, 196
    acc = t["hues"][i % len(t["hues"])]
    tag = r["release"] or "source"
    tag_w = tw(tag, 11, True) + 20
    desc = wrap(r["description"], W - 56, 13.5)
    lang_w = tw(r["language"], 13)
    sx = 44 + lang_w + 16
    topics = "  ·  ".join(r["topics"][:2])
    body = f"""
<defs>
 <clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath>
 <linearGradient id="bg" x1="0" y1="0" x2="0" y2="{H}" gradientUnits="userSpaceOnUse"><stop stop-color="{t['card2']}"/><stop offset="1" stop-color="{t['card']}"/></linearGradient>
 <radialGradient id="g" cx="{W}" cy="0" r="260" gradientUnits="userSpaceOnUse"><stop stop-color="{acc}" stop-opacity="{t['glow'] * .6:.2f}"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></radialGradient>
 <linearGradient id="hl" x1="60" y1="0" x2="{W - 20}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="{acc}" stop-opacity="0"/><stop offset=".7" stop-color="{acc}" stop-opacity=".8"/><stop offset="1" stop-color="{acc}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#g)"/><rect x="60" width="{W - 80}" height="1.2" fill="url(#hl)"/></g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="13.5" stroke="{t['line']}" stroke-opacity="{t['lo']}"/>
<rect x="24" y="24" width="42" height="42" rx="11" fill="{acc}" fill-opacity="{t['tile']}"/>
<rect x="24.5" y="24.5" width="41" height="41" rx="10.5" stroke="{acc}" stroke-opacity=".38"/>
{icon("s:" + project_icon(r["topics"]), 34, 34, 22, acc)}
{T(80, 43, pretty(r["name"]), "t17", t["text"])}
{T(80, 61, f"{LOGIN.lower()}/{r['name']}", "m10", t["subtle"])}
<rect x="{n(W - 24.5 - tag_w)}" y="27.5" width="{n(tag_w)}" height="22" rx="11" fill="{t['chip']}" stroke="{t['line']}" stroke-opacity="{t['lo']}"/>
{T(W - 24.5 - tag_w / 2, 42.5, tag, "m10", t["muted"], "middle")}
{"".join(T(24, 102 + k * 21, ln, "r135", t["muted"]) for k, ln in enumerate(desc))}
{rule(t, 24, 146, W - 48)}
<circle cx="29" cy="171" r="5" fill="{r['color']}"/>
{T(41, 175.5, r["language"], "s13", t["muted"])}
{icon("s:star", sx, 164, 14, t["muted"], 1.7)}
{T(sx + 19, 175.5, f"{r['stars']:,}", "s13", t["muted"])}
{T(W - 24, 175.5, topics, "r12", t["subtle"], "end")}"""
    return svg(W, H, body, f"{pretty(r['name'])}: {r['description']}")


def stack(t: dict) -> str:
    W, rh, gap, x0, pad = 880, 32, 8, 152, 60
    cw = lambda s: 11 + 16 + 8 + tw(s, 13) + 12
    items, y = [], pad
    for gi, (label, entries) in enumerate(STACK):
        if gi:
            items.append(rule(t, 28, y + 8, W - 56, -0.04))
            y += 17
        items.append(T(28, y + 20.5, label, "lab", t["subtle"]))
        x = x0
        for name, ic in entries:
            w = cw(name)
            if x + w > W - 28:
                x, y = x0, y + rh + gap
            col = BRAND.get(ic, t["text"])
            if contrast(col, t["chip"]) < 1.7:
                col = t["text"]
            items.append(
                f'<rect x="{n(x + .5)}" y="{y + .5}" width="{n(w - 1)}" height="{rh - 1}" rx="8" fill="{t["chip"]}" '
                f'stroke="{t["line"]}" stroke-opacity="{t["lo"] - .02:.2f}"/>'
                + icon(ic, x + 11, y + 8, 16, col) + T(x + 35, y + 20.5, name, "s13", t["text"]))
            x += w + 8
        y += rh
    H = int(y + 28)
    return svg(W, H, card(t, W, H, "".join(items), "STACK", "04"),
               "Stack: " + ", ".join(nm for _, e in STACK for nm, _ in e))


def credentials(t: dict) -> str:
    W = 880
    colw = (W - 56) / 2
    heights = [24 + len(r) * 42 for _, r in CREDENTIALS]
    row1 = max(heights[0], heights[1])
    H = int(60 + row1 + 26 + max(heights[2], heights[3]) + 18)
    parts = [vrule(t, W / 2, 60, H - 84), rule(t, 28, 60 + row1 + 8, W - 56)]
    for i, (label, rows) in enumerate(CREDENTIALS):
        x = 28 if i % 2 == 0 else W / 2 + 24
        y = 60 if i < 2 else 60 + row1 + 26
        parts.append(T(x, y + 10, label, "lab", t["a1"]))
        for j, (a, b) in enumerate(rows):
            ry = y + 24 + j * 42
            parts.append(T(x, ry + 15, a, "b14", t["text"]) + T(x, ry + 33, b, "r12", t["muted"]))
    return svg(W, H, card(t, W, H, "".join(parts), "EDUCATION & CREDENTIALS", "05"),
               "; ".join(f"{a}, {b}" for _, r in CREDENTIALS for a, b in r))


def activity(t: dict, d: dict) -> str:
    W, H = 880, 338
    fmt = lambda v: f"{v:,}"
    stats = [(fmt(d["contributions"]), "CONTRIBUTIONS", "in the past 12 months"),
             (fmt(d["stars"]), "STARS", "across my repositories"),
             (fmt(d["releases"]), "RELEASES", "shipped to date"),
             (fmt(d["repos"]), "REPOSITORIES", "original and public")]
    parts = []
    colw = (W - 56) / 4
    for i, (v, lab, sub) in enumerate(stats):
        x = 28 + i * colw + (16 if i else 0)
        if i:
            parts.append(vrule(t, x - 16, 62, 64))
        parts.append(T(x, 72, lab, "lab", t["subtle"]) + T(x - 1.5, 108, v, "num", t["text"]) + T(x, 126, sub, "r12", t["muted"]))
    parts.append(rule(t, 28, 150, W - 56))

    counts = sorted(c for w in d["weeks"] for _, c in w if c)
    q = [counts[int(len(counts) * f)] for f in (.25, .5, .75)] if counts else [0, 0, 0]
    lvl = lambda c: 0 if not c else 1 + sum(c > v for v in q)
    step, weeks = 14, d["weeks"]
    gw = len(weeks) * step - 3
    gx, gy = round((W - gw) / 2), 196
    first = dt.date.fromisoformat(d["first_day"]) - dt.timedelta(days=weeks[0][0][0])
    defs = f'<rect id="q" width="11" height="11" rx="2.5"/>'
    last = -9
    for wi, week in enumerate(weeks):
        for wd, c in week:
            parts.append(f'<use href="#q" xlink:href="#q" x="{gx + wi * step}" y="{gy + wd * step}" class="h{lvl(c)}"/>')
        sun = first + dt.timedelta(days=wi * 7)
        if sun.day <= 7 and wi - last >= 3 and wi < len(weeks) - 1:
            parts.append(T(gx + wi * step, gy - 10, sun.strftime("%b"), "m10", t["subtle"]))
            last = wi
    fy = gy + 7 * step + 20
    lx = gx + gw - 5 * step - 34
    parts.append(T(gx, fy, f"Updated {d['fetched']}", "m10", t["subtle"]))
    parts.append(T(lx - 8, fy, "Less", "m10", t["subtle"], "end"))
    parts += [f'<use href="#q" xlink:href="#q" x="{lx + i * step}" y="{fy - 10}" class="h{i}"/>' for i in range(5)]
    parts.append(T(lx + 5 * step + 5, fy, "More", "m10", t["subtle"]))
    css = "".join(f".h{i}{{fill:{c}}}" for i, c in enumerate(t["heat"]))
    body = f"<defs>{defs}</defs>" + "".join(parts)
    return svg(W, H, card(t, W, H, body, "ACTIVITY", "06"),
               f"{fmt(d['contributions'])} contributions in the past year, {d['stars']} stars, "
               f"{d['releases']} releases, {d['repos']} public repositories", css)


# ==========================================================================
# README
# ==========================================================================

def pic(name: str, alt: str, attrs: str = 'width="100%"') -> str:
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/dark/{name}.svg">'
            f'<img src="assets/light/{name}.svg" {attrs} alt="{escape(alt)}"></picture>')


def readme(d: dict) -> str:
    btns = "&nbsp;".join(f'<a href="{h}">{pic("btn-" + s, l, "height=\"38\"")}</a>' for s, l, _, h in LINKS)
    stack_alt = "; ".join(f"{g.title()}: {', '.join(nm for nm, _ in e)}" for g, e in STACK)
    blocks = [
        f'<div align="center">\n\n{pic("hero", NAME + ". " + " ".join(TAGLINE))}\n\n{btns}\n\n</div>',
        pic("about", " ".join(ABOUT)),
        pic("section-work", "Selected work") + "\n" + "\n".join(
            "<p>\n" + "\n".join(f'<a href="{r["url"]}">{pic("project-" + r["name"].lower(), pretty(r["name"]) + ": " + r["description"], "width=\"49%\"")}</a>'
                                 for r in d["pinned"][k:k + 2]) + "\n</p>"
            for k in range(0, len(d["pinned"]), 2)),
        pic("focus", "; ".join(f"{a}: {' '.join(c)}" for _, _, a, c in FOCUS)),
        pic("stack", stack_alt),
        pic("credentials", "; ".join(f"{a}, {b}" for _, r in CREDENTIALS for a, b in r)),
        pic("activity", "Contribution activity over the past year, refreshed daily"),
        '<div align="center"><sub>'
        '<a href="https://github.com/Kernel-Hunter?tab=repositories&amp;type=source">all repositories</a> &nbsp;·&nbsp; '
        '<a href="mailto:karim.masmoudi.pro@gmail.com">karim.masmoudi.pro@gmail.com</a></sub></div>',
    ]
    return "\n\n".join(blocks) + "\n"


def main() -> None:
    d = load_data("--offline" in sys.argv)
    for theme, t in THEMES.items():
        out = ASSETS / theme
        out.mkdir(parents=True, exist_ok=True)
        for old in out.glob("*.svg"):
            old.unlink()
        files = {"hero": hero(t), "about": about(t), "focus": focus(t), "stack": stack(t),
                 "credentials": credentials(t), "activity": activity(t, d)}
        for i, (slug, label, ic, _) in enumerate(LINKS):
            files["btn-" + slug] = button(t, label, ic, i == 0)
        files["section-work"] = section_header(t, "02", "SELECTED WORK")
        for i, r in enumerate(d["pinned"]):
            files["project-" + r["name"].lower()] = project(t, r, i)
        for k, v in files.items():
            (out / f"{k}.svg").write_text(v)
    (ROOT / "README.md").write_text(readme(d))
    print(f"built {len(files)} SVGs x {len(THEMES)} themes and README.md")


if __name__ == "__main__":
    main()
