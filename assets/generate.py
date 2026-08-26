#!/usr/bin/env python3
"""Generate the animated stack visual used by the profile README.

Deliberately carries no project names, no per-project figures and no dates.
It describes the toolset only, so there is nothing here that reveals anything
about an employer's roadmap.

Two files are written, one per colour scheme, because GitHub renders READMEs in
both light and dark and an SVG loaded through <img> cannot read the page theme.
The README pairs them with <picture>.

Usage:  python assets/generate.py
"""

import math
from pathlib import Path

OUT = Path(__file__).parent

W, H = 880, 430
CX, CY = W / 2, H / 2

# (radius, seconds per revolution, direction, [labels])
RINGS = [
    (88,  46, 1,  ["Python", "Django", "PostgreSQL"]),
    (146, 62, -1, ["TypeScript", "React", "Next.js", "React Native"]),
    (200, 84, 1,  ["GCP", "Docker", "Celery", "Redis", "pgvector", "Gemini"]),
]

THEMES = {
    "dark": dict(
        ink="#ECEAE5", muted="#8B8983", ring="#33333B",
        accent="#E4384A", blue="#5FA8FF", chip="#15151A", chip_line="#2E2E36",
    ),
    "light": dict(
        ink="#1B1B1F", muted="#6B6A66", ring="#D6D6DE",
        accent="#D22D40", blue="#1F6FD0", chip="#F7F7FA", chip_line="#C9C9D3",
    ),
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
CHAR_W, FONT = 6.35, 10.5


def chip(label: str, colour: str, t: dict) -> str:
    """A pill centred on its own origin, so it can be counter-rotated."""
    w = len(label) * CHAR_W + 22
    h = 24
    return (
        f'<rect x="{-w/2:.1f}" y="{-h/2}" width="{w:.1f}" height="{h}" rx="3" '
        f'fill="{t["chip"]}" stroke="{t["chip_line"]}" stroke-width="1"/>'
        f'<circle cx="{-w/2 + 9:.1f}" cy="0" r="2.4" fill="{colour}"/>'
        f'<text x="{-w/2 + 17:.1f}" y="3.6" font-family="{MONO}" '
        f'font-size="{FONT}" fill="{t["ink"]}">{label}</text>'
    )


def build(t: dict) -> str:
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Technology stack, arranged in three orbits. Core: Python, '
        f'Django, PostgreSQL. Interface: TypeScript, React, Next.js, React '
        f'Native. Platform: GCP, Docker, Celery, Redis, pgvector, Gemini.">',
        "<style>"
        "@media (prefers-reduced-motion: reduce){"
        "  .orbit,.pulse,.halo{animation:none !important;}"
        "}"
        ".orbit{animation:spin linear infinite;transform-box:view-box;}"
        ".anti{animation:anti linear infinite;transform-box:fill-box;"
        "transform-origin:center;}"
        f"@keyframes spin{{from{{transform:rotate(0deg);}}"
        f"to{{transform:rotate(360deg);}}}}"
        f"@keyframes anti{{from{{transform:rotate(0deg);}}"
        f"to{{transform:rotate(-360deg);}}}}"
        ".pulse{animation:pulse 3.2s ease-in-out infinite;transform-box:fill-box;"
        "transform-origin:center;}"
        "@keyframes pulse{0%,100%{opacity:.55;transform:scale(1);}"
        "50%{opacity:1;transform:scale(1.18);}}"
        ".halo{animation:halo 3.2s ease-in-out infinite;transform-box:fill-box;"
        "transform-origin:center;}"
        "@keyframes halo{0%{opacity:.5;transform:scale(.7);}"
        "70%,100%{opacity:0;transform:scale(2.4);}}"
        "</style>",
    ]

    # orbit paths
    for r, _, _, _ in RINGS:
        p.append(
            f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" '
            f'stroke="{t["ring"]}" stroke-width="1" stroke-dasharray="3 6"/>'
        )

    # centre
    p.append(
        f'<circle class="halo" cx="{CX}" cy="{CY}" r="14" fill="{t["accent"]}"/>'
    )
    p.append(
        f'<circle class="pulse" cx="{CX}" cy="{CY}" r="7" fill="{t["accent"]}"/>'
    )

    # orbiting chips
    for idx, (r, secs, direction, labels) in enumerate(RINGS):
        colour = [t["accent"], t["blue"], t["muted"]][idx]
        spin = "spin" if direction > 0 else "anti"
        anti = "anti" if direction > 0 else "spin"

        p.append(
            f'<g class="orbit" style="animation-name:{spin};'
            f'animation-duration:{secs}s;transform-origin:{CX}px {CY}px">'
        )
        for i, label in enumerate(labels):
            a = math.radians(360 * i / len(labels) - 90)
            x, y = CX + r * math.cos(a), CY + r * math.sin(a)
            p.append(
                f'<g transform="translate({x:.1f},{y:.1f})">'
                f'<g class="anti" style="animation-name:{anti};'
                f'animation-duration:{secs}s">{chip(label, colour, t)}</g></g>'
            )
        p.append("</g>")

    p.append("</svg>")
    return "\n".join(p)


def main() -> None:
    for theme, palette in THEMES.items():
        (OUT / f"stack-{theme}.svg").write_text(build(palette), encoding="utf8")
    print(f"wrote 2 svgs to {OUT}")


if __name__ == "__main__":
    main()
