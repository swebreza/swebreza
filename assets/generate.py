#!/usr/bin/env python3
"""Generate the animated SVGs used by the profile README.

Everything here is driven by counted git data, not estimates. Regenerate the
commit numbers with:

    for d in */; do
      [ -d "$d/.git" ] || continue
      n=$(git -C "$d" log --author="swebreza" --oneline | wc -l)
      echo "$n  $d"
    done | sort -rn

Two files are written per chart, one per colour scheme, because GitHub renders
READMEs in both light and dark and an SVG loaded through <img> cannot read the
page theme. The README pairs them with <picture>.

Usage:  python assets/generate.py
"""

from datetime import date
from pathlib import Path

OUT = Path(__file__).parent

# --- verified data ----------------------------------------------------------

# (vertical, commits, first commit, last commit)
VERTICALS = [
    ("Emireq",    462, date(2026, 3, 18), date(2026, 8, 26)),
    ("Hashtora",  298, date(2026, 5, 22), date(2026, 8, 26)),
    ("Zymedics",  290, date(2026, 4, 21), date(2026, 8, 25)),
    ("Credorz",    86, date(2026, 7, 14), date(2026, 7, 30)),
    ("DataZonn",   37, date(2026, 8,  6), date(2026, 8, 14)),
    ("Takafulik",   7, date(2026, 4, 16), date(2026, 4, 16)),
]

TOTAL_COMMITS = 1350
TOTAL_REPOS = 17

WINDOW_START = date(2026, 3, 1)
WINDOW_END = date(2026, 9, 1)

MONTHS = [
    (date(2026, 3, 1), "MAR"),
    (date(2026, 4, 1), "APR"),
    (date(2026, 5, 1), "MAY"),
    (date(2026, 6, 1), "JUN"),
    (date(2026, 7, 1), "JUL"),
    (date(2026, 8, 1), "AUG"),
]

THEMES = {
    "dark":  dict(ink="#ECEAE5", muted="#8B8983", line="#2A2A30",
                  accent="#E4384A", accent_soft="#8A2733", blue="#5FA8FF",
                  track="#17171B"),
    "light": dict(ink="#1B1B1F", muted="#6B6A66", line="#DFDFE4",
                  accent="#D22D40", accent_soft="#E0788A", blue="#1F6FD0",
                  track="#F1F1F4"),
}

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --- chart 1: commits per vertical ------------------------------------------

def commits_chart(t: dict) -> str:
    row_h, top, left, bar_left = 34, 74, 0, 132
    width, right_pad = 840, 74
    bar_max = width - bar_left - right_pad
    peak = max(v[1] for v in VERTICALS)
    height = top + row_h * len(VERTICALS) + 26

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Commits per product vertical: '
        + ", ".join(f"{n} {c}" for n, c, _, _ in VERTICALS) + '">',
        "<style>"
        f".t{{font-family:{MONO};}}"
        f".h{{font-family:{SANS};font-weight:600;}}"
        "@media (prefers-reduced-motion: reduce){"
        ".bar,.val{animation:none !important;}"
        ".bar{transform:scaleX(1) !important;}"
        ".val{opacity:1 !important;}}"
        ".bar{transform-origin:left center;animation:grow .95s cubic-bezier(.2,.7,.3,1) both;}"
        ".val{animation:fade .5s ease-out both;}"
        "@keyframes grow{from{transform:scaleX(0);}to{transform:scaleX(1);}}"
        "@keyframes fade{from{opacity:0;}to{opacity:1;}}"
        "</style>",
        f'<text x="0" y="26" class="h" font-size="17" fill="{t["ink"]}">'
        f"Commits per product vertical</text>",
        f'<text x="0" y="48" class="t" font-size="11.5" fill="{t["muted"]}" '
        f'letter-spacing="0.08em">{TOTAL_COMMITS} COMMITS  '
        f"·  {TOTAL_REPOS} REPOSITORIES  ·  MAR TO AUG 2026</text>",
        f'<line x1="0" y1="{top - 16}" x2="{width}" y2="{top - 16}" '
        f'stroke="{t["line"]}" stroke-width="1"/>',
    ]

    for i, (name, commits, _, _) in enumerate(VERTICALS):
        y = top + i * row_h
        w = max(2, round(bar_max * commits / peak))
        delay = 0.09 * i
        fill = t["accent"] if i == 0 else t["accent_soft"]

        p.append(
            f'<text x="0" y="{y + 15}" class="t" font-size="12.5" '
            f'fill="{t["ink"]}">{esc(name)}</text>'
        )
        p.append(
            f'<rect x="{bar_left}" y="{y + 3}" width="{bar_max}" height="15" '
            f'rx="1.5" fill="{t["track"]}"/>'
        )
        p.append(
            f'<rect class="bar" x="{bar_left}" y="{y + 3}" width="{w}" height="15" '
            f'rx="1.5" fill="{fill}" style="animation-delay:{delay:.2f}s"/>'
        )
        p.append(
            f'<text class="val t" x="{bar_left + w + 10}" y="{y + 15}" '
            f'font-size="12" fill="{t["muted"]}" '
            f'style="animation-delay:{delay + 0.55:.2f}s">{commits}</text>'
        )

    p.append("</svg>")
    return "\n".join(p)


