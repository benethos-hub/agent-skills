"""What leaves the repository: the ZIPs, skills.json, the marketplace and the
READMEs that point to them, plus the workflows that build them."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from support import ROOT, categories, rel, skill_folders, skills

MARKETPLACE = skills.MARKETPLACE_NAME


def header(name: str, description: str | None = None) -> str:
    """A closed SKILL.md header with a name and, if given, a description."""
    lines = ["---", f"name: {name}"]
    if description is not None:
        lines.append(f"description: {description}")
    return "\n".join([*lines, "---", ""])


def pack(out_dir: Path, version: str | None = None) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        skills.pack(out_dir, version)


class PackTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        pack(self.tmp, "9.9.9")
        self.index = json.loads((self.tmp / "skills.json").read_text(encoding="utf-8"))
        self.names = sorted(f.name for c in categories() for f in skill_folders(c))

    def test_two_zips_per_skill_and_the_index(self):
        written = sorted(p.name for p in self.tmp.iterdir())
        expected = [f"{n}.zip" for n in self.names]
        expected += [f"{n}-9.9.9.zip" for n in self.names]
        self.assertEqual(written, sorted([*expected, "skills.json"]))

    def test_versioned_zip_has_the_same_bytes(self):
        for name in self.names:
            with self.subTest(skill=name):
                self.assertEqual(
                    (self.tmp / f"{name}-9.9.9.zip").read_bytes(),
                    (self.tmp / f"{name}.zip").read_bytes(),
                )

    def test_without_a_version_only_the_stable_names(self):
        out = Path(tempfile.mkdtemp())
        pack(out)
        written = sorted(p.name for p in out.iterdir())
        expected = [f"{n}.zip" for n in self.names]
        self.assertEqual(written, sorted([*expected, "skills.json"]))

    def test_zip_holds_one_folder_with_skill_md(self):
        for name in self.names:
            with zipfile.ZipFile(self.tmp / f"{name}.zip") as archive:
                entries = archive.namelist()
            with self.subTest(skill=name):
                self.assertIn(f"{name}/SKILL.md", entries)
                self.assertEqual(
                    [e for e in entries if not e.startswith(f"{name}/")], []
                )

    def test_index_matches_the_archives(self):
        self.assertEqual(self.index["version"], "9.9.9")
        self.assertEqual([s["name"] for s in self.index["skills"]], self.names)
        for entry in self.index["skills"]:
            data = (self.tmp / f"{entry['name']}.zip").read_bytes()
            with self.subTest(skill=entry["name"]):
                self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())
                self.assertEqual(entry["size"], len(data))
                self.assertTrue(
                    entry["url"].endswith(
                        f"/releases/download/v9.9.9/{entry['name']}-9.9.9.zip"
                    )
                )
                self.assertTrue(
                    entry["latest_url"].endswith(
                        f"/releases/latest/download/{entry['name']}.zip"
                    )
                )
                self.assertTrue((ROOT / entry["path"] / "SKILL.md").is_file())

    def test_entries_are_stored_uncompressed(self):
        # Deflate output differs between zlib builds, stored entries do not.
        for name in self.names:
            with zipfile.ZipFile(self.tmp / f"{name}.zip") as archive:
                types = {entry.compress_type for entry in archive.infolist()}
                systems = {entry.create_system for entry in archive.infolist()}
            with self.subTest(skill=name):
                self.assertEqual(types, {zipfile.ZIP_STORED})
                # The system Python would write differs between Windows and Unix.
                self.assertEqual(systems, {3})

    def test_same_content_gives_same_bytes(self):
        again = Path(tempfile.mkdtemp())
        pack(again, "9.9.9")
        for name in self.names:
            with self.subTest(skill=name):
                self.assertEqual(
                    (self.tmp / f"{name}.zip").read_bytes(),
                    (again / f"{name}.zip").read_bytes(),
                )


class PackRulesTest(unittest.TestCase):
    """The checks and exclusions of skills.py, on a repository made up for the test."""

    def make_repo(self, files: dict[str, str]) -> Path:
        root = Path(tempfile.mkdtemp())
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return root

    def problems(self, root: Path) -> str:
        stderr = io.StringIO()
        with (
            mock.patch.object(skills, "ROOT", root),
            contextlib.redirect_stderr(stderr),
        ):
            with self.assertRaises(SystemExit):
                skills.load_skills()
        return stderr.getvalue()

    def test_broken_headers_are_rejected(self):
        root = self.make_repo(
            {
                "skills/a/good-one/SKILL.md": header("good-one", "fine"),
                "skills/a/Bad_Name/SKILL.md": header("Bad_Name", "x"),
                "skills/a/other/SKILL.md": header("different", "x"),
                "skills/a/no-description/SKILL.md": header("no-description"),
                "skills/a/too-long/SKILL.md": header("too-long", "x" * 1025),
                "skills/a/open-header/SKILL.md": "---\nname: open-header\n",
                "skills/b/good-one/SKILL.md": header("good-one", "twin"),
            }
        )
        report = self.problems(root)
        for expected in (
            "skills/a/Bad_Name: name 'Bad_Name' must be lower-case",
            "skills/a/other: name 'different' differs from the folder name",
            "skills/a/no-description: the header has no description",
            "skills/a/too-long: description has 1025 characters",
            "skills/a/open-header: the header of SKILL.md is not closed",
            "skills/b/good-one: the skill name is already used by skills/a/good-one",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, report)
        self.assertNotIn("skills/a/good-one:", report)

    def test_leftovers_stay_out_of_the_zip(self):
        root = self.make_repo(
            {
                "skills/a/kept/SKILL.md": "---\nname: kept\ndescription: x\n---\n",
                "skills/a/kept/references/notes.md": "notes",
                "skills/a/kept/evals/case.yaml": "x",
                "skills/a/kept/scripts/__pycache__/tool.cpython-312.pyc": "x",
                "skills/a/kept/scripts/tool.py": "print()",
                "skills/a/kept/.DS_Store": "x",
            }
        )
        out = Path(tempfile.mkdtemp())
        with mock.patch.object(skills, "ROOT", root):
            pack(out)
        with zipfile.ZipFile(out / "kept.zip") as archive:
            entries = sorted(archive.namelist())
        self.assertEqual(
            entries,
            ["kept/SKILL.md", "kept/references/notes.md", "kept/scripts/tool.py"],
        )


class MarketplaceTest(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / ".claude-plugin" / "marketplace.json"
        self.document = json.loads(self.path.read_text(encoding="utf-8"))

    def test_file_is_current(self):
        number, _ = skills.current_version(
            (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        )
        expected = skills.to_json(
            skills.marketplace_document(skills.load_skills(), number)
        )
        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            expected,
            "run: uv run .github/scripts/skills.py marketplace",
        )

    def test_every_skill_is_a_plugin(self):
        plugins = {p["name"]: p for p in self.document["plugins"]}
        for category in categories():
            for folder in skill_folders(category):
                with self.subTest(skill=folder.name):
                    self.assertIn(folder.name, plugins)
                    self.assertEqual(
                        plugins[folder.name]["skills"], [f"./{rel(folder)}"]
                    )
                    self.assertEqual(plugins[folder.name]["category"], category.name)

    def test_skills_come_from_the_current_release(self):
        number, _ = skills.current_version(
            (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        )
        names = {f.name for c in categories() for f in skill_folders(c)} | {
            c.name for c in categories()
        }
        for plugin in self.document["plugins"]:
            if plugin["name"] not in names:
                continue
            with self.subTest(plugin=plugin["name"]):
                self.assertEqual(plugin["version"], number)
                self.assertEqual(plugin["source"]["ref"], f"v{number}")
                # The "github" source clones over SSH, which fails without a key.
                self.assertEqual(plugin["source"]["source"], "url")
                self.assertTrue(plugin["source"]["url"].startswith("https://"))

    def test_every_category_is_a_bundle(self):
        plugins = {p["name"]: p for p in self.document["plugins"]}
        for category in categories():
            servers = [p for p in skills.MCP_PLUGINS if p["category"] == category.name]
            with self.subTest(category=category.name):
                self.assertIn(category.name, plugins)
                bundle = plugins[category.name]
                self.assertEqual(
                    bundle["skills"], [f"./{rel(f)}" for f in skill_folders(category)]
                )
                expected = {k: v for p in servers for k, v in p["mcpServers"].items()}
                self.assertEqual(bundle.get("mcpServers", {}), expected)

    def test_plugin_names_are_unique(self):
        names = [p["name"] for p in self.document["plugins"]]
        self.assertEqual(len(names), len(set(names)))


class ReadmeTest(unittest.TestCase):
    """The READMEs name every skill and every way to get it."""

    def test_root_readme_opens_with_the_badge_rows(self):
        # The rule of the organisation: CI, coverage and licence, then where
        # to get it, then the sponsor links, each row apart by a blank line.
        lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
        badges = [line.split("]")[0] for line in lines[2:11] if line]
        self.assertEqual(
            badges,
            [
                "[![CI",
                "[![Coverage",
                "[![License",
                "[![Release",
                "[![Sponsor",
                "[![PayPal",
            ],
        )
        self.assertEqual([lines[5], lines[7], lines[10]], ["", "", ""])

    def test_root_readme_lists_every_category_and_skill(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        rows = [line for line in text.splitlines() if line.startswith("| [")]
        listed = {}
        for row in rows:
            match = re.match(r"\| \[[^\]]+\]\(skills/([^/]+)/README\.md\)", row)
            self.assertIsNotNone(
                match,
                "the row does not start with a link to "
                f"skills/<category>/README.md: {row}",
            )
            category = match.group(1)
            listed[category] = sorted(
                re.findall(rf"\]\(skills/{category}/([^/]+)/SKILL\.md\)", row)
            )
        expected = {
            c.name: sorted(f.name for f in skill_folders(c)) for c in categories()
        }
        self.assertEqual(listed, expected)

    def test_category_readme_names_every_skill(self):
        for category in categories():
            text = (category / "README.md").read_text(encoding="utf-8")
            for folder in skill_folders(category):
                name = folder.name
                with self.subTest(skill=name):
                    self.assertIn(
                        f"]({name}/SKILL.md)", text, "no link to the SKILL.md"
                    )
                    self.assertIn(
                        f"/releases/latest/download/{name}.zip",
                        text,
                        "no download link",
                    )
                    self.assertIn(
                        f"claude plugin install {name}@{MARKETPLACE}",
                        text,
                        "no install command",
                    )

    def test_category_readme_names_its_bundle(self):
        for category in categories():
            text = (category / "README.md").read_text(encoding="utf-8")
            with self.subTest(category=category.name):
                self.assertIn(
                    f"claude plugin install {category.name}@{MARKETPLACE}", text
                )

    def test_category_readme_names_its_mcp_plugins(self):
        for plugin in skills.MCP_PLUGINS:
            text = (ROOT / "skills" / plugin["category"] / "README.md").read_text(
                encoding="utf-8"
            )
            with self.subTest(plugin=plugin["name"]):
                self.assertIn(
                    f"claude plugin install {plugin['name']}@{MARKETPLACE}", text
                )


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))

    def test_actions_are_pinned_to_a_commit(self):
        for path in self.workflows:
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1
            ):
                match = re.search(r"uses:\s*(\S+)", line)
                if not match or match.group(1).startswith("./"):
                    continue
                # Reusable workflows of the organisation follow its main, so a
                # change to a shared rule reaches every repository at once.
                if match.group(1).startswith("benethos-hub/.github/.github/workflows/"):
                    continue
                with self.subTest(line=f"{rel(path)}:{number}"):
                    self.assertRegex(
                        line,
                        r"@[0-9a-f]{40} # v\d",
                        "pin to a full SHA with the version as comment",
                    )

    def test_workflows_limit_the_token(self):
        for path in self.workflows:
            with self.subTest(workflow=rel(path)):
                self.assertRegex(
                    path.read_text(encoding="utf-8"),
                    r"(?m)^permissions:\n  contents: read$",
                )

    def test_workflows_run_existing_scripts(self):
        # Every path of a Python file in this repository a workflow names.
        script = re.compile(r"(?<![\w/.-])((?:\.github|assets|tests)/[\w./-]+\.py)")
        for path in self.workflows:
            for name in script.findall(path.read_text(encoding="utf-8")):
                with self.subTest(workflow=rel(path), script=name):
                    self.assertTrue((ROOT / name).is_file())

    def test_workflows_run_python_through_uv(self):
        for path in self.workflows:
            text = path.read_text(encoding="utf-8")
            with self.subTest(workflow=rel(path)):
                self.assertNotRegex(text, r"(?m)^\s*run: python3? ", "use uv run")


class CommandLineTest(unittest.TestCase):
    """skills.py as the workflows and the README call it."""

    def run_main(self, *args: str) -> str:
        out = io.StringIO()
        with (
            mock.patch.object(sys, "argv", ["skills.py", *args]),
            contextlib.redirect_stdout(out),
        ):
            skills.main()
        return out.getvalue()

    def test_version(self):
        number, _ = skills.current_version(
            (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        )
        self.assertEqual(self.run_main("version"), f"{number}\n")
        self.assertEqual(self.run_main("version", "--tag", f"v{number}"), f"{number}\n")
        self.assertTrue(self.run_main("version", "--notes").strip())

    def test_version_rejects_another_tag(self):
        with self.assertRaises(SystemExit):
            self.run_main("version", "--tag", "v0.0.0")

    def test_marketplace_check_passes(self):
        self.assertIn("matches the skills", self.run_main("marketplace", "--check"))

    def test_marketplace_writes_what_it_checks(self):
        # A missing file fails the check, the written one passes it and equals
        # the file in the repository.
        target = Path(tempfile.mkdtemp()) / ".claude-plugin" / "marketplace.json"
        with mock.patch.object(skills, "MARKETPLACE_FILE", target):
            with self.assertRaises(SystemExit):
                self.run_main("marketplace", "--check")
            self.run_main("marketplace")
            self.assertIn("matches the skills", self.run_main("marketplace", "--check"))
        committed = ROOT / ".claude-plugin" / "marketplace.json"
        self.assertEqual(
            target.read_text(encoding="utf-8"), committed.read_text(encoding="utf-8")
        )

    def test_pack(self):
        out = Path(tempfile.mkdtemp())
        self.run_main("pack", str(out), "--version", "9.9.9")
        self.assertTrue((out / "skills.json").is_file())


if __name__ == "__main__":
    unittest.main()
