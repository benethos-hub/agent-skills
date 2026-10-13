# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.5.0"]
# ///
"""Render the PNGs in brand/ from brand/icon.svg.

- icon.png, 512x512, the fallback for places that show no SVG.
- social-preview.png, 1280x640, the image GitHub shows when the repository
  link is shared. It is uploaded by hand under Settings > General > Social
  preview, there is no API for it.

Run it after every change to the SVG or to the text below and commit the
results together:

    uv run assets/render_brand.py

uv reads the dependency above and runs the script in a throwaway environment,
so the renderer never enters the repository's own tooling, which uses the
standard library only. resvg is pinned because another version may draw the
same SVG a few pixels differently. The preview's text is set in the system's
sans-serif font, so it was rendered on Windows (Segoe UI) and looks a little
different elsewhere.
"""

from __future__ import annotations

import re
from pathlib import Path

import resvg_py

BRAND = Path(__file__).resolve().parent / "brand"
ICON_SVG = BRAND / "icon.svg"
ICON_PNG = BRAND / "icon.png"
ICON_SIZE = 512
PREVIEW_PNG = BRAND / "social-preview.png"
PREVIEW_WIDTH, PREVIEW_HEIGHT = 1280, 640

# The preview's words and colours. The colours come from the icon: its deep
# blue for the ground, its cyan and violet for the accents.
PREVIEW = """\
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640"
     viewBox="0 0 1280 640">
  <defs>
    <linearGradient id="sp-bg" x1="0" y1="0" x2="0.35" y2="1">
      <stop offset="0%" stop-color="#1B2457"/>
      <stop offset="100%" stop-color="#06091A"/>
    </linearGradient>
    <linearGradient id="sp-line" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#22D3EE"/>
      <stop offset="100%" stop-color="#7C6BFF"/>
    </linearGradient>
  </defs>
  <rect width="1280" height="640" fill="url(#sp-bg)"/>
  {pattern}
  <rect x="0" y="632" width="1280" height="8" fill="url(#sp-line)" opacity="0.7"/>
  {backdrop}
  {icon}
  <g font-family="Segoe UI, Inter, Helvetica, Arial, sans-serif">
    <text x="380" y="200" font-family="Consolas, Menlo, monospace" font-size="26"
          fill="#22D3EE">benethos-hub/agent-skills</text>
    <text x="380" y="282" font-size="68" font-weight="700" fill="#F8FAFC"
          >Agent Skills</text>
    <text x="380" y="346" font-size="25" fill="#CBD5E1"
          >Skills for AI agents to the open Agent Skills standard.</text>
    {chips}
    <text x="380" y="500" font-size="18" fill="#7C8AB8"
          >Open source under the MIT License.</text>
  </g>
</svg>
"""

# A faint editor window behind the text on the right, holding the head of a
# SKILL.md. Placeholders instead of a real skill, so it names no category and
# does not go stale. Each line is a key and its value, or plain text.
BACKDROP_LINES = (
    ("---", ""),
    ("name: ", "skill-name"),
    ("description: ", "What it does and"),
    ("", "  when an agent should use it."),
    ("license: ", "MIT"),
    ("---", ""),
    ("# Skill name", ""),
)

CHIPS = ("Agent Skills standard", "Claude Code marketplace", "ZIP per skill", "Tested")


def _chips(x: int, y: int) -> str:
    """Rounded labels in one row. Widths are estimated from the text length."""
    parts = []
    for label in CHIPS:
        width = round(len(label) * 9.3) + 40
        parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="38" rx="19" '
            'fill="#22D3EE" fill-opacity="0.10" '
            'stroke="#22D3EE" stroke-opacity="0.45"/>'
            f'<text x="{x + width / 2}" y="{y + 26}" font-size="19" fill="#E2E8F0" '
            f'text-anchor="middle">{label}</text>'
        )
        x += width + 14
    return "".join(parts)


# Circuit traces like the ones in the icon, kept to the edges and away from
# the text. Each is a list of points, the last one gets a node.
TRACES = (
    ((0, 92), (130, 92), (170, 132), (232, 132)),
    ((0, 548), (210, 548), (250, 588), (330, 588)),
    ((1280, 560), (1120, 560), (1080, 520), (960, 520)),
    ((1280, 352), (1236, 352), (1206, 382)),
)


