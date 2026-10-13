"""Shared helpers for the tests: the repository's paths and a small Markdown reader."""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Top-level folders that are not a category.
NOT_CATEGORIES = {"tests"}


def load_skills_module():
    """Import .github/scripts/skills.py, which is not on the import path."""
    path = ROOT / ".github" / "scripts" / "skills.py"
    spec = importlib.util.spec_from_file_location("skills", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


skills = load_skills_module()


def categories() -> list[Path]:
    return sorted(
        p
        for p in ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".") and p.name not in NOT_CATEGORIES
    )


def skill_folders(category: Path) -> list[Path]:
    return sorted(p for p in category.iterdir() if p.is_dir())


def markdown_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(ROOT).parts[:-1])
    )


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


# --- Markdown -------------------------------------------------------------

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


@dataclass
class Line:
    number: int
    text: str  # the line with inline code removed


def prose_lines(text: str) -> list[Line]:
    """The lines outside fenced code blocks, with inline code removed.

    What is left is what a reader sees as running text, headings and tables,
    the part the link and text checks apply to.
    """
    lines: list[Line] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(Line(number, INLINE_CODE.sub("", line)))
    return lines


def slug(heading: str) -> str:
    """The anchor GitHub gives a heading."""
    text = LINK.sub(r"\1", heading).replace("`", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


@dataclass
class Heading:
    level: int
    title: str
    anchor: str


def headings(text: str) -> list[Heading]:
    found: list[Heading] = []
    seen: dict[str, int] = {}
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        match = None if in_fence else HEADING.match(line)
        if not match:
            continue
        anchor = slug(match.group(2))
        # GitHub numbers a repeated anchor: name, name-1, name-2.
        if anchor in seen:
            seen[anchor] += 1
            anchor = f"{anchor}-{seen[anchor]}"
        else:
            seen[anchor] = 0
        found.append(Heading(len(match.group(1)), match.group(2), anchor))
    return found


@dataclass
class Link:
    number: int
    target: str


def links(text: str) -> list[Link]:
    return [
        Link(line.number, match.group(2))
        for line in prose_lines(text)
        for match in LINK.finditer(line.text)
    ]
