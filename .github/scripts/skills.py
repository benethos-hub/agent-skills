"""Check the skills in this repository and build what is delivered from them.

A skill is a folder <category>/<skill-name>/ with a SKILL.md. Two commands:

    python3 .github/scripts/skills.py pack OUT_DIR [--version X.Y.Z]
    python3 .github/scripts/skills.py marketplace [--check]
    python3 .github/scripts/skills.py version [--tag vX.Y.Z] [--notes]

`pack` writes one ZIP per skill into OUT_DIR, named <skill-name>.zip. Each
holds exactly that one folder, under its skill name and without the
category, which is the shape claude.ai and Claude Desktop take as an upload.
Next to them goes skills.json, an index with each skill's header, download
links, size and SHA-256. --version names the release the links point to.

`marketplace` writes .claude-plugin/marketplace.json, through which Claude
Code installs every skill as a plugin of its own, and the MCP servers listed
in MCP_PLUGINS as well. With --check it writes
nothing and fails if the file in the repository is not what it would write.

`version` prints the newest version in CHANGELOG.md. With --tag it fails
unless the tag is that version with a leading v. With --notes it prints that
version's section instead, as release notes.

`pack` and `marketplace` check every skill first and stop with a list of
problems if one fails.
Only the standard library is used, so the script runs on a bare runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "benethos-hub/agent-skills")
REPOSITORY_URL = f"https://github.com/{REPOSITORY}"
MARKETPLACE_FILE = ROOT / ".claude-plugin" / "marketplace.json"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
VERSION_HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})$", re.MULTILINE)
MARKETPLACE_NAME = "benethos-agent-skills"
OWNER = "Benedikt Oswald"

# MCP servers the marketplace offers next to the skills, each as a plugin of
# its own. Claude Code only, a ZIP cannot carry a server. No skill depends on
# them, because the skills work with any provider of the same data.
MCP_PLUGINS = [
    {
        "name": "benethos-yahoo-finance-mcp",
        "description": (
            "Market data from Yahoo Finance as an MCP server, for the finance skills. "
            "Read-only, no account and no API key. Needs uv."
        ),
        "category": "finance",
        "license": "MIT",
        "repository": "https://github.com/benethos-hub/yahoo-finance-mcp",
        "mcpServers": {
            "benethos-yahoo-finance-mcp": {
                "command": "uvx",
                "args": ["benethos-yahoo-finance-mcp"],
            }
        },
    },
]

# Limits of the Agent Skills specification (agentskills.io/specification).
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024

# Never part of a delivered skill: test material and local leftovers.
EXCLUDED_DIRS = {"evals", "__pycache__", ".pytest_cache", "node_modules"}
EXCLUDED_FILES = {".DS_Store", "Thumbs.db", "desktop.ini"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}

# A fixed date for every entry, so the same content gives the same bytes.
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


@dataclass
class Skill:
    folder: Path
    header: dict[str, str]

    @property
    def name(self) -> str:
        return self.folder.name

    @property
    def category(self) -> str:
        return self.folder.parent.name

    @property
    def path(self) -> str:
        return self.folder.relative_to(ROOT).as_posix()


def read_header(skill_md: Path) -> dict[str, str]:
    """Return the top-level `key: value` pairs of the YAML header.

    A small reader instead of a YAML library, enough for the flat headers
    used here. A value in double or single quotes loses its quotes. Nested
    keys are skipped.
    """
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md does not start with a --- header")
    header: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return header
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        header[key.strip()] = value
    raise ValueError("the header of SKILL.md is not closed by ---")


def load_skills() -> list[Skill]:
    """Read and check every skill. Exit with a list of problems if one fails."""
    folders = sorted(p.parent for p in ROOT.glob("*/*/SKILL.md"))
    if not folders:
        sys.exit("No skills found.")
    skills: list[Skill] = []
    problems: list[str] = []
    seen: dict[str, str] = {}
    for folder in folders:
        where = folder.relative_to(ROOT).as_posix()
        try:
            header = read_header(folder / "SKILL.md")
        except ValueError as error:
            problems.append(f"{where}: {error}")
            continue
        name = header.get("name", "")
        description = header.get("description", "")
        if not name:
            problems.append(f"{where}: the header has no name")
        elif name != folder.name:
            problems.append(f"{where}: name '{name}' differs from the folder name")
        elif len(name) > NAME_MAX or not NAME_PATTERN.match(name):
            problems.append(
                f"{where}: name '{name}' must be lower-case letters, digits and "
                f"single hyphens, at most {NAME_MAX} characters"
            )
        if not description:
            problems.append(f"{where}: the header has no description")
        elif len(description) > DESCRIPTION_MAX:
            problems.append(
                f"{where}: description has {len(description)} characters, "
                f"at most {DESCRIPTION_MAX} are allowed"
            )
        # ZIPs and plugins carry the skill name only, so two categories cannot share one.
        if folder.name in seen:
            problems.append(f"{where}: the skill name is already used by {seen[folder.name]}")
        seen[folder.name] = where
        skills.append(Skill(folder, header))
    if problems:
        print("The skills do not pass the check:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        sys.exit(1)
    return skills


def included(path: Path, folder: Path) -> bool:
    parts = path.relative_to(folder).parts
    if any(part in EXCLUDED_DIRS for part in parts[:-1]):
        return False
    return path.name not in EXCLUDED_FILES and path.suffix not in EXCLUDED_SUFFIXES


def pack_one(skill: Skill, target: Path) -> int:
    files = sorted(
        (p for p in skill.folder.rglob("*") if p.is_file() and included(p, skill.folder)),
        key=lambda p: p.relative_to(skill.folder).as_posix(),
    )
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            arcname = f"{skill.name}/{path.relative_to(skill.folder).as_posix()}"
            entry = zipfile.ZipInfo(arcname, date_time=ZIP_DATE)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, path.read_bytes())
    return len(files)


def pack(out_dir: Path, version: str | None) -> None:
    skills = load_skills()
    out_dir.mkdir(parents=True, exist_ok=True)
    latest = f"{REPOSITORY_URL}/releases/latest/download"
    index: list[dict[str, object]] = []
    for skill in skills:
        target = out_dir / f"{skill.name}.zip"
        count = pack_one(skill, target)
        data = target.read_bytes()
        url = f"{latest}/{target.name}"
        if version:
            url = f"{REPOSITORY_URL}/releases/download/v{version}/{target.name}"
        index.append(
            {
                "name": skill.name,
                "category": skill.category,
                "description": skill.header["description"],
                "license": skill.header.get("license"),
                "path": skill.path,
                "url": url,
                "latest_url": f"{latest}/{target.name}",
                "size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
        print(f"{skill.path}: {count} files -> {target.name}")
    document = {"repository": REPOSITORY_URL, "version": version, "skills": index}
    write_json(out_dir / "skills.json", document)
    print(f"index: {len(index)} skills -> skills.json")


def marketplace_document(skills: list[Skill]) -> dict[str, object]:
    # One plugin per skill, so each can be installed alone, as with the ZIPs.
    # The source is the repository root, and with strict off the entry itself
    # names the one skill folder the plugin loads. The MCP servers follow.
    servers = [{**plugin, "source": "./", "strict": False} for plugin in MCP_PLUGINS]
    taken = {skill.name for skill in skills} & {plugin["name"] for plugin in MCP_PLUGINS}
    if taken:
        sys.exit(f"Plugin names used by a skill and an MCP server: {', '.join(sorted(taken))}")
    return {
        "name": MARKETPLACE_NAME,
        "owner": {"name": OWNER},
        "metadata": {
            "description": "Skills for AI agents to the open Agent Skills standard.",
        },
        "plugins": [
            {
                "name": skill.name,
                "description": skill.header["description"],
                "source": "./",
                "strict": False,
                "category": skill.category,
                "license": skill.header.get("license"),
                "repository": REPOSITORY_URL,
                "skills": [f"./{skill.path}"],
            }
            for skill in skills
        ]
        + servers,
    }


def marketplace(check: bool) -> None:
    expected = to_json(marketplace_document(load_skills()))
    relative = MARKETPLACE_FILE.relative_to(ROOT).as_posix()
    if check:
        current = MARKETPLACE_FILE.read_text(encoding="utf-8") if MARKETPLACE_FILE.exists() else ""
        if current != expected:
            sys.exit(
                f"{relative} does not match the skills. "
                "Run: python3 .github/scripts/skills.py marketplace"
            )
        print(f"{relative} matches the skills.")
        return
    MARKETPLACE_FILE.parent.mkdir(exist_ok=True)
    MARKETPLACE_FILE.write_text(expected, encoding="utf-8", newline="\n")
    print(f"wrote {relative}")


def current_version(changelog: str) -> tuple[str, str]:
    """The newest released version in the changelog and its section text."""
    match = VERSION_HEADING.search(changelog)
    if not match:
        sys.exit("CHANGELOG.md has no heading of the form '## [X.Y.Z] - YYYY-MM-DD'.")
    rest = changelog[match.end() :]
    end = re.search(r"^## ", rest, re.MULTILINE)
    notes = rest[: end.start()] if end else rest
    return match.group(1), notes.strip() + "\n"


def version(tag: str | None, notes: bool) -> None:
    number, section = current_version(CHANGELOG_FILE.read_text(encoding="utf-8"))
    if tag is not None and tag != f"v{number}":
        sys.exit(f"Tag '{tag}' is not the newest version in CHANGELOG.md, which is {number}.")
    print(section if notes else number, end="" if notes else "\n")


def to_json(document: object) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def write_json(path: Path, document: object) -> None:
    path.write_text(to_json(document), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    pack_parser = commands.add_parser("pack", help="write the ZIPs and skills.json")
    pack_parser.add_argument("out_dir", type=Path)
    pack_parser.add_argument("--version", help="the release X.Y.Z the index links to")
    market_parser = commands.add_parser("marketplace", help="write .claude-plugin/marketplace.json")
    market_parser.add_argument("--check", action="store_true", help="only compare, write nothing")
    version_parser = commands.add_parser("version", help="print the version in CHANGELOG.md")
    version_parser.add_argument("--tag", help="fail unless this tag is v plus that version")
    version_parser.add_argument("--notes", action="store_true", help="print the version's section")
    args = parser.parse_args()
    if args.command == "pack":
        pack(args.out_dir, args.version)
    elif args.command == "marketplace":
        marketplace(args.check)
    else:
        version(args.tag, args.notes)


if __name__ == "__main__":
    main()