def _pattern() -> str:
    """The ground behind everything: two soft glows, a dot grid fading out
    to the left and a few circuit traces at the edges."""
    defs = (
        "<defs>"
        '<radialGradient id="pt-violet" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#7C6BFF" stop-opacity="0.35"/>'
        '<stop offset="1" stop-color="#7C6BFF" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="pt-cyan" cx="0.5" cy="0.5" r="0.5">'
        '<stop offset="0" stop-color="#22D3EE" stop-opacity="0.18"/>'
        '<stop offset="1" stop-color="#22D3EE" stop-opacity="0"/></radialGradient>'
        '<pattern id="pt-dots" width="28" height="28" patternUnits="userSpaceOnUse">'
        '<circle cx="14" cy="14" r="1.4" fill="#A5B4FC"/></pattern>'
        '<linearGradient id="pt-fade" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0.25" stop-color="#FFFFFF" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#FFFFFF" stop-opacity="1"/></linearGradient>'
        '<mask id="pt-mask"><rect width="1280" height="640" fill="url(#pt-fade)"/></mask>'
        "</defs>"
    )
    glows = (
        '<ellipse cx="200" cy="320" rx="360" ry="300" fill="url(#pt-violet)"/>'
        '<ellipse cx="1120" cy="600" rx="420" ry="260" fill="url(#pt-cyan)"/>'
    )
    dots = '<rect width="1280" height="640" fill="url(#pt-dots)" opacity="0.22" mask="url(#pt-mask)"/>'
    traces = ['<g fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.16">']
    for points in TRACES:
        line = " ".join(f"{x},{y}" for x, y in points)
        end_x, end_y = points[-1]
        traces.append(
            f'<polyline points="{line}"/>'
            f'<circle cx="{end_x}" cy="{end_y}" r="5" fill="#06091A"/>'
        )
    traces.append("</g>")
    return defs + glows + dots + "".join(traces)


def _backdrop(x: int, bottom: int, width: int, opacity: float) -> str:
    """The editor window with the SKILL.md head, faint enough to read past.

    It starts above the image and runs past its right edge, so only its left
    and bottom border show, as if cut out of a larger screen.
    """
    first_line = bottom - 28 * len(BACKDROP_LINES) - 10
    parts = [
        f'<g opacity="{opacity}">',
        f'<rect x="{x}" y="-40" width="{width}" height="{bottom + 40}" rx="16" '
        'fill="#0B1030" stroke="#22D3EE" stroke-width="2"/>',
        '<g font-family="Consolas, Menlo, monospace" font-size="20">',
    ]
    for i, (key, value) in enumerate(BACKDROP_LINES):
        parts.append(
            f'<text x="{x + 28}" y="{first_line + 28 * i}" xml:space="preserve">'
            f'<tspan fill="#7C6BFF">{key}</tspan><tspan fill="#22D3EE">{value}</tspan></text>'
        )
    parts.append("</g></g>")
    return "".join(parts)


def _icon(x: int, y: int, size: int) -> str:
    """icon.svg as a nested svg, its ids prefixed so they cannot clash."""
    svg = ICON_SVG.read_text(encoding="utf-8")
    view_box = re.search(r'viewBox="([^"]+)"', svg).group(1)
    svg = re.sub(r'id="([^"]+)"', r'id="ic-\1"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", r"url(#ic-\1)", svg)
    return re.sub(
        r"<svg [^>]*>",
        f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{view_box}">',
        svg,
        count=1,
    )


def render(svg: str, width: int, height: int, target: Path) -> None:
    png = resvg_py.svg_to_bytes(svg_string=svg, width=width, height=height)
    target.write_bytes(png)
    print(f"{target.name}: {width}x{height}, {len(png)} bytes")


def main() -> None:
    render(ICON_SVG.read_text(encoding="utf-8"), ICON_SIZE, ICON_SIZE, ICON_PNG)
    preview = PREVIEW.format(
        pattern=_pattern(),
        backdrop=_backdrop(900, 262, 440, 0.22),
        icon=_icon(80, 200, 240),
        chips=_chips(380, 408),
    )
    render(preview, PREVIEW_WIDTH, PREVIEW_HEIGHT, PREVIEW_PNG)


if __name__ == "__main__":
    main()