# --- chart 2: build timeline ------------------------------------------------

def timeline_chart(t: dict) -> str:
    row_h, top, bar_left = 34, 98, 132
    width, right_pad = 840, 24
    span = width - bar_left - right_pad
    days = (WINDOW_END - WINDOW_START).days
    height = top + row_h * len(VERTICALS) + 30

    def x_of(d: date) -> float:
        return bar_left + span * ((d - WINDOW_START).days / days)

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Build timeline, March to August 2026: '
        + ", ".join(
            f"{n} from {s.strftime('%d %b')} to {e.strftime('%d %b')}"
            for n, _, s, e in VERTICALS
        ) + '">',
        "<style>"
        f".t{{font-family:{MONO};}}"
        f".h{{font-family:{SANS};font-weight:600;}}"
        "@media (prefers-reduced-motion: reduce){"
        ".sp{animation:none !important;transform:scaleX(1) !important;}}"
        ".sp{transform-origin:left center;"
        "animation:span 1s cubic-bezier(.2,.7,.3,1) both;}"
        "@keyframes span{from{transform:scaleX(0);}to{transform:scaleX(1);}}"
        "</style>",
        f'<text x="0" y="26" class="h" font-size="17" fill="{t["ink"]}">'
        f"Six verticals, built in parallel</text>",
        f'<text x="0" y="48" class="t" font-size="11.5" fill="{t["muted"]}" '
        f'letter-spacing="0.08em">FIRST COMMIT TO LAST, PER PRODUCT</text>',
    ]

    for d, label in MONTHS:
        x = x_of(d)
        p.append(
            f'<line x1="{x:.1f}" y1="{top - 24}" x2="{x:.1f}" '
            f'y2="{top + row_h * len(VERTICALS) - 6}" stroke="{t["line"]}" '
            f'stroke-width="1"/>'
        )
        p.append(
            f'<text x="{x + 6:.1f}" y="{top - 32}" class="t" font-size="10.5" '
            f'fill="{t["muted"]}" letter-spacing="0.12em">{label}</text>'
        )

    for i, (name, _, start, end) in enumerate(VERTICALS):
        y = top + i * row_h
        x0 = x_of(start)
        w = max(4, x_of(end) - x0)
        delay = 0.09 * i
        fill = t["accent"] if i == 0 else t["blue"]

        p.append(
            f'<text x="0" y="{y + 15}" class="t" font-size="12.5" '
            f'fill="{t["ink"]}">{esc(name)}</text>'
        )
        p.append(
            f'<rect class="sp" x="{x0:.1f}" y="{y + 4}" width="{w:.1f}" height="13" '
            f'rx="1.5" fill="{fill}" style="animation-delay:{delay:.2f}s"/>'
        )

    p.append("</svg>")
    return "\n".join(p)


def main() -> None:
    for theme, palette in THEMES.items():
        (OUT / f"commits-{theme}.svg").write_text(
            commits_chart(palette), encoding="utf8"
        )
        (OUT / f"timeline-{theme}.svg").write_text(
            timeline_chart(palette), encoding="utf8"
        )
    print(f"wrote 4 svgs to {OUT}")


if __name__ == "__main__":
    main()
