# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.5.0"]
# ///
"""Render brand/icon.png, 512x512, from brand/icon.svg.

The PNG is the fallback for places that show no SVG. Run the script after
every change to the SVG and commit both together:

    uv run assets/render_icon.py

uv reads the dependency above and runs the script in a throwaway environment,
so the renderer never enters the repository's own tooling, which uses the
standard library only. resvg is pinned because another version may draw the
same SVG a few pixels differently.
"""

from __future__ import annotations

from pathlib import Path

import resvg_py

BRAND = Path(__file__).resolve().parent / "brand"
ICON_SVG = BRAND / "icon.svg"
ICON_PNG = BRAND / "icon.png"
ICON_SIZE = 512


def render(svg: str, width: int, height: int, target: Path) -> None:
    png = resvg_py.svg_to_bytes(svg_string=svg, width=width, height=height)
    target.write_bytes(png)
    print(f"{target.name}: {width}x{height}, {len(png)} bytes")


def main() -> None:
    render(ICON_SVG.read_text(encoding="utf-8"), ICON_SIZE, ICON_SIZE, ICON_PNG)


if __name__ == "__main__":
    main()
