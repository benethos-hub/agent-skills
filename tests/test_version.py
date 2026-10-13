"""The version: CHANGELOG.md names it, the Markdown files repeat it, the
release tag has to match it."""

from __future__ import annotations

import contextlib
import datetime
import io
import re
import unittest
from unittest import mock

from support import ROOT, markdown_files, rel, skills

# A version of this repository as the Markdown files write it.
VERSION_IN_TEXT = re.compile(r"\bv(\d+\.\d+\.\d+)\b")


def changelog() -> str:
    return (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")


class ChangelogTest(unittest.TestCase):
    def test_has_unreleased_section_first(self):
        sections = re.findall(r"^## (.+)$", changelog(), re.MULTILINE)
        self.assertTrue(sections, "CHANGELOG.md has no sections")
        self.assertEqual(sections[0], "[Unreleased]", "the first section is [Unreleased]")

    def test_every_version_section_has_the_form(self):
        sections = re.findall(r"^## (.+)$", changelog(), re.MULTILINE)[1:]
        for section in sections:
            with self.subTest(section=section):
                self.assertRegex(f"## {section}", skills.VERSION_HEADING)

    def test_versions_rise_and_dates_are_real(self):
        found = skills.VERSION_HEADING.findall(changelog())
        self.assertTrue(found, "CHANGELOG.md names no version")
        numbers = [tuple(int(n) for n in number.split(".")) for number, _ in found]
        self.assertEqual(numbers, sorted(numbers, reverse=True), "newest version first, no repeats")
        self.assertEqual(len(numbers), len(set(numbers)), "a version appears twice")
        dates = [datetime.date.fromisoformat(date) for _, date in found]
        self.assertEqual(dates, sorted(dates, reverse=True), "newest date first")


class VersionInTextTest(unittest.TestCase):
    def test_markdown_names_the_current_version(self):
        current, _ = skills.current_version(changelog())
        for path in markdown_files():
            if path.name == "CHANGELOG.md":
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                for found in VERSION_IN_TEXT.findall(line):
                    with self.subTest(line=f"{rel(path)}:{number}"):
                        self.assertEqual(
                            found,
                            current,
                            f"v{found} is not v{current}, the newest version in CHANGELOG.md",
                        )


class VersionCommandTest(unittest.TestCase):
    SAMPLE = (
        "# Changelog\n\n## [Unreleased]\n\n"
        "## [1.2.0] - 2026-11-01\n\nNotes for 1.2.0.\n\n### Added\n\n- A thing.\n\n"
        "## [1.1.0] - 2026-10-01\n\nOlder.\n"
    )

    def run_version(self, tag=None, notes=False) -> str:
        out = io.StringIO()
        with mock.patch.object(skills.Path, "read_text", return_value=self.SAMPLE), contextlib.redirect_stdout(out):
            skills.version(tag, notes)
        return out.getvalue()

    def test_newest_version_and_its_notes(self):
        number, notes = skills.current_version(self.SAMPLE)
        self.assertEqual(number, "1.2.0")
        self.assertEqual(notes, "Notes for 1.2.0.\n\n### Added\n\n- A thing.\n")

    def test_matching_tag_passes(self):
        self.assertEqual(self.run_version(tag="v1.2.0"), "1.2.0\n")

    def test_other_tag_fails(self):
        for tag in ("v1.1.0", "1.2.0", "v1.2.0-rc1"):
            with self.subTest(tag=tag), self.assertRaises(SystemExit):
                self.run_version(tag=tag)

    def test_notes_are_printed(self):
        self.assertTrue(self.run_version(notes=True).startswith("Notes for 1.2.0."))


if __name__ == "__main__":
    unittest.main()
